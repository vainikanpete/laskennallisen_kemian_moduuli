import numpy as np
from scipy import linalg
import plotly.graph_objects as go
import streamlit as st

from plot_style import COLORS, INK, MUTED, initialise, preset_picker, show_plot

st.set_page_config(page_title="Laajennettu Hückel", layout="wide")
st.title("Moduuli 2: Laajennettu Hückel ja MO-teoria")
st.caption("Orbitaalien sekoittuminen, polarisaatio ja elektronimiehityksen vaikutus.")
st.divider()
initialise({"eht_a": -13.6, "eht_b": -13.6, "eht_overlap": .3, "eht_constant": 1.75, "eht_electrons": 2})
preset_picker("eht", {
    "Symmetrinen sidos": {"eht_a": -13.6, "eht_b": -13.6, "eht_overlap": .3, "eht_constant": 1.75, "eht_electrons": 2},
    "Polarisoitunut sidos": {"eht_a": -13.6, "eht_b": -20., "eht_overlap": .25, "eht_constant": 1.75, "eht_electrons": 2},
    "Täysi miehitys ja hylkiminen": {"eht_a": -13.6, "eht_b": -13.6, "eht_overlap": .3, "eht_constant": 1.75, "eht_electrons": 4},
    "Kytkemättömät orbitaalit": {"eht_a": -13.6, "eht_b": -13.6, "eht_overlap": 0., "eht_constant": 1.75, "eht_electrons": 2},
})
diagram_tab, theory_tab = st.tabs(["MO-diagrammi", "Taustaa ja teoria"])
with diagram_tab:
    controls, plot = st.columns([1, 2.5])
    with controls:
        a = st.slider("Orbitaalin A energia (eV)", -25., -5., key="eht_a", step=.1)
        b = st.slider("Orbitaalin B energia (eV)", -25., -5., key="eht_b", step=.1)
        overlap = st.slider("Peittointegraali S", 0., .8, key="eht_overlap", step=.05,
            help="Tässä Wolfsberg–Helmholtz-mallissa S=0 poistaa myös resonanssikytkennän.")
        constant = st.slider("Wolfsberg–Helmholtz-vakio K", 1., 3., key="eht_constant", step=.05)
        electrons = st.slider("Elektronien määrä", 0, 4, key="eht_electrons")
        coupling = constant*overlap*(a+b)/2
        st.metric("Resonanssikytkentä Hₐᵦ", f"{coupling:.3f} eV")
    hamiltonian = np.array([[a, coupling], [coupling, b]])
    metric = np.array([[1., overlap], [overlap, 1.]])
    energies, coefficients = linalg.eigh(hamiltonian, metric)
    occupations = [min(electrons, 2), max(0, electrons-2)]
    degenerate = abs(energies[1]-energies[0]) < 1e-9
    with plot:
        fig = go.Figure()
        for centre, energy, text in [(-1., a, "Atomin A orbitaali"), (1., b, "Atomin B orbitaali")]:
            fig.add_trace(go.Scatter(x=[centre-.14, centre+.14], y=[energy, energy],
                mode="lines", line=dict(color=INK, width=4), name=text,
                hovertemplate="Energia = %{y:.4f} eV<extra>"+text+"</extra>"))
            fig.add_annotation(x=centre, y=energy, text=text, showarrow=False, yshift=-22,
                               font=dict(size=12, color=MUTED))
        for index, energy in enumerate(energies):
            color = COLORS[index]
            label = ("Alempi MO" if index == 0 else "Ylempi MO") if degenerate else (
                "Sitova MO" if index == 0 else "Hajottava MO")
            weights = coefficients[:, index]**2 / np.sum(coefficients[:, index]**2)
            for centre, old_energy, weight in zip([-1., 1.], [a, b], weights):
                fig.add_trace(go.Scatter(x=[centre*.85, np.sign(centre)*.14], y=[old_energy, energy],
                    mode="lines", line=dict(color=color, dash="dot", width=1+5*float(weight)),
                    showlegend=False, hoverinfo="skip"))
            fig.add_trace(go.Scatter(x=[-.16, .16], y=[energy, energy], mode="lines", name=label,
                line=dict(color=color, width=5), hovertemplate="Energia = %{y:.4f} eV<extra>"+label+"</extra>"))
            fig.add_annotation(x=0, y=energy, text=label, showarrow=False,
                               yshift=-23 if index == 0 else 23, font=dict(size=12, color=color))
            if occupations[index]:
                fig.add_annotation(x=0, y=energy, text="↑↓" if occupations[index] == 2 else "↑",
                                   showarrow=False, yshift=6, font=dict(size=21, color=INK))
        fig.update_layout(title="Kahden atomiorbitaalin vuorovaikutus", height=540,
                           yaxis_title="Energia (eV)", showlegend=False,
                           yaxis_range=[min(energies[0], a, b)-3, max(energies[1], a, b)+3])
        fig.update_xaxes(range=[-1.5, 1.5], showgrid=False, zeroline=False, showticklabels=False)
        show_plot(fig)
        if degenerate:
            st.info("Tasot ovat degeneroituneet. Tällöin yksittäisten ominaisvektorien AO-luonne ei ole yksikäsitteinen.")
        st.caption("Yhdistävien viivojen paksuus on karkea AO-luonteen ilmaisin. "
                   "Peittyvässä kannassa kertoimien neliöt eivät yksin ole elektronipopulaatioita.")
        st.metric("Miehitettyjen orbitaalien energiasumma", f"{np.dot(occupations, energies):.4f} eV")
        st.caption("Energiasumma on tämän EHT-mallin suure. Se ei sisällä täydellistä molekyylin potentiaalienergiaa.")

