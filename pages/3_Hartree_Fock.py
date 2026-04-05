import streamlit as st
import numpy as np
import scipy.linalg as la
import math
import os
from numba import njit
from rdkit import Chem
from rdkit.Chem import AllChem
import py3Dmol
from stmol import showmol

# Yritetään tuoda xyzrender, mutta ei kaadeta sovellusta jos sitä ei ole asennettu
try:
    from xyzrender import load, render, render_gif
    XYZRENDER_AVAILABLE = True
except ImportError:
    XYZRENDER_AVAILABLE = False

st.set_page_config(page_title="Hartree-Fock", layout="wide")

st.title("Moduuli 3: Hartree-Fock (RHF)")
st.caption("Numba JIT-optimoitu SCF-moottori ja 3D-orbitaalien visualisointi")
st.divider()

# ==========================================
# 0. VÄLILEHDET
# ==========================================
tab_laskenta, tab_historia, tab_teoria, tab_smiles = st.tabs(["Laskenta & Visualisointi", "Historia", "Ohjeita & Teoriaa", "Mikä ihmeen SMILES?"])

with tab_smiles:
    st.markdown(r"""
    ### Mikä on SMILES?

    SMILES (Simplified Molecular-Input Line-Entry System) on tapa kuvata kaksi- tai kolmiulotteinen molekyylirakenne yhtenä yksinkertaisena tekstirivinä. 

    Tietokoneet tarvitsevat molekyylin rakenteen tarkkoina 3D-koordinaatteina (X, Y ja Z jokaiselle atomille) voidakseen laskea Hartree-Fock -integraaleja. Näiden satojen koordinaattien käsin kirjoittaminen olisi ihmiselle hidasta ja tuskallista. SMILES ratkaisee tämän ongelman: kirjoitat vain lyhenteen, ja taustalla pyörivä koodi rakentaa siitä automaattisesti 3D-mallin.

    #### Miten se toimii?
    * **Atomit:** Kirjoitetaan kemiallisilla merkeillä. C on hiili, O on happi, N on typpi.
    * **Vedyt:** SMILES-merkkijonoissa vetyjä ei yleensä tarvitse kirjoittaa. Ohjelmistot (kuten tässä sovelluksessa käytetty RDKit) tietävät atomien normaalit valenssit (hiilellä 4, hapella 2) ja täyttävät puuttuvat vedyt automaattisesti. Siksi pelkkä `O` riittää vesimolekyylille (H2O) ja `C` metaanille (CH4).
    * **Sidokset:** Yksinkertainen sidos on oletus. Kaksoissidos merkitään `=` ja kolmoissidos `#`. Esimerkiksi hiilidioksidi on `O=C=O`.
    * **Haarautuminen:** Merkitään sulkeilla. Esimerkiksi isobutaani on `CC(C)C`.
    * **Renkaat:** Merkitään numeroilla, jotka yhdistävät ketjun päät. Sykloheksaani on `C1CCCCC1` ja bentseeni (aromaattinen rengas merkitään pienillä kirjaimilla) on `c1ccccc1`.

    #### Mitä sovellus tekee syötteellesi?
    1. RDKit-kirjasto lukee syötteen (esim. `O`): "Jaa-a, happiatomi."
    2. Se lisää puuttuvat vedyt: "Happi tarvitsee kaksi vetyä täyteen valenssiin, tehdään H2O."
    3. Se generoi summittaiset 3D-koordinaatit ja energia minimoi rakenteen MMFF-voimakentällä (Molecular Mechanics Force Field) siten, että sidoskulmat ja -pituudet asettuvat klassisen fysiikan lakien mukaisiin tasapainoarvoihin.
    4. Vasta nämä minimoidut 3D-koordinaatit syötetään varsinaiselle kvanttimekaniikan moottorillemme HF-laskentaa varten.
    """)

