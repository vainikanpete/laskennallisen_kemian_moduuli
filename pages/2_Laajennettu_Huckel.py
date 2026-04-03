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
    4. **Lävistäjän ulkopuoliset elementit ($H_{ij}$):** Atomien välinen vuorovaikutus (resonanssi/sidos) lasketaan **Wolfsberg-Helmholtz -approksimaatiolla**:
       $H_{ij} = K \cdot S_{ij} \\frac{H_{ii} + H_{jj}}{2}$
       Tässä $K$ on empiirinen vakio (yleensä 1.75).

    ### Kantafunktiot: STO vs. GTO
    Aaltofunktioita mallinnetaan tietokoneessa kantafunktioilla. Kaksi päätyyppiä ovat:
    
    * **Slater-tyyppiset orbitaalit (Slater Type Orbitals, STO, $e^{-\zeta r}$):** Fyysisesti erittäin tarkkoja. Niillä on terävä kärki (cusp) atomin ytimen kohdalla ja ne suppenevat etäisyyden kasvaessa juuri kuten oikeatkin elektronipilvet. Ongelma: Monikeskisten integraalien laskeminen STO:illa on matemaattisesti raskasta. **EHT käyttää STO-funktioita**, koska siinä lasketaan vain helppoja kahden keskuksen peittointegraaleja ($S_{ij}$).
    
    * **Gaussin orbitaalit (Gaussian Type Orbital, $e^{-\\alpha r^2}$):**
      Fyysisesti hieman vääriä (liian nopeasti suppeneva), mutta niillä on hyödyllinen matemaattinen ominaisuus: kahden GTO:n tulo on aina uusi GTO. Tämä tekee miljoonien integraalien laskemisesta tietokoneella mukavaa, käytännöllistä ja nopeaa. **Hartree-Fock ja moderni DFT käyttävätkin usein GTO-funktioita.**
    """)

with tab_mo:
    st.markdown("""
    ### Kahden orbitaalin vuorovaikutus
    Tämä työkalu ratkaisee yleisen $A-B$ sidoksen MO-diagramminmatriisimuotoisen ajasta riippumattoman Schrödingerin yhtälön HC=ESC avulla.
    Voit säätää atomien energioita ja peittointegraalia ja nähdä kaksi MO-teorian perussääntöä:
    1. Sitova orbitaali saa enemmän luonnetta elektronegatiivisemmalta (alempana olevalta) atomilta. Hajottava orbitaali saa enemmän luonnetta elektropositiivisemmalta atomilta.
    2. Jos peittointegraali $S > 0$, hajottava tila nousee ylöspäin **enemmän** kuin sitova tila laskee alaspäin (steerinen repulsio).
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
            * **Steerinen repulsio ($S > 0$):** Aseta energiat samoiksi ja liikuta peittointegraalin $S$ arvoa nollasta ylöspäin. Huomaat, että hajottava tila nousee nopeammin ylös kuin sitova tila laskee alas. Siksi kahden jalokaasuatomin (kuten $He_2$) vuorovaikutus on repulsiivinen!
            """)
