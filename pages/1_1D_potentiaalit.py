import streamlit as st
import numpy as np
import scipy.linalg as la
import plotly.graph_objects as go
from scipy.special import eval_genlaguerre

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
# 2. PHYSICS FUNCTIONS 
# ==========================================
@st.cache_data
def solve_schrodinger_1d(x, V, mass, d, norbs):
    npts = len(x)
    t0 = 1.0 / (2.0 * mass * d**2)
    
    main_diag = 2.0 * t0 + V
    off_diag = -t0 * np.ones(npts - 1)
    
    H = np.diag(main_diag) + np.diag(off_diag, k=1) + np.diag(off_diag, k=-1)
    eigvals, eigvecs = la.eigh(H)
    
    return eigvals[:norbs], eigvecs[:, :norbs]

@st.cache_data
def solve_morse_analytical(x, De, alpha, mass, requested_orbs):
    lam = np.sqrt(2.0 * mass * De) / alpha
    max_n = int(np.floor(lam - 0.5))
    
    if max_n < 0:
        return np.array([]), np.array([[]])
        
    eigvals = []
    eigvecs = []
    z = 2.0 * lam * np.exp(-alpha * x)
    n_states = min(max_n + 1, requested_orbs)
    
    for n in range(n_states):
        E_n = alpha * np.sqrt(2.0 * De / mass) * (n + 0.5) - (alpha**2 / (2.0 * mass)) * (n + 0.5)**2
        eigvals.append(E_n)
        
        alpha_L = 2.0 * lam - 2.0 * n - 1.0
        laguerre_poly = eval_genlaguerre(n, alpha_L, z)
        
        psi = (z**(lam - n - 0.5)) * np.exp(-z / 2.0) * laguerre_poly
        
        dx = x[1] - x[0]
        norm = np.sqrt(np.sum(psi**2) * dx)
        psi_normalized = psi / norm
        
        eigvecs.append(psi_normalized)
        
    if len(eigvals) == 0:
        return np.array([]), np.array([[]])
        
    return np.array(eigvals), np.column_stack(eigvecs)

def calculate_expectation_values(x, eigvec, d):
    norm_factor = np.sum(eigvec**2) * d
    psi_norm = eigvec / np.sqrt(norm_factor)
    
    psi2 = psi_norm**2
    exp_x = np.sum(psi2 * x) * d
    exp_x2 = np.sum(psi2 * x**2) * d
    
    first_deriv = np.gradient(psi_norm, d)
    second_deriv = np.gradient(first_deriv, d)
    
    exp_p = 0.0 
    exp_p2 = np.sum(psi_norm * (-second_deriv)) * d
    
    return exp_x, exp_x2, exp_p, exp_p2

# ==========================================
# 3. SIDEBAR PARAMETERS & RESET LOGIC
# ==========================================
# Callback-funktio arvojen nollaamiseen
def reset_parameters():
    st.session_state.clear()

st.sidebar.header("Järjestelmän asetukset")

# HUOM: Kaikilla on nyt "key"-parametri
pot_type = st.sidebar.selectbox(
    "Potentiaalin tyyppi", 
    [
        "Ääretön kaivo", 
        "Äärellinen kaivo", 
        "Kaksoiskaivo", 
        "Harmoninen värähtelijä", 
        "Morse-potentiaali (Numeerinen)", 
        "Morse-potentiaali (Analyyttinen)", 
        "Säännöllinen kidehila"
    ],
    key="pot_type"
)

mass = st.sidebar.number_input("Hiukkasen massa (au)", value=2.0, min_value=0.1, step=0.5, key="mass")
L = st.sidebar.number_input("Tilan leveys L (au)", value=10.0, min_value=0.1, step=1.0, key="L")

d = st.sidebar.number_input(
    "Hilan tiheys d (au)", 
    value=0.05, 
    min_value=0.01,
    step=0.01, 
    format="%.3f",
    help="Hila (grid) tarkoittaa niitä diskreettejä pisteitä, joissa aaltofunktio lasketaan. Pienempi luku tarkoittaa tiheämpää hilaa ja tarkempaa tulosta, mutta raskaampaa laskentaa.",
    key="d"
)
norbs = st.sidebar.number_input(
    "Laskettavien tilojen määrä", 
    value=4, 
    min_value=1, 
    step=1,
    help="Määrittää, kuinka monta alinta kvanttitilaa (energiatasoa ja aaltofunktiota) Hamiltonin matriisista ratkaistaan ja visualisoidaan.",
    key="norbs"
)

npts = int(L / d)
x = np.linspace(-L/2, L/2, npts)
V = np.zeros(npts)

De = None

st.sidebar.header("Potentiaalin parametrit")

if pot_type == "Ääretön kaivo":
    st.sidebar.info("Reunaehdot on asetettu äärettömiksi laatikon reunoilla (Dirichlet-reunaehto).")
    V[0] = 1e6
    V[-1] = 1e6
    