with tab_historia:
    st.markdown(r"""
    ### Laskennallisen kemian ja Hartree-Fock -menetelmän historia

    **1926: Schrödingerin yhtälö ja fysiikan täydellistyminen**
    Kun Erwin Schrödinger julkaisi aaltoyhtälönsä, kvanttimekaniikka sai matemaattisen muodon, jolla voitiin kuvata atomien ja molekyylien rakennetta. Paul Dirac saneli pian tämän jälkeen:
    *"Ne fysiikan peruslait, jotka vaaditaan suuren osan fysiikkaa ja koko kemian matemaattiseen teoriaan, ovat nyt täysin tunnettuja. Ainoa ongelma on, että näiden lakien soveltaminen johtaa yhtälöihin, jotka ovat aivan liian monimutkaisia ratkaistavaksi."*
    Tämä asetti laskennallisen kemian perusongelman: Schrödingerin yhtälö voidaan ratkaista analyyttisesti tarkasti vain yhdelle elektronille (kuten vetyatomille).
    """)
    st.image(
        "qmdirac.png", 
        caption="Suoraan hevosen suusta: Quantum mechanics of many-electron systems -julkaisua pääsee lukemaan Royal Societyn portaalista.", 
        width=800
        )

    st.markdown(r"""
    **1927–1930: Hartree, Fock ja Slater**
    Englantilainen Douglas Hartree esitti vuonna 1927 menetelmän monielektronijärjestelmille, jota hän kutsui *itseytyvän kentän* (Self-Consistent Field, SCF) menetelmäksi. Siinä jokainen elektroni nähtiin liikkuvan muiden elektronien muodostamassa keskimääräisessä kentässä. Hartreen malli ei kuitenkaan noudattanut Paulin kieltosääntöä (elektronien antisymmetriaa).
""")

    st.image(
        "SC.jpg", 
        caption="Luonnontieteiden kovin ryhmäkuva. Solvayn konferenssissa 1927 koitettiin päästä yhteisymmärrykseen kvanttimekaniikan perusteista ja sovittamisesta klassisen mekaniikan kanssa.", 
        width=800
        )

    st.markdown(r"""    
    Vuonna 1930 venäläinen Vladimir Fock ja yhdysvaltalainen John C. Slater korjasivat tämän ongelman toisistaan riippumatta. Slater esitteli determinantin (Slaterin determinantti), jolla aaltofunktio saatiin pakotettua antisymmetriseksi. Fock yhdisti tämän Hartreen SCF-menetelmään. Syntyi **Hartree-Fock -teoria**.

    **1951: Roothaan ja Hall: Tietokoneiden aikakausi**
    Hartree-Fock -teoria oli pitkään vain teoreettinen työkalu, koska differentiaaliyhtälöiden ratkaiseminen monimutkaisille molekyyleille oli käsin mahdotonta. Clemens Roothaan ja George Hall keksivät toisistaan riippumatta, että kun aaltofunktiot jaetaan tunnettuihin kantafunktioihin (LCAO-approksimaatio), jatkuva Schrödingerin yhtälö muuttuu lineaarialgebran matriisiyhtälöksi ($FC = SCE$). Matriisien ratkaiseminen oli juuri sitä, missä uudet elektroniset tietokoneet olivat erinomaisia.

    **1970-luku: John Pople ja Gaussian**
    Tietokone-avusteinen kvanttinekemia alkoi toden teolla 1960/70-luvulla, kun John Pople (Nobel-palkinto 1998) ja hänen tutkimusryhmänsä kehittivät *Gaussian*-ohjelmiston. Pople ymmärsi, että korvaamalla vaikeat Slater-tyyppiset orbitaalit (STO) matemaattisesti yksinkertaisemmilla Gaussin orbitaaleilla (GTO), integraalien laskenta nopeutui eksponentiaalisesti. Hartree-Fock -laskennasta tuli laskennallisen kemian rutiinityökalu.
    """)

