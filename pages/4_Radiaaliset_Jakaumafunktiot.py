import numpy as np
import plotly.graph_objects as go
import streamlit as st
from scipy.integrate import simpson

from plot_style import COLORS, initialise, preset_picker, show_plot
from qm_models import CLEMENTI_ZEFF, ELEMENTS, radial_orbitals

st.set_page_config(page_title="Säteittäiset jakaumat", layout="wide")
st.title("Moduuli 4: Säteittäiset jakaumat")
st.caption("Aaltofunktion radiaalinen osa, elektronin sijaintijakauma ja efektiivinen ydinvaraus.")
st.divider()
initialise({"rad_element": 6, "rad_max": 8., "rad_scale": False, "rad_orthogonal": True})
preset_picker("rad", {
    "Vety: tilavuusvaikutus": {"rad_element": 1, "rad_max": 6., "rad_scale": False, "rad_orthogonal": True},
    "Litium: ulompi kuori": {"rad_element": 3, "rad_max": 10., "rad_scale": False, "rad_orthogonal": True},
    "Neon: orbitaalien kutistuminen": {"rad_element": 10, "rad_max": 6., "rad_scale": False, "rad_orthogonal": True},
    "Natrium: varjostus ja solmut": {"rad_element": 11, "rad_max": 10., "rad_scale": False, "rad_orthogonal": True},
}, {"Vety: tilavuusvaikutus": "Vertaa R(r):ää ja P(r):ää aivan ytimen lähellä.",
    "Natrium: varjostus ja solmut": "Vertaa 1s-, 2s- ja 3s-funktioiden laajuutta ja solmuja."})
st.sidebar.header("Jakauman asetukset")
atomic_number = st.sidebar.selectbox("Alkuaine", list(ELEMENTS),
    format_func=lambda z: f"{z} – {ELEMENTS[z]}", key="rad_element")
r_max = st.sidebar.slider("Kuvaajan yläraja r (a₀)", 2., 20., key="rad_max", step=.5)
scale_peaks = st.sidebar.checkbox("Skaalaa huiput samaan korkeuteen", key="rad_scale")
orthogonal = st.sidebar.checkbox("Ortogonalisoidut STO-funktiot", key="rad_orthogonal",
    help="Saman kulmakvanttiluvun funktiot ortogonalisoidaan. Poista valinta nähdäksesi puhtaat STO:t.")
st.sidebar.caption("Kuvaajan rajaus ei muuta laskettuja orbitaaleja.")

@st.cache_data(max_entries=36)
def calculate(z, orthogonal):
    return radial_orbitals(z, orthogonal)

r, orbitals = calculate(atomic_number, orthogonal)
mask = r <= r_max
amplitude_tab, probability_tab, theory_tab = st.tabs(
    ["Säteittäinen aaltofunktio R(r)", "Todennäköisyystiheys P(r)", "Taustaa ja teoria"])
for tab, probability_mode in [(amplitude_tab, False), (probability_tab, True)]:
    with tab:
        fig = go.Figure()
        reference_peak = None
        for i, label in enumerate(sorted(orbitals, key=lambda value: (int(value[0]), "spdf".index(value[1])))):
            function = orbitals[label]
            values = r*r*function**2 if probability_mode else function.copy()
            if reference_peak is None:
                reference_peak = float(np.max(np.abs(values)))
            plot_values = values.copy()
            if scale_peaks and i > 0:
                plot_values *= reference_peak/np.max(np.abs(values))
            fig.add_trace(go.Scatter(x=r[mask], y=plot_values[mask], mode="lines",
                name=label + (" (skaalattu)" if scale_peaks and i > 0 else ""),
                line=dict(color=COLORS[i % len(COLORS)], width=2.5,
                          dash="dash" if label.endswith("p") else "solid"),
                customdata=values[mask],
                hovertemplate="r = %{x:.4f} a₀<br>"+("P(r)" if probability_mode else "R(r)")+
                              " = %{customdata:.5f}<extra>"+label+"</extra>"))
        fig.update_layout(title=f"{ELEMENTS[atomic_number]}: {'todennäköisyystiheys' if probability_mode else 'säteittäinen aaltofunktio'}",
            xaxis_title="Etäisyys ytimestä r (a₀)",
            yaxis_title=("P(r) (a₀⁻¹)" if probability_mode else "R(r) (a₀⁻³ᐟ²)")+
                        (" · suhteellinen skaala" if scale_peaks else ""), height=540)
        show_plot(fig)
        if scale_peaks:
            st.caption("Huippujen skaalaus helpottaa muotojen vertailua. Skaalattujen käyrien pinta-ala muuttuu; "
                       "kohdistustiedot näyttävät alkuperäiset arvot.")
        if probability_mode:
            st.latex(r"P(r)=r^2|R(r)|^2,\qquad \int_0^\infty P(r)\,dr=1")
            st.table([{"Orbitaali": label, "Efektiivinen ydinvaraus": f"{CLEMENTI_ZEFF[atomic_number][label]:.4f}",
                       "Integraali laskenta-alueella": f"{simpson(r*r*function**2, x=r):.6f}"}
                      for label, function in orbitals.items()])
            st.caption("Integraalit lasketaan kiinteällä 0–60 a₀ alueella. Kuvaajan yläraja on erillinen näyttöasetus.")

