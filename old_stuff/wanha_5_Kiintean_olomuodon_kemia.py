import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ==========================================
# 1. UI ASETUKSET
# ==========================================
st.set_page_config(
    page_title="Kiinteän olomuodon kemia", 
    layout="wide"
)

st.title("Moduuli 5: Kiinteän olomuodon kemia")
st.caption("Vyörakenne ja tilatiheys (DOS) Tight-binding -mallilla")
st.divider()

# ==========================================
# 2. FYSIKAALISET LASKENTAFUNKTIOT
# ==========================================
@st.cache_data
def calc_1d_monatomic(alpha, beta, n_k=500, a=1.0):
    """1D monatominen ketju (esim. polyasetyleenin säännöllinen runko)"""
    k = np.linspace(-np.pi/a, np.pi/a, n_k)
    E = alpha + 2 * beta * np.cos(k * a)
    
    # DOS laskenta (käytetään tiheämpää k-verkkoa tarkan histogrammin saamiseksi)
    k_dos = np.linspace(-np.pi/a, np.pi/a, 50000)
    E_dos = alpha + 2 * beta * np.cos(k_dos * a)
    hist, bin_edges = np.histogram(E_dos, bins=200, density=True)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    
    return k, E, bin_centers, hist

@st.cache_data
def calc_1d_diatomic(alpha1, alpha2, beta1, beta2, n_k=500, a=1.0):
    """
    1D biatominen ketju. 
    Kattaa sekä vuorottelevat atomit (alpha1 != alpha2) 
    että vuorottelevat sidokset / Peierls-vääristymä (beta1 != beta2).
    """
    k = np.linspace(-np.pi/a, np.pi/a, n_k)
    # Ratkaistaan 2x2 sekulaariyhtälö
    delta_alpha = (alpha1 - alpha2) / 2
    mean_alpha = (alpha1 + alpha2) / 2
    
    off_diag_sq = beta1**2 + beta2**2 + 2 * beta1 * beta2 * np.cos(k * a)
    
    E_upper = mean_alpha + np.sqrt(delta_alpha**2 + off_diag_sq)
    E_lower = mean_alpha - np.sqrt(delta_alpha**2 + off_diag_sq)
    
    # DOS laskenta
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
    """2D Neliöhila. Reitti: Gamma(0,0) -> X(pi/a, 0) -> M(pi/a, pi/a) -> Gamma(0,0)"""
    # K-avaruuden reitit
    k_Gamma_X_x = np.linspace(0, np.pi/a, n_k)
    k_Gamma_X_y = np.zeros(n_k)
    
    k_X_M_x = np.ones(n_k) * np.pi/a
    k_X_M_y = np.linspace(0, np.pi/a, n_k)
    
    k_M_Gamma_x = np.linspace(np.pi/a, 0, n_k)
    k_M_Gamma_y = np.linspace(np.pi/a, 0, n_k)
    
    # Yhdistetään reitit
    kx_path = np.concatenate([k_Gamma_X_x, k_X_M_x, k_M_Gamma_x])
    ky_path = np.concatenate([k_Gamma_X_y, k_X_M_y, k_M_Gamma_y])
    
    # Etäisyysakseli (x-akseli kuvaajalle)
    path_len = np.zeros(len(kx_path))
    for i in range(1, len(kx_path)):
        dk = np.sqrt((kx_path[i]-kx_path[i-1])**2 + (ky_path[i]-ky_path[i-1])**2)
        path_len[i] = path_len[i-1] + dk
        
    E_path = alpha + 2 * beta * (np.cos(kx_path * a) + np.cos(ky_path * a))
    
    # K-pisteiden lokaatiot x-akselilla
    ticks = [0, path_len[n_k-1], path_len[2*n_k-1], path_len[-1]]
    tick_labels = ['Gamma', 'X', 'M', 'Gamma']
    
    # DOS laskenta (2D grid)
    kx_grid = np.linspace(-np.pi/a, np.pi/a, 500)
    ky_grid = np.linspace(-np.pi/a, np.pi/a, 500)
    KX, KY = np.meshgrid(kx_grid, ky_grid)
    E_dos = alpha + 2 * beta * (np.cos(KX * a) + np.cos(KY * a))
    
    hist, bin_edges = np.histogram(E_dos.flatten(), bins=200, density=True)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    
    return path_len, E_path, ticks, tick_labels, bin_centers, hist

# ==========================================
# 3. SIVUPALKKI JA PARAMETRIT
# ==========================================
st.sidebar.header("Hilan malli")
lattice_type = st.sidebar.selectbox(
    "Valitse tutkittava hila",
    ["1D Monatominen ketju", "1D Biatominen (Peierls)", "2D Neliöhila"]
)

st.sidebar.divider()
st.sidebar.header("Fysikaaliset parametrit")

if lattice_type == "1D Monatominen ketju":
    alpha = st.sidebar.slider("Atomin energia (alpha)", -10.0, 0.0, -5.0, 0.5)
    beta = st.sidebar.slider("Resonanssi-integraali (beta)", -5.0, 0.0, -2.0, 0.1)

