import streamlit as st
import time
import base64

# ==========================================
# 1. YLEISET ASETUKSET & TYYLIT
# ==========================================
st.set_page_config(
    page_title="Laskennallinen Kemia",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .block-container { animation: fadeIn 1.2s ease-in; } 
    @keyframes fadeIn { 0% { opacity: 0; } 100% { opacity: 1; } }
    
    .main-card {
        background-color: #f8f9fa;
        padding: 30px;
        border-radius: 10px;
        border-left: 5px solid #4A90E2;
        margin-bottom: 20px;
    }
    .module-list {
        line-height: 1.8;
    }
    .pulse-logo {
        animation: pulse 2.0s infinite;
        max-width: 500px;
    }
    @keyframes pulse {
        0% { transform: scale(0.98); opacity: 0.9; }
        50% { transform: scale(1.02); opacity: 1; }
        100% { transform: scale(0.98); opacity: 0.9; }
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. LATAUSRUUTU (SPLASH SCREEN)
# ==========================================



@st.cache_data
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

if 'app_loaded' not in st.session_state:
    st.session_state.app_loaded = False

if not st.session_state.app_loaded:
    splash = st.empty()
    with splash.container():
        try:
            logo_base64 = get_base64_image("logo.png")
            # Added border-radius and box-shadow to make the square background look like a stylized app icon
            img_element = f'<img src="data:image/png;base64,{logo_base64}" style="width: 480px; border-radius: 20px; box-shadow: 0 8px 16px rgba(0,0,0,0.4); animation: pulse 1.5s infinite;">'
        except FileNotFoundError:
            img_element = '<div style="font-size: 80px; animation: pulse 1.5s infinite;">⚛️</div>'

        # Force absolute centering using a 100% width flex container
        st.markdown(f"""
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 80vh; width: 100%;">
            {img_element}
            <h2 style="color: #4A90E2; font-weight: 300; letter-spacing: 2px; margin-top: 30px; animation: pulse 1.5s infinite;">Ladataan laskennallisen kemian moduuleja ...</h2>
        </div>
        <style>
        @keyframes pulse {{
            0% {{ transform: scale(0.95); opacity: 0.8; }}
            50% {{ transform: scale(1.05); opacity: 1; }}
            100% {{ transform: scale(0.95); opacity: 0.8; }}
        }}
        </style>
        """, unsafe_allow_html=True)
        
    time.sleep(4.0)
    splash.empty()
    st.session_state.app_loaded = True
    st.rerun()


# Apply the fade-in effect and custom CSS to the main UI
st.markdown("""
    <style>
    .block-container { animation: fadeIn 1.2s ease-in; } 
    @keyframes fadeIn { 0% { opacity: 0; } 100% { opacity: 1; } }
    
    .stSelectbox div[data-baseweb="select"] {
        cursor: pointer;
        background-color: #f0f2f6;
        border-radius: 8px;
        border: 2px solid #4A90E2;
    }
    .metric-container {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
    }
    </style>
""", unsafe_allow_html=True)




# ==========================================
# 3. PÄÄSIVUN SISÄLTÖ
# ==========================================
st.title("Lyhyt esittely laskennallisesta kemiasta")
st.write("**Turun yliopisto | Kemian laitos**")
st.divider()

col1, col2 = st.columns([1.5, 1])

with col1:
    st.markdown("""
    <div class="main-card">
        <h3>Moduulin tavoite</h3>
        <p>Tämä oppimisympäristö on suunniteltu havainnollistamaan kvanttimekaniikan ja laskennallisen kemian keskeisiä ilmiöitä ja mekanismeja. 
        Teorian lukemisen sijaan pääset kokeilemaan reaaliajassa, miten parametrien muuttaminen vaikuttaa aaltofunktioihin, 
        energiatasoihin ja molekyylien ominaisuuksiin.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("Valitse moduuli vasemman reunan valikosta aloittaaksesi tutkimuksen.")

    st.subheader("Moduulit")
    st.markdown("""
    <div class="module-list">
    <b>1. 1D Potentiaalit:</b> Ratkaise Schrödingerin yhtälö numeerisesti ja tarkastele klassisia potentiaalimalleja.<br>
    <b>2. Laajennettu Hückel:</b> Tutki MO-teoriaa, sidosenergioita ja Wolfsberg-Helmholz -approksimaatiota.<br>
    <b>3. Hartree-Fock (RHF):</b> Syvenny itseytyvän kentän (SCF) menetelmään ja 3D-orbitaalien visualisointiin.<br>
    <b>4. Radiaaliset jakautumafunktiot:</b> Vertaile atomiorbitaalien säteittäisiä jakaumia ja varjostusefektejä.<br>
    <b>5. Tunneloituminen:</b> Tutki hiukkasen läpäisytodennäköisyyksiä siirtomatriisimenetelmällä.<br>
    <b>6. Extrat:</b> Syventävää materiaalia Walsh-diagrammeista ja kiinteän olomuodon kemiasta.
    </div>
    """, unsafe_allow_html=True)

with col2:
    # Käytetään pot.png kuvaa visualisointina
    st.image("picture1.jpeg", 
             caption="", width=320)
    
    with st.expander("Ohjeita käyttöön", expanded=True):
        st.write("""
        * **Visualisointi:** Kaikki 3D-mallit ja kuvaajat ovat interaktiivisia.
        """)

# Alatunniste
st.sidebar.markdown("---")
st.sidebar.caption("Phys. & Comp. Chem. Über Alles")
st.sidebar.markdown(
    "<div style='color: #888; font-size: 0.85em; margin-top: 20px; font-style: italic;'>"
    "Omistettu J. Sinkkoselle <br> Le Roi est mort. Vive le Roi!"
    "</div>", 
    unsafe_allow_html=True
)
import streamlit as st
import numpy as np
import scipy.linalg as la
import plotly.graph_objects as go

# ==========================================
# 1. UI CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="1D Potentiaalit", 
    layout="wide"
)

st.title("Moduuli 1: 1D Potentiaalit")
st.caption("Numeerinen Schrödingerin yhtälön ratkaisija differenssimenetelmällä")
st.divider()

# ==========================================
# 2. PHYSICS FUNCTIONS (Cached for performance)
# ==========================================
@st.cache_data
def solve_schrodinger_1d(x, V, mass, d, norbs):
    npts = len(x)
    t0 = 1.0 / (2.0 * mass * d**2)
    
    main_diag = 2.0 * t0 + V
    off_diag = -t0 * np.ones(npts - 1)
    
    # Construct tridiagonal Hamiltonian matrix
    H = np.diag(main_diag) + np.diag(off_diag, k=1) + np.diag(off_diag, k=-1)
    
    # Solve eigenvalue problem
    eigvals, eigvecs = la.eigh(H)
    
    # Return requested number of orbitals
    return eigvals[:norbs], eigvecs[:, :norbs]

def calculate_expectation_values(x, eigvec, d):
    # Oikeaoppinen normitus dx:n (d) avulla
    norm_factor = np.sum(eigvec**2) * d
    psi_norm = eigvec / np.sqrt(norm_factor)
    
    psi2 = psi_norm**2
    
    # Sijainnin odotusarvot (integraalit dx yli)
    exp_x = np.sum(psi2 * x) * d
    exp_x2 = np.sum(psi2 * x**2) * d
    
    # Derivaatat numeerisesti
    first_deriv = np.gradient(psi_norm, d)
    second_deriv = np.gradient(first_deriv, d)
    
    # Liikemäärän odotusarvo <p>. Koska psi on reaalinen, <p> on tasan 0.
    exp_p = 0.0 
    
    # Liikemäärän neliön odotusarvo <p^2> = int( psi * (-d^2/dx^2 psi) ) dx
    exp_p2 = np.sum(psi_norm * (-second_deriv)) * d
    
    return exp_x, exp_x2, exp_p, exp_p2

# ==========================================
# 3. SIDEBAR PARAMETERS
# ==========================================
st.sidebar.header("Järjestelmän asetukset")
pot_type = st.sidebar.selectbox(
    "Potentiaalin tyyppi", 
    ["Ääretön kaivo", "Äärellinen kaivo", "Kaksoiskaivo", "Harmoninen värähtelijä", "Morse-potentiaali", "Kronig-Penney (Hila)"]
)

mass = st.sidebar.number_input("Hiukkasen massa (au)", value=2.0, min_value=0.1, step=0.5)
L = st.sidebar.number_input("Tilan leveys L (au)", value=10.0, min_value=0.1, step=1.0)

d = st.sidebar.number_input(
    "Hilan tiheys d (au)", 
    value=0.05, 
    min_value=0.01,
    step=0.01, 
    format="%.3f",
    help="Hila (grid) tarkoittaa niitä diskreettejä pisteitä, joissa aaltofunktio lasketaan. Pienempi luku tarkoittaa tiheämpää hilaa ja tarkempaa tulosta, mutta raskaampaa laskentaa."
)
norbs = st.sidebar.number_input(
    "Laskettavien tilojen määrä", 
    value=4, 
    min_value=1, 
    step=1,
    help="Määrittää, kuinka monta alinta kvanttitilaa (energiatasoa ja aaltofunktiota) Hamiltonin matriisista ratkaistaan ja visualisoidaan."
)

npts = int(L / d)
x = np.linspace(-L/2, L/2, npts)
V = np.zeros(npts)

st.sidebar.header("Potentiaalin parametrit")

if pot_type == "Ääretön kaivo":
    st.sidebar.info("Reunaehdot on asetettu automaattisesti äärettömiksi laatikon reunoilla.")
    
elif pot_type == "Äärellinen kaivo":
    depth = st.sidebar.number_input("Kaivon syvyys (au)", value=1.0, step=0.1)
    width = st.sidebar.number_input("Kaivon leveys (au)", value=2.0, step=0.1)
    V = np.zeros(npts)
    V[np.abs(x) <= width/2] = -depth
    V = V - np.min(V)

elif pot_type == "Kaksoiskaivo":
    depth = st.sidebar.number_input("Kaivojen syvyys (au)", value=2.0, step=0.1)
    width = st.sidebar.number_input("Yksittäisen kaivon leveys (au)", value=2.0, step=0.1)
    distance = st.sidebar.number_input("Kaivojen välimatka (au)", value=4.0, step=0.1)
    V = np.zeros(npts)
    V[np.abs(x - distance/2) <= width/2] = -depth
    V[np.abs(x + distance/2) <= width/2] = -depth
    V = V - np.min(V)

elif pot_type == "Harmoninen värähtelijä":
    spring = st.sidebar.number_input("Jousivakio k", value=10.0, step=1.0)
    V = (spring / 2.0) * x**2

elif pot_type == "Morse-potentiaali":
    De = st.sidebar.number_input("Dissosiaatioenergia (De)", value=5.0, step=0.5)
    alpha = st.sidebar.number_input("Kuoppaparametri (alpha)", value=1.0, step=0.1)
    V = De * (1 - np.exp(-alpha * x))**2
    V = np.minimum(V, De * 2.0)

elif pot_type == "Kronig-Penney (Hila)":
    wells = st.sidebar.number_input("Kaivojen lukumäärä", value=4, min_value=2, step=1)
    depth = st.sidebar.number_input("Kaivon syvyys (au)", value=0.5, step=0.1)
    lattice_const = L / wells
    V = np.where(np.sin(2 * np.pi * (x + L/2) / lattice_const) > 0, -depth, 0)
    V = V - np.min(V)

# ==========================================
# 4. CALCULATION & VISUALIZATION
# ==========================================
with st.spinner("Ratkaistaan Hamiltonin matriisia..."):
    eigvals, eigvecs = solve_schrodinger_1d(x, V, mass, d, norbs)

tab1, tab2, tab3 = st.tabs(["Ohjeet", "Aaltofunktiot", "Odotusarvot"])

with tab1:
    st.subheader("Yleistä")
    st.markdown("""
    Tervetuloa leikkimään yksiulotteisten potentiaalien kanssa! Ruudun takana kirjoittamani pieni ohjelma ratkoo ajasta riippumattoman Schrödingerin yhtälön yksittäiselle hiukkaselle erilaisissa yksiulotteisissa potentiaalikuopissa.

Ratkaisu tapahtuu differenssimenetelmällä (oikeasti) jatkuvan aaltofunktion approksimoimiseksi rajallisessa, diskreetissä tilassa. Säätämällä sivupalkissa potentiaalin muotoa, hiukkasen massaa ja tilan parametreja voit tutkia, miten nämä tekijät vaikuttavat:

    * Energiatasoihin
    * Aaltofunktion todennäköisyysjakaumiin
    * Heisenbergin epätarkkuusperiaatteeseen

Aloita valitsemalla potentiaalityyppi ja säätämällä parametreja. Siirry Aaltofunktiot-välilehdelle tarkastellaksesi tuloksena olevia tiloja.


### Hiukan eri potentiaaleista... 

Tässä moduulissa voit tutkia tavanomaisten potentiaalikaivojen lisäksi kolmea fysiikan ja kemian kannalta tärkeää potentiaalimallia, joista ensimmäinen lieneekin jo tuttu:

**1. Harmoninen värähtelijä (Harmonic Oscillator)** $V(x) = \\frac{1}{2}kx^2$  
Kvanttimekaaninen harmoninen värähtelijä on yksi modernin fysiikan tärkeimmistä malleista. Se kuvaa hiukkasta, johon kohdistuu Hooken lain mukainen palauttava voima (kuten jousi). Kemiassa tätä käytetään mallintamaan molekyylien välisten sidosten värähtelyä lähellä niiden tasapainoetäisyyttä (esim. IR-spektroskopia).  
* **Erityispiirre:** Energiatasot ovat täysin tasavälein ($E_n = \hbar\omega(n + 1/2)$). Lisäksi huomaat, että alin energiataso ei ole koskaan nolla (ns. nollapiste-energia), mikä on suora seuraus Heisenbergin epätarkkuusperiaatteesta.

**2. Morse-potentiaali (Morse Potential)** $V(x) = D_e(1 - e^{-\\alpha x})^2$  
Harmoninen malli on vain approksimaatio, sillä oikeaa vieteriä ei voi venyttää loputtomiin – kemialliset sidokset katkeavat. Morse-potentiaali on realistisempi malli kaksiatomisen molekyylin värähtelylle. Se huomioi epäharmonisuuden ja sidoksen dissosiaation (hajoamisen).  
* **Erityispiirre:** Kun energia kasvaa (mennään ylemmille tiloille), energiatasot pakkautuvat yhä tiheämmin yhteen. Kun energia ylittää dissosiaatioenergian ($D_e$), sidos katkeaa ja hiukkanen on vapaa.

**3. Kronig-Penney -malli (1D Kidehila)** Tämä potentiaali mallintaa elektronin liikettä säännöllisessä kidehilassa (esim. metallijohdin tai puolijohde). Jaksollisesti toistuvat potentiaalikaivot edustavat säännöllisin välimatkoin sijaitsevia positiivisesti varautuneita atomiytimiä, jotka vetävät elektronia puoleensa.  
* **Erityispiirre:** Kun aaltofunktio venyy usean kaivon yli, kaivojen väliset vuorovaikutukset saavat yksittäiset energiatasot jakautumaan. Jos kasvatat tilojen määrää, näet kuinka tasot alkavat muodostaa tiheitä ryppäitä eli **energiavöitä** (allowed bands), joiden väliin jää tyhjiä **vyöaukkoja** (band gaps). Tämä on koko modernin puolijohdefysiikan (ja tietokoneiden) perusta!

    """)

with tab2:
    fig = go.Figure()
    
    # Plot potential
    fig.add_trace(go.Scatter(x=x, y=V, mode='lines', name='Potentiaali V(x)', line=dict(color='black', width=3)))
    
    # Dynaaminen skaalaus: katsotaan vain sitä energia-aluetta jota opiskelija oikeasti tutkii
    energy_span = max(eigvals[-1] - np.min(V), 1.0)
    
    # Plot wavefunctions
    for i in range(len(eigvals)):
        energy = eigvals[i]
        psi = eigvecs[:, i]
        
        # Phase standardization
        if psi[npts // 2] < 0 if pot_type != "Ääretön kaivo" else psi[1] < 0:
            psi = -psi
        
        # Amplitudi skaalataan suhteessa tarkasteltavaan energia-alueeseen (15% koko välistä)
        scale_factor = (energy_span * 0.15) / np.max(np.abs(psi))
        psi_plot = (psi * scale_factor) + energy
        
        fig.add_trace(go.Scatter(x=x, y=psi_plot, mode='lines', name=f'ψ_{i} (E={energy:.3f})'))
        fig.add_trace(go.Scatter(x=[x[0], x[-1]], y=[energy, energy], mode='lines', line=dict(color='gray', dash='dash'), showlegend=False))
    
    # Rajataan y-akseli ylimmän pyydetyn tilan ympärille
    y_max_plot = eigvals[-1] + energy_span * 0.4
    y_min_plot = np.min(V) - energy_span * 0.1
    
    fig.update_layout(
        title=f"Kvanttijärjestelmän aaltofunktiot: {pot_type}",
        xaxis_title="Sijainti x (au)",
        yaxis_title="Energia (au)",
        yaxis=dict(range=[y_min_plot, y_max_plot]),
        height=600
    )
    
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Tilojen odotusarvot ja epätarkkuusperiaate")
    
    st.markdown("""
    **Merkintöjen selitykset:**
    * $\langle x \\rangle$: Sijainnin odotusarvo. Kertoo hiukkasen keskimääräisen sijainnin.
    * $\langle x^2 \\rangle$: Sijainnin neliön odotusarvo.
    * $\langle p \\rangle$: Liikemäärän odotusarvo. Tässä simulaatiossa aaltofunktiot ovat seisovia aaltoja (reaalisia), joten hiukkanen ei etene keskimäärin kumpaankaan suuntaan ($\langle p \\rangle = 0$).
    * $\Delta x$: Sijainnin epätarkkuus eli keskihajonta ($\sqrt{\langle x^2 \\rangle - \langle x \\rangle^2}$).
    * $\Delta p$: Liikemäärän epätarkkuus eli keskihajonta ($\sqrt{\langle p^2 \\rangle - \langle p \\rangle^2}$). Tämä **ei** ole nolla, koska hiukkasella on kineettistä energiaa ($\langle p^2 \\rangle > 0$).
    * $\Delta x \Delta p$: Heisenbergin epätarkkuustulo. Kvanttimekaniikan mukaan tämän on aina oltava vähintään $\hbar/2$ (atomiyksiköissä $0.5$). Numeerinen approksimaatio voi heittää desimaalin osilla.
    """)
    st.divider()
    
    results = []
    for i in range(len(eigvals)):
        exp_x, exp_x2, exp_p, exp_p2 = calculate_expectation_values(x, eigvecs[:, i], d)
        
        # Heisenberg uncertainty principle: delta_x * delta_p >= hbar/2
        delta_x = np.sqrt(np.abs(exp_x2 - exp_x**2))
        delta_p = np.sqrt(np.abs(exp_p2 - exp_p**2))
        uncertainty_product = delta_x * delta_p
        
        results.append({
            "Tila (n)": i,
            "Energia (au)": f"{eigvals[i]:.4f}",
            "<x>": f"{exp_x:.4f}",
            "<x²>": f"{exp_x2:.4f}",
            "<p>": f"{exp_p:.4f}",
            "Δx": f"{delta_x:.4f}",
            "Δp": f"{delta_p:.4f}",
            "ΔxΔp": f"{uncertainty_product:.4f}"
        })
        
    st.table(results)

# ==========================================
# 5. PEDAGOGICAL EXPANDER
# ==========================================
with st.expander("Kysymyksiä ja huomioita"):
    st.write("""
    1. **Kvantittuminen:** Kuinka energiatasojen välimatka muuttuu, kun kasvatat hiukkasen massaa tai levennät potentiaalikaivoa?
    2. **Tunneloituminen:** Tarkastele äärellistä kaivoa. Huomaatko, kuinka aaltofunktio ei putoa nollaan kaivon reunoilla, vaan tunkeutuu klassisesti kielletylle alueelle?
    3. **Epätarkkuusperiaate:** Katso Odotusarvot-välilehteä ja kokeile kaventaa kaivon leveyttä (L); mitä tapahtuu $\Delta p$:lle, kun pakotat hiukkasen tarkempaan sijaintiin ($\Delta x$ pienenee)?
    4. **Solmukohdat:** Laske kunkin aaltofunktion nollakohdat (solmut / noodit). Mikä sääntö yhdistää tilan järjestysnumeron ja solmujen määrän?
    5. **Harmoninen värähtelijä:** Onko energia koskaan 0? Miksi näin on? Kokeile kasvattaa jousivakiota (k). Mitä tapahtuu energiatasojen välimatkalle?
    """)
import streamlit as st
import numpy as np
import scipy.linalg as la
import plotly.graph_objects as go

# ==========================================
# 1. UI ASETUKSET
# ==========================================
st.set_page_config(
    page_title="Laajennettu Hückel", 
    layout="wide"
)

st.title("Moduuli 2: Laajennettu Hückel (EHT) ja MO-teoria")
st.caption("Semiempiiriset menetelmät ja molekyyliorbitaalidiagrammit")
st.divider()

# ==========================================
# 2. VÄLILEHDET
# ==========================================
tab_teoria, tab_mo = st.tabs(["Selitykset ja ohjeet", "Interaktiivinen MO-diagrammi"])

with tab_teoria:
    st.markdown("""
    ### Mihin on semiempiria viittaa?
    Kvanttikemiassa *ab initio* -menetelmät (kuten Hartree-Fock) laskevat kaikki elektronien väliset vuorovaikutukset *alusta alkaen* (ab initio on latinaa, ja tarkoittaa kirjaimellisesti 'alusta lähtien'), mikä vaatii suuren joukon raskaita integraalilaskuja. 
    **Semiempiirisissä menetelmissä** nämä raskaimmat ja hitaimmat matemaattiset funktiot (kuten 2-elektroni-integraalit) jätetään kokonaan laskematta ja ne korvataan kokeellisesta datasta tai erityisen fiksuista arvauksista johdetuilla parametreilla. Tämä tekee laskennasta nopeaa, säilyttäen kuitenkin molekyylin kvanttimekaanisen symmetrian ja orbitaalien perusluonteen.

    ### Laajennettu Hückel -teoria (EHT)
    Alkuperäinen Erich Hückelin teoria (1930-luku) otti huomioon vain tasomaisten molekyylien $\pi$-elektronit (esim. bentseeni). Roald Hoffmannin vuonna 1963 kehittämä **Laajennettu Hückel -teoria (Extended Hückel Theory, EHT)** ottaa huomioon *kaikki* valenssielektronit (sekä $\sigma$- että $\pi$-orbitaalit) ja toimii myös ei-tasomaisille rakenteille.

    EHT:n kulmakivet:
    1. **Kantafunktiot:** Vain valenssiorbitaalit otetaan mukaan. Sisäkuorten elektronit oletetaan passiiviseksi ytimeksi.
    2. **Diagonaalielementit ($H_{ii}$):** Atomin oman orbitaalin energia. Tähän käytetään suoraan atomin **VOIP-arvoa** (Valence Orbital Ionization Potential), joka on kokeellisesti mitattu ionisaatioenergia.
    3. **Peittomatriisi ($S_{ij}$):** Orbitaalien välinen spatiaalinen peittyminen lasketaan tarkasti. Mitä lähempänä vuorovaikuttavat hituset (atomit/ionit) ovat, sitä suurempi $S$.
    4. **Päälävistäjän ulkopuoliset elementit ($H_{ij}$):** Atomien välinen vuorovaikutus (resonanssi/sidos) lasketaan **Wolfsberg-Helmholtz -approksimaatiolla**:
       $H_{ij} = K \cdot S_{ij} \\frac{H_{ii} + H_{jj}}{2}$
       Tässä $K$ on empiirinen vakio (yleensä 1.75).

    ### Kantafunktiot: STO vs. GTO
    Aaltofunktioita mallinnetaan tietokoneessa kantafunktioilla. Kaksi päätyyppiä ovat:
    
    * **Slater-tyyppiset orbitaalit (Slater Type Orbitals, STO, $e^{-\zeta r}$):** Fyysisesti erittäin tarkkoja. Niillä on terävä kärki (cusp) atomin ytimen kohdalla ja ne suppenevat etäisyyden kasvaessa juuri kuten oikeatkin elektronipilvet. Ongelma: Monikeskisten integraalien laskeminen STO:illa on matemaattisesti raskasta. **EHT käyttää STO-funktioita**, koska siinä lasketaan vain helppoja kahden keskuksen peittymisintegraaleja ($S_{ij}$).
    
    * **Gaussin orbitaalit (Gaussian Type Orbital, $e^{-\\alpha r^2}$):**
      Fyysisesti hieman vääriä (liian nopeasti suppeneva), mutta niillä on hyödyllinen matemaattinen ominaisuus: kahden GTO:n tulo on aina uusi GTO. Tämä tekee miljoonien integraalien laskemisesta tietokoneella mukavaa, käytännöllistä ja nopeaa. **Hartree-Fock ja moderni DFT käyttävätkin usein GTO-funktioita.**
    """)

with tab_mo:
    st.markdown("""
    ### Kahden orbitaalin vuorovaikutus
    Tämä työkalu ratkaisee yleisen $A-B$ sidoksen MO-diagramminmatriisimuotoisen ajasta riippumattoman Schrödingerin yhtälön HC=ESC avulla.
    Voit säätää atomien energioita ja peittymisintegraalia ja nähdä kaksi MO-teorian perussääntöä:
    1. Sitova orbitaali saa enemmän luonnetta elektronegatiivisemmalta (alempana olevalta) atomilta. Hajottava orbitaali saa enemmän luonnetta elektropositiivisemmalta atomilta.
    2. Jos peittointegraali $S > 0$, hajottava tila nousee ylöspäin **enemmän** kuin sitova tila laskee alaspäin (sterinen repulsio).
    """)
    
    col_ctrl, col_plot = st.columns([1, 2.5])
    
    with col_ctrl:
        st.subheader("Parametrit")
        alpha_a = st.slider("Atomi A energia $(α_A)$ eV", -25.0, -5.0, -13.6, 0.5)
        alpha_b = st.slider("Atomi B energia $(α_B)$ eV", -25.0, -5.0, -13.6, 0.5)
        
        st.divider()
        S_ab = st.slider("Peittointegraali ($S$)", 0.0, 0.8, 0.3, 0.05, help="S=0 tarkoittaa ortogonaalista Hückel-teoriaa. S>0 on oikeampi EHT.")
        K_val = st.slider("Wolfsberg-Helmholtz vakio (K)", 1.0, 3.0, 1.75, 0.05)
        
        # Wolfsberg-Helmholtz approksimaatio beta:lle
        beta = K_val * S_ab * (alpha_a + alpha_b) / 2.0
        st.info(f"Laskettu resonanssi-integraali $(H_{{ij}})$: **{beta:.2f} eV**")

    with col_plot:
        # 1. Rakennetaan matriisit
        H = np.array([
            [alpha_a, beta],
            [beta, alpha_b]
        ])
        S_mat = np.array([
            [1.0, S_ab],
            [S_ab, 1.0]
        ])
        
        # 2. Ratkaistaan ominaisarvot (E) ja vektorit (C)
        # Käytetään scipy.linalg.eigh joka ratkaisee H*C = E*S*C
        evals, evecs = la.eigh(H, S_mat)
        
        # Evals[0] on sitova (alempi), Evals[1] on hajottava (ylempi)
        E_bind = evals[0]
        E_anti = evals[1]
        
        # Kertoimet (C) on normalisoitu S:n suhteen: C^T * S * C = I
        C_bind_A, C_bind_B = evecs[0, 0], evecs[1, 0]
        C_anti_A, C_anti_B = evecs[0, 1], evecs[1, 1]
        
        # Visuaaliset painot viivoille (pelkkä kerroin^2 antaa karkean arvion)
        w_bind_A = max(1, int(10 * (C_bind_A**2 / (C_bind_A**2 + C_bind_B**2))))
        w_bind_B = max(1, int(10 * (C_bind_B**2 / (C_bind_A**2 + C_bind_B**2))))
        
        w_anti_A = max(1, int(10 * (C_anti_A**2 / (C_anti_A**2 + C_anti_B**2))))
        w_anti_B = max(1, int(10 * (C_anti_B**2 / (C_anti_A**2 + C_anti_B**2))))
        
        # 3. Piirretään diagrammi
        fig = go.Figure()
        
        # Atomi A (Vasen, x=0)
        fig.add_trace(go.Scatter(x=[-1.1, -0.9], y=[alpha_a, alpha_a], mode='lines', line=dict(color='black', width=4), name='Atomi A (AO)'))
        fig.add_annotation(x=-1.0, y=alpha_a - 0.5, text="Atomi A (AO)", showarrow=False)
        
        # Atomi B (Oikea, x=2)
        fig.add_trace(go.Scatter(x=[0.9, 1.1], y=[alpha_b, alpha_b], mode='lines', line=dict(color='black', width=4), name='Atomi B (AO)'))
        fig.add_annotation(x=1.0, y=alpha_b - 0.5, text="Atomi B (AO)", showarrow=False)
        
        # Molekyyli AB (Keskellä, x=1)
        fig.add_trace(go.Scatter(x=[-0.1, 0.1], y=[E_bind, E_bind], mode='lines', line=dict(color='blue', width=4), name='Sitova MO'))
        fig.add_annotation(x=0.0, y=E_bind - 0.5, text="Sitova MO (σ)", showarrow=False)
        
        fig.add_trace(go.Scatter(x=[-0.1, 0.1], y=[E_anti, E_anti], mode='lines', line=dict(color='red', width=4), name='Hajottava MO'))
        fig.add_annotation(x=0.0, y=E_anti + 0.5, text="Hajottava MO (σ*)", showarrow=False)
        
        # Yhdistävät katkoviivat (Sitova MO)
        fig.add_trace(go.Scatter(x=[-0.9, -0.1], y=[alpha_a, E_bind], mode='lines', line=dict(color='blue', width=w_bind_A, dash='dot'), showlegend=False))
        fig.add_trace(go.Scatter(x=[0.9, 0.1], y=[alpha_b, E_bind], mode='lines', line=dict(color='blue', width=w_bind_B, dash='dot'), showlegend=False))
        
        # Yhdistävät katkoviivat (Hajottava MO)
        fig.add_trace(go.Scatter(x=[-0.9, -0.1], y=[alpha_a, E_anti], mode='lines', line=dict(color='red', width=w_anti_A, dash='dot'), showlegend=False))
        fig.add_trace(go.Scatter(x=[0.9, 0.1], y=[alpha_b, E_anti], mode='lines', line=dict(color='red', width=w_anti_B, dash='dot'), showlegend=False))
        
        # Elektronien piirtäminen (Oletetaan 2 elektronia järjestelmään -> molemmat sitovalla)
        fig.add_annotation(x=-0.02, y=E_bind, text="↑", font=dict(size=20, color="black"), showarrow=False)
        fig.add_annotation(x=0.02, y=E_bind, text="↓", font=dict(size=20, color="black"), showarrow=False)
        
        # Asetellaan y-akseli automaattisesti
        y_min = min(E_bind, alpha_a, alpha_b) - 2.0
        y_max = max(E_anti, alpha_a, alpha_b) + 2.0
        
        fig.update_layout(
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1.5, 1.5]),
            yaxis=dict(title="Energia (eV)", range=[y_min, y_max]),
            height=600,
            showlegend=False,
            plot_bgcolor="white"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        with st.expander("Kysymyksiä ja kokeiltavaa"):
            st.write("""
            * **Homonukleaarinen sidos ($H_2$, $N_2$ jne):** Aseta Atomien A ja B energiat tismalleen samoiksi. Huomaatko, kuinka sitovan orbitaalin yhdistävät viivat ovat yhtä paksut molemmille puolille? Tämä tarkoittaa 100% kovalenttista sidosta, jossa elektronit jaetaan tasan.
            * **Polarisaatio:** Laske Atomin B energiaa (esim. atomin A = H ja B = F). Sitova orbitaali painuu lähemmäs atomin B energiaa, ja B:ltä tuleva viiva paksunee. Sidoksen ioniluonne on nyt kasvanut ja elektronitiheys on siirtynyt lähemmäs B:tä!
            * **Steerinen repulsio ($S > 0$):** Aseta energiat samoiksi ja liikuta peittymisintegraalin $S$ arvoa nollasta ylöspäin. Huomaat, että hajottava tila nousee nopeammin ylös kuin sitova tila laskee alas. Siksi kahden jalokaasuatomin (kuten $He_2$) vuorovaikutus on repulsiivinen!
            """)
import streamlit as st
import numpy as np
import scipy.linalg as la
import math
from numba import njit
from rdkit import Chem
from rdkit.Chem import AllChem
import plotly.graph_objects as go

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

    #### 2. LCAO-approksimaatio (Linear Combination of Atomic Orbitals)
    Molekyylin aaltofunktio muodostuu molekyyliorbitaaleista ($\psi_i$). Koska emme tiedä niiden muotoa, rakennamme ne atomeilla olevista kantafunktioista ($\phi_\mu$):
    $$ \psi_i = \sum_{\mu} C_{\mu i} \phi_\mu $$
    Tavoitteemme on löytää nämä laajennuskertoimet $C_{\mu i}$. Sovelluksemme käyttää STO-3G -kantajoukkoa, jossa jokainen STO-orbitaali on sovitettu kolmen Gaussin funktion summaksi.

    #### 3. Hartree-Fock -yhtälö ja Fock-matriisi
    Haluamme ratkaista ominaisarvoyhtälön $HC = EC$. Koska elektronit hylkivät toisiaan, yhden elektronin ratkaisu riippuu kaikkien muiden elektronien sijainnista. Tämä pakottaa meidät käyttämään iteraatiota ja rakentamaan **Fock-matriisin ($F$)**:
    
    $$ F_{\mu\nu} = H_{\mu\nu}^{core} + \sum_{\lambda\sigma} P_{\lambda\sigma} \left[ (\mu\nu|\lambda\sigma) - \frac{1}{2}(\mu\lambda|\nu\sigma) \right] $$
    
    * $H_{\mu\nu}^{core}$: **Ydinhamiltonian.** Kuvaa elektronin kineettisen energian ja ytimien vetovoiman (sovelluksen `compute_core_hamiltonian_jit`).
    * $P_{\lambda\sigma}$: **Tiheysmatriisi.** Kuvaa elektronien todennäköisyysjakaumaa.
    * $(\mu\nu|\lambda\sigma)$: **Coulomb-integraali ($J$).** Kuvaa klassista sähköstaattista repulsiota kahden elektronipilven välillä.
    * $-\frac{1}{2}(\mu\lambda|\nu\sigma)$: **Vaihtointegraali ($K$).** Kvanttimekaaninen termi, joka syntyy Paulin kieltosäännöstä. Se stabiloi järjestelmää vähentämällä samanspinnaisten elektronien välistä repulsiota.
    
    *(Huom: Näitä $J$ ja $K$ termejä lasketaan sovelluksen raskaassa `compute_eri_jit` -funktiossa (Electron Repulsion Integrals). Kymmenen atomin molekyylissä näitä integraaleja voi olla kymmeniä tuhansia!)*

    #### 4. Roothaan-Hall -yhtälö ja SCF-silmukka (Self-Consistent Field)
    Lopullinen yhtälö, joka koodissa ratkaistaan, on:
    $$ FC = SCE $$
    missä $S$ on peittymismatriisi, $C$ on kerroinmatriisi ja $E$ sisältää orbitaalienergiat.
    
    Koska Fock-matriisi ($F$) vaatii tiheysmatriisia ($P$), ja tiheysmatriisi saadaan kertoimista ($C$), ollaan noidankehässä. Tämä ratkaistaan **SCF-iteraatiolla**:
    1. Arvataan elektronitiheys ($P = 0$).
    2. Rakennetaan Fock-matriisi ($F$).
    3. Ratkaistaan kertoimet ominaisarvoyhtälöstä ($FC = SCE$).
    4. Lasketaan kertoimista uusi elektronitiheys ($P$).
    5. Verrataan uutta tiheyttä ja energiaa vanhaan. Jos ne muuttuivat, palataan kohtaan 2. Kun ne eivät enää muutu, järjestelmä on "itseytyvä" (converged).

    #### Hartree-Fockin suurin heikkous: Elektronikorrelaatio
    Hartree-Fock olettaa, että elektronit tuntevat toisensa vain staattisena, keskimääräisenä pilvenä (Mean-field approximation). Oikeasti elektronit välttelevät toisiaan dynaamisesti ja hetkellisesti. Tätä HF ei huomioi, mikä on ns. **elektronikorrelaation** puute. Tämän vuoksi HF yliarvioi sidospituuksia ja virheellisesti arvioi energioita, mutta on silti perusta lähes kaikille tarkemmille kvanttikemian menetelmille.
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
    # 2. RDKIT MUUNNIN
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
        for i, atom in enumerate(mol.GetAtoms()):
            atoms.append(atom.GetAtomicNum())
            pos = conf.GetAtomPosition(i)
            coords.append([pos.x / A0, pos.y / A0, pos.z / A0])
        return np.array(atoms, dtype=np.int32), np.array(coords, dtype=np.float64), None

    # ==========================================
    # 3. NUMBA-OPTIMOIDUT INTEGRAALIT JA 3D HILA
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

    # ==========================================
    # 4. SCF SILMUKKA JA VISUALISOINTI
    # ==========================================
    def scf_loop(S, H_core, g, N_elec, max_iter=50, conv=1e-6, mix=0.5):
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
                    
            energies.append(Eg)
            if count > 0 and abs(energies[-1] - energies[-2]) < conv: break
                
        return energies, enew, C, P

    def plot_3d_orbital(coords, atoms, cgf_ptr, exps, coeffs, norms, lmns, centers, mo_coeffs, isovalue=0.03):
        margin = 4.0
        x_min, x_max = np.min(coords[:,0]) - margin, np.max(coords[:,0]) + margin
        y_min, y_max = np.min(coords[:,1]) - margin, np.max(coords[:,1]) + margin
        z_min, z_max = np.min(coords[:,2]) - margin, np.max(coords[:,2]) + margin
        
        grid_size = 35
        xi, yi, zi = np.linspace(x_min, x_max, grid_size), np.linspace(y_min, y_max, grid_size), np.linspace(z_min, z_max, grid_size)
        X, Y, Z = np.meshgrid(xi, yi, zi, indexing='ij')
        
        X_flat, Y_flat, Z_flat = X.flatten(), Y.flatten(), Z.flatten()
        psi_flat = evaluate_mo_on_grid(X_flat, Y_flat, Z_flat, cgf_ptr, exps, coeffs, norms, lmns, centers, mo_coeffs)
        
        fig = go.Figure()
        fig.add_trace(go.Isosurface(
            x=X_flat, y=Y_flat, z=Z_flat, value=psi_flat,
            isomin=isovalue, isomax=np.max(psi_flat),
            surface_fill=0.6, caps=dict(x_show=False, y_show=False, z_show=False),
            colorscale=[[0, 'blue'], [1, 'blue']], showscale=False, name="Positiivinen vaihe"
        ))
        fig.add_trace(go.Isosurface(
            x=X_flat, y=Y_flat, z=Z_flat, value=psi_flat,
            isomin=np.min(psi_flat), isomax=-isovalue,
            surface_fill=0.6, caps=dict(x_show=False, y_show=False, z_show=False),
            colorscale=[[0, 'red'], [1, 'red']], showscale=False, name="Negatiivinen vaihe"
        ))
        
        atom_colors = {1: 'lightgray', 6: 'black', 7: 'blue', 8: 'red'}
        for i, Z_at in enumerate(atoms):
            fig.add_trace(go.Scatter3d(
                x=[coords[i,0]], y=[coords[i,1]], z=[coords[i,2]],
                mode='markers', marker=dict(size=10, color=atom_colors.get(Z_at, 'green')),
                name=f"Atomi {Z_at}"
            ))
            
        fig.update_layout(scene=dict(xaxis_title='X (Bohr)', yaxis_title='Y (Bohr)', zaxis_title='Z (Bohr)', aspectmode='data'), height=600, showlegend=False)
        return fig

    # ==========================================
    # 5. KÄYTTÖLIITTYMÄ
    # ==========================================
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Järjestelmän asetukset")
        smiles = st.text_input("Syötä molekyylin SMILES", value="O", help="Kokeile: O (vesi), C (metaani), N (ammoniakki)")
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
                            
                        with st.spinner("Lasketaan raskaat 2-e integraalit (JIT)..."):
                            g = compute_eri_jit(cgf_ptr, exps, coeffs, norms, centers)
                            
                        with st.spinner("Iteroidaan SCF-silmukkaa..."):
                            energies, evals, C, P = scf_loop(S, H_core, g, N_elec, max_iter, 1e-6, mixing)
                            
                        st.success(f"SCF suppeni {len(energies)} iteraatiossa.")
                        
                        st.session_state['hf_results'] = {
                            'energies': energies, 'evals': evals, 'C': C, 'N_elec': N_elec,
                            'cgf_ptr': cgf_ptr, 'exps': exps, 'coeffs': coeffs, 'norms': norms,
                            'lmns': lmns, 'centers': centers, 'coords': coords, 'atoms': atoms
                        }
                        
                    except Exception as e:
                        st.error(f"Laskennassa tapahtui virhe: {str(e)}")

    # Jos data on olemassa, näytetään tulokset ja 3D-malli napin painamisen jälkeenkin
    if 'hf_results' in st.session_state:
        res = st.session_state['hf_results']
        
        st.markdown("---")
        st.subheader("3D-visualisointi")
        st.write("Tässä näet, mitä ominaisarvoyhtälön kertoimet tarkoittavat: ne muovaavat kantafunktioista molekyyliorbitaaleja.")
        
        homo_idx = int(res['N_elec'] / 2) - 1
        orb_options = {f"HOMO (Orbitaali {homo_idx}, E={res['evals'][homo_idx]:.3f} au)": homo_idx,
                       f"LUMO (Orbitaali {homo_idx+1}, E={res['evals'][homo_idx+1]:.3f} au)": homo_idx+1}
        
        for i in range(max(0, homo_idx-2), min(len(res['evals']), homo_idx+3)):
            if i not in [homo_idx, homo_idx+1]:
                orb_options[f"Orbitaali {i} (E={res['evals'][i]:.3f} au)"] = i
                
        col_plot1, col_plot2 = st.columns([1, 2])
        with col_plot1:
            selected_orb_label = st.selectbox("Valitse piirrettävä orbitaali", list(orb_options.keys()))
            selected_orb_idx = orb_options[selected_orb_label]
            isovalue = st.slider("Isopinnan arvo (Isovalue)", 0.01, 0.10, 0.03, 0.01)
            
            fig_energies = go.Figure()
            fig_energies.add_trace(go.Scatter(x=list(range(1, len(res['energies'])+1)), y=res['energies'], mode='lines+markers'))
            fig_energies.update_layout(title="SCF suppeneminen", xaxis_title="Iteraatio", yaxis_title="Energia (au)", height=300)
            st.plotly_chart(fig_energies, use_container_width=True)

        with col_plot2:
            with st.spinner("Rakennetaan 3D-pintaa (tämä voi kestää muutaman sekunnin)..."):
                mo_coeffs = res['C'][:, selected_orb_idx]
                fig_3d = plot_3d_orbital(res['coords'], res['atoms'], res['cgf_ptr'], res['exps'], res['coeffs'], res['norms'], res['lmns'], res['centers'], mo_coeffs, isovalue)
                st.plotly_chart(fig_3d, use_container_width=True)

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


import streamlit as st
import numpy as np
import plotly.graph_objects as go
from math import factorial

# ==========================================
# 1. UI ASETUKSET
# ==========================================
st.set_page_config(
    page_title="Radiaaliset jakautumafunktiot", 
    layout="wide"
)

st.title("Moduuli 4: Radiaaliset jakautumafunktiot")
st.caption("Atomiorbitaalien säteittäiset osat ja elektronien todennäköisyysjakaumat (Clementi-Raimondi STO)")
st.divider()

# ==========================================
# 2. CLEMENTI-RAIMONDI Z_eff SANAKIRJA (Z=1 - 18)
# Voit lisätä tähän loputkin notebookisi alkuaineista!
# Rakenne: Z: {'orbitaali': Z_eff}
# ==========================================
clementi_zeff = {
    1: {'1s': 1.0000},
    2: {'1s': 1.6875},
    3: {'1s': 2.6906, '2s': 1.2792},
    4: {'1s': 3.6848, '2s': 1.9120},
    5: {'1s': 4.6795, '2s': 2.5885, '2p': 2.4214},
    6: {'1s': 5.6727, '2s': 3.2236, '2p': 3.1358},
    7: {'1s': 6.6651, '2s': 3.8340, '2p': 3.8312},
    8: {'1s': 7.6579, '2s': 4.4532, '2p': 4.4532},
    9: {'1s': 8.6501, '2s': 5.1000, '2p': 5.1000},
    10: {'1s': 9.6421, '2s': 5.7584, '2p': 5.7584},
    11: {'1s': 10.6259, '2s': 6.5714, '2p': 6.8018, '3s': 2.5057},
    12: {'1s': 11.6089, '2s': 7.3920, '2p': 7.4263, '3s': 3.3075},
    13: {'1s': 12.5910, '2s': 8.2136, '2p': 8.4028, '3s': 4.1112, '3p': 3.5011},
    14: {'1s': 13.5745, '2s': 9.0338, '2p': 9.3345, '3s': 4.9032, '3p': 4.2852},
    15: {'1s': 14.5553, '2s': 9.8544, '2p': 10.2631, '3s': 5.6418, '3p': 4.8856},
    16: {'1s': 15.5381, '2s': 10.6830, '2p': 11.1810, '3s': 6.3682, '3p': 5.4868},
    17: {'1s': 16.5239, '2s': 11.5300, '2p': 12.0940, '3s': 7.0683, '3p': 6.1169},
    18: {'1s': 17.5075, '2s': 12.3221, '2p': 13.0062, '3s': 7.7588, '3p': 6.7641}
}

atno_to_element = {
    1: 'H', 2: 'He', 3: 'Li', 4: 'Be', 5: 'B', 6: 'C', 7: 'N', 8: 'O', 9: 'F', 10: 'Ne',
    11: 'Na', 12: 'Mg', 13: 'Al', 14: 'Si', 15: 'P', 16: 'S', 17: 'Cl', 18: 'Ar'
}

# ==========================================
# 3. FYSIKAALISET FUNKTIOT
# ==========================================
@st.cache_data
def calculate_sto_radial(n, zeff, r):
    """
    Laskee Slater-tyyppisen orbitaalin (STO) säteittäisen osan R(r).
    r on NumPy-taulukko etäisyyksistä (Bohr).
    """
    # STO Normeerausvakio: N = (2*zeta)**(n+0.5) / sqrt((2n)!)
    # Huom: Zeta (ζ) Slaterin säännöissä on Z_eff / n
    zeta = zeff / n 
    
    norm = (2 * zeta)**(n + 0.5) / np.sqrt(factorial(2 * n))
    R_r = norm * (r**(n - 1)) * np.exp(-zeta * r)
    return R_r

def get_n_from_label(label):
    """Erottaa pääkvanttiluvun orbitaalin nimestä (esim. '2p' -> 2)"""
    return int(label[0])

# ==========================================
# 4. SIVUPALKKI JA PARAMETRIT
# ==========================================
st.sidebar.header("Parametrit")

# Alkuaineen valinta
element_options = {f"{Z} - {sym}": Z for Z, sym in atno_to_element.items()}
selected_element_str = st.sidebar.selectbox("Valitse alkuaine", list(element_options.keys()), index=5)
Z = element_options[selected_element_str]

st.sidebar.divider()

# Kuvaajan asetukset
r_max = st.sidebar.slider("Maksimietäisyys r (Bohr)", 2.0, 20.0, 8.0, 0.5)
scale_peaks = st.sidebar.checkbox("Skaalaa huiput samaan korkeuteen", value=False, 
                                  help="Helpottaa uloimpien orbitaalien muodon vertailua 1s-orbitaaliin.")

# ==========================================
# 5. LASKENTA JA VISUALISOINTI
# ==========================================
r = np.linspace(0.001, r_max, 1000)
element_data = clementi_zeff[Z]


tab1, tab2, tab_taustaa = st.tabs(["Säteittäinen aaltofunktio R(r)", "Radiaalinen jakautumafunktio P(r)", "Taustaa & Teoriaa"])

with tab_taustaa:
    st.markdown(r"""
    ### Mitä tässä ihmetellään?

    Kvanttimekaniikassa atomin elektronin tilaa kuvataan aaltofunktiolla $\psi$. Pallosymmetrisissä systeemeissä (kuten atomit) tämä funktio voidaan jakaa kahteen osaan: kulmaosaan (joka antaa orbitaalille sen tutun 3D-muodon, esim. p-orbitaalin kahdeksikkomaisen muodon) ja **säteittäiseen osaan $R(r)$**, joka riippuu vain etäisyydestä ytimestä.

    Tässä moduulissa tarkastelemme juuri tätä säteittäistä osaa. 

    #### $R(r)$ vs. $P(r)$ - Mitä eroa niillä on?
    1. **Säteittäinen aaltofunktio $R(r)$:** Kertoo puhtaan aaltofunktion amplitudin etäisyyden $r$ funktiona. Ydintä lähestyttäessä ($r \rightarrow 0$) s-orbitaalien $R(r)$ kasvaa kohti maksimia, koska aaltofunktio itsessään on tiheimmillään ytimessä.
    2. **Radiaalinen jakautumafunktio $P(r)$:** Elektronin todennäköisyys ei riipu vain aaltofunktion neliöstä $R(r)^2$, vaan myös sen alueen koosta, josta elektronia etsitään. Kolmiulotteisessa avaruudessa tietyn säteen $r$ etäisyydellä oleva alue on pallokuori, jonka tilavuus kasvaa kaavalla $4\pi r^2$. Siksi todennäköisyys löytää elektroni tietyltä etäisyydeltä on $P(r) = 4\pi r^2 R(r)^2$. 

    Vaikka aaltofunktio $R(r)$ on maksimissaan ytimessä, todennäköisyys $P(r)$ on siellä nolla, koska pisteen (ytimen) tilavuus on nolla! $P(r)$ vastaa kysymykseen: *"Jos piirrän pallonkuoren etäisyydelle r, kuinka todennäköisesti elektroni on sen kuoren sisällä?"*

    #### Mitä Clementi-Raimondi -arvot ($Z_{eff}$) ovat?
    Vetyatomilla on vain yksi elektroni, joka tuntee koko ytimen +1 varauksen. Mutta monielektronisissa atomeissa (esim. Hiili, $Z=6$) uloimmat elektronit eivät tunne koko ytimen vetovoimaa. Sisemmät elektronit ovat ytimen ja ulkoelektronin välissä ja "varjostavat" (shield) osan ytimen positiivisesta varauksesta. 

    Elektroni tuntee siis vain **efektiivisen ydinvarauksen ($Z_{eff}$)**, joka on aina pienempi kuin todellinen varaus $Z$. Vuonna 1963 Enrico Clementi ja D. L. Raimondi laskivat SCF-menetelmällä optimaaliset $Z_{eff}$-arvot atomeille, jotta ne vastaisivat mahdollisimman hyvin todellisia aaltofunktioita käyttäen yksinkertaistettuja Slater-tyyppisiä orbitaaleja (STO). Näitä samoja arvoja ohjelmamme nyt käyttää orbitaalien leveyden ja huipun sijainnin laskemiseen.
    """)



# Värikartta orbitaaleille
colors = {'1s': '#1f77b4', '2s': '#ff7f0e', '2p': '#2ca02c', 
          '3s': '#d62728', '3p': '#9467bd', '3d': '#8c564b'}




with tab1:
    st.subheader(f"Säteittäinen aaltofunktio $R(r)$ atomille {atno_to_element[Z]}")
    st.markdown("Aaltofunktion arvo etäisyyden $r$ funktiona. Kertoo orbitaalin amplitudin ja solmukohtien (nodes) paikat.")
    
    fig1 = go.Figure()
    
    max_1s = None
    
    for orb, zeff in element_data.items():
        n = get_n_from_label(orb)
        R_r = calculate_sto_radial(n, zeff, r)
        
        # Oletetaan puhtaita STO-funktioita, joten pakotetaan solmut 
        # ortogonalisoimalla karkeasti visualisointia varten (Schmidt-tyyppinen) 
        # STO-funktioilla itsessään ei ole radiaalisia solmuja ilman lineaarikombinaatioita!
        # Pedagoginen korjaus: R_nl = P_n(r) * exp(-zeta r). STO on vain yksi termi.
        # Näytetään tässä perus STO-muoto kuten alkuperäisessäkin koodissa.
        
        plot_y = R_r
        
        if scale_peaks:
            if orb == '1s':
                max_1s = np.max(R_r)
            elif max_1s is not None:
                # Skaalataan muiden huiput 1s:n tasolle
                scale_factor = max_1s / np.max(R_r)
                plot_y = R_r * scale_factor
                
        line_style = 'dash' if 'p' in orb else 'solid'
        color = colors.get(orb, '#7f7f7f')
        
        name_label = f"{orb} (skaalattu)" if scale_peaks and orb != '1s' else orb
        fig1.add_trace(go.Scatter(x=r, y=plot_y, mode='lines', name=name_label, 
                                  line=dict(width=3, dash=line_style, color=color)))

    fig1.add_trace(go.Scatter(x=[0, r_max], y=[0, 0], mode='lines', line=dict(color='black', width=1), showlegend=False))
    
    fig1.update_layout(
        xaxis_title="Etäisyys r (Bohr)",
        yaxis_title="Amplitudi R(r)",
        height=550,
        hovermode="x unified"
    )
    st.plotly_chart(fig1, use_container_width=True)

with tab2:
    st.subheader(f"Radiaalinen jakautumafunktio $4\pi r^2 R(r)^2$ atomille {atno_to_element[Z]}")
    st.markdown("Kertoo todennäköisyyden löytää elektroni tietyltä etäisyydeltä ytimestä (pallokuoren tilavuus huomioiden).")
    
    fig2 = go.Figure()
    
    max_1s_rdf = None
    
    for orb, zeff in element_data.items():
        n = get_n_from_label(orb)
        R_r = calculate_sto_radial(n, zeff, r)
        
        # Radiaalinen todennäköisyystiheys P(r) = r^2 * R(r)^2
        # (4 pi integroituu pois pallokoordinaatistossa, kun normalisointi on tehty)
        RDF = (r**2) * (R_r**2)
        plot_y_rdf = RDF
        
        if scale_peaks:
            if orb == '1s':
                max_1s_rdf = np.max(RDF)
            elif max_1s_rdf is not None:
                scale_factor_rdf = max_1s_rdf / np.max(RDF)
                plot_y_rdf = RDF * scale_factor_rdf
                
        line_style = 'dash' if 'p' in orb else 'solid'
        color = colors.get(orb, '#7f7f7f')
        
        name_label = f"{orb} (skaalattu)" if scale_peaks and orb != '1s' else orb
        fig2.add_trace(go.Scatter(x=r, y=plot_y_rdf, mode='lines', name=name_label, 
                                  line=dict(width=3, dash=line_style, color=color), fill='tozeroy', opacity=0.5))

    fig2.update_layout(
        xaxis_title="Etäisyys r (Bohr)",
        yaxis_title="Todennäköisyystiheys P(r)",
        height=550,
        hovermode="x unified"
    )
    st.plotly_chart(fig2, use_container_width=True)

# ==========================================
# 6. PEDAGOGINEN OSIO
# ==========================================
st.markdown("---")
with st.expander("Kysymyksiä ja huomioita"):
    st.markdown(r"""
    **1. Volyymiefekti ja ydin:** Valitse alkuaineeksi Vety (H) ja vertaa $R(r)$ ja $P(r)$ kuvaajia. Miksi $R(r)$ on maksimissaan täsmälleen ytimessä ($r=0$), mutta $P(r)$ lähtee nollasta? Mitä tämä kertoo elektronin mahdollisuudesta "törmätä" ytimeen?

    **2. Efektiivinen ydinvaraus ja atomin koko:** Aseta r-akselin maksimiksi 6 Bohr. Vaihda alkuaineeksi ensin Litium (Z=3) ja kelaa sitten valikkoa alaspäin kohti Neonia (Z=10). Seuraa 2s- ja 2p-orbitaalien $P(r)$ huippujen sijaintia. 
    Mitä huomaat? Vaikka pääkvanttiluku pysyy samana ($n=2$), miksi orbitaalit kutistuvat lähemmäs ydintä, kun liikutaan jaksoa oikealle? *(Vinkki: Katso sivupalkin yläpuolelta Z-arvon kasvua ja mieti ytimen vetovoimaa).*

    **3. Varjostus (Shielding):** Valitse natrium. Katso 1s, 2s ja 3s -orbitaalien todennäköisyysjakaumia. Koska 1s ja 2s ovat fyysisesti paljon lähempänä ydintä, ne varjostavat ytimen varausta. Natriumin $Z=11$, mutta Clementi-Raimondi -taulukon mukaan 3s-elektroni tuntee vain efektiivisen varauksen $Z_{eff} \approx 2.5$. Miten tämä varjostus selittää alkalimetallien (kuten Na) suuren reaktiivisuuden ja taipumuksen luovuttaa uloin elektroninsa?

    **4. STO-funktion rajat (Puuttuvat solmukohdat):**
    Tämä työkalu käyttää puhtaita Slater-orbitaaleja (STO). Kvanttimekaniikan teorian mukaan aaltofunktiolla on $n - l - 1$ säteittäistä solmukohtaa (kohtaa, jossa $R(r) = 0$). Siten esimerkiksi 2s-orbitaalilla pitäisi olla yksi solmukohta ja 3s-orbitaalilla kaksi. 
    Näetkö näitä solmukohtia $R(r)$ -kuvaajassa? Et näe. Yksittäisillä STO-funktioilla ei ole sisäänrakennettuja säteittäisiä solmuja. Tästä syystä raskaammissa laskuissa (esim. Hartree-Fock -moduulimme) orbitaalit rakennetaan *lineaarikombinaatioina* useista funktioista, jotta solmukohdat saadaan muodostettua oikein!
    """)
import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from numba import njit

# ==========================================
# 1. UI ASETUKSET
# ==========================================
st.set_page_config(
    page_title="Tunneloituminen", 
    layout="wide"
)

st.title("Moduuli 5: Kvanttimekaaninen tunneloituminen")
st.caption("Siirtomatriisimenetelmä (TMM) yksiulotteisille potentiaalivalleille")
st.divider()

# ==========================================
# 2. NUMBA-OPTIMOITU TMM-LASKENTA
# ==========================================
@njit
def calc_transmission_jit(E_arr, V, dx, mass):
    """
    Laskee läpäisytodennäköisyyden T(E) siirtomatriisimenetelmällä.
    Numba-kiihdytys mahdollistaa massiivisen k-avaruuden iteroinnin viiveettä.
    """
    n_E = len(E_arr)
    n_x = len(V)
    T_prob = np.zeros(n_E, dtype=np.float64)
    
    for idx in range(n_E):
        E = E_arr[idx]
        
        # M-matriisi (identiteettimatriisi alussa)
        M11 = 1.0 + 0.0j
        M12 = 0.0 + 0.0j
        M21 = 0.0 + 0.0j
        M22 = 1.0 + 0.0j
        
        k_prev = np.sqrt(2.0 * mass * (E - V[0] + 0.0j))
        if k_prev.real == 0 and k_prev.imag == 0:
            k_prev = 1e-10 + 0.0j
            
        for j in range(1, n_x):
            k_curr = np.sqrt(2.0 * mass * (E - V[j] + 0.0j))
            if k_curr.real == 0 and k_curr.imag == 0:
                k_curr = 1e-10 + 0.0j
            
            # Etenemismatriisi (Phase matrix)
            phase = np.exp(1j * k_prev * dx)
            inv_phase = 1.0 / phase
            
            # Rajapinnan sovitusmatriisi (Boundary matching matrix D)
            r = k_curr / k_prev
            D11 = 0.5 * (1.0 + r)
            D12 = 0.5 * (1.0 - r)
            D21 = 0.5 * (1.0 - r)
            D22 = 0.5 * (1.0 + r)
            
            # Matriisien kertolasku: M_new = M * P * D
            MP11 = M11 * phase
            MP12 = M12 * inv_phase
            MP21 = M21 * phase
            MP22 = M22 * inv_phase
            
            M11_new = MP11 * D11 + MP12 * D21
            M12_new = MP11 * D12 + MP12 * D22
            M21_new = MP21 * D11 + MP22 * D21
            M22_new = MP21 * D12 + MP22 * D22
            
            M11 = M11_new
            M12 = M12_new
            M21 = M21_new
            M22 = M22_new
            k_prev = k_curr
            
        # Läpäisykertoimen laskenta T = |k_out / k_in| * |1 / M11|^2
        k_in = np.sqrt(2.0 * mass * (E - V[0] + 0.0j))
        k_out = np.sqrt(2.0 * mass * (E - V[-1] + 0.0j))
        
        if k_in.real > 0:
            abs_M11 = np.abs(M11)
            # Suojataan ylivuodoilta (hyvin paksut/korkeat esteet)
            if abs_M11 > 1e100:
                T_prob[idx] = 0.0
            else:
                T_val = (k_out.real / k_in.real) * (1.0 / (abs_M11**2))
                if T_val > 1.0: 
                    T_val = 1.0
                T_prob[idx] = T_val
        else:
            T_prob[idx] = 0.0
            
    return T_prob

def generate_potential(x, shape, num_barriers, V0, width, separation):
    """Luo potentiaalivallin muodon."""
    V = np.zeros_like(x)
    positions = []
    
    if num_barriers == 1:
        positions = [0.0]
    elif num_barriers == 2:
        positions = [-separation/2, separation/2]
    elif num_barriers == 3:
        positions = [-separation, 0.0, separation]
        
    for pos in positions:
        if shape == "Suorakulmainen":
            V += np.where(np.abs(x - pos) <= width/2, V0, 0.0)
        elif shape == "Gaussin käyrä":
            V += V0 * np.exp(-((x - pos) / (width/2))**2)
        elif shape == "Lorentzian":
            V += V0 / (1.0 + ((x - pos) / (width/2))**2)
            
    return V

# ==========================================
# 3. SIVUPALKKI JA PARAMETRIT
# ==========================================
st.sidebar.header("Järjestelmän asetukset")

mass = st.sidebar.number_input("Hiukkasen massa (au)", value=1.0, step=0.1, min_value=0.1)

st.sidebar.header("Potentiaalivalli")
shape = st.sidebar.selectbox("Esteen muoto", ["Suorakulmainen", "Gaussin käyrä", "Lorentzian"])
num_barriers = st.sidebar.slider("Esteiden lukumäärä", 1, 3, 1)

V0 = st.sidebar.slider("Esteen korkeus V0 (au)", 1.0, 15.0, 5.0, 0.5)
width = st.sidebar.slider("Esteen leveys (au)", 0.2, 5.0, 1.0, 0.1)

separation = 0.0
if num_barriers > 1:
    separation = st.sidebar.slider("Esteiden välimatka (au)", width, 10.0, 3.0, 0.1)

st.sidebar.header("Laskenta")
E_max = st.sidebar.slider("Maksimienergia E (au)", V0*0.5, V0*3.0, V0*1.5, 0.5)

# ==========================================
# 4. LASKENTA JA VISUALISOINTI
# ==========================================
# X-hila (riittävän laaja ja tiheä TMM-stabiiliudelle)
x_max = max(10.0, (num_barriers * separation) + 5.0)
x = np.linspace(-x_max, x_max, 2500)
dx = x[1] - x[0]

V = generate_potential(x, shape, num_barriers, V0, width, separation)

# E-hila (lasketaan läpäisy eri energioille)
E_arr = np.linspace(0.01, E_max, 800)

with st.spinner("Ratkaistaan siirtomatriiseja Numballa..."):
    T_prob = calc_transmission_jit(E_arr, V, dx, mass)

# Piirretään kuvaajat
fig = make_subplots(rows=2, cols=1, shared_xaxes=False, vertical_spacing=0.15,
                    subplot_titles=(f"Läpäisytodennäköisyys T(E) | Esteen korkeus V0 = {V0} au", 
                                    "Potentiaalienergian muoto V(x)"))

# T(E) kuvaaja
fig.add_trace(go.Scatter(x=E_arr, y=T_prob, mode='lines', line=dict(color='blue', width=3), name="T(E)"), row=1, col=1)
fig.add_trace(go.Scatter(x=[V0, V0], y=[0, 1], mode='lines', line=dict(color='red', dash='dash'), name="Klassinen raja V0"), row=1, col=1)

# V(x) kuvaaja
fig.add_trace(go.Scatter(x=x, y=V, mode='lines', fill='tozeroy', line=dict(color='gray', width=2), name="V(x)"), row=2, col=1)

fig.update_layout(height=700, showlegend=True, hovermode="x unified")
fig.update_yaxes(title_text="Läpäisytodennäköisyys T", range=[-0.05, 1.05], row=1, col=1)
fig.update_xaxes(title_text="Hiukkasen energia E (au)", row=1, col=1)
fig.update_yaxes(title_text="Energia (au)", row=2, col=1)
fig.update_xaxes(title_text="Paikka x (au)", row=2, col=1)

st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 5. PEDAGOGINEN OSIO
# ==========================================
with st.expander("Pedagogisia kysymyksiä ja huomioita"):
    st.write("""
    1. **Klassinen vs. Kvanttimekaaninen:** Klassisen fysiikan mukaan hiukkanen ei voi koskaan läpäistä estettä, jos sen energia on pienempi kuin esteen korkeus ($E < V_0$). Katso ylempää kuvaajaa alueella vasemmalla punaisesta katkoviivasta. Mitä havaitset?
    2. **Massan vaikutus:** Kokeile kasvattaa hiukkasen massaa (esim. arvosta 1.0 arvoon 5.0). Miten se vaikuttaa tunneloitumisen todennäköisyyteen matalilla energioilla?
    3. **Resonanssitunneloituminen:** Aseta esteiden määräksi 2. Huomaatko T(E)-käyrässä teräviä piikkejä, joissa läpäisytodennäköisyys pomppaa sataan prosenttiin ($T=1$), vaikka energia on reilusti alle esteen korkeuden? Tämä johtuu aaltofunktion konstruktiivisesta interferenssistä kahden esteen välisessä \"kaivossa\" (vertaa Fabry-Pérot -interferometriin optiikassa).
    4. **Heijastus vallin yläpuolella:** Tarkastele aluetta $E > V_0$. Miksi $T(E)$ ei ole puhtaasti 1.0, vaan oskilloiva? (Klassinen hiukkanen lentäisi esteen yli sataprosenttisesti, mutta aaltofunktio kokee heijastumista potentiaalin muutoskohdissa).
    """)
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
    page_title="Extraa: Edistyneet aiheet", 
    layout="wide"
)

st.title("Extraa: Edistyneet aiheet")
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
    
    with st.expander("Lue ensin: Mitä Walsh-diagrammit kertovat?", expanded=True):
        st.markdown("""
        ### Mistä Walsh-diagrammeissa on kyse?
        Miksi vesi (H2O) on muodoltaan vääntynyt kulmaan, mutta hiilidioksidi (CO2) on täysin lineaarinen suora? Vuonna 1953 A.D. Walsh kehitti graafisen menetelmän, jolla näihin kysymyksiin voidaan vastata ilman raskaita tietokonelaskuja, pelkkää molekyyliorbitaaliteoriaa käyttäen.

        Walsh-diagrammi kuvaa **molekyyliorbitaalien energioiden muutosta, kun molekyylin geometriaa (useimmiten sidoskulmaa) muutetaan**.
        
        * **X-akseli:** Molekyylin sidoskulma (esim. 90 asteesta 180 asteeseen).
        * **Y-akseli:** Yksittäisten molekyyliorbitaalien (MO) energiat.

        ### Miten luet diagrammia?
        Kun molekyyliä väännetään, atomien orbitaalien välinen päällekkäisyys muuttuu. 
        1. **Energian nousu:** Jos taivuttaminen rikkoo suotuisan sidoksen tai lisää atomien välistä hylkimistä, orbitaalin energia nousee (käyrä menee ylöspäin).
        2. **Energian lasku:** Jos taivuttaminen mahdollistaa uuden, suotuisan vuorovaikutuksen (esimerkiksi keskusatomin p-orbitaali pääsee sekoittumaan vetyjen s-orbitaalien kanssa), orbitaalin energia laskee.

        ### Kultainen sääntö geometrialle
        Molekyyli pyrkii aina tilaan, jossa sen kokonaisenergia on matalin. Nyrkkisääntönä tämä tarkoittaa, että **molekyylin muoto määräytyy sen ylimmän miehitetyn orbitaalin (HOMO) mukaan**. 

        **Käytännön testi:**
        Laske tutkittavan molekyylin valenssielektronit. Aloita diagrammin alimmasta käyrästä ja sijoita kaksi elektronia jokaiselle orbitaalille ylöspäin edeten. Katso, mihin ylin elektronipari (HOMO) asettuu. Jos tuon käyrän energia laskee jyrkästi sidoskulman pienentyessä, molekyyli taipuu. Jos käyrän energia on matalin 180 asteen kohdalla, molekyyli pysyy lineaarisena.
        """)
    
    st.markdown("---")
    
    col_w_input, col_w_plot = st.columns([1, 2])

    with col_w_input:
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
                
            fig_w.add_vline(x=original_angle, line_width=2, line_dash="dot", line_color="red", annotation_text=" RDKit Optimigeometria")
            fig_w.update_layout(title=f"Walsh-diagrammi: Kulman {selected_angle_str} muutos", xaxis_title="Sidoskulma (°)", yaxis_title="MO Energia (eV)", height=600, showlegend=False, hovermode="x unified")
            st.plotly_chart(fig_w, use_container_width=True)


with tab_solid:
    st.header("Molekyyleistä materiaaleihin: Kiinteän olomuodon kemia")
    
    with st.expander("Lue ensin: Orbitaaleista energiavöihin", expanded=True):
        st.markdown("""
        ### Mistä kiinteän olomuodon kemiassa on kyse?
        Aiemmissa moduuleissa olemme tarkastelleet yksittäisiä molekyylejä, joilla on diskreetit (erilliset) energiatasot. Mutta mitä tapahtuu, kun ketjutamme loputtoman määrän atomeja vierekkäin kidehilaksi, kuten metallilangassa tai piikiteessä?

        Kun tuomme kaksi atomia yhteen, niiden atomiorbitaalit jakautuvat kahdeksi molekyyliorbitaaliksi (sitova ja hajottava). Kun tuomme N atomia yhteen, syntyy N molekyyliorbitaalia. Kun N kasvaa makroskooppisiin mittoihin (kuten 10^23), energiatasot pakkautuvat niin tiheästi yhteen, ettei niitä voi enää erottaa toisistaan. Erillisistä viivoista tulee jatkuvia **energiavöitä** (energy bands).

        Tämä ns. vyöteoria (Band Theory) on koko modernin elektroniikan, puolijohteiden ja materiaalikemian perusta.

        ### Keskeiset käsitteet diagrammeissa
        
        **1. Tilatiheys eli DOS (Density of States)**
        Koska emme voi piirtää miljardeja erillisiä viivoja kuvaajaan, käytämme tilatiheyttä. DOS kertoo yksinkertaisesti, kuinka monta sallittua kvanttitilaa tietyllä energiatasolla on tarjolla elektroneille.
        * Leveä huippu DOS-kuvaajassa tarkoittaa, että kyseisellä energialla on paljon "istumapaikkoja" elektroneille.
        * Nolla-arvo DOS-kuvaajassa tarkoittaa **vyöaukkoa** (band gap). Se on energia-alue, jolla ei ole yhtään kvanttimekaanisesti sallittua tilaa. Elektroni ei voi koskaan omata energiaa, joka osuu vyöaukon sisälle.

        **2. Fermi-taso (Fermi Level)**
        Kuvittele energiavyöt vesilasina ja elektronit vetenä. Fermi-taso on "elektronimeren" absoluuttinen pinta 0 Kelvinin lämpötilassa. Kaikki DOS-tilat Fermi-tason alapuolella ovat miehitettyjä, ja sen yläpuolella olevat tilat ovat tyhjiä.

        ### Mistä tiedän, onko aine metalli vai eriste?
        Voit lukea materiaalin sähkönjohtavuuden suoraan Fermi-tason ja DOS-kuvaajan leikkauskohdasta:
        * **Johteet (Metallit):** Jos Fermi-taso osuu suoraan keskelle DOS-huippua (energiavyötä), aine on metalli. Elektronien yläpuolella on välittömästi tyhjiä tiloja, joihin ne voivat siirtyä pienimmälläkin jännitteellä, jolloin sähkövirta kulkee.
        * **Eristeet ja Puolijohteet:** Jos Fermi-taso putoaa tasan nollaan eli vyöaukon (band gap) kohdalle, alempi vyö on aivan täynnä ja ylempi täysin tyhjä. Koska elektronit ovat jumissa eikä tyhjiä paikkoja ole lähistöllä, aine ei johda sähköä. Jos vyöaukko on riittävän kapea (esim. pii), lämpöenergia voi nostaa yksittäisiä elektroneja kuilun yli, jolloin aine on puolijohde.
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
        fig_s.update_xaxes(title_text="DOS", row=1, col=2)
        fig_s.update_layout(height=600, showlegend=False, hovermode="y unified")

        st.plotly_chart(fig_s, use_container_width=True)

        with st.expander("Pedagogisia huomioita ja tehtäviä"):
            st.write("""
            1. **Van Hoven singulariteetit:** Tarkastele 1D monatomista ketjua. Huomaatko, kuinka tilatiheys (DOS) kasvaa äärettömäksi vyön ala- ja yläreunoilla? Tämä on tyypillistä 1D-järjestelmille, koska $dE/dk = 0$ reunoilla. Miten DOS eroaa 2D-neliöhilassa?
            2. **Peierlsin vääristymä:** Valitse "1D Biatominen". Aseta aluksi kaikki parametrit samoiksi ($\alpha_1 = \alpha_2$, $\beta_1 = \beta_2$). Pienennä sitten $\beta_2$:n absoluuttista arvoa hieman (esim. $\beta_1 = -2.0, \beta_2 = -1.5$). Mitä tapahtuu pisteessä $k = \pm \pi/a$? Tämä on ns. Peierlsin vääristymä, jossa tasamittainen 1D-metalli muuttuu eristeeksi dimerisoitumalla!
            3. **Elektronegatiivisuus:** Pidä $\beta_1$ ja $\beta_2$ samoina, mutta muuta atomien energioita $\alpha$. Tämä vastaa kidehilaa, joka koostuu kahdesta eri alkuaineesta (esim. hiili ja typpi vuorotellen). Miten vyöaukon (band gap) koko riippuu $\alpha_1$:n ja $\alpha_2$:n erotuksesta?
            """)