elif pot_type == "Äärellinen kaivo":
    depth = st.sidebar.number_input("Kaivon syvyys (au)", value=1.0, step=0.1, key="fin_depth")
    width = st.sidebar.number_input("Kaivon leveys (au)", value=2.0, step=0.1, key="fin_width")
    V = np.zeros(npts)
    V[np.abs(x) <= width/2] = -depth
    V = V - np.min(V)

elif pot_type == "Kaksoiskaivo":
    depth = st.sidebar.number_input("Kaivojen syvyys (au)", value=2.0, step=0.1, key="dbl_depth")
    width = st.sidebar.number_input("Yksittäisen kaivon leveys (au)", value=2.0, step=0.1, key="dbl_width")
    distance = st.sidebar.number_input("Kaivojen välimatka (au)", value=4.0, step=0.1, key="dbl_dist")
    V = np.zeros(npts)
    V[np.abs(x - distance/2) <= width/2] = -depth
    V[np.abs(x + distance/2) <= width/2] = -depth
    V = V - np.min(V)

elif pot_type == "Harmoninen värähtelijä":
    spring = st.sidebar.number_input("Jousivakio k", value=10.0, step=1.0, key="spring_k")
    V = (spring / 2.0) * x**2

elif "Morse-potentiaali" in pot_type:
    De = st.sidebar.number_input("Dissosiaatioenergia (De)", value=5.0, step=0.5, key="morse_De")
    alpha = st.sidebar.number_input("Kuoppaparametri (alpha)", value=1.0, step=0.1, key="morse_alpha")
    V = De * (1 - np.exp(-alpha * x))**2
    V = np.minimum(V, De * 2.0)

elif pot_type == "Säännöllinen kidehila":
    wells = st.sidebar.number_input("Kaivojen lukumäärä", value=4, min_value=2, step=1, key="lat_wells")
    depth = st.sidebar.number_input("Kaivon syvyys (au)", value=0.5, step=0.1, key="lat_depth")
    lattice_const = L / wells
    V = np.where(np.sin(2 * np.pi * (x + L/2) / lattice_const) > 0, -depth, 0)
    V = V - np.min(V)

st.sidebar.divider()
# Callback-metodilla nappi tyhjentää tilan ennen sivun uudelleenlatausta
st.sidebar.button("🔄 Palauta oletusasetukset", on_click=reset_parameters)

# ==========================================
# 4. CALCULATION & VISUALIZATION
# ==========================================
with st.spinner("Ratkaistaan kvanttijärjestelmää..."):
    if pot_type == "Morse-potentiaali (Analyyttinen)":
        eigvals, eigvecs = solve_morse_analytical(x, De, alpha, mass, norbs)
        if len(eigvals) == 0:
            st.error("⚠️ Potentiaali on liian matala tai leveä (De tai alpha liian pieni suhteessa massaan) sitomaan yhtäkään tilaa!")
    else:
        eigvals, eigvecs = solve_schrodinger_1d(x, V, mass, d, norbs)

tab1, tab2, tab3 = st.tabs(["Ohjeet", "Aaltofunktiot", "Odotusarvot"])

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

**1. Harmoninen värähtelijä** $V(x) = \\frac{1}{2}kx^2$  
Kvanttimekaaninen harmoninen värähtelijä on yksi modernin fysiikan tärkeimmistä malleista. Se kuvaa hiukkasta, johon kohdistuu Hooken lain mukainen palauttava voima. Kemiassa tätä käytetään mallintamaan molekyylien välisten sidosten värähtelyä lähellä niiden tasapainoetäisyyttä (esim. IR-spektroskopia).  
* **Erityispiirre:** Energiatasot ovat täysin tasavälein ($E_n = \hbar\omega(n + 1/2)$). Lisäksi huomaat, että alin energiataso ei ole koskaan nolla (ns. nollapiste-energia), mikä on suora seuraus Heisenbergin epätarkkuusperiaatteesta.

**2. Morse-potentiaali** $V(x) = D_e(1 - e^{-\\alpha (x - r_e)})^2$  
Harmoninen malli on vain approksimaatio, sillä oikeaa kemiallista sidosta ei voi venyttää loputtomiin. Morse-potentiaali on realistisempi malli kaksiatomisen molekyylin värähtelylle. Se huomioi epäharmonisuuden ja sidoksen hajoamisen.

Tässä simulaattorissa voit tutkia Morse-potentiaalia kahdella eri menetelmällä:

* **Analyyttinen menetelmä:** Käyttää tarkkoja matemaattisia kaavoja (Laguerren polynomeja) Schrödingerin yhtälön ratkaisemiseen. Tämä näyttää puhtaan : sidottuja tiloja on vain rajallinen määrä. Kun hiukkasen energia ylittää dissosiaatioenergian ($D_e$), sidos katkeaa ja hiukkasesta tulee vapaa (energian spektri muuttuu jatkuvaksi).
* **Numeerinen menetelmä:** Ratkaisee aaltofunktion matriisilaskennalla "laatikossa" (jonka koko on asettamasi Tilan leveys L). Vaikka hiukkasen energia ylittäisi $D_e$:n, se ei pääse laatikosta ulos! Laskentahilan reunat toimivat läpipääsemättöminä seininä. Hiukkanen kimpoaa niistä ja muodostaa keinotekoisia seisovia aalloja $D_e$:n yläpuolelle.
  
  
*Huom: Tässä simulaatiossa oletamme yksinkertaisuuden vuoksi, että tasapainoetäisyys $r_e = 0$.*

