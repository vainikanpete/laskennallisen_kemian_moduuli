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
# 2. VÄLILEHDET & TEORIA
# ==========================================
tab_laskenta, tab_teoria = st.tabs(["Laskenta & Visualisointi", "Taustaa & Teoriaa"])

with tab_teoria:
    st.markdown(r"""
    ### Mitä kvanttitunneloituminen on?

    Kuvittele, että potkaiset jalkapallon kohti jyrkkää ylämäkeä. Jos pallon kineettinen energia ei riitä ylittämään mäen huippua, klassinen fysiikka sanoo, että pallo pysähtyy ja vierii takaisin. Pallo ei voi koskaan ilmestyä mäen toiselle puolelle.

    Kvanttimaailmassa hiukkasilla on aaltoluonne, jolloin niitä kuvataan avaruuteen levinneinä todennäköisyysamplitudeina. Kun kvanttimekaaninen aalto törmää potentiaalivalliin, jonka korkeus $V_0$ on suurempi kuin hiukkasen energia $E$, aalto ei pysähdy seinän pintaan välittömästi. Schrödingerin yhtälön ratkaisu jatkuu esteen sisälle, mutta muuttuu oskillatorisesta muodosta eksponentiaaliseksi:
    
    $$ \psi(x) = A e^{-\kappa x} + B e^{\kappa x} $$
    
    Yleisesti ratkaisu on näiden kahden eksponentin yhdistelmä, mutta fyysisesti hyväksyttävä ratkaisu vaimenee esteen sisällä. Atomiyksiköissä ($\hbar = 1$) tämä vaimenemiskerroin on:
    $$ \kappa = \sqrt{2m(V - E)} $$

    Jos seinä on tarpeeksi ohut, aaltofunktio ei ehdi vaimentua nollaan ennen kuin este loppuu, jolloin aalto "vuotaa" läpi. **Tärkeä huomio:** Hiukkasen energia *ei muutu* tunneloitumisessa! Kyse on todennäköisyysamplitudin vaimenemisesta, ei siitä, että hiukkanen kuluttaisi energiaansa esteen puskemiseen.

    💡 *Huomio! Tunneloituminen ei ole pelkkä kvantti-ilmiö. Täysin sama matematiikka esiintyy myös optiikassa (evanescent waves) ja klassisissa aaltojärjestelmissä!*

    ---

    ### Siirtomatriisimenetelmä (TMM) ja sen realiteetit

    Ohjelma laskee läpäisytodennäköisyyden $T(E)$ pilkkomalla esteen satoihin tasapaksuihin osioihin ja yhdistämällä aaltofunktion jatkuvuusehdot rajapinnoilla 2x2 -matriiseilla. Laskennassa oletetaan, että potentiaali on vakio esteen ulkopuolella, jolloin hiukkanen saapuu ja poistuu vapaana asymptoottisena tasoaaltona.

    **Numeeriset huomiot (Mitä koodissa tapahtuu fysiikan ohella?):**
    * **Paksujen esteiden epävakaus:** Siirtomatriisimenetelmä on altis numeeriselle epävakaudelle (eksponentiaalinen kasvu) erittäin paksuilla tai korkeilla esteillä. Koodi tunnistaa ylivuodot (overflow) ja asettaa läpäisyn nollaan, mutta menetelmä saattaa aliarvioida minimaalisia läpäisyjä pyöristysvirheiden vuoksi.
    * **Singulariteetit ($E \approx V$):** Kun hiukkasen energia on tasan esteen korkuinen, aaltoluku $k \to 0$. Koodi käyttää pientä numeerista kikkailua nollalla jakamisen estämiseksi.
    * **Fyysiset rajat:** Laskennallisten virheiden kasaantuessa $T$ saattaa matemaattisesti ylittää arvon 1, joten ohjelma leikkaa (clip) tuloksen fyysiseen maksimiinsa $T \le 1$.
    """)

with tab_laskenta:
    # ==========================================
    # 3. NUMBA-OPTIMOITU TMM-LASKENTA
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
            # Numeerinen regularisointi E \approx V kohdalla nollalla jaon estämiseksi
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
            # Olettaa asymptoottiset tasoaallot molemmin puolin (V = vakio reunoilla)
            k_in = np.sqrt(2.0 * mass * (E - V[0] + 0.0j))
            k_out = np.sqrt(2.0 * mass * (E - V[-1] + 0.0j))
            
            if k_in.real > 0:
                abs_M11 = np.abs(M11)
                # Suojataan TMM:n eksponentiaaliselta ylivuodolta paksulla esteellä
                if abs_M11 > 1e100:
                    T_prob[idx] = 0.0
                else:
                    T_val = (k_out.real / k_in.real) * (1.0 / (abs_M11**2))
                    # Rajataan tulos [0, 1] numeerisen kohinan yliampumisen vuoksi
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
    # 4. SIVUPALKKI JA PARAMETRIT
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
    # 5. LASKENTA JA VISUALISOINTI
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
    # 6. PEDAGOGINEN OSIO
    # ==========================================
    with st.expander("Kysymyksiä ja huomioita"):
        st.write("""
        1. **Klassinen vs. Kvanttimekaaninen:** Klassisen fysiikan mukaan hiukkanen ei voi koskaan läpäistä estettä, jos sen energia on pienempi kuin esteen korkeus ($E < V_0$). Katso ylempää kuvaajaa alueella vasemmalla punaisesta katkoviivasta. Mitä havaitset?
        2. **Massan vaikutus:** Kokeile kasvattaa hiukkasen massaa (esim. arvosta 1.0 arvoon 5.0). Miten se vaikuttaa tunneloitumisen todennäköisyyteen matalilla energioilla?
        3. **Resonanssitunneloituminen:** Aseta esteiden määräksi 2. Huomaatko T(E)-käyrässä teräviä piikkejä, joissa läpäisytodennäköisyys pomppaa sataan prosenttiin ($T=1$), vaikka energia on reilusti alle esteen korkeuden? Tämä johtuu aaltofunktion konstruktiivisesta interferenssistä kahden esteen välisessä \"kaivossa\" (resonanssiehto $kL = n\pi$).
        """)
