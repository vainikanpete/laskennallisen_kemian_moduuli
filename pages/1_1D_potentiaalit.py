import numpy as np
import plotly.graph_objects as go
import streamlit as st

from plot_style import COLORS, MUTED, POTENTIAL, THRESHOLD, initialise, preset_picker, show_plot
from qm_models import spatial_grid, solve_schrodinger_1d, solve_morse_analytical, state_moments

st.set_page_config(page_title="1D-potentiaalit", layout="wide")
st.title("Moduuli 1: 1D-potentiaalit")
st.caption("Muuta potentiaalia, ennusta energiatasojen muutos ja tarkista tulos.")
st.divider()

defaults = {"one_potential": "Ääretön kaivo", "one_mass": 2., "one_length": 10.,
            "one_spacing": .05, "one_states": 4, "one_depth": 2., "one_width": 2.,
            "one_distance": 4., "one_spring": 10., "one_morse_depth": 5.,
            "one_alpha": 1., "one_wells": 6}
initialise(defaults)
examples = {
    "Hiukkanen laatikossa": {**defaults},
    "Lähes erilliset kaivot": {"one_potential": "Kaksoiskaivo", "one_mass": 1.,
        "one_length": 16., "one_depth": 4., "one_width": 1.4, "one_distance": 5., "one_states": 6},
    "Kytkeytyneet kaivot": {"one_potential": "Kaksoiskaivo", "one_mass": 1.,
        "one_length": 16., "one_depth": 4., "one_width": 1.4, "one_distance": 2., "one_states": 6},
    "Harmoninen värähtely": {"one_potential": "Harmoninen värähtelijä", "one_mass": 2.,
        "one_length": 10., "one_spring": 10., "one_states": 6},
    "Morse: laatikon vaikutus": {"one_potential": "Morse-potentiaali (numeerinen)",
        "one_mass": 2., "one_length": 14., "one_morse_depth": 5., "one_alpha": 1., "one_states": 8},
    "Morse: sidotut tilat": {"one_potential": "Morse-potentiaali (analyyttinen)",
        "one_mass": 2., "one_length": 14., "one_morse_depth": 5., "one_alpha": 1., "one_states": 8},
    "Energiavöiden alku": {"one_potential": "Säännöllinen kidehila", "one_mass": 1.,
        "one_length": 20., "one_depth": 2., "one_wells": 6, "one_states": 18},
}
examples = {name: {**defaults, **parameters} for name, parameters in examples.items()}
preset_picker("one", examples, {
    "Lähes erilliset kaivot": "Seuraa lähekkäisiä energiatasopareja. Vaihda sitten kytkeytyneiden kaivojen esimerkkiin.",
    "Morse: laatikon vaikutus": "Kasvata laskenta-aluetta. Mitkä tasot muuttuvat eniten?",
    "Energiavöiden alku": "Usean kaivon vuorovaikutus jakaa energiatasot ryhmiksi.",
})
st.sidebar.header("Järjestelmän asetukset")
potential_type = st.sidebar.selectbox("Potentiaalin tyyppi", ["Ääretön kaivo", "Äärellinen kaivo",
    "Kaksoiskaivo", "Harmoninen värähtelijä", "Morse-potentiaali (numeerinen)",
    "Morse-potentiaali (analyyttinen)", "Säännöllinen kidehila"], key="one_potential")
mass = st.sidebar.number_input("Hiukkasen massa (mₑ)", .1, 100., key="one_mass", step=.5)
length = st.sidebar.number_input("Laskenta-alueen leveys L (a₀)", .1, 80., key="one_length", step=1.)
spacing = st.sidebar.number_input("Tavoiteltu hilaväli Δx (a₀)", .01, .5,
    key="one_spacing", step=.01, format="%.3f", help="Pienempi hilaväli tarkentaa laskentaa.")
nstates = st.sidebar.number_input("Näytettävien tilojen määrä", 1, 24, key="one_states", step=1)
try:
    x = spatial_grid(length, spacing)
except ValueError as error:
    st.error(str(error)); st.stop()
dx = x[1]-x[0]
potential = np.zeros_like(x)
depth = None
st.sidebar.header("Potentiaalin parametrit")
if potential_type in ["Äärellinen kaivo", "Kaksoiskaivo", "Säännöllinen kidehila"]:
    depth = st.sidebar.number_input("Kaivon syvyys (Eh)", .05, 20., key="one_depth", step=.1)
if potential_type in ["Äärellinen kaivo", "Kaksoiskaivo"]:
    width = st.sidebar.number_input("Yksittäisen kaivon leveys (a₀)", .1, 40., key="one_width", step=.1)
    if potential_type == "Äärellinen kaivo":
        potential = np.where(np.abs(x) <= width/2, 0., depth)
    else:
        distance = st.sidebar.number_input("Kaivojen keskipisteiden väli (a₀)", 0., 40.,
                                           key="one_distance", step=.1)
        inside = (np.abs(x-distance/2) <= width/2) | (np.abs(x+distance/2) <= width/2)
        potential = np.where(inside, 0., depth)
