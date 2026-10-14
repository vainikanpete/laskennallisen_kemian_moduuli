import tempfile
from pathlib import Path

import numpy as np
import plotly.graph_objects as go
import py3Dmol
import streamlit as st
from stmol import showmol
from plot_style import COLORS, initialise, orbital_energy_figure, preset_picker, show_plot

st.set_page_config(page_title="Hartree-Fock", layout="wide")

try:
    from hf_engine import geometry_from_smiles, orbital_cube, run_rhf
except ImportError:
    st.error("HF-laskentakirjasto puuttuu. Tarkista sovelluksen riippuvuuksien asennus.")
    st.stop()

try:
    from xyzrender import load, render, render_gif
    XYZRENDER_AVAILABLE = True
except ImportError:
    XYZRENDER_AVAILABLE = False

ASSETS = Path(__file__).resolve().parents[1]


@st.cache_data(max_entries=32)
def cached_geometry(smiles):
    return geometry_from_smiles(smiles)


@st.cache_data(max_entries=32)
def cached_rhf(atoms, coords, charge, max_iter, mix, use_diis):
    return run_rhf(atoms, coords, charge, max_iter, mix, use_diis)


@st.cache_data(max_entries=16)
def cached_cube(result, orbital_index):
    return orbital_cube(result, orbital_index)


st.title("Moduuli 3: Hartree-Fock (RHF)")
st.caption("RHF/STO-3G: aidot yhden ja kahden elektronin integraalit ja 3D-orbitaalit")
st.divider()
tab_laskenta, tab_historia, tab_teoria, tab_smiles = st.tabs(
    ["Laskenta & Visualisointi", "Historia", "Ohjeita & Teoriaa", "Mikä ihmeen SMILES?"]
)

with tab_smiles:
    st.markdown(r"""
    ### Mikä on SMILES?
    SMILES kuvaa molekyylin atomit ja sidokset tekstinä. Se ei yksin määritä
    tarkkoja 3D-koordinaatteja. RDKit rakentaa tässä yhden toistettavan konformeerin,
    lisää vedyt ja minimoi geometrian MMFF-voimakentällä (vetymolekyylille UFF).
    Tämä geometria syötetään HF-laskentaan. Geometriaa ei optimoida HF-menetelmällä.

    * **Atomit:** `C`, `N` ja `O` tarkoittavat hiiltä, typpeä ja happea.
    * **Vedyt:** Normaali valenssi täydentyy automaattisesti: `O` on vesi,
      `N` ammoniakki ja `C` metaani.
    * **Sidokset:** Yksinkertainen sidos on oletus, `=` kaksoissidos ja `#` kolmoissidos.
      Hiilidioksidi on `O=C=O` ja vetymolekyyli `[H][H]`.
    * **Haarat ja renkaat:** Isobutaani on `CC(C)C` ja bentseeni `c1ccccc1`.

    Sovellus ehdottaa SMILES-merkkijonon formaalivarausta. Voit muuttaa varauksen
    laskentaa varten. RHF-moduuli käyttää suljetun kuoren singlettiä ja tukee H-, C-,
    N- ja O-atomeja. Pariton elektronimäärä tarvitsee avoimen kuoren menetelmän.
    """)