**3. Säännöllinen kidehila (Kronig-Penney -tyyppinen malli)** Tämä potentiaali mallintaa elektronin liikettä säännöllisessä kidehilassa (esim. metallijohdin tai puolijohde). Jaksollisesti toistuvat kanttiaaltomaiset potentiaalikaivot edustavat säännöllisin välimatkoin sijaitsevia positiivisesti varautuneita atomiytimiä, jotka vetävät elektronia puoleensa.  
* **Erityispiirre:** Kun aaltofunktio venyy usean kaivon yli, kaivojen väliset vuorovaikutukset saavat yksittäiset energiatasot jakautumaan. Jos kasvatat tilojen määrää, näet kuinka tasot alkavat muodostaa tiheitä ryppäitä eli **energiavöitä** (eng. allowed bands), joiden väliin jää tyhjiä **vyöaukkoja** (eng. band gaps). Tämä on koko modernin puolijohdefysiikan perusta!

    """)

with tab2:
    if len(eigvals) > 0:
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
        
        if "Morse-potentiaali" in pot_type and De is not None:
            fig.add_hline(y=De, line_dash="dot", line_color="red", annotation_text="Dissosiaatioenergia (D_e)", annotation_position="top left")

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
    
    st.info("💡 **Huomio yksiköistä:** Tämä ohjelma käyttää laskennallisen kemian standardia eli **atomiyksiköitä (eng. atomic units, lyh. a.u.)**. Näissä yksiköissä Planckin vakio $\hbar = 1$ ja elektronin massa $m_e = 1$. Tämä yksinkertaistaa yhtälöitä huomattavasti.")

    st.markdown("""
    **Merkintöjen selitykset:**
    * $\langle x \\rangle$: Sijainnin odotusarvo. Kertoo hiukkasen keskimääräisen sijainnin.
    * $\langle x^2 \\rangle$: Sijainnin neliön odotusarvo.
    * $\langle p \\rangle$: Liikemäärän odotusarvo. Koska ratkaisemme reaalisia stationääritiloja (seisovia aaltoja) symmetrisissä reunaehdoissa, hiukkanen ei etene keskimäärin kumpaankaan suuntaan ($\langle p \\rangle = 0$).
    * $\Delta x$: Sijainnin epätarkkuus eli keskihajonta ($\sqrt{\langle x^2 \\rangle - \langle x \\rangle^2}$).
    * $\Delta p$: Liikemäärän epätarkkuus eli keskihajonta ($\sqrt{\langle p^2 \\rangle - \langle p \\rangle^2}$). Tämä **ei** ole nolla, koska hiukkasella on kineettistä energiaa ($\langle p^2 \\rangle > 0$).
    * $\Delta x \Delta p$: Heisenbergin epätarkkuustulo. Kvanttimekaniikan mukaan tämän on aina oltava vähintään $\hbar/2$. Koska käytämme atomiyksiköitä ($\hbar=1$), numeerinen alaraja on tasan $0.5$.
    """)
    st.divider()
    
    if len(eigvals) > 0:
        results = []
        for i in range(len(eigvals)):
            exp_x, exp_x2, exp_p, exp_p2 = calculate_expectation_values(x, eigvecs[:, i], d)
            
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
    3. **Epätarkkuusperiaate:** Katso Odotusarvot-välilehteä. Toteutuuko Heisenbergin epätarkkuusperiaate ($\ge 0.5$) kaikilla laskemillasi tiloilla? Kokeile kaventaa kaivon leveyttä (L); mitä tapahtuu $\Delta p$:lle, kun pakotat hiukkasen tarkempaan sijaintiin ($\Delta x$ pienenee)?
    4. **Solmukohdat:** Laske kunkin aaltofunktion nollakohdat (solmut, joskus puhutaan noodeista). Mikä sääntö yhdistää tilan järjestysnumeron ja solmujen määrän?
    5. **Harmoninen värähtelijä:** Huomaatko, että alin energiataso ei ole koskaan nolla (nollapiste-energia)? Kokeile kasvattaa jousivakiota (k). Mitä tapahtuu energiatasojen välimatkalle?
    6. **Morse-potentiaali ja numeeriset reunaehdot (Artefakti):** Vertaile "Numeerista" ja "Analyyttista" Morse-potentiaalia valikosta! Oikealla analyyttisella Morsella on vain rajallinen määrä sidottuja tiloja. Numeerinen malli kuitenkin laskee kentän "laatikossa" (Tilan leveys L), jolloin laatikon reunat toimivat läpipääsemättöminä seininä, muodostaen keksittyjä kvantittuneita tiloja D_e:n yläpuolelle. Analyyttinen vaihtoehto piirtää vain todelliset sidotut tilat.
    """)
