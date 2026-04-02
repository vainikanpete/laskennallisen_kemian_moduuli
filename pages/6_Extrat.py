import streamlit as st
import numpy as np
import scipy.linalg as la
import math
from numba import njit
from rdkit import Chem
from rdkit.Chem import AllChem
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ==========================================
# 1. UI ASETUKSET
# ==========================================
st.set_page_config(
    page_title="Extrat: Muita aiheita", 
    layout="wide"
)

st.title("Moduuli 6: Ekstraa - muita aiheita")
st.caption("Syventävää materiaalia molekyylien geometriasta ja laajoista hila-rakenteista")
st.divider()

# ==========================================
# 2. FYSIKAALISET FUNKTIOT JA DATA (YHTEISET)
# ==========================================

# --- WALSH DATA JA FUNKTIOT ---
basis_dict = {
    1: {'exps': [[3.42525091, 0.62391373, 0.1688554]], 
        'coeffs': [[0.15432897, 0.53532814, 0.44463454]], 
        'lmn': [[0, 0, 0]]},
    6: {'exps': [[71.616837, 13.045096, 3.5305122], [2.9412494, 0.6834831, 0.2222899], [2.9412494, 0.6834831, 0.2222899], [2.9412494, 0.6834831, 0.2222899]], 
        'coeffs': [[0.15432897, 0.53532814, 0.44463454], [-0.09996723, 0.39951283, 0.70011547], [-0.09996723, 0.39951283, 0.70011547], [-0.09996723, 0.39951283, 0.70011547]], 
        'lmn': [[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]]},
    7: {'exps': [[99.106169, 18.052312, 4.8856602], [3.7804559, 0.8784966, 0.2857144], [3.7804559, 0.8784966, 0.2857144], [3.7804559, 0.8784966, 0.2857144]], 
        'coeffs': [[0.15432897, 0.53532814, 0.44463454], [-0.09996723, 0.39951283, 0.70011547], [-0.09996723, 0.39951283, 0.70011547], [-0.09996723, 0.39951283, 0.70011547]], 
        'lmn': [[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]]},
    8: {'exps': [[130.7093214, 23.80886605, 6.443608313], [5.033151319, 1.169596125, 0.38038896], [5.033151319, 1.169596125, 0.38038896], [5.033151319, 1.169596125, 0.38038896]], 
        'coeffs': [[0.1543289673, 0.5353281423, 0.4446345422], [-0.09996722919, 0.3995128261, 0.7001154689], [-0.09996722919, 0.3995128261, 0.7001154689], [-0.09996722919, 0.3995128261, 0.7001154689]], 
        'lmn': [[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]]}
}

voip_dict = {1: [-13.6], 6: [-21.4, -11.4, -11.4, -11.4], 7: [-26.0, -13.4, -13.4, -13.4], 8: [-32.3, -14.8, -14.8, -14.8]}
A0 = 0.52917721092 

def flatten_basis(atoms, coords):
    exps, coeffs, norms, lmns, centers, h_ii = [], [], [], [], [], []
    cgf_pointers = [] 
    current_idx = 0
    for i, Z in enumerate(atoms):
        atom_basis = basis_dict[Z]
        atom_voips = voip_dict[Z]
        coord = coords[i]
        for b_idx in range(len(atom_basis['exps'])):
            prim_exps, prim_coeffs, lmn = atom_basis['exps'][b_idx], atom_basis['coeffs'][b_idx], atom_basis['lmn'][b_idx]
            n_prims = len(prim_exps)
            cgf_pointers.append([current_idx, current_idx + n_prims])
            h_ii.append(atom_voips[b_idx])
            for p in range(n_prims):
                alpha, c = prim_exps[p], prim_coeffs[p]
                L = sum(lmn)
                norm = (2 * alpha / np.pi)**0.75 * ((8 * alpha)**L * math.factorial(lmn[0]) * math.factorial(lmn[1]) * math.factorial(lmn[2]) / 
                        (math.factorial(2*lmn[0]) * math.factorial(2*lmn[1]) * math.factorial(2*lmn[2])))**0.5
                exps.append(alpha); coeffs.append(c); norms.append(norm); lmns.append(lmn); centers.append(coord)
                current_idx += 1
    return (np.array(cgf_pointers, dtype=np.int32), np.array(exps, dtype=np.float64), 
            np.array(coeffs, dtype=np.float64), np.array(norms, dtype=np.float64), 
            np.array(lmns, dtype=np.int32), np.array(centers, dtype=np.float64), np.array(h_ii, dtype=np.float64))