with tab_historia:
    st.markdown(r"""
    ### Laskennallisen kemian ja Hartree-Fock -menetelmän historia

    **1926: Schrödingerin yhtälö ja fysiikan täydellistyminen**
    Kun Erwin Schrödinger julkaisi aaltoyhtälönsä, kvanttimekaniikka sai matemaattisen muodon, jolla voitiin kuvata atomien ja molekyylien rakennetta. Paul Dirac saneli pian tämän jälkeen:
    *"Ne fysiikan peruslait, jotka vaaditaan suuren osan fysiikkaa ja koko kemian matemaattiseen teoriaan, ovat nyt täysin tunnettuja. Ainoa ongelma on, että näiden lakien soveltaminen johtaa yhtälöihin, jotka ovat aivan liian monimutkaisia ratkaistavaksi."*
    Vetyä muistuttavat yhden elektronin atomit voidaan ratkaista analyyttisesti. Monielektronisten molekyylien elektronirakenne vaatii käytännössä numeerisia approksimaatioita.
    """)
    st.image(
        str(ASSETS / "qmdirac.png"), 
        caption="Suoraan hevosen suusta: Quantum mechanics of many-electron systems -julkaisua pääsee lukemaan Royal Societyn portaalista.", 
        width=800
        )

    st.markdown(r"""
    **1927–1930: Hartree, Fock ja Slater**
    Englantilainen Douglas Hartree esitti vuonna 1927 menetelmän monielektronijärjestelmille, jota hän kutsui *itseytyvän kentän* (Self-Consistent Field, SCF) menetelmäksi. Siinä jokainen elektroni nähtiin liikkuvan muiden elektronien muodostamassa keskimääräisessä kentässä. Hartreen malli ei kuitenkaan noudattanut Paulin kieltosääntöä (elektronien antisymmetriaa).
""")

    st.image(
        str(ASSETS / "SC.jpg"), 
        caption="Luonnontieteiden kovin ryhmäkuva. Solvayn konferenssissa 1927 koitettiin päästä yhteisymmärrykseen kvanttimekaniikan perusteista ja sovittamisesta klassisen mekaniikan kanssa.", 
        width=800
        )

    st.markdown(r"""    
    Vuonna 1930 venäläinen Vladimir Fock ja yhdysvaltalainen John C. Slater korjasivat tämän ongelman toisistaan riippumatta. Slater esitteli determinantin (Slaterin determinantti), jolla aaltofunktio saatiin pakotettua antisymmetriseksi. Fock yhdisti tämän Hartreen SCF-menetelmään. Syntyi **Hartree-Fock -teoria**.

    **1951: Roothaan ja Hall: Tietokoneiden aikakausi**
    Hartree-Fock -teoria oli pitkään vain teoreettinen työkalu, koska differentiaaliyhtälöiden ratkaiseminen monimutkaisille molekyyleille oli käsin mahdotonta. Clemens Roothaan ja George Hall keksivät toisistaan riippumatta, että kun aaltofunktiot jaetaan tunnettuihin kantafunktioihin (LCAO-approksimaatio), jatkuva Schrödingerin yhtälö muuttuu lineaarialgebran matriisiyhtälöksi ($FC = SCE$). Matriisien ratkaiseminen oli juuri sitä, missä uudet elektroniset tietokoneet olivat erinomaisia.

    **1970-luku: John Pople ja Gaussian**
    Tietokone-avusteinen kvanttikemia alkoi toden teolla 1960/70-luvulla, kun John Pople (Nobel-palkinto 1998) ja hänen tutkimusryhmänsä kehittivät *Gaussian*-ohjelmiston. Gaussin kantafunktiot yksinkertaistivat monikeskisten integraalien laskentaa huomattavasti. Hartree-Fock-laskennasta tuli laskennallisen kemian rutiinityökalu.
    """)


