import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from plot_style import COLORS, POTENTIAL, THRESHOLD, initialise, preset_picker, show_plot
from qm_models import barrier_potential, transmission, resolve_resonances

st.set_page_config(page_title="Tunneloituminen", layout="wide")
st.title("Moduuli 5: Kvanttimekaaninen tunneloituminen")
st.caption("Tutki esteen läpäisyä ja tarkenna kapeat resonanssit näkyviin.")
st.divider()
defaults = {"tun_shape": "Suorakulmainen", "tun_count": 1, "tun_height": 5.,
            "tun_width": 1., "tun_sep": 3., "tun_mass": 1., "tun_max": 7.5,
            "tun_zoom": False}
initialise(defaults)
preset_picker("tun", {
    "Yksi suorakulmainen este": {**defaults},
    "Raskaampi hiukkanen": {**defaults, "tun_mass": 5.},
    "Kahden esteen resonanssi": {**defaults, "tun_count": 2, "tun_zoom": True},
    "Kolmen esteen rakenne": {**defaults, "tun_count": 3, "tun_zoom": True},
    "Sileä Gaussin este": {**defaults, "tun_shape": "Gaussin käyrä"},
    "Pitkähäntäinen Lorentz-este": {**defaults, "tun_shape": "Lorentz-muoto"},
}, {"Kahden esteen resonanssi": "Tarkennus hakeutuu ensimmäiseen yleiskuvasta löytyvään resonanssiin.",
    "Raskaampi hiukkanen": "Vertaa saman esteen läpäisyä kevyempään hiukkaseen."})
st.sidebar.header("Hiukkanen ja esteet")
mass = st.sidebar.number_input("Massa (mₑ)", .1, 20., key="tun_mass", step=.1)
shape = st.sidebar.selectbox("Esteen muoto", ["Suorakulmainen", "Gaussin käyrä", "Lorentz-muoto"], key="tun_shape")
count = st.sidebar.slider("Esteiden lukumäärä", 1, 3, key="tun_count")
height = st.sidebar.slider("Yksittäisen esteen korkeus V₀ (Eh)", 1., 15., key="tun_height", step=.5)
width = st.sidebar.slider("Esteen leveysparametri (a₀)", .2, 5., key="tun_width", step=.1,
    help="Suorakulmaiselle esteelle leveys; Lorentz-muodolle puoliarvoleveys. "
         "Gauss-muodolle leveys kohdassa V = V₀/e.")
if count > 1:
    if st.session_state["tun_sep"] < width:
        st.session_state["tun_sep"] = float(width)
    separation = st.sidebar.number_input("Esteiden keskipisteiden väli (a₀)", float(width), 10.,
                                          key="tun_sep", step=.1)
else:
    separation = 0.
maximum_energy = st.sidebar.number_input("Yleiskuvan yläenergia (Eh)", .1, 60., key="tun_max", step=.5)
zoom_enabled = st.sidebar.checkbox("Näytä resonanssin tarkennus", key="tun_zoom")

@st.cache_data(max_entries=24)
def overview(shape, count, height, width, separation, mass, maximum_energy):
    extent = max(12., count*separation + 6*width)
    cells = min(6000, max(1800, 2*int(np.ceil(extent/.01))))
    dx = 2*extent/cells
    x = -extent + (np.arange(cells)+.5)*dx
    potential = barrier_potential(x, shape, count, height, width, separation)
    energies = np.linspace(.01, maximum_energy, 800)
    values = transmission(energies, potential, dx, mass)
    peaks = resolve_resonances(energies, values, potential, dx, mass) if count > 1 else []
    return x, potential, dx, energies, values, peaks

with st.spinner("Lasketaan sironta ja etsitään resonansseja..."):
    x, potential, dx, energies, values, peaks = overview(
        shape, count, height, width, separation, mass, maximum_energy)
