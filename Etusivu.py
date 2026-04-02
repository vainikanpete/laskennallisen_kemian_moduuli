import streamlit as st
import time
import base64

# ==========================================
# 1. YLEISET ASETUKSET & TYYLIT
# ==========================================
st.set_page_config(
    page_title="Laskennallinen Kemia",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .block-container { animation: fadeIn 1.2s ease-in; } 
    @keyframes fadeIn { 0% { opacity: 0; } 100% { opacity: 1; } }
    
    .main-card {
        background-color: #f8f9fa;
        padding: 30px;
        border-radius: 10px;
        border-left: 5px solid #4A90E2;
        margin-bottom: 20px;
    }
    .module-list {
        line-height: 1.8;
    }
    .pulse-logo {
        animation: pulse 2.0s infinite;
        max-width: 500px;
    }
    @keyframes pulse {
        0% { transform: scale(0.98); opacity: 0.9; }
        50% { transform: scale(1.02); opacity: 1; }
        100% { transform: scale(0.98); opacity: 0.9; }
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. LATAUSRUUTU (SPLASH SCREEN)
# ==========================================



@st.cache_data
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

if 'app_loaded' not in st.session_state:
    st.session_state.app_loaded = False

if not st.session_state.app_loaded:
    splash = st.empty()
    with splash.container():
        try:
            logo_base64 = get_base64_image("logo.png")
            # Added border-radius and box-shadow to make the square background look like a stylized app icon
            img_element = f'<img src="data:image/png;base64,{logo_base64}" style="width: 480px; border-radius: 20px; box-shadow: 0 8px 16px rgba(0,0,0,0.4); animation: pulse 1.5s infinite;">'
        except FileNotFoundError:
            img_element = '<div style="font-size: 80px; animation: pulse 1.5s infinite;">⚛️</div>'

        # Force absolute centering using a 100% width flex container
        st.markdown(f"""
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 80vh; width: 100%;">
            {img_element}
            <h2 style="color: #4A90E2; font-weight: 300; letter-spacing: 2px; margin-top: 30px; animation: pulse 1.5s infinite;">Ladataan laskennallisen kemian moduuleja ...</h2>
        </div>
        <style>
        @keyframes pulse {{
            0% {{ transform: scale(0.95); opacity: 0.8; }}
            50% {{ transform: scale(1.05); opacity: 1; }}
            100% {{ transform: scale(0.95); opacity: 0.8; }}
        }}
        </style>
        """, unsafe_allow_html=True)
        
    time.sleep(4.0)
    splash.empty()
    st.session_state.app_loaded = True
    st.rerun()


# Apply the fade-in effect and custom CSS to the main UI
st.markdown("""
    <style>
    .block-container { animation: fadeIn 1.2s ease-in; } 
    @keyframes fadeIn { 0% { opacity: 0; } 100% { opacity: 1; } }
    
    .stSelectbox div[data-baseweb="select"] {
        cursor: pointer;
        background-color: #f0f2f6;
        border-radius: 8px;
        border: 2px solid #4A90E2;
    }
    .metric-container {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
    }
    </style>
""", unsafe_allow_html=True)




# ==========================================
# 3. PÄÄSIVUN SISÄLTÖ
# ==========================================
st.title("Lyhyt esittely laskennallisesta kemiasta")
st.write("**Turun yliopisto | Kemian laitos**")
st.divider()

col1, col2 = st.columns([1.5, 1])

with col1:
    st.markdown("""
    <div class="main-card">
        <h3>Tavoitteeni</h3>
        <p>Olen luonut tämän oppimisympäristön  havainnollistamaan kvanttimekaniikan ja laskennallisen kemian keskeisiä ilmiöitä ja mekanismeja. 
        Olen itse oppinut aina parhaiten tekemällä ja kikkailemalla. Tässä on teille mahdollisuus samaan - vasemmalla olevat moduulit on tehty käytettäviksi ja rikottaviksi. Toivon, että saatte näiden pienten ohjelmien kanssa pelaamisesta samaa iloa, jota itse koin aikanani ensimmäisiä laskuja ajaessani - laskennallisen kemian ehdoton kauneus on siinä, että vain mielikuvitus (ja fysiikka, tiettyyn pisteeseen asti) on rajana.<br>
Pitäkää hauskaa!<br>
- Petteri
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("Valitse moduuli vasemman reunan valikosta aloittaaksesi tutkimuksen.")

    st.subheader("Moduulit")
    st.markdown("""
    <div class="module-list">
    <b>1. 1D Potentiaalit:</b> Ratkaise Schrödingerin yhtälö numeerisesti ja tarkastele klassisia potentiaalimalleja.<br>
    <b>2. Laajennettu Hückel:</b> Tutki MO-teoriaa, sidosenergioita ja Wolfsberg-Helmholz -approksimaatiota.<br>
    <b>3. Hartree-Fock (RHF):</b> Syvenny itseytyvän kentän (SCF) menetelmään ja 3D-orbitaalien visualisointiin.<br>
    <b>4. Radiaaliset jakautumafunktiot:</b> Vertaile atomiorbitaalien säteittäisiä jakaumia ja varjostusefektejä.<br>
    <b>5. Tunneloituminen:</b> Tutki hiukkasen läpäisytodennäköisyyksiä siirtomatriisimenetelmällä.<br>
    <b>6. Extrat:</b> Syventävää materiaalia Walsh-diagrammeista ja kiinteän olomuodon kemiasta.
    </div>
    """, unsafe_allow_html=True)

with col2:
    # Käytetään pot.png kuvaa visualisointina
    st.image("picture1.jpeg", 
             caption="", width=320)
    
    with st.expander("Ohjeita käyttöön", expanded=True):
        st.write("""
        * **Visualisointi:** Kaikki 3D-mallit ja kuvaajat ovat interaktiivisia.
        """)

# Alatunniste
st.sidebar.markdown("---")
st.sidebar.caption("Phys. & Comp. Chem. Über Alles")
st.sidebar.markdown(
    "<div style='color: #888; font-size: 0.85em; margin-top: 20px; font-style: italic;'>"
    "Omistettu J. Sinkkoselle <br> Le Roi est mort. Vive le Roi!"
    "</div>", 
    unsafe_allow_html=True
)