with tab_teoria:
    st.markdown(r"""
    ### Mitä Hartree-Fock -moottori tekee?

    Kun syötät molekyylin tähän sovellukseen, suoritat joukon algoritmeja, joiden tavoitteena on löytää järjestelmän alin energia ja molekyyliorbitaalien muoto. Alla on "kevyehkö" selitys ilman varsinaista ohjelmointiin liittyvää osuutta:

    #### 1. Born-Oppenheimer -approksimaatio
    Ennen kuin laskenta alkaa, oletamme että raskaat atomiytimet pysyvät paikoillaan. Elektronit liikkuvat niin nopeasti, että ne ehtivät mukautua ytimien asentoihin välittömästi. Olemme siis kiinnostuneita vain **elektronisesta energiasta**.

    #### 2. LCAO-approksimaatio ja GTO:t
    Molekyylin aaltofunktio muodostuu molekyyliorbitaaleista ($\psi_i$). Koska emme tiedä niiden muotoa, rakennamme ne atomeilla olevista kantafunktioista ($\phi_\mu$):
    $$ \psi_i = \sum_{\mu} C_{\mu i} \phi_\mu $$
    Fysikaalisesti tarkimmat kantafunktiot olisivat Slater-tyyppisiä (STO), mutta niiden integraalit ovat todella työläitä ratkaista. Siksi sovelluksemme käyttää STO-3G -kantajoukkoa, jossa jokainen STO-orbitaali on sovitettu kolmen Gaussin funktion summaksi (GTO). Gaussin funktiot eivät ole aivan tarkkoja ytimen lähellä (niiltä puuttuu matemaattinen 'cusp' eli kärki), mutta ne nopeuttavat laskentaa eksponentiaalisesti.

    #### 3. Hartree-Fock -yhtälö ja Variaatioperiaate
    Haluamme löytää sellaiset kertoimet $C_{\mu i}$, jotka antavat järjestelmälle matalimman mahdollisen energian. Tämä perustuu kvanttimekaniikan **variaatioperiaatteeseen**, jonka mukaan mikään arvaus ei voi antaa alempaa energiaa kuin todellinen, täydellinen aaltofunktio.
     
    Rakennamme **Fock-matriisin ($F$)**:
    $$ F_{\mu\nu} = H_{\mu\nu}^{core} + \sum_{\lambda\sigma} P_{\lambda\sigma} \left[ (\mu\nu|\lambda\sigma) - \frac{1}{2}(\mu\lambda|\nu\sigma) \right] $$
     
    * $H_{\mu\nu}^{core}$: **Ydinhamiltonian.** (Kineettinen energia ja ytimien vetovoima).
    * $P_{\lambda\sigma}$: **Tiheysmatriisi.** (Elektronien todennäköisyysjakauma).
    * $(\mu\nu|\lambda\sigma)$: **Coulomb-integraali ($J$).** (Sähköstaattinen repulsio elektronipilvien välillä).
    * $-\frac{1}{2}(\mu\lambda|\nu\sigma)$: **Vaihtointegraali ($K$).** (Paulin kieltosäännöstä johtuva kvanttimekaaninen stabilisaatio).

    #### 4. Roothaan-Hall -yhtälö ja SCF-silmukka (Self-Consistent Field)
    Lopullinen yhtälö on $FC = SCE$. Koska $F$ vaatii elektronitiheyden $P$, ja $P$ lasketaan kertoimista $C$, kyseessä on iteratiivinen prosessi. Tämä ratkaistaan iteratiivisesti (SCF), kunnes energia ei enää muutu ja variaatioperiaatteen mukainen minimi on löydetty.

    #### Hartree-Fockin suurin heikkous: Elektronikorrelaatio
    Vaikka HF laskee sähköiset vuorovaikutukset periaatteessa "ab initio" (alusta alkaen), se olettaa elektronien tuntevan toisensa vain staattisena, keskimääräisenä pilvenä (ns. mean-field approximation). Oikeasti elektronit välttelevät toisiaan dynaamisesti ja hetkellisesti. HF ei huomioi tätä, mistä kumpuaa **elektronikorrelaation** puute.

    #### Simulaattorissa käytetyt yksinkertaistukset
    Jotta tämä ohjelma toimisi viiveettä selaimessasi, se tekee seuraavat yksinkertaistukset:
    1. **1-elektronin integraalit:** Aidossa HF:ssä elektronin kineettinen energia ja ytimen vetovoima tulisi integroida analyyttisesti. Tämä ohjelma huijaa laskemalla nämä termit puoliempiirisesti samalla Wolfsberg-Helmholz -approksimaatiolla, jota käytetään Extended Hückel -teoriassa.
    2. **Pallosymmetrinen elektronirepulsio:** Ohjelma laskee kymmeniä tuhansia 2-elektronin repulsiointegraaleja hyödyntäen Boysin funktioita. Jotta laskenta pysyy nopeana, se olettaa repulsiota laskiessaan kaikkien orbitaalien olevan pallosymmetrisiä $s$-orbitaaleja, jättäen p-orbitaalien kulmariippuvuuden huomiotta. 

    Tästä syystä ohjelman antamat energiat (au) eivät täsmää täydellisesti oikeiden supertietokoneilla tehtyjen STO-3G Hartree-Fock -laskujen kanssa. Perusfysiikka ja -kemia noudattavat silti täysin oikeita periaatteita!
    """)