@njit
def overlap_1D(l1, l2, xA, xB, alpha, beta):
    asum = alpha + beta
    P = (alpha * xA + beta * xB) / asum
    if l1 == 0 and l2 == 0: val = 1.0
    elif l1 == 1 and l2 == 0: val = P - xA
    elif l1 == 0 and l2 == 1: val = P - xB
    elif l1 == 1 and l2 == 1: val = 1.0 / (2.0 * asum) + (P - xA)*(P - xB)
    else: val = 0.0
    return val * math.sqrt(np.pi / asum)

@njit
def compute_overlap_jit(cgf_ptr, exps, coeffs, norms, lmns, centers):
    n_cgf = len(cgf_ptr)
    S = np.zeros((n_cgf, n_cgf), dtype=np.float64)
    for i in range(n_cgf):
        for j in range(n_cgf):
            S_ij = 0.0
            for p1 in range(cgf_ptr[i, 0], cgf_ptr[i, 1]):
                for p2 in range(cgf_ptr[j, 0], cgf_ptr[j, 1]):
                    alpha, beta = exps[p1], exps[p2]
                    A, B = centers[p1], centers[p2]
                    l1, m1, n1 = lmns[p1]
                    l2, m2, n2 = lmns[p2]
                    
                    dist_sq = (A[0]-B[0])**2 + (A[1]-B[1])**2 + (A[2]-B[2])**2
                    rat = (alpha * beta) / (alpha + beta)
                    exp_part = math.exp(-rat * dist_sq)
                    
                    Ix = overlap_1D(l1, l2, A[0], B[0], alpha, beta)
                    Iy = overlap_1D(m1, m2, A[1], B[1], alpha, beta)
                    Iz = overlap_1D(n1, n2, A[2], B[2], alpha, beta)
                    
                    S_ij += coeffs[p1] * coeffs[p2] * norms[p1] * norms[p2] * exp_part * Ix * Iy * Iz
            S[i, j] = S_ij
    return S

@njit
def compute_eh_hamiltonian(S, H_ii, K):
    n = len(S)
    H = np.zeros((n, n), dtype=np.float64)
    for i in range(n):
        H[i, i] = H_ii[i]
        for j in range(i+1, n):
            H[i, j] = K * S[i, j] * 0.5 * (H_ii[i] + H_ii[j])
            H[j, i] = H[i, j]
    return H

@st.cache_data
def get_molecule_and_angles(smiles):
    mol = Chem.MolFromSmiles(smiles)
    if not mol: return None, None, []
    mol = Chem.AddHs(mol)
    AllChem.EmbedMolecule(mol, AllChem.ETKDG())
    AllChem.MMFFOptimizeMolecule(mol)
    angles = []
    for atom in mol.GetAtoms():
        neighbors = atom.GetNeighbors()
        if len(neighbors) >= 2:
            for i in range(len(neighbors)):
                for j in range(i+1, len(neighbors)):
                    angles.append((neighbors[i].GetIdx(), atom.GetIdx(), neighbors[j].GetIdx()))
    atoms = [a.GetAtomicNum() for a in mol.GetAtoms()]
    return mol, atoms, angles