with theory_tab:
    st.markdown(r"""
    ### Mitä semiempiria tarkoittaa?
    Semiempiirinen elektronirakennemalli korvaa osan integraaleista sovitetuilla
    parametreilla. Laajennettu Hückel ottaa valenssiorbitaalit mukaan ja käyttää
    empiirisiä atomi- ja valenssitilaenergioita. Tavallinen valinta on K=1,75.

    Tässä kahden orbitaalin mallissa
    $$H_{AB}=KS\frac{\alpha_A+\alpha_B}{2},\qquad HC=SCE.$$
    Peittomatriisi normalisoi orbitaalit ehdolla $C^TSC=I$.
    Alempi MO saa yleensä enemmän luonnetta alempienergisestä AO:sta ja ylempi
    korkeaenergisemmästä AO:sta. Symmetrisessä tapauksessa sekoittuminen on tasasuuruista.

    **S=0 tarkoittaa tässä kytkemätöntä rajaa**, koska myös H_AB on verrannollinen S:ään.
    Tavallisessa ortogonaalisessa Hückel-mallissa peitto voidaan asettaa nollaksi
    säilyttäen erillinen, äärellinen resonanssikytkentä.

    ### Täysien orbitaalien vuorovaikutus
    Kun AO-energiat ovat samat, S>0 ja K>1, hajottava taso nousee enemmän kuin sitova
    laskee. Kahdella elektronilla vain alempi taso täyttyy. Neljällä elektronilla
    myös ylempi täyttyy ja energiasumman käyttäytyminen muuttuu. Tämä havainnollistaa
    täysien orbitaalien lyhyen etäisyyden hylkimistä. Esimerkiksi He₂:n täydellinen
    vuorovaikutuspotentiaali tarvitsee tämän lisäksi muut vuorovaikutustermit.

    Jos AO-energiat ovat samat ja K=1, H=αS ja tasot ovat degeneroituneet.
    Tasaväkiset kertoimet eivät yksin määritä sidoksen prosentuaalista kovalenttisuutta.
    """)

with st.expander("Kysymyksiä ja kokeiltavaa"):
    st.markdown(r"""
    1. **Symmetria:** Lataa symmetrinen sidos ja muuta molempia AO-energioita saman verran.
       Mitkä piirteet pysyvät samoina?
    2. **Polarisaatio:** Laske vain B:n energiaa. Miten alempi ja ylempi MO muuttuvat?
    3. **Miehitys:** Lataa täyden miehityksen esimerkki. Kasvata S:ää ja seuraa
       neljän elektronin energiasummaa. Vertaa kahteen elektroniin.
    4. **Mallin rajat:** Tutki erikseen S=0 ja K=1. Miksi molemmat voivat hävittää
       tasojen eron symmetrisessä tapauksessa, vaikka ne tarkoittavat eri asioita?
    """)
