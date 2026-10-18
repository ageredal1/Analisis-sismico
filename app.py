"""
app.py  –  Análisis Sísmico Modal Espectral
Aplicación Streamlit para análisis sísmico por el método modal espectral.
Basado en ET2_logic.py del curso de Especialización en Python.
"""

import io
import sys
import os

import numpy as np
import pandas as pd
import streamlit as st

# Añadir el directorio actual al path
sys.path.insert(0, os.path.dirname(__file__))

import calculos as calc
import graficos as graf
import reporte as rep
import datos as dt

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Análisis Sísmico Modal Espectral",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# CSS PERSONALIZADO
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Header principal */
.main-header {
    background: linear-gradient(135deg, #1a237e 0%, #283593 50%, #3949ab 100%);
    padding: 2rem 2.5rem;
    border-radius: 16px;
    margin-bottom: 1.8rem;
    color: white;
    box-shadow: 0 8px 32px rgba(26,35,126,0.3);
}
.main-header h1 { margin: 0; font-size: 2rem; font-weight: 700; letter-spacing: -0.5px; }
.main-header p  { margin: 0.4rem 0 0; font-size: 0.95rem; opacity: 0.85; font-weight: 300; }

/* Tarjetas de resultado */
.metric-card {
    background: linear-gradient(135deg, #1a237e, #3949ab);
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    color: white;
    text-align: center;
    box-shadow: 0 4px 20px rgba(26,35,126,0.25);
    transition: transform 0.2s ease;
}
.metric-card:hover { transform: translateY(-3px); }
.metric-card .value { font-size: 1.8rem; font-weight: 700; }
.metric-card .label { font-size: 0.8rem; opacity: 0.85; margin-top: 4px; }

/* Sección */
.section-title {
    font-size: 1.15rem; font-weight: 600; color: #1a237e;
    border-left: 4px solid #3949ab; padding-left: 12px;
    margin: 1.5rem 0 0.8rem;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1b4b 0%, #1a237e 60%, #283593 100%) !important;
}
section[data-testid="stSidebar"] * { color: #e8eaf6 !important; }
section[data-testid="stSidebar"] .stTextInput label,
section[data-testid="stSidebar"] .stNumberInput label,
section[data-testid="stSidebar"] .stSlider label { color: #c5cae9 !important; font-size: 0.85rem !important; }
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 { color: #ffffff !important; font-weight: 600 !important; }

/* Tablas */
.dataframe { border-radius: 8px !important; overflow: hidden; }

/* Alertas */
.stAlert { border-radius: 10px; }

/* Botones */
.stDownloadButton button {
    background: linear-gradient(135deg, #1a237e, #3949ab) !important;
    color: white !important; border: none !important;
    border-radius: 8px !important; font-weight: 600 !important;
    transition: opacity 0.2s;
}
.stDownloadButton button:hover { opacity: 0.88; }

/* Divider */
hr { border-color: #e8eaf6; margin: 1.5rem 0; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# FUNCIONES AUXILIARES
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def calcular(hi, m_list, T_list, Phi_list, Z, U, S, R):
    m      = np.array(m_list)
    T_modos = np.array(T_list)
    Phi    = np.array(Phi_list)
    return calc.ejecutar_calculos(hi, m, T_modos, Phi, Z, U, S, R)


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR – PARÁMETROS DE ENTRADA
# ─────────────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🏗️ Análisis Sísmico")
    st.markdown("### ⚙️ Parámetros de Entrada")
    st.markdown("---")

    st.markdown("**📐 Geometría**")
    hi = st.number_input("Altura de entrepiso hi (m)", min_value=1.0,
                          max_value=20.0, value=3.0, step=0.1,
                          help="Altura uniforme de cada piso en metros")

    st.markdown("---")
    st.markdown("**🌊 Periodos de vibración (s)**")
    col1, col2, col3 = st.columns(3)
    with col1: T1 = st.number_input("T₁", min_value=0.001, max_value=10.0, value=0.556, step=0.001, format="%.3f")
    with col2: T2 = st.number_input("T₂", min_value=0.001, max_value=10.0, value=0.193, step=0.001, format="%.3f")
    with col3: T3 = st.number_input("T₃", min_value=0.001, max_value=10.0, value=0.126, step=0.001, format="%.3f")
    T_modos = [T1, T2, T3]

    st.markdown("---")
    st.markdown("**🗺️ Factores sísmicos**")
    Z = st.select_slider("FFactor de zona sísmica (Z)", options=[0.10, 0.25, 0.35, 0.45], value=0.45, help="Z1 (0.10), Z2 (0.25), Z3 (0.35), Z4 (0.45)")
    U = st.select_slider("Factor de uso (U)", options=[1.00, 1.30, 1.50], value=1.00, help="Cat. C/D (1.00), Cat. B (1.30), Cat. A (1.50)")
    S = st.slider("Factor de amplificación de suelo (S)", min_value=0.80, max_value=1.40, value=1.00, step=0.05, help="Varía entre 0.80 (S0) y 1.40 (S3 según la zona)",)
    R = st.slider("Factor de reducción de fuerza sísmica (R)", min_value=3, max_value=8, value=8, step=1, help="Albañilería (3) a Pórticos/Acero (8)",)

    st.markdown("---")
    st.markdown("**📂 Archivo de datos**")
    st.download_button(
        label="⬇️ Descargar plantilla .xlsx",
        data=dt.generar_plantilla_bytes(),
        file_name="plantilla_datos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    archivo = st.file_uploader(
        "Subir archivo .xlsx con masas y modos",
        type=["xlsx"],
        help="El archivo debe tener columnas: Pisos, Masas, Modo 1, Modo 2, Modo 3",
    )


# ─────────────────────────────────────────────────────────────────────────────
# ENCABEZADO PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="main-header">
    <h1>🏗️ Análisis Sísmico Modal Espectral</h1>
    <p>Método de superposición modal espectral – NTE E.030 / RNE</p>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# ESTADO PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────

if archivo is None:
    st.info("👈  **Sube el archivo .xlsx** con las masas y la matriz de modos de vibración "
            "para comenzar el análisis. Puedes descargar la plantilla desde la barra lateral.")
    st.stop()

# Leer datos del archivo
try:
    m_arr, Phi_arr = dt.leer_excel_usuario(archivo)
except Exception as e:
    st.error(f"❌ Error al leer el archivo: {e}")
    st.stop()

n_pisos = len(m_arr)
n_modos = 3
pisos_labels = [f"Piso {i+1}" for i in range(n_pisos)]

# Ejecutar cálculos
try:
    res = calcular(
        hi, m_arr.tolist(), T_modos,
        Phi_arr.tolist(), Z, U, S, R
    )
except Exception as e:
    st.error(f"❌ Error en los cálculos: {e}")
    st.stop()

T_modos_arr = np.array(T_modos)


# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN 1 – PERIODO FUNDAMENTAL
# ─────────────────────────────────────────────────────────────────────────────

st.markdown('<div class="section-title">📊 Periodo Fundamental de Vibración</div>', unsafe_allow_html=True)

col_t1, col_t2, col_t3 = st.columns([1, 1, 2])
with col_t1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="value">{res['T_aprox']:.4f} s</div>
        <div class="label">Período fundamental aproximado T</div>
    </div>""", unsafe_allow_html=True)
with col_t2:
    H_total = hi * n_pisos
    st.markdown(f"""
    <div class="metric-card">
        <div class="value">{H_total:.1f} m</div>
        <div class="label">Altura total del edificio H</div>
    </div>""", unsafe_allow_html=True)
with col_t3:
    st.markdown(f"""
    <div class="metric-card" style="background: linear-gradient(135deg,#283593,#5c6bc0);">
        <div class="value">{n_pisos} pisos · {n_modos} modos</div>
        <div class="label">Configuración estructural analizada</div>
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN 2 – TABLA DE PARÁMETROS MODALES
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("---")
st.markdown('<div class="section-title">📋 Parámetros Modales</div>', unsafe_allow_html=True)

df_modal = pd.DataFrame({
    "Modo":          [f"Modo {j+1}" for j in range(n_modos)],
    "Período T (s)": np.round(T_modos_arr, 4),
    "Factor C":      np.round(res["C"], 4),
    "Sa (m/s²)":     np.round(res["Sa"], 4),
    "W (rad/s)":     np.round(res["W"], 4),
    "Sd (m)":        np.round(res["Sd"], 6),
})
st.dataframe(df_modal.set_index("Modo"), use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN 3 – FUERZAS SÍSMICAS Y CORTANTES POR MODO
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("---")
st.markdown('<div class="section-title">⚡ Fuerza Sísmica y Cortante por Piso (cada Modo)</div>', unsafe_allow_html=True)

tab_tabla, tab_grafico = st.tabs(["📊 Tabla", "📈 Gráfico"])

df_fv = pd.DataFrame(
    {
        "Piso":        pisos_labels,
        "F Modo 1 (t)": np.round(res["F"][:, 0], 4),
        "F Modo 2 (t)": np.round(res["F"][:, 1], 4),
        "F Modo 3 (t)": np.round(res["F"][:, 2], 4),
        "V Modo 1 (t)": np.round(res["V"][:, 0], 4),
        "V Modo 2 (t)": np.round(res["V"][:, 1], 4),
        "V Modo 3 (t)": np.round(res["V"][:, 2], 4),
    }
)

with tab_tabla:
    st.dataframe(df_fv.set_index("Piso"), use_container_width=True)

with tab_grafico:
    fig1 = graf.grafico_fuerza_cortante(res["F"], res["V"], n_pisos, n_modos)
    st.pyplot(fig1, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN 4 – CORTANTES DE COMBINACIÓN MODAL
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("---")
st.markdown('<div class="section-title">🔗 Cortantes de Combinación Modal</div>', unsafe_allow_html=True)

df_comb = pd.DataFrame({
    "Piso":          pisos_labels,
    "Vsum_abs (t)":  np.round(res["Vsum_abs"], 4),
    "Vrcsc (t)":     np.round(res["Vrcsc"],    4),
    "Vrnc_h (t)":    np.round(res["Vrnc_h"],   4),
    "Vreal (t)":     np.round(res["Vreal"],    4),
})

tab_ct, tab_cg = st.tabs(["📊 Tabla", "📈 Gráficos"])

with tab_ct:
    st.dataframe(df_comb.set_index("Piso"), use_container_width=True)

with tab_cg:
    fig2 = graf.grafico_cortantes_combinacion(
        res["Vsum_abs"], res["Vrcsc"],
        res["Vrnc_h"], res["Vreal"], n_pisos
    )
    st.pyplot(fig2, use_container_width=True)

# Gráficos individuales expandibles
with st.expander("🔍 Ver gráficos individuales"):
    colores_ind = ["#4361ee", "#f72585", "#7209b7", "#f77f00"]
    titulos_ind = ["Vsum_abs – Suma de Absolutos", "Vrcsc – Raíz Cuadrática",
                   "Vrnc_h – Respuesta Máxima",    "Vreal – Cortante Real"]
    vals_ind    = [res["Vsum_abs"], res["Vrcsc"], res["Vrnc_h"], res["Vreal"]]

    ci1, ci2 = st.columns(2)
    for k, (v, t, c) in enumerate(zip(vals_ind, titulos_ind, colores_ind)):
        fig_ind = graf.grafico_cortante_individual(v, t, c, n_pisos)
        if k % 2 == 0:
            ci1.pyplot(fig_ind, use_container_width=True)
        else:
            ci2.pyplot(fig_ind, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN 5 – DESCARGA DEL REPORTE
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("---")
st.markdown('<div class="section-title">📥 Descargar Reporte</div>', unsafe_allow_html=True)

try:
    reporte_bytes = rep.generar_reporte(
        res, hi, Z, U, S, R, T_modos_arr
    )
    st.download_button(
        label="📥 Descargar reporte completo (.xlsx)",
        data=reporte_bytes,
        file_name="reporte_sismico_modal.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
except Exception as e:
    st.warning(f"No se pudo generar el reporte: {e}")

st.markdown("<br><br>", unsafe_allow_html=True)
st.caption("Análisis Sísmico Modal Espectral · Especialización en Python · 2026")
