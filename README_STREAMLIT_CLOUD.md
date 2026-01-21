# Presupuesto_py — Deploy en Streamlit Cloud (sin frontend toolchain)

Este setup **no requiere Vite / CRA / Next**.  
La UI se renderiza con **React + Recharts via CDN**, embebido dentro de Streamlit.

## Qué tenés que hacer
1. En el repo, agregá estos archivos:
   - `app.py` (el nuevo)
   - `requirements.txt` (actualizado)
2. Asegurate de mantener `presup_py_v3.xlsx` en la raíz (ya está en tu repo).
3. En Streamlit Community Cloud:
   - New app
   - Repo: `sfkaplan/Presupuesto_py`
   - Branch: `main`
   - Main file: `app.py`
   - Deploy

## Notas
- Los **rankings (Top 15)** se calculan **del Excel real** (`presup_py_v3.xlsx`).
- El **desglose por objeto (100/200/...)** está en modo **mock** (igual que en el JSX),
  porque ese detalle no viene en el Excel actual. Si me pasás el detalle, lo conecto.