elif potential_type == "Harmoninen värähtelijä":
    spring = st.sidebar.number_input("Jousivakio k (Eh/a₀²)", .1, 100., key="one_spring", step=.5)
    potential = .5*spring*x**2
elif potential_type.startswith("Morse"):
    depth = st.sidebar.number_input("Dissosiaatioenergia Dₑ (Eh)", .05, 20., key="one_morse_depth", step=.1)
    alpha = st.sidebar.number_input("Kuoppaparametri α (a₀⁻¹)", .1, 3., key="one_alpha", step=.1)
    potential = depth * np.expm1(-alpha*x)**2
elif potential_type == "Säännöllinen kidehila":
    wells = st.sidebar.number_input("Kaivojen lukumäärä", 2, 16, key="one_wells", step=1)
    phase = 2*np.pi*(x-x[0])/(length/wells)
    potential = np.where(np.cos(phase) < 0, 0., depth)
st.sidebar.caption(f"Todellinen hilaväli: {dx:.5f} a₀ · Hilapisteitä: {len(x)}")

@st.cache_data(max_entries=32)
def calculate(x, potential, mass, count, kind, depth, alpha):
    if kind == "Morse-potentiaali (analyyttinen)":
        return solve_morse_analytical(x, depth, alpha, mass, count)
    return solve_schrodinger_1d(x, potential, mass, count)

with st.spinner("Ratkaistaan kvanttijärjestelmää..."):
    energies, states = calculate(x, potential, mass, nstates, potential_type, depth,
                                st.session_state["one_alpha"])
if not len(energies):
    st.info("Näillä Morse-parametreilla ei ole sidottuja tiloja. Kasvata Dₑ:tä tai massaa, tai pienennä α:aa.")

plot_tab, theory_tab, moment_tab = st.tabs(["Aaltofunktiot ja tiheydet", "Ohjeet ja teoria", "Odotusarvot"])
with plot_tab:
    display = st.radio("Näytettävä suure", ["Aaltofunktio ψ(x)", "Todennäköisyystiheys |ψ(x)|²"],
                       horizontal=True, key="one_display")
    if len(energies):
        density_mode = display.startswith("Todennäköisyys")
        values = np.abs(states)**2 if density_mode else states.copy()
        if not density_mode:
            for i in range(values.shape[1]):
                peak_index = np.argmax(np.abs(values[:, i]))
                if values[peak_index, i] < 0:
                    values[:, i] *= -1
        span = max(float(energies[-1]-potential.min()), 1.)
        scale = span*.22 / max(float(np.max(np.abs(values))), 1e-20)
        fig = go.Figure(go.Scatter(x=x, y=potential, name="Potentiaali V(x)",
                                  mode="lines", line=dict(color=POTENTIAL, width=3),
                                  hovertemplate="x = %{x:.3f} a₀<br>V = %{y:.5f} Eh<extra></extra>"))
        for i, energy in enumerate(energies):
            name = f"n = {i}, E = {energy:.4f} Eh"
            fig.add_trace(go.Scatter(x=x, y=values[:, i]*scale+energy, mode="lines", name=name,
                line=dict(color=COLORS[i % len(COLORS)], width=2.5), customdata=values[:, i],
                hovertemplate="x = %{x:.3f} a₀<br>" + ("|ψ|²" if density_mode else "ψ") +
                              " = %{customdata:.5f}<extra>"+name+"</extra>"))
            fig.add_hline(y=float(energy), line_width=1, line_dash="dot", line_color="#CBD5E1")
        upper = energies[-1]+span*.35
        if potential_type == "Ääretön kaivo":
            for edge in [x[0], x[-1]]:
                fig.add_shape(type="line", x0=edge, x1=edge, y0=0, y1=upper,
                              line=dict(color=POTENTIAL, width=4))
        if potential_type.startswith("Morse"):
            fig.add_hline(y=depth, line_dash="dash", line_color=THRESHOLD,
                          annotation_text="Dissosiaatioraja Dₑ")
        fig.update_layout(title=f"{potential_type}: {'todennäköisyystiheydet' if density_mode else 'aaltofunktiot'}",
                           xaxis_title="Sijainti x (a₀)", yaxis_title="Energia (Eh)", height=620,
                           yaxis_range=[float(potential.min()-span*.15), float(upper)])
        show_plot(fig)
        st.caption("Käyrät on siirretty oman energiatasonsa kohdalle ja skaalattu yhteisellä kertoimella. "
                   "Kohdista osoitin käyrään nähdäksesi aaltofunktion tai tiheyden arvon.")
        if potential_type.startswith("Morse"):
            st.caption(f"Kuvassa on {int(np.sum(energies < depth))} tasoa dissosiaatiorajan alapuolella.")