# --- KIINTEÄN OLOMUODON FUNKTIOT ---
@st.cache_data
def calc_1d_monatomic(alpha, beta, n_k=500, a=1.0):
    k = np.linspace(-np.pi/a, np.pi/a, n_k)
    E = alpha + 2 * beta * np.cos(k * a)
    
    k_dos = np.linspace(-np.pi/a, np.pi/a, 50000)
    E_dos = alpha + 2 * beta * np.cos(k_dos * a)
    hist, bin_edges = np.histogram(E_dos, bins=200, density=True)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    
    return k, E, bin_centers, hist

@st.cache_data
def calc_1d_diatomic(alpha1, alpha2, beta1, beta2, n_k=500, a=1.0):
    k = np.linspace(-np.pi/a, np.pi/a, n_k)
    delta_alpha = (alpha1 - alpha2) / 2
    mean_alpha = (alpha1 + alpha2) / 2
    
    off_diag_sq = beta1**2 + beta2**2 + 2 * beta1 * beta2 * np.cos(k * a)
    
    E_upper = mean_alpha + np.sqrt(delta_alpha**2 + off_diag_sq)
    E_lower = mean_alpha - np.sqrt(delta_alpha**2 + off_diag_sq)
    
    k_dos = np.linspace(-np.pi/a, np.pi/a, 50000)
    off_diag_sq_dos = beta1**2 + beta2**2 + 2 * beta1 * beta2 * np.cos(k_dos * a)
    E_upper_dos = mean_alpha + np.sqrt(delta_alpha**2 + off_diag_sq_dos)
    E_lower_dos = mean_alpha - np.sqrt(delta_alpha**2 + off_diag_sq_dos)
    
    E_dos_all = np.concatenate([E_lower_dos, E_upper_dos])
    hist, bin_edges = np.histogram(E_dos_all, bins=300, density=True)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    
    return k, E_lower, E_upper, bin_centers, hist

@st.cache_data
def calc_2d_square(alpha, beta, n_k=200, a=1.0):
    k_Gamma_X_x = np.linspace(0, np.pi/a, n_k)
    k_Gamma_X_y = np.zeros(n_k)
    
    k_X_M_x = np.ones(n_k) * np.pi/a
    k_X_M_y = np.linspace(0, np.pi/a, n_k)
    
    k_M_Gamma_x = np.linspace(np.pi/a, 0, n_k)
    k_M_Gamma_y = np.linspace(np.pi/a, 0, n_k)
    
    kx_path = np.concatenate([k_Gamma_X_x, k_X_M_x, k_M_Gamma_x])
    ky_path = np.concatenate([k_Gamma_X_y, k_X_M_y, k_M_Gamma_y])
    
    path_len = np.zeros(len(kx_path))
    for i in range(1, len(kx_path)):
        dk = np.sqrt((kx_path[i]-kx_path[i-1])**2 + (ky_path[i]-ky_path[i-1])**2)
        path_len[i] = path_len[i-1] + dk
        
    E_path = alpha + 2 * beta * (np.cos(kx_path * a) + np.cos(ky_path * a))
    
    ticks = [0, path_len[n_k-1], path_len[2*n_k-1], path_len[-1]]
    tick_labels = ['Gamma', 'X', 'M', 'Gamma']
    
    kx_grid = np.linspace(-np.pi/a, np.pi/a, 500)
    ky_grid = np.linspace(-np.pi/a, np.pi/a, 500)
    KX, KY = np.meshgrid(kx_grid, ky_grid)
    E_dos = alpha + 2 * beta * (np.cos(KX * a) + np.cos(KY * a))
    
    hist, bin_edges = np.histogram(E_dos.flatten(), bins=200, density=True)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    
    return path_len, E_path, ticks, tick_labels, bin_centers, hist


# ==========================================
# 3. VÄLILEHDET JA KÄYTTÖLIITTYMÄ
# ==========================================
tab_walsh, tab_solid = st.tabs(["Walsh-diagrammit", "Kiinteän olomuodon kemia"])