with tab_teoria:
    st.markdown(r"""
    ### Mitä Hartree-Fock-moottori tekee?

    **1. Kiinteä geometria ja Born–Oppenheimer-approksimaatio**
    Elektronirakenne ratkaistaan annetuilla ydinten koordinaateilla. Näytetty
    kokonaisenergia on elektroninen energia sekä ytimien välinen repulsio.
    Ydinten värähtelyenergia ja lämpötilan vaikutukset eivät sisälly siihen.

    **2. LCAO ja STO-3G-kantajoukko**
    Molekyyliorbitaalit rakennetaan atomikeskisistä kantafunktioista:
    $$\psi_i = \sum_\mu C_{\mu i}\phi_\mu.$$
    STO-3G on minimaalinen kantajoukko. C-, N- ja O-atomeilla on ydin-1s,
    valenssi-2s ja kolme 2p-funktiota; vedyllä yksi 1s-funktio. Kukin supistettu
    funktio muodostuu kolmesta Gaussin funktiosta. S- ja p-funktioilla on omat
    supistuskertoimensa.

    **3. Aidot integraalit ja Fock-matriisi**
    PySCF laskee peittomatriisin, kineettisen energian, ytimen vetovoiman ja
    elektronien repulsiointegraalit tästä samasta kantajoukosta. P-orbitaalien
    kulmariippuvuus sisältyy integraaleihin.
    $$F_{\mu\nu}=H^{core}_{\mu\nu}+\sum_{\lambda\sigma}P_{\lambda\sigma}
    \left[(\mu\nu|\lambda\sigma)-\frac12(\mu\lambda|\nu\sigma)\right].$$
    Coulomb-termi kuvaa elektronien repulsiota. Vaihtotermi seuraa
    antisymmetrisestä Slaterin determinantista.

    **4. Itseytyvä kenttä ja tiheyden sekoitus**
    Ratkaisemme Roothaan–Hall-yhtälön $FC=SCE$. Miehitetyt orbitaalit antavat
    uuden tiheyden $P_{uusi}$, jota sekoitetaan edelliseen tiheyteen:
    $$P_{seuraava}=(1-mix)P_{edellinen}+mix\,P_{uusi}.$$
    Alkutiheys sisältää oikean määrän elektroneja, ja sekoitus säilyttää määrän.
    Energia lasketaan aina saman tiheyden ja siitä rakennetun Fock-matriisin avulla:
    $$E=\frac12\sum_{\mu\nu}P_{\mu\nu}
    (H^{core}_{\mu\nu}+F_{\mu\nu})+E_{ydinrepulsio}.$$
    Suppeneminen tarkistetaan energian muutoksesta, tiheyden itsekonsistenssista
    ja SCF-yhtälön jäännöksestä. Pelkkä iteraatiorajan saavuttaminen ei tarkoita
    suppenemista. DIIS käyttää aiempia Fock-matriiseja suppenemisen nopeuttamiseen.

    **5. Mitä tuloksista voi päätellä?**
    Tämä on aito suljetun kuoren RHF/STO-3G-laskenta. HF sisältää vaihtovuorovaikutuksen,
    mutta elektronien korreloitu liike yhden determinantin kuvauksen ulkopuolella
    puuttuu. Minimaalinen kantajoukko rajoittaa etenkin virtuaalisten orbitaalien
    ja pienten energiaerojen tarkkuutta. SCF:n suppeneminen antaa itsekonsistentin
    ratkaisun; se ei yksin takaa kaikkien mahdollisten ratkaisujen alinta energiaa.

    HOMO–LUMO-väli on **orbitaalienergioiden erotus**. Absorptioenergiaa varten
    tarvitaan viritystilan laskenta, esimerkiksi TDHF. Positiivinen virtuaalisen
    orbitaalin energia voi esiintyä aidossa HF-laskennassa.
    """)

