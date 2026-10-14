import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from rdkit import Chem
import streamlit as st

from hf_engine import geometry_from_smiles, BOHR_ANGSTROM
from plot_style import COLORS, MUTED, initialise, preset_picker, show_plot
from qm_models import valence_eht, calc_1d_monatomic, calc_1d_diatomic, calc_2d_square

st.set_page_config(page_title="Walsh ja kiinteä olomuoto", layout="wide")
st.title("Moduuli 6: Walsh-diagrammit ja kiinteä olomuoto")
st.caption("Yhdistä geometrian muutos orbitaaleihin ja yksittäiset orbitaalit energiavöihin.")
st.divider()
walsh_tab, solid_tab = st.tabs(["Walsh-diagrammit", "Kiinteän olomuodon kemia"])
initialise({"walsh_smiles": "O", "walsh_start": 90., "walsh_end": 180., "walsh_points": 40,
            "walsh_constant": 1.75, "solid_type": "1D: yhden atomin ketju", "solid_alpha": -5.,
            "solid_beta": -2., "solid_a1": -5., "solid_a2": -5., "solid_b1": -2., "solid_b2": -2.})

@st.cache_data(max_entries=16)
def molecule_and_angles(smiles):
    geometry = geometry_from_smiles(smiles)
    molecule = Chem.AddHs(Chem.MolFromSmiles(smiles))
    conformer = Chem.Conformer(len(geometry["atoms"]))
    for index, coord in enumerate(geometry["coords"]*BOHR_ANGSTROM):
        conformer.SetAtomPosition(index, tuple(float(c) for c in coord))
    molecule.AddConformer(conformer, assignId=True)
    angles = []
    for atom in molecule.GetAtoms():
        neighbours = [a.GetIdx() for a in atom.GetNeighbors()]
        for i in range(len(neighbours)):
            for j in range(i+1, len(neighbours)):
                angles.append((neighbours[i], atom.GetIdx(), neighbours[j]))
    return molecule, geometry, angles

@st.cache_data(max_entries=24)
def angle_scan(smiles, atom_indices, start, end, count, constant):
    original, geometry, _ = molecule_and_angles(smiles)
    original_angle = Chem.rdMolTransforms.GetAngleDeg(original.GetConformer(), *atom_indices)
    scan_angles = np.linspace(start, end, count)
    eigenvalues = []
    for angle in scan_angles:
        molecule = Chem.Mol(original)
        conformer = molecule.GetConformer()
        Chem.rdMolTransforms.SetAngleDeg(conformer, *atom_indices, float(angle))
        coords = np.asarray(conformer.GetPositions())/BOHR_ANGSTROM
        energies, _, _ = valence_eht(geometry["atoms"], coords, constant)
        eigenvalues.append(energies)
    valence = sum({1: 1, 6: 4, 7: 5, 8: 6}[int(z)] for z in geometry["atoms"])-geometry["formal_charge"]
    return scan_angles, np.asarray(eigenvalues), original_angle, valence