with tab_walsh:
    st.header("Molekyylin geometrian ennustaminen: Walsh-diagrammit")
    
    with st.expander("Lue ensin: Mitä Walsh-diagrammit kertovat ja miten niitä luetaan?", expanded=True):
        st.markdown("""
        ### Mistä Walsh-diagrammeissa on kyse?
        Miksi vesi (H2O) on muodoltaan vääntynyt kulmaan, mutta hiilidioksidi (CO2) on täysin lineaarinen suora? Vuonna 1953 Walsh kehitti graafisen menetelmän, jolla näihin kysymyksiin voidaan vastata pelkkää molekyyliorbitaaliteoriaa käyttäen.

        Walsh-diagrammi kuvaa **molekyyliorbitaalien energioiden muutosta, kun molekyylin geometriaa (esim. sidoskulmaa) muutetaan**.

        ### Miten luet diagrammia?
        Kun molekyyliä väännetään, atomien orbitaalien välinen päällekkäisyys muuttuu. 
        1. **Symmetria on vaatimus:** Orbitaalit voivat vuorovaikuttaa ja sekoittua toisiinsa vain, jos niillä on sama symmetria.
        2. **Energian lasku:** Jos taivuttaminen mahdollistaa uuden, suotuisan vuorovaikutuksen (esimerkiksi keskusatomin p-orbitaali pääsee sekoittumaan vetyjen s-orbitaalien kanssa), orbitaalin energia laskee.
        3. **Energian nousu:** Jos taivuttaminen rikkoo suotuisan sidoksen tai lisää atomien välistä hylkimistä, energia nousee. <br>

        Huom! Punainen viiva näyttää klassisen voimakentän (MMFF) optimigeometrian, joka ei ole suoraan verrannollinen EH-energiaminimiin.

        ### Perussääntö geometrialle
        Molekyyli pyrkii tilaan, jossa sen kokonaisenergia on matalin. Nyrkkisääntönä tämä tarkoittaa usein sitä, että **geometrian muutosta dominoi ylin miehitetty orbitaali (HOMO)**. 
        
        *Huomio opiskelijalle: Tämä pätee aika hyvin pienille molekyyleille. Todellisuudessa kokonaisenergia riippuu kuitenkin **kaikkien** miehitettyjen orbitaalien energioiden summasta. Pelkän HOMO:n pohjalta vedetyt päätelmät voivat siksi antaa harhaanjohtavia tuloksia monimutkaisemmissa järjestelmissä.*

        **Laskennan reunaehdot (approksimaatiot):**
        Tässä työkalussa käytetään yksinkertaistettua mallia, joka olettaa **minimaalisen STO-3G-tyyppisen kantajoukon**. Energiat ovat Extended Hückel -approksimaation tuottamia **suhteellisia energioita**, eli ne ovat vain semi-kvantitatiivisia suuntaa-antavia arvoja. Lisäksi skannauksessa muut vapausasteet pidetään jäädytettyinä, eli kyseessä ei ole täydellinen relaksoitu optimointi.
        """)
    
    st.markdown("---")
    
    col_w_input, col_w_plot = st.columns([1, 2])

    with col_w_input:
        st.subheader("Molekyyli")
        smiles = st.text_input("Syötä SMILES (H, C, N, O)", value="O", key="walsh_smiles")
        mol, atoms, available_angles = get_molecule_and_angles(smiles)
        
        if mol and available_angles:
            symbols = [a.GetSymbol() for a in mol.GetAtoms()]
            angle_options = {f"{symbols[i]}{i} - {symbols[j]}{j} - {symbols[k]}{k}": (i, j, k) for (i, j, k) in available_angles}
            selected_angle_str = st.selectbox("Valitse muutettava sidoskulma", list(angle_options.keys()))
            i_idx, j_idx, k_idx = angle_options[selected_angle_str]
            
            st.subheader("Skannauksen asetukset")
            start_angle = st.number_input("Alkukulma (°)", value=90.0)
            end_angle = st.number_input("Loppukulma (°)", value=180.0)
            points = st.slider("Mittapisteiden määrä", 10, 100, 40)
            K_const = st.slider("Wolfsberg-Helmholz vakio (K)", 1.0, 2.5, 1.75, 0.05)
            run_scan = st.button("Laske Walsh-diagrammi", type="primary")

    with col_w_plot:
        if mol and 'run_scan' in locals() and run_scan:
            conf = mol.GetConformer()
            original_angle = Chem.rdMolTransforms.GetAngleDeg(conf, i_idx, j_idx, k_idx)
            scan_angles = np.linspace(start_angle, end_angle, points)
            eigenvalues = []
            
            bar = st.progress(0, text="Lasketaan Extended Hückel matriiseja...")
            
            for idx, angle in enumerate(scan_angles):
                Chem.rdMolTransforms.SetAngleDeg(conf, i_idx, j_idx, k_idx, float(angle))
                coords = []
                for a in range(mol.GetNumAtoms()):
                    pos = conf.GetAtomPosition(a)
                    coords.append([pos.x / A0, pos.y / A0, pos.z / A0])
                    
                cgf_ptr, exps, coeffs, norms, lmns, centers, h_ii = flatten_basis(atoms, coords)
                S = compute_overlap_jit(cgf_ptr, exps, coeffs, norms, lmns, centers)
                H = compute_eh_hamiltonian(S, h_ii, K_const)
                
                S_reg = S + np.eye(len(S)) * 1e-8
                evals = la.eigvalsh(H, S_reg)
                eigenvalues.append(evals)
                bar.progress((idx + 1) / points, text="Lasketaan Extended Hückel matriiseja...")
                
            eigenvalues = np.array(eigenvalues)
            fig_w = go.Figure()
            for band in range(eigenvalues.shape[1]):
                fig_w.add_trace(go.Scatter(x=scan_angles, y=eigenvalues[:, band], mode='lines', line=dict(color='blue')))
                
            fig_w.add_vline(x=original_angle, line_width=2, line_dash="dot", line_color="red", annotation_text=" RDKit Klassinen Minimi")
            
            fig_w.update_layout(
                title=f"Walsh-diagrammi: Kulman {selected_angle_str} muutos", 
                xaxis_title="Sidoskulma (°)", 
                yaxis_title="Suhteellinen MO Energia (EH, eV)", 
                height=600, 
                showlegend=False, 
                hovermode="x unified",
                annotations=[dict(x=0.5, y=-0.15, xref="paper", yref="paper", 
                                  text="", 
                                  showarrow=False, font=dict(size=12, color="gray"))]
            )
            st.plotly_chart(fig_w, use_container_width=True)