elif lattice_type == "1D Biatominen (Peierls)":
    st.sidebar.markdown("**Atomien energiat**")
    alpha1 = st.sidebar.slider("Atomi 1 (alpha 1)", -10.0, 0.0, -5.0, 0.5)
    alpha2 = st.sidebar.slider("Atomi 2 (alpha 2)", -10.0, 0.0, -5.0, 0.5)
    st.sidebar.markdown("**Sidosten vahvuudet**")
    beta1 = st.sidebar.slider("Sidos 1 (beta 1)", -5.0, 0.0, -2.0, 0.1)
    beta2 = st.sidebar.slider("Sidos 2 (beta 2)", -5.0, 0.0, -2.0, 0.1)

elif lattice_type == "2D Neliöhila":
    alpha = st.sidebar.slider("Atomin energia (alpha)", -10.0, 0.0, -5.0, 0.5)
    beta = st.sidebar.slider("Resonanssi-integraali (beta)", -5.0, 0.0, -1.0, 0.1)

# ==========================================
# 4. LASKENTA JA VISUALISOINTI
# ==========================================
fig = make_subplots(rows=1, cols=2, shared_yaxes=True, 
                    column_widths=[0.7, 0.3], horizontal_spacing=0.02,
                    subplot_titles=("Vyörakenne E(k)", "Tilatiheys (DOS)"))

if lattice_type == "1D Monatominen ketju":
    k, E, e_dos, dos = calc_1d_monatomic(alpha, beta)
    
    fig.add_trace(go.Scatter(x=k, y=E, mode='lines', line=dict(color='blue', width=3), name='E(k)'), row=1, col=1)
    fig.add_trace(go.Scatter(x=dos, y=e_dos, mode='lines', fill='tozerox', line=dict(color='gray'), name='DOS'), row=1, col=2)
    
    fig.update_xaxes(title_text="Aaltovektori k", tickvals=[-np.pi, 0, np.pi], ticktext=['-pi/a', '0', 'pi/a'], row=1, col=1)
    
elif lattice_type == "1D Biatominen (Peierls)":
    k, E1, E2, e_dos, dos = calc_1d_diatomic(alpha1, alpha2, beta1, beta2)
    
    fig.add_trace(go.Scatter(x=k, y=E1, mode='lines', line=dict(color='red', width=3), name='Alempi vyö'), row=1, col=1)
    fig.add_trace(go.Scatter(x=k, y=E2, mode='lines', line=dict(color='blue', width=3), name='Ylempi vyö'), row=1, col=1)
    fig.add_trace(go.Scatter(x=dos, y=e_dos, mode='lines', fill='tozerox', line=dict(color='gray'), name='DOS'), row=1, col=2)
    
    fig.update_xaxes(title_text="Aaltovektori k", tickvals=[-np.pi, 0, np.pi], ticktext=['-pi/a', '0', 'pi/a'], row=1, col=1)

elif lattice_type == "2D Neliöhila":
    path_len, E, ticks, tick_labels, e_dos, dos = calc_2d_square(alpha, beta)
    
    fig.add_trace(go.Scatter(x=path_len, y=E, mode='lines', line=dict(color='green', width=3), name='E(k)'), row=1, col=1)
    fig.add_trace(go.Scatter(x=dos, y=e_dos, mode='lines', fill='tozerox', line=dict(color='gray'), name='DOS'), row=1, col=2)
    
    # Lisätään pystyviivat K-pisteiden merkiksi
    for t in ticks:
        fig.add_vline(x=t, line_width=1, line_dash="dash", line_color="gray", row=1, col=1)
        
    fig.update_xaxes(title_text="K-pisteiden reitti", tickvals=ticks, ticktext=tick_labels, row=1, col=1)

# Yhteiset kuvaajan asetukset
fig.update_yaxes(title_text="Energia (E)", row=1, col=1)
fig.update_xaxes(title_text="DOS", row=1, col=2)
fig.update_layout(height=600, showlegend=False, hovermode="y unified")

st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 5. PEDAGOGINEN OSIO
# ==========================================
with st.expander("Pedagogisia huomioita ja tehtäviä"):
    st.write("""
    1. **Van Hoven singulariteetit:** Tarkastele 1D monatomista ketjua. Huomaatko, kuinka tilatiheys (DOS) kasvaa äärettömäksi vyön ala- ja yläreunoilla? Tämä on tyypillistä 1D-järjestelmille, koska $dE/dk = 0$ reunoilla. Miten DOS eroaa 2D-neliöhilassa?
    2. **Peierlsin vääristymä:** Valitse "1D Biatominen". Aseta aluksi kaikki parametrit samoiksi ($\alpha_1 = \alpha_2$, $\beta_1 = \beta_2$). Pienennä sitten $\beta_2$:n absoluuttista arvoa hieman (esim. $\beta_1 = -2.0, \beta_2 = -1.5$). Mitä tapahtuu pisteessä $k = \pm \pi/a$? Tämä on ns. Peierlsin vääristymä, jossa tasamittainen 1D-metalli muuttuu eristeeksi dimerisoitumalla!
    3. **Elektronegatiivisuus:** Pidä $\beta_1$ ja $\beta_2$ samoina, mutta muuta atomien energioita $\alpha$. Tämä vastaa kidehilaa, joka koostuu kahdesta eri alkuaineesta (esim. hiili ja typpi vuorotellen). Miten vyöaukon (band gap) koko riippuu $\alpha_1$:n ja $\alpha_2$:n erotuksesta?
    """)