with walsh_tab:
    st.header("Geometrian vaikutus molekyyliorbitaaleihin")
    with st.expander("Miten Walsh-diagrammia luetaan?", expanded=True):
        st.markdown(r"""
        Walsh-diagrammi näyttää, miten orbitaalien energiat muuttuvat sidoskulman mukana.
        Taivutus muuttaa orbitaalien peittymistä ja symmetriaa. Samassa symmetriassa olevat
        funktiot voivat sekoittua ja muuttaa sekä miehitettyjä että tyhjiä tasoja.

        Tässä käytetään EHT-mallia ja normalisoituja valenssi-2s/2p-funktioita
        STO-3G-sovituksesta; vedyllä on 1s-funktio. Sisäkuoren 1s-funktioita ei käytetä
        valenssi-2s-funktioiden tilalla. Geometrian muut vapausasteet jäädytetään.

        **Orbitaalikuvaaja auttaa tulkitsemaan geometrian vaikutusta.** Tämän
        Gauss-kantaan sovitetun EHT-mallin avulla ei luvata oikeita tasapainokulmia.
        Pelkkä HOMO ei määrää kokonaisenergiaa. EHT:n yksinkertaisessa energiatulkinnassa
        kaikki miehitetyt tasot vaikuttavat; aidon HF:n energia sisältää lisäksi
        elektronivuorovaikutuksen kaksoislaskennan korjauksen ja ydinrepulsion.

        Katkoviiva merkitsee MMFF/UFF-voimakenttägeometrian kulmaa. Se on erillisen
        mallin vertailuarvo. Käyrät järjestetään energian mukaan jokaisessa pisteessä,
        joten sama väri ei takaa saman orbitaaliluonteen säilymistä risteämisissä.
        """)
    inputs, plot = st.columns([1, 2])
    with inputs:
        preset_picker("walsh", {
            "Veden taivutus": {"walsh_smiles": "O", "walsh_start": 90., "walsh_end": 180., "walsh_constant": 1.75},
            "Hiilidioksidin taivutus": {"walsh_smiles": "O=C=O", "walsh_start": 90., "walsh_end": 180., "walsh_constant": 1.75},
            "Ammoniakin sidoskulma": {"walsh_smiles": "N", "walsh_start": 80., "walsh_end": 120., "walsh_constant": 1.75},
        }, container=inputs)
        smiles = st.text_input("Molekyylin SMILES (H, C, N, O)", key="walsh_smiles")
        molecule, geometry, available_angles = None, None, []
        try:
            molecule, geometry, available_angles = molecule_and_angles(smiles)
        except (ValueError, RuntimeError) as error:
            st.error(str(error))
        symbols = [a.GetSymbol() for a in molecule.GetAtoms()] if molecule else []
        if available_angles:
            selected = st.selectbox("Muutettava sidoskulma", available_angles,
                format_func=lambda ids: " – ".join(f"{symbols[i]}{i+1}" for i in ids), key="walsh_angle")
        else:
            selected = None
            if molecule:
                st.info("Molekyylillä ei ole muutettavaa kolmen atomin sidoskulmaa.")
        start = st.number_input("Alkukulma (°)", 5., 179.9, key="walsh_start", step=1.)
        end = st.number_input("Loppukulma (°)", 5., 180., key="walsh_end", step=1.)
        points = st.slider("Mittapisteiden määrä", 10, 100, key="walsh_points")
        constant = st.slider("Wolfsberg–Helmholtz-vakio K", 1., 2.5, key="walsh_constant", step=.05)
        signature = (smiles, selected, start, end, points, constant)
        if st.button("Laske Walsh-diagrammi", type="primary", disabled=selected is None):
            st.session_state.pop("walsh_result", None)
            if start >= end:
                st.error("Alkukulman tulee olla loppukulmaa pienempi.")
            else:
                try:
                    with st.spinner("Lasketaan valenssiorbitaalien energiatasoja..."):
                        result = angle_scan(smiles, selected, start, end, points, constant)
                    st.session_state["walsh_result"] = (signature, result)
                except (ValueError, RuntimeError, np.linalg.LinAlgError) as error:
                    st.error(f"Kulman tarkastelu epäonnistui: {error}")
    with plot:
        stored = st.session_state.get("walsh_result")
        if stored and stored[0] == signature:
            angles, levels, original_angle, valence_electrons = stored[1]
            fig = go.Figure()
            for band in range(levels.shape[1]):
                occupied = band < (valence_electrons+1)//2
                fig.add_trace(go.Scatter(x=angles, y=levels[:, band], mode="lines",
                    name=f"MO {band+1}" + (" · miehitetty" if occupied else " · tyhjä"),
                    line=dict(color=COLORS[band % len(COLORS)], width=2.5,
                              dash="solid" if occupied else "dash"),
                    hovertemplate="Kulma = %{x:.2f}°<br>Energia = %{y:.4f} eV<extra>MO "+str(band+1)+"</extra>"))
            fig.add_vline(x=float(original_angle), line_width=2, line_dash="dot", line_color=MUTED,
                           annotation_text="Voimakenttägeometrian kulma")
            fig.update_layout(title="Valenssiorbitaalien Walsh-diagrammi", height=600,
                                xaxis_title="Sidoskulma (°)", yaxis_title="EHT-orbitaalienergia (eV)")
            show_plot(fig)
            st.caption(f"Valenssielektroneja: {valence_electrons}. Katkoviivalla piirretyt MO-käyrät ovat miehittämättömiä.")
        else:
            st.info("Valitse molekyyli ja kulma, ja laske diagrammi. Vertaa usean orbitaalin muutosta.")