with theory_tab:
    st.markdown(r"""
    ### Näin tutkit mallia
    Valitse valmis esimerkki tai rakenna oma. Ennusta ensin, miten yhden parametrin
    muutos vaikuttaa. Vaihda sitten aaltofunktion ja todennäköisyystiheyden välillä.
    Aaltofunktion etumerkki näkyy amplitudissa; tiheys $|\psi|^2$ on aina epänegatiivinen.

    **Laatikko ja äärellinen kaivo.** Laatikon tasot ovat
    $E_n=\pi^2(n+1)^2/(2mL^2)$, kun perustila on $n=0$ ja $\hbar=1$.
    Äärellisessä kaivossa sidottu tila ulottuu myös klassisesti kielletylle alueelle.
    Laskenta-alueen reunoilla numeerinen aaltofunktio on nolla.

    **Kaksoiskaivo.** Kaivojen välinen vuorovaikutus hajottaa lähes samanenergiset
    tilat pareiksi. Muuta keskipisteiden välimatkaa ja seuraa energiatasojen eroa.
    Malli on symmetrinen myös silloin, kun tilat ulottuvat molempiin kaivoihin.

    **Harmoninen värähtelijä.** Tasavälisten energioiden väli on $\sqrt{k/m}$.
    Nollapiste-energia jää jäljelle perustilassakin. Tämä on sidoksen värähtelyn
    paikallinen malli tasapainoetäisyyden lähellä.

    **Morse-potentiaali.** $V(x)=D_e(1-e^{-\alpha x})^2$ kuvaa epäharmonisuutta ja
    dissosiaatiota. Tasapainokohta on tässä $x=0$. Analyyttinen malli näyttää vain
    aidot sidotut tilat, joiden kvanttiluku toteuttaa $n<\lambda-1/2$,
    $\lambda=\sqrt{2mD_e}/\alpha$. Numeerisessa laatikossa myös jatkumosta tulee
    erillisiä tasoja. Tämä tarkoituksellinen laatikkovaikutus näkyy etenkin $D_e$:n
    yläpuolella. Kasvata L:ää ja vertaa tuloksia. Molemmissa käytetään samaa
    Morse-potentiaalia ilman repulsiivisen haaran leikkausta.

    **Kidehila.** Usean kaivon vuorovaikutus muodostaa energiatasoryhmiä. Äärellisen
    ketjun ryhmät auttavat ymmärtämään makroskooppisen kiteen energiavöitä.
    """)

with moment_tab:
    st.markdown(r"""
    $\langle x\rangle$ ja $\langle p\rangle$ ovat sijainnin ja liikemäärän odotusarvot.
    $\Delta x$ ja $\Delta p$ ovat niiden keskihajonnat. Reaalisissa stationääritiloissa
    $\langle p\rangle=0$, vaikka $\langle p^2\rangle>0$.
    Atomiyksiköissä epätarkkuusperiaate on $\Delta x\Delta p\geq 1/2$.
    """)
    rows = []
    truncated = []
    for i in range(len(energies)):
        visible_norm = float(np.trapezoid(states[:, i]**2, x))
        if potential_type.endswith("(analyyttinen)") and visible_norm < .999:
            truncated.append(i); continue
        mean_x, mean_x2, mean_p, mean_p2 = state_moments(x, states[:, i])
        variance = mean_x2-mean_x**2
        product = np.sqrt(max(variance, 0)*mean_p2)
        rows.append({"Tila n": i, "Energia (Eh)": f"{energies[i]:.5f}",
                     "⟨x⟩ (a₀)": f"{mean_x:.5f}", "Δx (a₀)": f"{np.sqrt(max(variance, 0)):.5f}",
                     "⟨p⟩": f"{mean_p:.3f}", "Δp": f"{np.sqrt(mean_p2):.5f}",
                     "Δx Δp": f"{product:.6f}"})
    if rows:
        st.table(rows)
    if truncated:
        st.info("Analyyttisten tilojen " + ", ".join(map(str, truncated)) +
                " jakauma jatkuu kuvan ulkopuolelle. Kasvata L:ää odotusarvojen arviointia varten.")
    st.caption("Liikemäärämomentit arvioidaan aaltofunktion jatkuvasta sini-interpolantista. "
               "Tarkista numeerinen tarkkuus pienentämällä hilaväliä ja suurentamalla laskenta-aluetta.")

with st.expander("Kysymyksiä ja kokeiltavaa"):
    st.markdown(r"""
    1. **Kvantittuminen:** Miten tasojen erot muuttuvat massan tai laatikon leveyden kasvaessa?
    2. **Amplitudi ja tiheys:** Vaihda $\psi$:stä $|\psi|^2$:een. Mitkä solmut säilyvät? Mitä etumerkille tapahtuu?
    3. **Penetraatio:** Valitse äärellinen kaivo ja tila, jonka energia on ulkopuolista potentiaalia pienempi.
       Kuinka aaltofunktio käyttäytyy kaivon ulkopuolella?
    4. **Epätarkkuus:** Kaventaessasi laatikkoa seuraa $\Delta x$:ää ja $\Delta p$:tä.
       Tarkista harmonisen perustilan epätarkkuustulo.
    5. **Solmut:** Kuinka sisäisten solmujen määrä liittyy tilan numeroon n? Laatikon reunat eivät ole sisäisiä solmuja.
    6. **Morse ja reunaehdot:** Vertaa numeerista ja analyyttistä esimerkkiä. Kasvata L:ää ja seuraa
       erityisesti dissosiaatiorajan yläpuolisia laatikkotiloja.
    """)
