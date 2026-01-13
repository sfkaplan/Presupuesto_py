import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

st.set_page_config(
    page_title="PGN Paraguay 2025 vs 2026 - Clasificación Institucional",
    layout="wide",
)

DEFAULT_FILE = Path("presup_py_v2.xlsx")  # dejalo en el repo (misma carpeta que app.py)
SHEET_NAME = "Sheet1"
MILLION = 1_000_000


@st.cache_data(show_spinner=False)
def load_excel(file) -> pd.DataFrame:
    # file puede ser Path o UploadedFile
    df = pd.read_excel(file, sheet_name=SHEET_NAME, engine="openpyxl")
    # limpiar columna basura típica de export (Unnamed: 0)
    df = df.loc[:, ~df.columns.astype(str).str.match(r"^Unnamed")]
    return df


def prepare_tables(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # 1) reemplazar NaN de 2025 (item inexistente en 2025)
    df["Item_2025"] = df["Item_2025"].fillna("Item inexistente")
    # si el monto 2025 es NaN para esos casos, poner 0
    df["Monto_2025"] = df["Monto_2025"].fillna(0)

    # 2) montos en millones de Gs (mantener numérico)
    df["Monto_2025_MM"] = df["Monto_2025"] / MILLION
    df["Monto_2026_MM"] = df["Monto_2026"] / MILLION

    # 3) variación % redondeada a 1 decimal (si existe)
    if "Variación %" in df.columns:
        df["Variación %"] = df["Variación %"].round(1)

    return df


def display_table(df_show: pd.DataFrame, key: str):
    # Config visual: montos en millones con 1 decimal, variación con 1 decimal
    colcfg = {
        "Monto_2025_MM": st.column_config.NumberColumn("Monto 2025 (MM Gs)", format="%.1f"),
        "Monto_2026_MM": st.column_config.NumberColumn("Monto 2026 (MM Gs)", format="%.1f"),
        "Variación %": st.column_config.NumberColumn("Variación %", format="%.1f"),
    }
    st.dataframe(
        df_show,
        use_container_width=True,
        hide_index=True,
        column_config=colcfg,
        key=key,
    )


st.title("Presupuesto General de la Nación (PY) – Comparación 2025 vs 2026")
st.caption("Clasificación Institucional – Montos expresados en **millones de guaraníes (Gs)**.")

with st.sidebar:
    st.header("Fuente de datos")
    uploaded = st.file_uploader("Subí el Excel final (opcional)", type=["xlsx"])
    if uploaded is None:
        if not DEFAULT_FILE.exists():
            st.error(
                "No encuentro el archivo 'presup_py.xlsx' en el repositorio. "
                "Subilo con el uploader o agregalo al repo."
            )
            st.stop()
        data_source = DEFAULT_FILE
        st.info("Usando archivo del repositorio: presup_py.xlsx")
    else:
        data_source = uploaded
        st.success("Usando archivo subido")

# Cargar y preparar
df_raw = load_excel(data_source)
df = prepare_tables(df_raw)

# Columnas base esperadas
required = {"Sección", "Categoría", "Código", "Item_2025", "Monto_2025", "Item_2026", "Monto_2026", "Variación %"}
missing_cols = required - set(df_raw.columns)
if missing_cols:
    st.warning(f"Faltan columnas esperadas en el Excel: {sorted(missing_cols)}")

# Tabla principal (entera)
st.subheader("1) Tabla completa (2025 vs 2026)")
df_main = df[["Sección", "Categoría", "Código", "Item_2025", "Monto_2025_MM", "Item_2026", "Monto_2026_MM", "Variación %"]].copy()
display_table(df_main, key="tabla_completa")

# 4) Top 10 por monto 2026
st.subheader("2) Top 10 ítems de mayor monto en 2026")
df_top_2026 = (
    df_main.sort_values("Monto_2026_MM", ascending=False)
           .head(10)
           .reset_index(drop=True)
)
display_table(df_top_2026, key="top10_monto_2026")

# 5) Top 10 subas % (positivas)
st.subheader("3) Top 10 ítems con mayor variación porcentual positiva (2026 vs 2025)")
df_pos = df_main.copy()
df_pos = df_pos[df_pos["Variación %"].notna() & (df_pos["Variación %"] > 0)]
df_top_pos = df_pos.sort_values("Variación %", ascending=False).head(10).reset_index(drop=True)
display_table(df_top_pos, key="top10_subas")

# 6) Top 10 bajas % (negativas)
st.subheader("4) Top 10 ítems con mayor variación porcentual negativa (2026 vs 2025)")
df_neg = df_main.copy()
df_neg = df_neg[df_neg["Variación %"].notna() & (df_neg["Variación %"] < 0)]
df_top_neg = df_neg.sort_values("Variación %", ascending=True).head(10).reset_index(drop=True)
display_table(df_top_neg, key="top10_bajas")

# 7) Items nuevos 2026 (no estaban en 2025)
st.subheader("5) Ítems que aparecen en 2026 y no existían en 2025")
df_new = df[df["Item_2025"].eq("Item inexistente")].copy()
df_new_show = df_new[["Sección", "Categoría", "Código", "Item_2025", "Monto_2025_MM", "Item_2026", "Monto_2026_MM", "Variación %"]]
if df_new_show.empty:
    st.info("No se detectaron ítems nuevos en 2026 (según Item_2025 == NaN en el Excel).")
else:
    display_table(df_new_show.reset_index(drop=True), key="items_nuevos_2026")

# Download (opcional)
st.divider()
st.subheader("Descargas")
csv_bytes = df_main.to_csv(index=False).encode("utf-8-sig")
st.download_button("Descargar tabla completa (CSV)", data=csv_bytes, file_name="tabla_completa_2025_2026.csv", mime="text/csv")