with solid_tab:
    st.header("Molekyyleistä energiavöihin")
    controls, plot = st.columns([1, 2])
    with controls:
        preset_picker("solid", {
            "Yksiulotteinen ketju": {"solid_type": "1D: yhden atomin ketju", "solid_alpha": -5., "solid_beta": -2.},
            "Tasavahvat sidokset": {"solid_type": "1D: kahden atomin solu", "solid_a1": -5., "solid_a2": -5., "solid_b1": -2., "solid_b2": -2.},
            "Vuorottelevat sidokset": {"solid_type": "1D: kahden atomin solu", "solid_a1": -5., "solid_a2": -5., "solid_b1": -2., "solid_b2": -1.5},
            "Eri atomien energiatasot": {"solid_type": "1D: kahden atomin solu", "solid_a1": -5., "solid_a2": -7., "solid_b1": -2., "solid_b2": -2.},
            "Kaksiulotteinen neliöhila": {"solid_type": "2D: neliöhila", "solid_alpha": -5., "solid_beta": -2.},
        }, container=controls)
        lattice = st.selectbox("Hilamalli", ["1D: yhden atomin ketju", "1D: kahden atomin solu", "2D: neliöhila"], key="solid_type")
        if lattice == "1D: kahden atomin solu":
            a1 = st.slider("Atomin 1 energia α₁ (eV)", -10., 0., key="solid_a1", step=.5)
            a2 = st.slider("Atomin 2 energia α₂ (eV)", -10., 0., key="solid_a2", step=.5)
            b1 = st.slider("Kytkentä β₁ (eV)", -5., 0., key="solid_b1", step=.1)
            b2 = st.slider("Kytkentä β₂ (eV)", -5., 0., key="solid_b2", step=.1)
        else:
            alpha = st.slider("Atomin energia α (eV)", -10., 0., key="solid_alpha", step=.5)
            beta = st.slider("Resonanssikytkentä β (eV)", -5., 0., key="solid_beta", step=.1)
    fig = make_subplots(rows=1, cols=2, shared_yaxes=True, column_widths=[.7, .3],
                         horizontal_spacing=.08, subplot_titles=("Vyörakenne E(k)", "Normalisoitu tilatiheys"))
    if lattice == "1D: yhden atomin ketju":
        k, band, dos_energy, dos = calc_1d_monatomic(alpha, beta)
        fig.add_trace(go.Scatter(x=k, y=band, mode="lines", name="Energiavyö", line=dict(color=COLORS[0], width=3)), row=1, col=1)
        fermi = alpha
        fig.update_xaxes(tickvals=[-np.pi, 0, np.pi], ticktext=["−π/a", "0", "π/a"], row=1, col=1)
    elif lattice == "1D: kahden atomin solu":
        k, lower, upper, dos_energy, dos = calc_1d_diatomic(a1, a2, b1, b2)
        fig.add_trace(go.Scatter(x=k, y=lower, mode="lines", name="Alempi vyö", line=dict(color=COLORS[0], width=3)), row=1, col=1)
        fig.add_trace(go.Scatter(x=k, y=upper, mode="lines", name="Ylempi vyö", line=dict(color=COLORS[1], width=3)), row=1, col=1)
        fermi = (a1+a2)/2
        fig.update_xaxes(tickvals=[-np.pi, 0, np.pi], ticktext=["−π/a", "0", "π/a"], row=1, col=1)
        controls.metric("Vyöaukko", f"{upper[0]-lower[0]:.4f} eV")
    else:
        path, band, ticks, labels, dos_energy, dos = calc_2d_square(alpha, beta)
        fig.add_trace(go.Scatter(x=path, y=band, mode="lines", name="Energiavyö", line=dict(color=COLORS[0], width=3)), row=1, col=1)
        fig.update_xaxes(tickvals=ticks, ticktext=["Γ", "X", "M", "Γ"], row=1, col=1)
        fermi = alpha
    fig.add_trace(go.Scatter(x=dos, y=dos_energy, mode="lines", fill="tozerox", name="Tilatiheys",
        line=dict(color=COLORS[2], width=2), fillcolor="rgba(5,150,105,.14)"), row=1, col=2)
    fig.add_hline(y=float(fermi), line_dash="dot", line_color=MUTED, row=1, col=1)
    fig.update_xaxes(title_text="Aaltovektori k" if lattice.startswith("1D") else "Reitti k-avaruudessa", row=1, col=1)
    fig.update_xaxes(title_text="Tilatiheys (eV⁻¹)", row=1, col=2)
    fig.update_yaxes(title_text="Energia (eV)", row=1, col=1)
    fig.update_layout(height=540, hovermode="closest")
    with plot:
        show_plot(fig)
        st.caption("Pisteviiva on puolitäytön vertailutaso. Mallissa on yksi orbitaali atomia kohti. "
                   "Tilatiheyden pinta-ala on normalisoitu yhteen; histogrammi esittää singulariteetit äärellisinä huippuina.")
    with st.expander("Taustaa ja kysymyksiä", expanded=True):
        st.markdown(r"""
        **Orbitaaleista vöihin.** Kun mallissa on yksi AO atomia kohti, N atomia antaa
        N MO:ta. Makroskooppisen kiteen tasot muodostavat lähes jatkuvia energiavöitä.
        Tämä lähimpien naapureiden tiukan sidoksen malli käyttää samaa matriisialgebraa
        kuin yksinkertainen Hückel-malli jaksollisilla reunaehdoilla.

        1. **1D-tilatiheys:** Vyön reunoilla $dE/dk=0$ ja tilatiheys kasvaa
           kääntäen verrannollisesti etäisyyden neliöjuureen reunasta. Singulariteetti on integroituva.
        2. **2D-neliöhila:** Logaritminen van Hove -singulariteetti on **vyön keskellä**,
           missä dispersiossa on satulapisteitä. Vyön reunoilla on äärellinen askelmainen alku.
           Vertaa kuvaajaa yksiulotteiseen ketjuun.
        3. **Vuorottelevat sidokset:** Valitse kahden atomin solu, samat α-arvot ja ensin samat β-arvot.
           Muuta sitten β₂:ta. Miten vyöaukko syntyy? Puolitäytöllä alempi vyö täyttyy.
           Tämä näyttää pakotetun dimerisaation vaikutuksen. Spontaanin Peierlsin vääristymän
           osoittaminen vaatisi myös elektronisen energian ja hilan muodonmuutosenergian vertailun.
        4. **Erilaiset atomit:** Pidä β-arvot samoina ja muuta α₁:n sekä α₂:n eroa.
           Vertaa vyöaukon syntyä sidosten vuorotteluun.
        """)
