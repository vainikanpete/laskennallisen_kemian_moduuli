import streamlit as st
import numpy as np
import scipy.linalg as la
import math
import plotly.graph_objects as go
from numba import njit
from rdkit import Chem
from rdkit.Chem import AllChem

st.set_page_config(page_title="Walsh-diagrammit (EHT)", layout="wide")

st.title("Moduuli 7: Walsh-diagrammit (Extended Hückel)")
st.caption("Yleinen EHT-ratkaisija mielivaltaisille molekyyligeometrioille ja deformaatioille")
st.divider()

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

col_input, col_plot = st.columns([1, 2])

with col_input:
    st.subheader("Molekyyli")
    smiles = st.text_input("Syötä SMILES (H, C, N, O)", value="O")
    mol, atoms, available_angles = get_molecule_and_angles(smiles)
    
    if mol and available_angles:
        symbols = [a.GetSymbol() for a in mol.GetAtoms()]
        angle_options = {f"{symbols[i]}{i} - {symbols[j]}{j} - {symbols[k]}{k}": (i, j, k) for (i, j, k) in available_angles}
        selected_angle_str = st.selectbox("Valitse muutettava sidoskulma", list(angle_options.keys()))
        i_idx, j_idx, k_idx = angle_options[selected_angle_str]
        
        st.subheader("Skannauksen asetukset")
        start_angle = st.number_input("Alkukula (°)", value=90.0)
        end_angle = st.number_input("Loppukulma (°)", value=180.0)
        points = st.slider("Mittapisteiden määrä", 10, 100, 40)
        K_const = st.slider("Wolfsberg-Helmholz vakio (K)", 1.0, 2.5, 1.75, 0.05)
        run_scan = st.button("Laske Walsh-diagrammi", type="primary")

with col_plot:
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
            
            # Lisätään numeerinen stabilisaattori (epsilon) lävistäjälle estämään singulaarisuus
            S_reg = S + np.eye(len(S)) * 1e-8
            
            evals = la.eigvalsh(H, S_reg)
            eigenvalues.append(evals)
            bar.progress((idx + 1) / points, text="Lasketaan Extended Hückel matriiseja...")
            
        eigenvalues = np.array(eigenvalues)
        fig = go.Figure()
        for band in range(eigenvalues.shape[1]):
            fig.add_trace(go.Scatter(x=scan_angles, y=eigenvalues[:, band], mode='lines', line=dict(color='blue')))
            
        fig.add_vline(x=original_angle, line_width=2, line_dash="dot", line_color="red", annotation_text=" RDKit Optimigeometria")
        fig.update_layout(title=f"Walsh-diagrammi: Kulman {selected_angle_str} muutos", xaxis_title="Sidoskulma (°)", yaxis_title="MO Energia (eV)", height=600, showlegend=False, hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)