with tab_laskenta:
    initialise({"hf_smiles": "O", "hf_max_iter": 100, "hf_mix": .5, "hf_diis": True})
    col1, col2 = st.columns([1, 2])
    geometry = None
    geometry_error = None
    with col1:
        st.subheader("Järjestelmän asetukset")
        examples = {}
        for name, molecule in [("Veden HOMO ja LUMO", "O"), ("Etanoli", "CCO"),
                               ("Dimetyylieetteri", "COC"), ("Eteeni", "C=C"),
                               ("Butadieeni", "C=CC=C"), ("Heksatrieeni", "C=CC=CC=C")]:
            examples[name] = {"hf_smiles": molecule, "hf_charge": 0, "hf_max_iter": 100,
                              "hf_mix": .5, "hf_diis": True}
        examples["Vesi: hidas tiheyden sekoitus"] = {
            "hf_smiles": "O", "hf_charge": 0, "hf_max_iter": 300, "hf_mix": .1, "hf_diis": False}
        preset_picker("hf", examples, {
            "Vesi: hidas tiheyden sekoitus": "Vertaa sekoituksen arvoja 0,1 ja 1,0 ilman DIIS-menetelmää."
        }, container=col1)
        smiles = st.text_input(
            "Syötä molekyylin SMILES", key="hf_smiles",
            help="Kokeile: O (vesi), C (metaani), N (ammoniakki), [H][H] (vetymolekyyli).",
        )
        if smiles:
            try:
                geometry = cached_geometry(smiles)
            except (ValueError, RuntimeError) as error:
                geometry_error = str(error)
        if st.session_state.get("hf_charge_smiles") != smiles:
            st.session_state["hf_charge_smiles"] = smiles
            st.session_state["hf_charge"] = geometry["formal_charge"] if geometry else 0
        charge = int(st.number_input("Molekyylin varaus", step=1, key="hf_charge"))
        st.markdown("---")
        st.write("SCF-parametrit")
        max_iter = int(st.number_input("Iteraatioiden enimmäismäärä", 10, 500, key="hf_max_iter", step=10))
        mixing = st.slider(
            "Tiheyden sekoitus (mix)", 0.1, 1.0, key="hf_mix", step=0.1,
            help="Uuden tiheyden osuus seuraavalla kierroksella. Pieni arvo vaimentaa "
                 "muutoksia ja usein hidastaa suppenemista; se ei takaa suppenemista.",
        )
        use_diis = st.checkbox(
            "Nopeuta suppenemista DIIS-menetelmällä", key="hf_diis",
            help="Poista käytöstä, kun haluat tutkia pelkän tiheyden sekoituksen vaikutusta.",
        )
        st.caption("RHF/STO-3G · suljetun kuoren singletti · yksi voimakenttägeometria")
    signature = (smiles, charge, max_iter, mixing, use_diis)
    with col2:
        if geometry_error:
            st.error(geometry_error)
        elif geometry:
            nelec = int(np.sum(geometry["atoms"])) - charge
            st.write(f"**Atomien määrä:** {len(geometry['atoms'])} | **Elektronien määrä:** {nelec}")
            st.caption(f"Geometria: {geometry['geometry_method']}, sama konformeeri jokaisella laskukerralla.")
            preview = py3Dmol.view(width=600, height=280)
            preview.addModel(geometry["xyz"], "xyz")
            preview.setStyle({"stick": {}, "sphere": {"scale": 0.25}})
            preview.zoomTo()
            showmol(preview, height=280, width=600)
            invalid_count = nelec <= 0 or nelec % 2 != 0
            if invalid_count:
                st.error("RHF tarvitsee positiivisen, parillisen elektronimäärän. "
                         "Avoimen kuoren systeemi tarvitsee toisen menetelmän.")
            if st.button("Suu suppuun ja laske!", type="primary", disabled=invalid_count):
                st.session_state.pop("hf_results", None)
                try:
                    with st.spinner("Lasketaan STO-3G-integraalit ja iteroidaan SCF..."):
                        result = cached_rhf(geometry["atoms"], geometry["coords"], charge,
                                            max_iter, mixing, use_diis)
                    result["signature"] = signature
                    result["smiles"] = smiles
                    result["geometry_method"] = geometry["geometry_method"]
                    st.session_state["hf_results"] = result
                except (ValueError, RuntimeError, np.linalg.LinAlgError) as error:
                    st.error(f"Laskenta epäonnistui: {error}")

    res = st.session_state.get("hf_results")
    if res and res.get("signature") != signature:
        st.info("Asetuksia on muutettu. Paina laskentapainiketta nähdäksesi uuden laskun.")
        res = None
    if res:
        st.markdown("---")
        if res["converged"]:
            st.success(f"SCF suppeni {res['iterations']} iteraatiossa.")
        else:
            st.warning(f"SCF ei suppentunut {res['iterations']} iteraatiossa. "
                       "Kasvata iteraatiorajaa tai muuta sekoitusta/DIIS-asetusta. "
                       "Näytetyt arvot ovat välituloksia.")
        st.subheader("SCF:n suppeneminen ja järjestelmän energia")
        metric1, metric2 = st.columns(2)
        with metric1:
            st.metric("Lopullinen RHF-kokonaisenergia" if res["converged"] else "Viimeisen iteraation energia",
                      f"{res['energy']:.9f} Eh",
                      help="Elektroninen energia sekä ytimien välinen repulsio kiinteässä geometriassa.")
        with metric2:
            if res["lumo_idx"] is not None:
                gap = res["evals"][res["lumo_idx"]] - res["evals"][res["homo_idx"]]
                st.metric("HOMO–LUMO-väli" if res["converged"] else "HOMO–LUMO-väli (välitulos)",
                          f"{gap:.6f} Eh", help="Orbitaalienergioiden erotus; ei suoraan absorptioenergia.")
        st.caption(f"Elektroneja: {res['N_elec']} · Kantafunktioita: {res['n_basis']} · "
                   f"Tr(PS) = {res['history'][-1]['electron_count']:.8f}")
        fig_scf = go.Figure(go.Scatter(
            x=[row["cycle"] for row in res["history"]],
            y=[row["energy"] for row in res["history"]],
            mode="lines+markers", name="Kokonaisenergia",
            marker=dict(size=7, color=COLORS[0]), line=dict(color=COLORS[0]),
        ))
        fig_scf.update_layout(xaxis_title="SCF-iteraatiokierros (0 = alkutiheys)",
                              yaxis_title="Kokonaisenergia (Eh)", height=400, hovermode="x unified")
        show_plot(fig_scf)
        with st.expander("Suppenemisen tarkistus"):
            last = res["history"][-1]
            st.write(f"Viimeinen energian muutos: {last['delta_energy']:.3e} Eh; "
                     f"tiheyden ero itsekonsistenttiin tiheyteen: {last['density_rms']:.3e}; "
                     f"SCF-jäännös: {last['residual_rms']:.3e}.")
            st.caption("Rajat: |ΔE| < 10⁻⁹ Eh; tiheyden ero ja SCF-jäännös < 10⁻⁷.")

        st.markdown("---")
        st.subheader("Energiatasot ja orbitaalien 3D-näkymä")
        homo, lumo = res["homo_idx"], res["lumo_idx"]
        order = [homo] + ([lumo] if lumo is not None else [])
        order += [index for index in range(res["n_basis"]) if index not in order]
        labels = {}
        for index in order:
            name = "HOMO" if index == homo else "LUMO" if index == lumo else "Orbitaali"
            labels[index] = f"{name} {index + 1} (E={res['evals'][index]:.6f} Eh)"
        if st.session_state.get("hf_orbital_signature") != signature:
            st.session_state["hf_orbital_signature"] = signature
            st.session_state["hf_orbital_index"] = homo
        selected_index = st.selectbox("Valitse piirrettävä orbitaali", order,
                                     format_func=labels.get, key="hf_orbital_index")
        include_core = st.checkbox("Näytä myös sisäkuoren tasot", key="hf_include_core")
        diagram_key = f"hf_mo_diagram_{signature}"

        def select_level():
            event = st.session_state.get(diagram_key, {})
            points = event.get("selection", {}).get("points", [])
            if points and points[-1].get("customdata"):
                index = int(points[-1]["customdata"][0])
                if 0 <= index < res["n_basis"]:
                    st.session_state["hf_orbital_index"] = index

        show_plot(orbital_energy_figure(res, selected_index, include_core),
                  key=diagram_key, on_select=select_level, selection_mode="points")
        st.caption("Valitse energiataso napsauttamalla viivaa tai käyttämällä valikkoa. "
                   "Violetti taso vastaa alla näkyvää orbitaalia; nuolet kuvaavat miehitystä. "
                   "Oletusnäkymä rajautuu HOMO:n ja LUMO:n ympärille.")
        st.write("Pyöritä 3D-mallia hiirellä ja zoomaa rullalla. Sininen ja punainen kuvaavat "
                 "aaltofunktion eri etumerkkejä; isopinta näyttää valitun amplitudin.")
        controls, viewer = st.columns([1, 2])
        with controls:
            isovalue = st.slider("Isopinnan amplitudi", 0.001, 0.100, 0.025, 0.005)
        cube_data = cached_cube(res, selected_index)
        with viewer:
            view = py3Dmol.view(width=600, height=500)
            view.addModel(cube_data, "cube")
            view.setStyle({"stick": {"radius": 0.15}, "sphere": {"radius": 0.4}})
            view.addVolumetricData(cube_data, "cube", {"isoval": isovalue, "color": "blue", "opacity": 0.85})
            view.addVolumetricData(cube_data, "cube", {"isoval": -isovalue, "color": "red", "opacity": 0.85})
            view.zoomTo()
            showmol(view, height=500, width=600)
        st.download_button("Lataa orbitaali (.cube)", cube_data,
                           file_name=f"RHF_STO3G_orbital_{selected_index + 1}.cube", mime="text/plain")
        with st.expander("Orbitaalienergiat ja miehitys"):
            st.table([{"Orbitaali": index + 1, "Energia (Eh)": f"{energy:.6f}",
                       "Elektroneja": 2 if index <= homo else 0}
                      for index, energy in enumerate(res["evals"])])

        st.markdown("---")
        st.subheader("Orbitaalin kuva tai animaatio")
        if XYZRENDER_AVAILABLE:
            animate_gif = st.checkbox("Animoitu pyörimisliike (GIF) - Tämä kestää kauemmin!")
            if st.button("Renderöi kuva", type="secondary"):
                with st.spinner("Luodaan renderöintiä..."):
                    try:
                        with tempfile.TemporaryDirectory(prefix="hf_render_") as folder:
                            cube_file = Path(folder) / "orbital.cube"
                            cube_file.write_text(cube_data)
                            mol_obj = load(str(cube_file))
                            output = Path(folder) / ("orbital.gif" if animate_gif else "orbital.png")
                            if animate_gif:
                                render_gif(mol_obj, output=str(output), gif_rot="y", canvas_size=800,
                                           mo=True, hy=True, iso=isovalue)
                            else:
                                render(mol_obj, output=str(output), canvas_size=800,
                                       mo=True, hy=True, iso=isovalue)
                            st.image(output.read_bytes(), width=1000)
                    except Exception as error:
                        st.warning(f"Renderöinti epäonnistui: {error}")
        else:
            st.caption("Valinnainen xyzrender-renderöinti ei ole käytettävissä.")

    st.markdown("---")
    with st.expander("Kysymyksiä ja tehtävää"):
        st.markdown(r"""
        **1. Veden HOMO ja LUMO (Symmetria ja sidokset)**
        Laske vedelle (`O`) ja tarkista suppeneminen.
        * Valitse HOMO ja LUMO energiatasokaaviosta. Mitkä tasot ovat miehitettyjä?
        * Tunnistatko HOMO:ssa hapen vapaan elektroniparin p-luonteen ja
          molekyylitason suhteen kohtisuoran suunnan?
        * Vaihda LUMO:on. Missä näet hajottavaa luonnetta ja etumerkin vaihtumista?
        * Muuta isopinnan arvoa. Muuttuuko laskettu orbitaali vai sen esitystapa?

        **2. Tiheyden sekoitus ja suppeneminen**
        Käytä vettä (`O`), poista DIIS käytöstä ja aseta iteraatiorajaksi 300.
        * Vertaa mix-arvoja 1.0 ja 0.1. Kirjaa iteraatioiden määrät, tarkista
          suppeneminen ja vertaa lopullisia energioita.
        * Miten kuvaajan muoto muuttuu? Miksi pienempi päivitys voi vaatia enemmän kierroksia?
        * Kokeile pienempää iteraatiorajaa. Mistä näet, että lasku jäi kesken?
        Vetymolekyylin (`[H][H]`) minimaalinen kahden orbitaalin ongelma voi suppenea
        heti alkutiheydestä. Hidas suppeneminen ei ole HF:n välttämätön ominaisuus.

        **3. Isomeerien elektroniset energiaerot**
        Laske etanoli (`CCO`) ja dimetyylieetteri (`COC`) oletusasetuksilla, DIIS käytössä.
        * Molemmilla on sama atomikoostumus ja sama kantajoukon koko.
          Tarkista kummankin laskun suppeneminen ja kirjaa kokonaisenergiat.
        * Kummalla on alempi RHF/STO-3G-energia näissä voimakenttägeometrioissa?
        * Riittääkö tämä ennustamaan kokeellisen termodynaamisen stabiilisuuden?
          Mieti kantajoukkoa, elektronikorrelaatiota, konformeereja, geometrian optimointia
          sekä nollapiste- ja lämpötilakorjauksia.

        **4. Konjugaatio ja HOMO–LUMO-väli**
        Vertaa eteeniä (`C=C`), butadieeniä (`C=CC=C`) ja heksatrieeniä (`C=CC=CC=C`).
        * Tarkista suppeneminen ja kirjaa kunkin HOMO–LUMO-väli.
        * Miten väli muuttuu konjugoidun ketjun pidentyessä?
        * Tarkastele HOMO:n ja LUMO:n ulottumista ketjulle.
        Pidempi konjugaatio auttaa ymmärtämään matalaenergisempiä elektronisia virityksiä
        ja pitkien polyenien väriä. Näytetty HF-orbitaaliväli ei kuitenkaan yksin
        anna absorptioenergiaa tai ennusta molekyylin väriä.
        """)