threshold = float(potential.max())
calc_tab, theory_tab = st.tabs(["Laskenta ja visualisointi", "Taustaa ja teoria"])
with calc_tab:
    fig = make_subplots(rows=2, cols=1, vertical_spacing=.19,
        subplot_titles=("Läpäisytodennäköisyys T(E)", "Potentiaalienergia V(x)"))
    fig.add_trace(go.Scatter(x=energies, y=values, mode="lines", name="Läpäisy T(E)",
        line=dict(color=COLORS[0], width=2.5),
        hovertemplate="E = %{x:.6f} Eh<br>T = %{y:.6f}<extra></extra>"), row=1, col=1)
    fig.add_vline(x=threshold, line_dash="dash", line_color=THRESHOLD,
                   annotation_text="Klassinen kynnys: max V(x)", row=1, col=1)
    if peaks:
        fig.add_trace(go.Scatter(x=[p["energy"] for p in peaks], y=[p["height"] for p in peaks],
            mode="markers", name="Tarkennetut resonanssit", marker=dict(color=COLORS[1], size=8),
            hovertemplate="E = %{x:.8f} Eh<br>T = %{y:.8f}<extra></extra>"), row=1, col=1)
    fig.add_trace(go.Scatter(x=x, y=potential, mode="lines", fill="tozeroy", name="Potentiaali",
        line=dict(color=POTENTIAL, width=2), fillcolor="rgba(51,65,85,.12)",
        hovertemplate="x = %{x:.3f} a₀<br>V = %{y:.5f} Eh<extra></extra>"), row=2, col=1)
    fig.update_xaxes(title_text="Energia E (Eh)", row=1, col=1)
    fig.update_xaxes(title_text="Sijainti x (a₀)", row=2, col=1)
    fig.update_yaxes(title_text="Läpäisytodennäköisyys", range=[-.03, 1.06], row=1, col=1)
    fig.update_yaxes(title_text="Potentiaalienergia (Eh)", row=2, col=1)
    fig.update_layout(height=700, hovermode="closest")
    show_plot(fig)
    st.caption(f"Todellinen kynnys max V(x) = {threshold:.4f} Eh · Hilaväli {dx:.5f} a₀. "
               "Yleiskuvan viiva on harva otos; oranssit pisteet näyttävät erikseen tarkennetut huiput.")
    if shape == "Lorentz-muoto":
        st.caption("Lorentz-muodon pitkät hännät on katkaistu laskenta-alueen reunoilla. "
                   "Mallin tulo- ja lähtöalueilla V=0.")
    if zoom_enabled:
        st.subheader("Resonanssin tarkennus")
        signature = (shape, count, height, width, separation, mass, maximum_energy)

        def bounds_for_peak(index):
            if index is None or not peaks:
                return .01, min(maximum_energy, max(.11, threshold))
            peak = peaks[index]
            radius = max(peak["width"]*6, 1e-5)
            return max(.01, peak["energy"]-radius), min(maximum_energy, peak["energy"]+radius)

        if st.session_state.get("tun_zoom_signature") != signature:
            st.session_state["tun_zoom_signature"] = signature
            st.session_state["tun_peak"] = 0 if peaks else None
            st.session_state["tun_low"], st.session_state["tun_high"] = bounds_for_peak(0 if peaks else None)

        def change_peak():
            lo, hi = bounds_for_peak(st.session_state["tun_peak"])
            st.session_state["tun_low"], st.session_state["tun_high"] = lo, hi

        choices = [*range(len(peaks)), None]
        selected_peak = st.selectbox("Tarkennettava resonanssi", choices, key="tun_peak", on_change=change_peak,
            format_func=lambda i: "Vapaasti valittu alue" if i is None else f"Resonanssi {i+1}: E = {peaks[i]['energy']:.8f} Eh")
        left, right = st.columns(2)
        with left:
            lower = st.number_input("Alueen alaenergia (Eh)", .01, maximum_energy,
                key="tun_low", step=.0001, format="%.8f")
        with right:
            upper = st.number_input("Alueen yläenergia (Eh)", .01, maximum_energy,
                key="tun_high", step=.0001, format="%.8f")
        if lower >= upper:
            st.error("Alaenergian tulee olla yläenergiaa pienempi.")
        else:
            exact_peaks = [p["energy"] for p in peaks if lower <= p["energy"] <= upper]
            fine_energies = np.unique(np.r_[np.linspace(lower, upper, 1601), exact_peaks])
            fine_values = transmission(fine_energies, potential, dx, mass)
            zoom = go.Figure(go.Scatter(x=fine_energies, y=fine_values, mode="lines", name="Tarkennettu läpäisy",
                line=dict(color=COLORS[0], width=3),
                hovertemplate="E = %{x:.10f} Eh<br>T = %{y:.8f}<extra></extra>"))
            zoom.update_layout(title="Kapean resonanssin rakenne", height=400,
                                xaxis_title="Energia E (Eh)", yaxis_title="Läpäisytodennäköisyys", yaxis_range=[-.02, 1.04])
            show_plot(zoom)
            maximum_index = int(np.argmax(fine_values))
            c1, c2 = st.columns(2)
            c1.metric("Suurin läpäisy tarkennusalueella", f"{fine_values[maximum_index]:.8f}")
            c2.metric("Huipun energia", f"{fine_energies[maximum_index]:.8f} Eh")
            st.caption("Tarkennuksessa on vähintään 1 601 energiapistettä. Pienennä aluetta, jos huippu näyttää yhä neulamaiselta.")
        if not peaks:
            st.info("Yleiskuvasta ei löytynyt tarkennettavaa huippua. Voit rajata energia-alueen käsin. "
                    "Hyvin kapea resonanssi voi jäädä yleiskuvan pisteiden väliin.")