with tab_solid:
    st.header("Molekyyleistä materiaaleihin: Kiinteän olomuodon kemia")
    
    with st.expander("Lue ensin: Orbitaaleista energiavöihin", expanded=True):
        st.markdown("""
        ### Mistä kiinteän olomuodon kemiassa on kyse?
        Aiemmissa moduuleissa olemme tarkastelleet yksittäisiä molekyylejä. Mitä tapahtuu, kun ketjutamme atomeja kidehilaksi?
        Kun N atomia tuodaan yhteen, syntyy N molekyyliorbitaalia. Kun N kasvaa makroskooppisiin mittoihin (kuten $10^{23}$), energiatasot pakkautuvat niin tiheästi yhteen, että erillisistä viivoista tulee jatkuvia **energiavöitä** (energy bands).

        **Huomio!** *Tämä "vyöteoria" perustuu Tight-binding -malliin. Matemaattisesti kyse on aivan tasan samasta asiasta kuin molekyylien Hückel-teoriassa! Ainoa ero on reunaehdoissa: molekyyleillä se on äärellinen, kiteillä jaksollinen.*

        ### Keskeiset käsitteet diagrammeissa
        
        **1. Tilatiheys eli DOS (Density of States)**
        DOS kertoo, kuinka monta sallittua kvanttitilaa tietyllä energiatasolla on tarjolla elektroneille.
        * Leveä huippu DOS-kuvaajassa tarkoittaa, että kyseisellä energialla on paljon "istumapaikkoja".
        * Nolla-arvo DOS-kuvaajassa tarkoittaa **vyöaukkoa** (band gap). Elektroni ei voi koskaan omata energiaa, joka osuu vyöaukon sisälle.
        * *Huom: Tämän ohjelman tuottama DOS on normalisoitu jakauma. Sen muoto on täysin oikea, mutta sen absoluuttinen mittakaava ei edusta oikeaa fysikaalista tilojen lukumäärää.*

        **2. Fermi-taso (Fermi Level)**
        Fermi-taso määrittää järjestelmän elektronimiehityksen. 
        Absoluuttisessa nollapisteessä (0 K) kyseessä on tiukka raja: kaikki DOS-tilat Fermi-tason alapuolella ovat täynnä, ja sen yläpuolella olevat tilat ovat tyhjiä. Metalleilla tämä raja osuu keskelle olemassa olevaa energiavyötä, jolloin sähkövirta pääsee kulkemaan. Puolijohteilla ja eristeillä Fermi-taso putoaa tyhjään vyöaukkoon, jolloin ylempi vyö on 0 K lämpötilassa täysin tyhjä ja alempi aivan täynnä.
        """)
        
    st.markdown("---")
    
    col_s_input, col_s_plot = st.columns([1, 2])
    
    with col_s_input:
        st.subheader("Hilan malli")
        lattice_type = st.selectbox(
            "Valitse tutkittava hila",
            ["1D Monatominen ketju", "1D Biatominen (Peierls)", "2D Neliöhila"]
        )

        st.divider()
        st.subheader("Fysikaaliset parametrit")

        if lattice_type == "1D Monatominen ketju":
            alpha_val = st.slider("Atomin energia (alpha)", -10.0, 0.0, -5.0, 0.5)
            beta_val = st.slider("Resonanssi-integraali (beta)", -5.0, 0.0, -2.0, 0.1)

        elif lattice_type == "1D Biatominen (Peierls)":
            st.markdown("**Atomien energiat**")
            alpha1 = st.slider("Atomi 1 (alpha 1)", -10.0, 0.0, -5.0, 0.5)
            alpha2 = st.slider("Atomi 2 (alpha 2)", -10.0, 0.0, -5.0, 0.5)
            st.markdown("**Sidosten vahvuudet**")
            beta1 = st.slider("Sidos 1 (beta 1)", -5.0, 0.0, -2.0, 0.1)
            beta2 = st.slider("Sidos 2 (beta 2)", -5.0, 0.0, -2.0, 0.1)

        elif lattice_type == "2D Neliöhila":
            alpha_val = st.slider("Atomin energia (alpha)", -10.0, 0.0, -5.0, 0.5)
            beta_val = st.slider("Resonanssi-integraali (beta)", -5.0, 0.0, -1.0, 0.1)

    with col_s_plot:
        fig_s = make_subplots(rows=1, cols=2, shared_yaxes=True, 
                            column_widths=[0.7, 0.3], horizontal_spacing=0.02,
                            subplot_titles=("Vyörakenne E(k)", "Tilatiheys (DOS)"))

        if lattice_type == "1D Monatominen ketju":
            k, E, e_dos, dos = calc_1d_monatomic(alpha_val, beta_val)
            
            fig_s.add_trace(go.Scatter(x=k, y=E, mode='lines', line=dict(color='blue', width=3), name='E(k)'), row=1, col=1)
            fig_s.add_trace(go.Scatter(x=dos, y=e_dos, mode='lines', fill='tozerox', line=dict(color='gray'), name='DOS'), row=1, col=2)
            
            fig_s.update_xaxes(title_text="Aaltovektori k", tickvals=[-np.pi, 0, np.pi], ticktext=['-pi/a', '0', 'pi/a'], row=1, col=1)
            
        elif lattice_type == "1D Biatominen (Peierls)":
            k, E1, E2, e_dos, dos = calc_1d_diatomic(alpha1, alpha2, beta1, beta2)
            
            fig_s.add_trace(go.Scatter(x=k, y=E1, mode='lines', line=dict(color='red', width=3), name='Alempi vyö'), row=1, col=1)
            fig_s.add_trace(go.Scatter(x=k, y=E2, mode='lines', line=dict(color='blue', width=3), name='Ylempi vyö'), row=1, col=1)
            fig_s.add_trace(go.Scatter(x=dos, y=e_dos, mode='lines', fill='tozerox', line=dict(color='gray'), name='DOS'), row=1, col=2)
            
            fig_s.update_xaxes(title_text="Aaltovektori k", tickvals=[-np.pi, 0, np.pi], ticktext=['-pi/a', '0', 'pi/a'], row=1, col=1)

        elif lattice_type == "2D Neliöhila":
            path_len, E, ticks, tick_labels, e_dos, dos = calc_2d_square(alpha_val, beta_val)
            
            fig_s.add_trace(go.Scatter(x=path_len, y=E, mode='lines', line=dict(color='green', width=3), name='E(k)'), row=1, col=1)
            fig_s.add_trace(go.Scatter(x=dos, y=e_dos, mode='lines', fill='tozerox', line=dict(color='gray'), name='DOS'), row=1, col=2)
            
            for t in ticks:
                fig_s.add_vline(x=t, line_width=1, line_dash="dash", line_color="gray", row=1, col=1)
                
            fig_s.update_xaxes(title_text="K-pisteiden reitti", tickvals=ticks, ticktext=tick_labels, row=1, col=1)

        fig_s.update_yaxes(title_text="Energia (E)", row=1, col=1)
        fig_s.update_xaxes(title_text="DOS (Normalisoitu)", row=1, col=2)
        fig_s.update_layout(height=600, showlegend=False, hovermode="y unified")

        st.plotly_chart(fig_s, use_container_width=True)

        with st.expander("Huomioita ja pohdittavaa"):
            st.write("""
            1. **Van Hoven singulariteetit:** Tarkastele 1D monatomista ketjua. Huomaatko, kuinka tilatiheys (DOS) divergoi jyrkästi vyön ala- ja yläreunoilla? Tämä on tyypillistä 1D-järjestelmille johtuen niille ominaisista integroituvista singulariteeteista ($dE/dk = 0$ reunoilla). 
            2. **2D vs 1D DOS:** Vaihda 2D-neliöhilaan. Miten DOS-kuvaaja muuttuu? 2D-hilassa reunan singulariteetit ovat logaritmisia, jolloin terävät piikit korvautuvat "portailla" ja huippu siirtyy vyön keskelle.
            3. **Peierlsin vääristymä:** Valitse "1D Biatominen". Aseta aluksi kaikki parametrit samoiksi ($\alpha_1 = \alpha_2$, $\beta_1 = \beta_2$). Pienennä sitten $\beta_2$:n absoluuttista arvoa hieman (esim. $\beta_1 = -2.0, \beta_2 = -1.5$). Mitä tapahtuu pisteessä $k = \pm \pi/a$? Tämä on ns. Peierlsin vääristymä, jossa tasamittainen 1D-metalli muuttuu eristeeksi avaten vyöaukon. *Huom: Tämä metalli-eriste -transitiomekanismi vaatii toimiakseen erityisesti sen, että alkuperäinen vyö oli puoliksi täytetty (half-filled band).*
            4. **Elektronegatiivisuus:** Pidä $\beta_1$ ja $\beta_2$ samoina, mutta muuta atomien energioita $\alpha$. Tämä vastaa kidehilaa, joka koostuu kahdesta eri alkuaineesta (esim. hiili ja typpi vuorotellen). Miten vyöaukon (band gap) koko riippuu $\alpha_1$:n ja $\alpha_2$:n erotuksesta?
            """)
