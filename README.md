# Interaktiivinen alusta laskennallisen kemian ja kvanttikemian perusteista

Tämä tietokanta sisältää Turun yliopiston "Atomit ja Molekyylit" kurssin tueksi suunnitellun interaktiivisen selainsovelluksen. Sovellus on rakennettu Pythonilla paketoitu **Streamlit**-kehykseen. 

Tavoitteenani on tehdä muuten abstrakteista kvanttimekaanisista konsepteista helpommin lähestyttäviä säädettävien ja visuaalisten mallien avulla.

## Ominaisuudet ja moduulit

Sovellus on jaettu kuuteen moduuliin, jotka etenevät yksinkertaisista 1D-malleista kohti monimutkaisempia (monielektronisia) järjestelmiä kohden.

* **Moduuli 1: 1D-potentiaalit ja kvanttitunneloituminen**
  * Vapaan hiukkasen aaltofunktiot ja seisovat aallot potentiaalikuopassa.
  * Symmetrian rikkoutuminen ja energiatasojen jakautuminen kaksoiskuoppapotentiaalissa.

* **Moduuli 2: Laajennettu Hückel-teoria ja MO-diagrammit**
  * Kahden orbitaalin vuorovaikutuksen ratkaiseminen matriisimuodossa.
  * Interaktiiviset molekyyliorbitaalidiagrammit.
  * Wolfsberg-Helmholz -approksimaatio ja steerisen repulsion visuaalinen tarkastelu.

* **Moduuli 3: Hartree-Fock (RHF) ja 3D-molekyyliorbitaalit**
  * Täysin ab initio -pohjainen SCF-moottori, joka on nopeutettu `Numba`-kirjastolla.
  * SMILES-kääntäjä molekyylien nopeaan 3D-mallinnukseen (`RDKit`).
  * Interaktiivinen molekyyliorbitaalien (HOMO/LUMO) 3D-visualisointi ja isopintojen säätö (`stmol`).

* **Moduuli 4: Radiaaliset jakautumafunktiot (RDF)**
  * Clementi-Raimondi efektiivisen ydinvarauksen ($Z_{eff}$) vaikutus atomiorbitaalien kokoon.
  * Säteittäisen aaltofunktion $R(r)$ ja todennäköisyystiheyden $P(r)$ erot (volyymiefekti).

* **Moduuli 5: Tunneloituminen siirtomatriisimenetelmällä**
  * Testaa kvanttitunneloitumista eri muotoisten, kokoisten ja energisten esteiden läpi

* **Moduuli 6: Kiinteän olomuodon kemia ja Walsh-diagrammit**
  * 1D- ja 2D-hilojen tilatiheyden (DOS) laskenta.
  * Van Hoven singulariteetit ja Peierlsin vääristymän mallintaminen (metallista eristeeksi).
  * Bloch-funktiot ja energiakytkökset laajoissa systeemeissä.

## Stack:

* **Käyttöliittymä:** Streamlit
* **Numeerinen laskenta:** NumPy, SciPy, Numba (JIT-käännös raskaille 2e integraaleille)
* **Kemiakirjastot:** RDKit (geometrian minimointi)
* **Visualisointi:** Plotly (2D-kuvaajat), stmol (py3Dmol-kääre interaktiiviseen 3D-grafiikkaan), xyzrender (korkealaatuiset oppikirjarenderöinnit)

## Asennus ja käyttö omalla koneella

Varmista, että koneellasi on Python 3.9 tai uudempi.

1. **Kloonaa repositorio:**
    ```bash
    git clone [https://github.com/vainikanpete/laskennallisen_kemian_moduuli.git](https://github.com/vainikanpete/laskennallisen_kemian_moduuli.git)
    cd laskennallisen_kemian_moduuli

2. **Luo virtuaaliympäristö ja asenna riippuvuudet:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windowsilla: venv\Scripts\activate
    pip install -r requirements.txt

3. **Käynnistä sovellus:**
    ```bash
    streamlit run comb.py
    Sovellus aukeaa automaattisesti selaimesi osoitteeseen http://localhost:8501


## Kehittäjä:
    Petteri Vainikka, TY:n alumni vuodelta 2018