with theory_tab:
    st.markdown(r"""
    ### Tunneloituminen ja energian säilyminen
    Klassinen hiukkanen ei läpäise estettä, jos sen energia jää potentiaalin maksimin
    alle. Kvanttimekaanisella hiukkasella voi silti olla läpäisevä aaltofunktion osa.
    **Hiukkasen energia säilyy** tässä ajasta riippumattomassa sirontamallissa.

    Esteen sisällä, kun E<V, ratkaisu on
    $\psi=Ae^{-\kappa x}+Be^{\kappa x}$ ja $\kappa=\sqrt{2m(V-E)}$.
    Äärellisessä esteessä molemmat eksponentit tarvitaan yleensä reunaehtojen
    täyttämiseen. Samanlainen evanesentti aalto esiintyy myös klassisessa optiikassa.

    ### Miksi kahden esteen läpäisy voi olla lähes yksi?
    Esteiden välissä tapahtuvat moninkertaiset heijastukset voivat interferoida
    konstruktiivisesti. Resonanssissa symmetrinen, koherentti ja elastinen rakenne
    voi läpäistä hiukkasen kokonaan, vaikka E jäisi esteen korkeuden alle.
    Resonanssiehto sisältää heijastusten vaihekulmat:
    $$2k\ell+\varphi_{r,1}+\varphi_{r,2}=2\pi n.$$
    Tässä ℓ on esteiden välinen vapaa alue, ei niiden keskipisteiden välimatka.
    Äärettömien seinien yksinkertainen seisovan aallon ehto on tämän erikoistapaus.

    ### Numeerinen malli
    Potentiaali jaetaan vakioarvoisiin soluihin. Sironta-amplitudit ketjutetaan
    sirontamatriiseilla, jotta paksujen esteiden kasvavat eksponentit eivät
    kasaudu siirtomatriisituloksi. Myös E=V:n raja-arvo käsitellään erikseen.
    Laskenta-alueen ulkopuolella V=0. Sileät esteet rajataan tälle alueelle.

    Kapea huippu voi jäädä harvan energiahilan väliin. Tarkennus etsii huipun
    lähellä olevaa energiaa ja näytteistää valitun alueen uudelleen. Se ei takaa,
    että jokainen mahdollinen resonanssi löytyisi yhdestä yleiskuvasta.
    """)

with st.expander("Kysymyksiä ja kokeiltavaa"):
    st.markdown(r"""
    1. **Klassinen raja:** Tarkastele energia-aluetta todellisen potentiaalimaksimin alapuolella.
       Millä energioilla läpäisy eroaa nollasta?
    2. **Massa:** Vertaa saman esteen läpäisyä massoilla 1 ja 5 mₑ. Miten ero riippuu energiasta?
    3. **Resonanssi:** Lataa kahden esteen esimerkki. Vertaa yleiskuvan harvaa viivaa ja
       tarkennettua huippua. Mitä olisi voinut päätellä virheellisesti pelkästä yleiskuvasta?
    4. **Rakenne:** Muuta esteiden keskipisteiden välimatkaa. Miten huippujen energiat siirtyvät?
    """)
