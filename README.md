# Interaktiivinen alusta laskennallisen kemian ja kvanttikemian perusteista

Tämä tietokanta sisältää Turun yliopiston "Atomit ja Molekyylit" kurssin tueksi suunnitellun interaktiivisen selainsovelluksen. Sovellus on rakennettu Pythonilla paketoitu **Streamlit**-kehykseen. 

Tavoitteenani on tehdä muuten abstrakteista kvanttimekaanisista konsepteista helpommin lähestyttäviä säädettävien ja visuaalisten mallien avulla.

## Ominaisuudet ja moduulit

Sovellus on jaettu kuuteen moduuliin, jotka etenevät yksinkertaisista 1D-malleista kohti monimutkaisempia (monielektronisia) järjestelmiä kohden.

* **Moduuli 1: 1D-potentiaalit**
  * Vapaan hiukkasen aaltofunktiot ja seisovat aallot potentiaalikuopassa.
  * Symmetria ja energiatasojen jakautuminen kaksoiskuoppapotentiaalissa.
  * Aaltofunktion ja todennäköisyystiheyden vaihtokytkin sekä numeerisen ja analyyttisen Morse-mallin vertailu.

* **Moduuli 2: Laajennettu Hückel-teoria ja MO-diagrammit**
  * Kahden orbitaalin vuorovaikutuksen ratkaiseminen matriisimuodossa.
  * Interaktiiviset molekyyliorbitaalidiagrammit.
  * Wolfsberg–Helmholtz-approksimaatio ja elektronimiehityksen vaikutus energiasummaan.

* **Moduuli 3: Hartree-Fock (RHF) ja 3D-molekyyliorbitaalit**
  * Aito RHF/STO-3G-laskenta: `PySCF` laskee integraalit ja kantafunktiot, ja oma SCF-silmukka havainnollistaa tiheyden sekoitusta ja DIIS-suppenemista.
  * SMILES-kääntäjä molekyylien nopeaan 3D-mallinnukseen (`RDKit`).
  * Interaktiivinen molekyyliorbitaalien (HOMO/LUMO) 3D-visualisointi ja isopintojen säätö (`stmol`).
  * Valittava energiatasokaavio, joka näyttää miehityksen ja ohjaa samaa 3D-orbitaalivalintaa.

* **Moduuli 4: Radiaaliset jakautumafunktiot (RDF)**
  * Clementi-Raimondi efektiivisen ydinvarauksen ($Z_{eff}$) vaikutus atomiorbitaalien kokoon.
  * Säteittäisen aaltofunktion $R(r)$ ja todennäköisyystiheyden $P(r)$ erot (volyymiefekti).
  * Normalisointi ehdolla $\int r^2|R(r)|^2dr=1$, korjattu Clementi–Raimondi-taulukko ja kuvaajan rajauksesta riippumaton ortogonalisointi.

* **Moduuli 5: Tunneloituminen sirontamatriisimenetelmällä**
  * Testaa kvanttitunneloitumista eri muotoisten ja kokoisten esteiden läpi.
  * Numeerisesti stabiili ketjutus, myös esteen korkeuden kohdalla E=V, sekä resonanssien tarkennus valitulla energia-alueella.

* **Moduuli 6: Kiinteän olomuodon kemia ja Walsh-diagrammit**
  * 1D- ja 2D-hilojen tilatiheyden (DOS) laskenta.
  * Van Hoven singulariteetit ja pakotetun sidospituuksien vuorottelun vaikutus vyöaukkoon.
  * Walsh-diagrammit oikeassa valenssi-2s/2p-kannassa; vedyllä käytetään 1s-funktiota.

Kaikissa moduuleissa on nimetyt esimerkkiasetukset ja yhtenäinen kuvaajatyyli. Uudet käyttöohjeet ja tehtävät ovat suomeksi. `plot_style.py` kokoaa yhteisen esitystavan ja `qm_models.py` muiden moduulien numeeriset mallit.

Morse-mallin äärellisen laatikon aiheuttamat jatkumotasot ovat tarkoituksellinen opetusesimerkki. Walsh-malli havainnollistaa orbitaalien muutoksia; Gauss-kantaan sovitettu EHT ei takaa oikeita tasapainokulmia. HF:n HOMO–LUMO-väli on orbitaalienergioiden erotus, ei suoraan absorptioenergia.

## Tekniikka

* **Käyttöliittymä:** Streamlit
* **Numeerinen laskenta:** NumPy, SciPy, PySCF (HF-integraalit ja STO-3G), Numba (muiden moduulien JIT-laskenta)
* **Kemiakirjastot:** RDKit (geometrian minimointi)
* **Visualisointi:** Plotly (2D-kuvaajat), stmol (py3Dmol-kääre interaktiiviseen 3D-grafiikkaan), xyzrender (korkealaatuiset oppikirjarenderöinnit)

## Asennus ja käyttö omalla koneella

Varmista, että koneellasi on Python 3.10 tai uudempi. `requirements.txt` sisältää myös HF-moduulin tarvitseman PySCF-kirjaston.

1. **Kloonaa repositorio:**
    ```bash
    git clone https://github.com/vainikanpete/laskennallisen_kemian_moduuli.git
    cd laskennallisen_kemian_moduuli
    ```

2. **Luo virtuaaliympäristö ja asenna riippuvuudet:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windowsilla: venv\Scripts\activate
    pip install -r requirements.txt
    ```

3. **Käynnistä sovellus:**
    ```bash
    streamlit run Etusivu.py
    ```
    Sovellus aukeaa selaimesi osoitteeseen http://localhost:8501.

HF-moduuli käsittelee pieniä H/C/N/O-molekyylejä suljetun kuoren singlettinä. Geometria minimoidaan MMFF/UFF-voimakentällä; laskettu energia on RHF/STO-3G-yksittäispistelaskun energia. Pariton elektronimäärä hylätään, ja kesken jäänyt SCF ilmoitetaan välituloksena. Tulokset eivät sisällä värähtely- tai lämpötilakorjauksia.

Numeeriset tarkistukset voi suorittaa komennolla:

```bash
python -m unittest discover -s tests -v
```

Testit tarkistavat HF-tulosten vastaavuuden PySCF:n RHF-ratkaisijan kanssa, elektronimäärän säilymisen, suppenemisen ja cube-tiedostot. Muiden mallien tarkistukset kattavat laatikon ja harmonisen värähtelijän energiatasot, epätarkkuustulon, Morse-tilojen lukumäärän, radiaalien normit ja ortogonaalisuuden, tunneloinnin analyyttiset vertailuarvot ja resonanssit, valenssikannan rotaatioinvarianssin sekä vyöaukot ja 2D-tilatiheyden.


## Kehittäjä:
    Petteri Vainikka, TY:n alumni vuodelta 2018
