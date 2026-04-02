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