with theory_tab:
    st.markdown(r"""
    ### R(r) ja P(r) kuvaavat eri asioita
    Atomikeskisessä mallissa $\psi(r,\theta,\phi)=R(r)Y_{lm}(\theta,\phi)$.
    Kulmaosa on normalisoitu: $\int |Y_{lm}|^2d\Omega=1$. Silloin säteittäinen
    todennäköisyystiheys on **$P(r)=r^2|R(r)|^2$**. Todennäköisyys löytää elektroni
    säteiden r ja r+dr välistä on P(r)dr.

    S-orbitaalin koko aaltofunktiolle $\psi=R/\sqrt{4\pi}$ sama asia voidaan kirjoittaa
    $P(r)=4\pi r^2|\psi(r)|^2$. Näitä R:n ja koko aaltofunktion merkintätapoja tulee
    käyttää johdonmukaisesti.

    Ytimessä s-elektronin **paikallinen tiheys voi olla äärellinen**, vaikka P(0)=0.
    Radiaalisen jakauman nolla seuraa pallokuoren tilavuustekijästä. Se ei sulje pois
    elektronin ja ytimen kontaktivuorovaikutuksia.

    ### Varjostus ja efektiivinen ydinvaraus
    Muut elektronit pienentävät elektronin kokemaa ytimen vetovoimaa. Clementin ja
    Raimondin taulukon arvot kuvaavat tätä yksittäisten STO-funktioiden eksponenttien
    avulla. Tässä $\zeta=Z_{eff}/n$ ja $R(r)\propto r^{n-1}e^{-\zeta r}$.
    Kasvava efektiivinen ydinvaraus supistaa malliorbitaalia.

    ### Mitä ortogonalisointi tekee?
    Puhtaalta STO:lta puuttuvat sisäiset säteittäiset solmut. Gram–Schmidt-menetelmä
    tekee saman kulmakvanttiluvun funktioista ortogonaalisia ja tuottaa tässä
    havainnolliset solmut. Rakennetut funktiot ovat opetusmalli; ortogonaalisuus
    ei yksin osoita, että ne ratkaisevat atomin HF-yhtälöt.
    """)
    st.caption("Parametrit: Clementi ja Raimondi, J. Chem. Phys. 38, 2686 (1963), taulukko I; Z_eff = nζ.")

with st.expander("Kysymyksiä ja kokeiltavaa"):
    st.markdown(r"""
    1. **Tilavuustekijä:** Valitse vety ja vertaa R(r):ää sekä P(r):ää ytimen lähellä.
       Miksi niiden maksimit ovat eri kohdissa?
    2. **Jaksollisuus:** Vertaa litiumin ja neonin 2s-jakaumia sekä neonin 2p-jakaumaa.
       Miten efektiivinen ydinvaraus auttaa selittämään eron?
    3. **Varjostus:** Valitse natrium. Vertaa sisäkuorten ja 3s-funktion laajuutta.
       Miten tämä liittyy uloimman elektronin helppoon irtoamiseen?
    4. **Solmut:** Vaihda puhtaiden ja ortogonalisoitujen STO-funktioiden välillä.
       Laske 2s- ja 3s-funktioiden sisäiset solmut. Mitä ortogonaalisuus edellyttää?
    5. **Rajaus:** Muuta vain kuvaajan ylärajaa. Funktioiden arvot samoilla etäisyyksillä
       säilyvät, vaikka osa jakaumasta jää kuvan ulkopuolelle.
    """)
