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
st.caption("Numeerinen Schrödingerin yhtälön ratkaisija differenssimenetelmällä (Atomiyksiköissä, $\hbar = 1$)")
st.divider()

# ==========================================
# 2. PHYSICS FUNCTIONS (Cached for performance)
# ==========================================
@st.cache_data
def solve_schrodinger_1d(x, V, mass, d, norbs):
    npts = len(x)
    # Kineettisen energian operaattori differenssimenetelmällä.
    # Huom: Käytämme atomiyksiköitä, joten hbar = 1.
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
    
    # Liikemäärän odotusarvo <p>. 
    # Huom: Koska ratkaisemme ajasta riippumatonta yhtälöä symetrisille/reunustetuille 
    # potentiaaleille, ratkaisut ovat reaalisia seisovia aaltoja, jolloin <p> = 0.
    exp_p = 0.0 
    
    # Liikemäärän neliön odotusarvo <p^2> = int( psi * (-hbar^2 * d^2/dx^2 psi) ) dx
    # Koska atomiyksiköissä hbar = 1, kaava pelkistyy:
    exp_p2 = np.sum(psi_norm * (-second_deriv)) * d
    
    return exp_x, exp_x2, exp_p, exp_p2

# ==========================================
# 3. SIDEBAR PARAMETERS
# ==========================================
st.sidebar.header("Järjestelmän asetukset")
pot_type = st.sidebar.selectbox(
    "Potentiaalin tyyppi", 
    ["Ääretön kaivo", "Äärellinen kaivo", "Kaksoiskaivo", "Harmoninen värähtelijä", "Morse-potentiaali", "Säännöllinen kidehila"]
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
    st.sidebar.info("Reunaehdot on asetettu äärettömiksi laatikon reunoilla (Dirichlet-reunaehto).")
    # Asetetaan potentiaali kirjaimellisesti erittäin suureksi reunoilla, 
    # jotta se on fysiikallisesti ehta ääretön kaivo eikä vain numeerinen artefakti.
    V[0] = 1e6
    V[-1] = 1e6
    
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
    # Klassisessa Morsessa on r_e (tasapainoetäisyys). 
    # Tässä 1D-mallissa yksinkertaistamme asettamalla r_e = 0.
    V = De * (1 - np.exp(-alpha * x))**2
    V = np.minimum(V, De * 2.0)

elif pot_type == "Säännöllinen kidehila":
    wells = st.sidebar.number_input("Kaivojen lukumäärä", value=4, min_value=2, step=1)
    depth = st.sidebar.number_input("Kaivon syvyys (au)", value=0.5, step=0.1)
    lattice_const = L / wells
    # Tämä on Kronig-Penney -tyyppinen kanttiaaltomalli kidehilalle
    V = np.where(np.sin(2 * np.pi * (x + L/2) / lattice_const) > 0, -depth, 0)
    V = V - np.min(V)

# ==========================================
# 4. CALCULATION & VISUALIZATION
# ==========================================
with st.spinner("Ratkaistaan Hamiltonin matriisia..."):
    eigvals, eigvecs = solve_schrodinger_1d(x, V, mass, d, norbs)

tab1, tab2, tab3 = st.tabs(["Ohjeet (Instructions)", "Aaltofunktiot", "Odotusarvot"])

with tab1:
    st.subheader("Yleistä")
    st.markdown("""
Tervetuloa leikkimään yksiulotteisten potentiaalien kanssa! Ruudun takana kirjoittamani pieni ohjelma ratkoo ajasta riippumattoman Schrödingerin yhtälön yksittäiselle hiukkaselle erilaisissa yksiulotteisissa tiloissa erilaisilla potentiaaleilla.

Ratkaisu tapahtuu differenssimenetelmällä jatkuvan aaltofunktion approksimoimiseksi rajallisessa, diskreetissä tilassa. Säätämällä sivupalkissa potentiaalin muotoa, hiukkasen massaa ja tilan parametreja voit tutkia, miten nämä tekijät vaikuttavat:

* Energiatasoihin
* Aaltofunktion todennäköisyysjakaumiin
* Heisenbergin epätarkkuusperiaatteeseen

Aloita valitsemalla potentiaalityyppi ja säätämällä parametreja. Siirry Aaltofunktiot-välilehdelle tarkastellaksesi tuloksena olevia tiloja.


### Hiukan eri potentiaaleista... 

Tässä moduulissa voit tutkia tavanomaisten potentiaalikaivojen lisäksi kolmea fysiikan ja kemian kannalta tärkeää potentiaalimallia, joista ensimmäinen lieneekin jo tuttu:

**1. Harmoninen värähtelijä (Harmonic Oscillator)** $V(x) = \\frac{1}{2}kx^2$  
Kvanttimekaaninen harmoninen värähtelijä on yksi modernin fysiikan tärkeimmistä malleista. Se kuvaa hiukkasta, johon kohdistuu Hooken lain mukainen palauttava voima (kuten jousi). Kemiassa tätä käytetään mallintamaan molekyylien välisten sidosten värähtelyä lähellä niiden tasapainoetäisyyttä (esim. IR-spektroskopia).  
* **Erityispiirre:** Energiatasot ovat täysin tasavälein ($E_n = \hbar\omega(n + 1/2)$). Lisäksi huomaat, että alin energiataso ei ole koskaan nolla (ns. nollapiste-energia), mikä on suora seuraus Heisenbergin epätarkkuusperiaatteesta.

**2. Morse-potentiaali (Morse Potential)** $V(x) = D_e(1 - e^{-\\alpha (x - r_e)})^2$  
Harmoninen malli on vain approksimaatio, sillä oikeaa vieteriä ei voi venyttää loputtomiin – kemialliset sidokset katkeavat. Morse-potentiaali on realistisempi malli kaksiatomisen molekyylin värähtelylle. Se huomioi epäharmonisuuden ja sidoksen dissosiaation (hajoamisen).  
*Huom: Tässä simulaatiossa oletamme yksinkertaisuuden vuoksi, että tasapainoetäisyys $r_e = 0$.*
* **Erityispiirre:** Kun energia kasvaa (mennään ylemmille tiloille), energiatasot pakkautuvat yhä tiheämmin yhteen. Kun energia ylittää dissosiaatioenergian ($D_e$), sidos katkeaa ja hiukkanen on vapaa.

**3. Säännöllinen kidehila (Kronig-Penney -tyyppinen malli)** Tämä potentiaali mallintaa elektronin liikettä säännöllisessä kidehilassa (esim. metallijohdin tai puolijohde). Jaksollisesti toistuvat kanttiaaltomaiset potentiaalikaivot edustavat säännöllisin välimatkoin sijaitsevia positiivisesti varautuneita atomiytimiä, jotka vetävät elektronia puoleensa.  
* **Erityispiirre:** Kun aaltofunktio venyy usean kaivon yli, kaivojen väliset vuorovaikutukset saavat yksittäiset energiatasot jakautumaan. Jos kasvatat tilojen määrää, näet kuinka tasot alkavat muodostaa tiheitä ryppäitä eli **energiavöitä** (allowed bands), joiden väliin jää tyhjiä **vyöaukkoja** (band gaps). Tämä on koko modernin puolijohdefysiikan (ja tietokoneiden) perusta!

    """)

with tab2:
    fig = go.Figure()
    
    # Plot potential
    fig.add_trace(go.Scatter(x=x, y=V, mode='lines', name='Potentiaali V(x)', line=dict(color='black', width=3)))
    
    energy_span = max(eigvals[-1] - np.min(V), 1.0)
    
    # Plot wavefunctions
    for i in range(len(eigvals)):
        energy = eigvals[i]
        psi = eigvecs[:, i]
        
        # Phase standardization
        if psi[npts // 2] < 0 if pot_type != "Ääretön kaivo" else psi[1] < 0:
            psi = -psi
        
        scale_factor = (energy_span * 0.15) / np.max(np.abs(psi))
        psi_plot = (psi * scale_factor) + energy
        
        fig.add_trace(go.Scatter(x=x, y=psi_plot, mode='lines', name=f'ψ_{i} (E={energy:.3f})'))
        fig.add_trace(go.Scatter(x=[x[0], x[-1]], y=[energy, energy], mode='lines', line=dict(color='gray', dash='dash'), showlegend=False))
    
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
    
    st.info("💡 **Huomio yksiköistä:** Tämä ohjelma käyttää laskennallisen kemian standardia eli **atomiyksiköitä (atomic units, a.u.)**. Näissä yksiköissä Planckin vakio $\hbar = 1$ ja elektronin massa $m_e = 1$. Tämä yksinkertaistaa yhtälöitä huomattavasti.")

    st.markdown("""
    **Merkintöjen selitykset:**
    * $\langle x \\rangle$: Sijainnin odotusarvo. Kertoo hiukkasen keskimääräisen sijainnin.
    * $\langle x^2 \\rangle$: Sijainnin neliön odotusarvo.
    * $\langle p \\rangle$: Liikemäärän odotusarvo. Koska ratkaisemme reaalisia stationääritiloja (seisovia aaltoja) symmetrisissä reunaehdoissa, hiukkanen ei etene keskimäärin kumpaankaan suuntaan ($\langle p \\rangle = 0$).
    * $\Delta x$: Sijainnin epätarkkuus eli keskihajonta ($\sqrt{\langle x^2 \\rangle - \langle x \\rangle^2}$).
    * $\Delta p$: Liikemäärän epätarkkuus eli keskihajonta ($\sqrt{\langle p^2 \\rangle - \langle p \\rangle^2}$). Tämä **ei** ole nolla, koska hiukkasella on kineettistä energiaa ($\langle p^2 \\rangle > 0$).
    * $\Delta x \Delta p$: Heisenbergin epätarkkuustulo. Kvanttimekaniikan mukaan tämän on aina oltava vähintään $\hbar/2$. Koska olemme atomiyksiköissä ($\hbar=1$), numeerisen alarajan pitäisi olla tasan $0.5$.
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
    3. **Epätarkkuusperiaate:** Katso Odotusarvot-välilehteä. Toteutuuko Heisenbergin epätarkkuusperiaate ($\ge 0.5$) kaikilla laskemillasi tiloilla? Kokeile kaventaa kaivon leveyttä (L tai Width); mitä tapahtuu $\Delta p$:lle, kun pakotat hiukkasen tarkempaan sijaintiin ($\Delta x$ pienenee)?
    4. **Solmukohdat:** Laske kunkin aaltofunktion nollakohdat (solmut). Mikä sääntö yhdistää tilan järjestysnumeron ja solmujen määrän?
    5. **Harmoninen värähtelijä:** Huomaatko, että alin energiataso ei ole koskaan nolla (nollapiste-energia)? Kokeile kasvattaa jousivakiota (k). Mitä tapahtuu energiatasojen välimatkalle?
    """)