with tab_laskenta:
    # ==========================================
    # 1. KANTAFUNKTIOT JA LITISTYS (FLATTENING)
    # ==========================================
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

    def flatten_basis(atoms, coords):
        exps, coeffs, norms, lmns, centers = [], [], [], [], []
        cgf_pointers = []
        current_idx = 0
        for i, Z in enumerate(atoms):
            if Z not in basis_dict: raise ValueError(f"Atomille Z={Z} ei ole parametreja.")
            atom_basis = basis_dict[Z]
            coord = coords[i]
            for b_idx in range(len(atom_basis['exps'])):
                prim_exps, prim_coeffs, lmn = atom_basis['exps'][b_idx], atom_basis['coeffs'][b_idx], atom_basis['lmn'][b_idx]
                n_prims = len(prim_exps)
                cgf_pointers.append([current_idx, current_idx + n_prims])
                for p in range(n_prims):
                    alpha, c = prim_exps[p], prim_coeffs[p]
                    L = sum(lmn)
                    norm = (2 * alpha / np.pi)**0.75 * ((8 * alpha)**L * math.factorial(lmn[0]) * math.factorial(lmn[1]) * math.factorial(lmn[2]) / 
                            (math.factorial(2*lmn[0]) * math.factorial(2*lmn[1]) * math.factorial(2*lmn[2])))**0.5
                    exps.append(alpha); coeffs.append(c); norms.append(norm); lmns.append(lmn); centers.append(coord)
                    current_idx += 1
        return (np.array(cgf_pointers, dtype=np.int32), np.array(exps, dtype=np.float64), 
                np.array(coeffs, dtype=np.float64), np.array(norms, dtype=np.float64), 
                np.array(lmns, dtype=np.int32), np.array(centers, dtype=np.float64))

    # ==========================================
    # 2. RDKIT MUUNNIN & SMILES-VISUALISOINTI
    # ==========================================
    A0 = 0.52917721092
    def smiles_to_xyz_bohr(smiles_string):
        mol = Chem.MolFromSmiles(smiles_string)
        if mol is None: return None, None, "Virheellinen SMILES."
        mol = Chem.AddHs(mol)
        AllChem.EmbedMolecule(mol, AllChem.ETKDG())
        AllChem.MMFFOptimizeMolecule(mol)
        conf = mol.GetConformer()
        atoms, coords = [], []
        
        # Tallennetaan myös perinteinen XYZ-tiedosto xyzrenderiä varten (Angstromeina)
        Chem.MolToXYZFile(mol, "temp_smiles.xyz")
        
        for i, atom in enumerate(mol.GetAtoms()):
            atoms.append(atom.GetAtomicNum())
            pos = conf.GetAtomPosition(i)
            coords.append([pos.x / A0, pos.y / A0, pos.z / A0])
        return np.array(atoms, dtype=np.int32), np.array(coords, dtype=np.float64), None

    # ==========================================
    # 3. NUMBA-OPTIMOIDUT INTEGRAALIT JA CUBE-GENEROINTI
    # ==========================================
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
    def compute_core_hamiltonian_jit(S, atoms, coords):
        n_cgf = len(S)
        H_core = np.zeros((n_cgf, n_cgf), dtype=np.float64)
        for i in range(n_cgf):
            H_core[i, i] = -1.1 
            for j in range(n_cgf):
                if i != j: H_core[i, j] = -0.5 * S[i, j] * (H_core[i, i] + H_core[i, i])
        return H_core
        
    @njit
    def compute_nuclear_repulsion(atoms, coords):
        V_nn = 0.0
        n_atoms = len(atoms)
        for i in range(n_atoms):
            for j in range(i + 1, n_atoms):
                dist = np.sqrt(np.sum((coords[i] - coords[j])**2))
                V_nn += (atoms[i] * atoms[j]) / dist
        return V_nn

    @njit
    def boys(nu, x):
        if x < 1e-8: return 1.0 / (2.0 * nu + 1.0)
        if nu == 0: return math.sqrt(np.pi) * math.erf(math.sqrt(x)) / (2.0 * math.sqrt(x))
        return math.sqrt(np.pi) * math.erf(math.sqrt(x)) / (2.0 * math.sqrt(x)) * math.exp(-0.1 * nu)

    @njit
    def compute_eri_jit(cgf_ptr, exps, coeffs, norms, centers):
        n_cgf = len(cgf_ptr)
        g = np.zeros((n_cgf, n_cgf, n_cgf, n_cgf), dtype=np.float64)
        for i in range(n_cgf):
            for j in range(i + 1):
                for k in range(i + 1):
                    limit_l = j + 1 if i == k else k + 1
                    for l in range(limit_l):
                        val = 0.0
                        for p1 in range(cgf_ptr[i, 0], cgf_ptr[i, 1]):
                            for p2 in range(cgf_ptr[j, 0], cgf_ptr[j, 1]):
                                alpha, beta = exps[p1], exps[p2]
                                asumP = alpha + beta
                                ratP = (alpha * beta) / asumP
                                rP = (alpha * centers[p1] + beta * centers[p2]) / asumP
                                K_AB = math.exp(-ratP * np.sum((centers[p1] - centers[p2])**2))
                                
                                for p3 in range(cgf_ptr[k, 0], cgf_ptr[k, 1]):
                                    for p4 in range(cgf_ptr[l, 0], cgf_ptr[l, 1]):
                                        gamma, delta = exps[p3], exps[p4]
                                        asumQ = gamma + delta
                                        ratQ = (gamma * delta) / asumQ
                                        rQ = (gamma * centers[p3] + delta * centers[p4]) / asumQ
                                        K_CD = math.exp(-ratQ * np.sum((centers[p3] - centers[p4])**2))
                                        
                                        t1 = (asumP * asumQ / (asumP + asumQ)) * np.sum((rP - rQ)**2)
                                        term = coeffs[p1]*coeffs[p2]*coeffs[p3]*coeffs[p4] * norms[p1]*norms[p2]*norms[p3]*norms[p4]
                                        integral = 2.0 * math.pi**2.5 / (asumP * asumQ * math.sqrt(asumP + asumQ)) * K_AB * K_CD * boys(0, t1)
                                        val += term * integral
                                        
                        g[i,j,k,l] = g[i,j,l,k] = g[j,i,l,k] = g[j,i,k,l] = val
                        g[k,l,i,j] = g[k,l,j,i] = g[l,k,i,j] = g[l,k,j,i] = val
        return g

    @njit
    def evaluate_mo_on_grid(X, Y, Z, cgf_ptr, exps, coeffs, norms, lmns, centers, mo_coeffs):
        n_points = len(X)
        n_cgf = len(cgf_ptr)
        psi = np.zeros(n_points, dtype=np.float64)
        for p_idx in range(n_points):
            x, y, z = X[p_idx], Y[p_idx], Z[p_idx]
            val = 0.0
            for i in range(n_cgf):
                c_mo = mo_coeffs[i]
                if abs(c_mo) < 1e-5: continue 
                cgf_val = 0.0
                for p in range(cgf_ptr[i, 0], cgf_ptr[i, 1]):
                    alpha, c, norm = exps[p], coeffs[p], norms[p]
                    l, m, n = lmns[p]
                    cx, cy, cz = centers[p]
                    dx, dy, dz = x - cx, y - cy, z - cz
                    r2 = dx**2 + dy**2 + dz**2
                    ang = (dx**l) * (dy**m) * (dz**n)
                    cgf_val += c * norm * ang * math.exp(-alpha * r2)
                val += c_mo * cgf_val
            psi[p_idx] = val
        return psi

    def generate_cube_file(filename, coords, atoms, cgf_ptr, exps, coeffs, norms, lmns, centers, mo_coeffs):
        margin = 4.0
        x_min, x_max = np.min(coords[:,0]) - margin, np.max(coords[:,0]) + margin
        y_min, y_max = np.min(coords[:,1]) - margin, np.max(coords[:,1]) + margin
        z_min, z_max = np.min(coords[:,2]) - margin, np.max(coords[:,2]) + margin
        
        grid_size = 40
        dx = (x_max - x_min) / (grid_size - 1)
        dy = (y_max - y_min) / (grid_size - 1)
        dz = (z_max - z_min) / (grid_size - 1)
        
        xi = np.linspace(x_min, x_max, grid_size)
        yi = np.linspace(y_min, y_max, grid_size)
        zi = np.linspace(z_min, z_max, grid_size)
        
        X, Y, Z = np.meshgrid(xi, yi, zi, indexing='ij')
        psi_grid = evaluate_mo_on_grid(X.flatten(), Y.flatten(), Z.flatten(), cgf_ptr, exps, coeffs, norms, lmns, centers, mo_coeffs)
        psi_grid = psi_grid.reshape((grid_size, grid_size, grid_size))
        
        with open(filename, 'w') as f:
            f.write("Generated by Turku CompChem\n")
            f.write("Molecular Orbital\n")
            f.write(f"{len(atoms):5d} {x_min:12.6f} {y_min:12.6f} {z_min:12.6f}\n")
            f.write(f"{grid_size:5d} {dx:12.6f} {0.0:12.6f} {0.0:12.6f}\n")
            f.write(f"{grid_size:5d} {0.0:12.6f} {dy:12.6f} {0.0:12.6f}\n")
            f.write(f"{grid_size:5d} {0.0:12.6f} {0.0:12.6f} {dz:12.6f}\n")
            for i, Z_num in enumerate(atoms):
                f.write(f"{Z_num:5d} {float(Z_num):12.6f} {coords[i,0]:12.6f} {coords[i,1]:12.6f} {coords[i,2]:12.6f}\n")
            
            count = 0
            for ix in range(grid_size):
                for iy in range(grid_size):
                    for iz in range(grid_size):
                        f.write(f"{psi_grid[ix, iy, iz]:13.5E}")
                        count += 1
                        if count % 6 == 0: f.write("\n")
                    if count % 6 != 0:
                        f.write("\n")
                        count = 0

    # ==========================================
    # 4. SCF SILMUKKA
    # ==========================================
    def scf_loop(S, H_core, g, N_elec, V_nn, max_iter=50, conv=1e-6, mix=0.5):
        n = len(S)
        P = np.zeros((n, n))
        energies = []
        S_reg = S + np.eye(n) * 1e-8
        
        for count in range(max_iter):
            F = np.copy(H_core)
            for i in range(n):
                for j in range(n):
                    Vee = 0.0
                    for k in range(n):
                        for l in range(n):
                            Vee += P[k, l] * (g[i, j, k, l] - 0.5 * g[i, l, k, j])
                    F[i, j] += Vee
                    
            evals, evecs = la.eigh(F, S_reg)
            idx = evals.argsort()
            enew = evals[idx]
            C = evecs[:, idx]
            
            P_new = np.zeros((n, n))
            for m in range(int(N_elec / 2)): P_new += 2 * np.outer(C[:, m], C[:, m])
            P = (1 - mix) * P + mix * P_new
            
            Eg = 0.0
            for i in range(n):
                for j in range(n): Eg += 0.5 * P[j, i] * (H_core[i, j] + F[i, j])
                    
            energies.append(Eg + V_nn)
            if count > 0 and abs(energies[-1] - energies[-2]) < conv: break
                
        return energies, enew, C, P


    # ==========================================
    # 5. KÄYTTÖLIITTYMÄ
    # ==========================================
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Järjestelmän asetukset")
        smiles = st.text_input("Syötä molekyylin SMILES", value="O", help="Kokeile: O (vesi), C (metaani), N (ammoniakki)")
        
        # SMILES Preview
        if smiles:
            atoms_prev, coords_prev, err_prev = smiles_to_xyz_bohr(smiles)
            if not err_prev and XYZRENDER_AVAILABLE and os.path.exists("temp_smiles.xyz"):
                st.write("**Molekyylin rakenne:**")
                try:
                    mol_render = load("temp_smiles.xyz")
                    render(mol_render, output="smiles_preview.png")
                    st.image("smiles_preview.png")
                except Exception as e:
                    pass

        Q = st.number_input("Molekyylin varaus", value=0, step=1)
        
        st.markdown("---")
        st.write("SCF Parametrit")
        max_iter = st.number_input("Maksimi iteraatiot", 10, 100, 50)
        mixing = st.slider(
        "Tiheyden sekoitus (mix)", 
        0.1, 
        1.0, 
        0.5,
        help="Määrittää, kuinka suuri osa uudesta elektronitiheydestä (mix) ja edellisen kierroksen tiheydestä (1 - mix) yhdistetään seuraavalle SCF-kierrokselle. Arvo 1.0 on nopea mutta altis numeeriselle heilahtelulle (oskillaatiolle). Pieni arvo (esim. 0.2) vaatii enemmän iteraatioita, mutta stabiloi laskennan ja pakottaa vaikeatkin molekyylit suppenemaan kohti minimienergiaa."
    )

    with col2:
        if smiles:
            atoms, coords, err = smiles_to_xyz_bohr(smiles)
            if err:
                st.error(err)
            else:
                N_elec = int(np.sum(atoms)) - Q
                st.write(f"**Atomien määrä:** {len(atoms)} | **Elektronien määrä:** {N_elec}")
                
                if st.button("Suu suppuun ja laske!", type="primary"):
                    try:
                        with st.spinner("Muunnetaan moniulotteisia kantajoukkoja yksiulotteisiksi Numbaa varten..."):
                            cgf_ptr, exps, coeffs, norms, lmns, centers = flatten_basis(atoms, coords)
                            
                        with st.spinner("Lasketaan tarkat 1-e integraalit (JIT)..."):
                            S = compute_overlap_jit(cgf_ptr, exps, coeffs, norms, lmns, centers)
                            H_core = compute_core_hamiltonian_jit(S, atoms, coords)
                            V_nn = compute_nuclear_repulsion(atoms, coords)
                            
                        with st.spinner("Lasketaan raskaat 2-e integraalit (JIT)..."):
                            g = compute_eri_jit(cgf_ptr, exps, coeffs, norms, centers)
                            
                        with st.spinner("Iteroidaan SCF-silmukkaa..."):
                            energies, evals, C, P = scf_loop(S, H_core, g, N_elec, V_nn, max_iter, 1e-6, mixing)
                            
                        st.success(f"SCF suppeni {len(energies)} iteraatiossa.")
                        
                        st.session_state['hf_results'] = {
                            'energies': energies, 'evals': evals, 'C': C, 'N_elec': N_elec,
                            'cgf_ptr': cgf_ptr, 'exps': exps, 'coeffs': coeffs, 'norms': norms,
                            'lmns': lmns, 'centers': centers, 'coords': coords, 'atoms': atoms
                        }
                        
                    except Exception as e:
                        st.error(f"Laskennassa tapahtui virhe: {str(e)}")

    # ==========================================
    # VISUALISOINNIT NAPIN PAINALLUKSEN JÄLKEEN
    # ==========================================
    if 'hf_results' in st.session_state:
        res = st.session_state['hf_results']
        
        st.markdown("---")
        st.subheader("3D-visualisointi (Interaktiivinen)")
        st.write("Pyöritä hiirellä, zoomaa rullalla. Näet kuinka kertoimet muovaavat kantafunktioista molekyyliorbitaaleja.")
        
        homo_idx = int(res['N_elec'] / 2) - 1
        orb_options = {f"HOMO (Orbitaali {homo_idx}, E={res['evals'][homo_idx]:.3f} au)": homo_idx,
                       f"LUMO (Orbitaali {homo_idx+1}, E={res['evals'][homo_idx+1]:.3f} au)": homo_idx+1}
        
        for i in range(max(0, homo_idx-2), min(len(res['evals']), homo_idx+3)):
            if i not in [homo_idx, homo_idx+1]:
                orb_options[f"Orbitaali {i} (E={res['evals'][i]:.3f} au)"] = i
                
        col_ctrl, col_plot = st.columns([1, 2])
        with col_ctrl:
            selected_orb_label = st.selectbox("Valitse piirrettävä orbitaali", list(orb_options.keys()))
            selected_orb_idx = orb_options[selected_orb_label]
            isovalue = st.slider("Isopinnan arvo (Isovalue)", 0.001, 0.100, 0.025, 0.005)

        with col_plot:
            with st.spinner("Rakennetaan .cube-tiedostoa stmol-kirjastoa varten..."):
                mo_coeffs = res['C'][:, selected_orb_idx]
                cube_filename = "current_orbital.cube"
                generate_cube_file(cube_filename, res['coords'], res['atoms'], res['cgf_ptr'], res['exps'], res['coeffs'], res['norms'], res['lmns'], res['centers'], mo_coeffs)
                
                with open(cube_filename, "r") as f:
                    cube_data = f.read()
                
                view = py3Dmol.view(width=600, height=500)
                view.addModel(cube_data, "cube")
                view.setStyle({'stick': {'radius': 0.15}, 'sphere': {'radius': 0.4}})
                view.addVolumetricData(cube_data, "cube", {'isoval': isovalue, 'color': 'blue', 'opacity': 0.85})
                view.addVolumetricData(cube_data, "cube", {'isoval': -isovalue, 'color': 'red', 'opacity': 0.85})
                view.zoomTo()
                showmol(view, height=500, width=600)

        st.markdown("---")
        st.subheader("Nätimpi, non-interaktiivinen visualisointi")
        if XYZRENDER_AVAILABLE:
            st.write("Tämä osio käyttää xyzrender-kirjastoa luomaan oppikirjatasoisen, varjostetun kuvan orbitaalista.")
            animate_gif = st.checkbox("Animoitu pyörimisliike (GIF) - Tämä kestää kauemmin!")
            
            if st.button("Renderöi kuva", type="secondary"):
                with st.spinner("Luodaan korkealaatuista renderöintiä..."):
                    try:
                        mol_obj = load(cube_filename)
                        
                        # Lisätään isovalue-teksti kuvaan nätisti
                        st.write(f"**Renderöidään valittu orbitaali:** {selected_orb_label}")
                        
                        if animate_gif:
                            # zoom < 1.0 loitontaa kameraa, hide_h=False pakottaa vedyt näkyviin
                            render_gif(mol_obj, output="beautiful_orb.gif", gif_rot="y", canvas_size=800, mo=True, hy=True, iso=isovalue)
                            st.image("beautiful_orb.gif", width=1000)
                        else:
                            render(mol_obj, output="beautiful_orb.png",canvas_size=800, mo=True, iso=isovalue, hy=True )
                            st.image("beautiful_orb.png", width=1000)
                    except Exception as e:
                        st.error(f"Renderöinti epäonnistui: {e}")
        else:
            st.warning("xyzrender-kirjastoa ei ole asennettu. Lisää 'xyzrender' requirements.txt-tiedostoon nähdäksesi tämän osion.")


    # ==========================================
    # 6. PEDAGOGISET TEHTÄVÄT
    # ==========================================
    st.markdown("---")
    with st.expander("Kysymyksiä ja tehtävää"):
        st.markdown(r"""
        **1. Veden HOMO ja LUMO (Symmetria ja sidokset)**
        Aja HF lasku vedelle (SMILES: `O`) ja tarkastele 3D-visualisointia. 
        * Valitse ylin miehitetty orbitaali (HOMO). Tunnistatko tästä hapen vapaan elektroniparin $p$-orbitaalin luonteen? 
        * Vaihda alimpaan miehittämättömään orbitaaliin (LUMO). Miltä näyttää antibonding- eli hajottava tila happi-vety -sidosten välillä?


        **2. Askelkoko ja iteraatioiden määrä (Numeerinen vaimennus)**
        Hartree-Fock on iteratiivinen prosessi. Kokeile muuttaa "Tiheyden sekoitus (mix)" -parametria vetymolekyylille (`[H][H]`). 
        * Aseta se arvoon 1.0 (aggressiivisin asetus: 100% uutta tiheyttä) ja kirjaa ylös vaadittujen iteraatioiden määrä.
        * Laske sekoitus sitten arvoon 0.1 (hyvin varovainen: vain 10% uutta tiheyttä kerrallaan) ja aja laskenta uudelleen.
        * Mitä tapahtuu iteraatioiden määrälle ja SCF-konvergenssikuvaajan muodolle? Ymmärrätkö tämän perusteella, miksi raskaammissa kvanttikemian ohjelmistoissa tasapainoillaan aina laskentanopeuden (suuri mix) ja numeerisen vakauden (pieni mix) välillä?
        
        **3. Isomeerien energiaerot (Kvanttikemiallinen stabiliteetti)**
        Syötä ohjelmaan peräkkäin etanoli (`CCO`) ja dimetyylieetteri (`COC`). Molemmilla on täsmälleen sama kemiallinen kaava (C2H6O) ja siten sama määrä elektroneja ja kantafunktioita.
        * Kirjaa ylös molempien järjestelmien kokonaisenergia (viimeisen iteraation arvo kuvaajasta tai au-yksiköissä). 
        * Kumpi isomeeri on kvanttimekaanisesti vakaampi (eli kummalla on alempi/negatiivisempi energia)?

        **4. Konjugaatio ja HOMO-LUMO -väli**
        Mitä tapahtuu elektronien energioille, kun ne pääsevät liikkumaan laajemmalla alueella? Vertaile seuraavia hiiliketjuja: etaani (`CC`), eteeni (`C=C`) ja butadieeni (`C=CC=C`).
        * Laske jokaiselle molekyylille HOMO:n ja LUMO:n välinen energiaero (E_LUMO - E_HOMO).
        * Huomaatko, kuinka konjugoitujen kaksoissidosten pidentäminen (butadieeni) pienentää tätä energiaväliä? Tämä on kvanttimekaaninen syy sille, miksi pitkät konjugoidut molekyylit (kuten beetakaroteeni porkkanassa) pystyvät absorboimaan matalaenergisempää näkyvää valoa ja ovat värillisiä!
        """)
