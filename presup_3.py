import json
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="PGN Dashboard Paraguay 2025-2026", layout="wide")

EXCEL_PATH = Path(__file__).parent / "presup_py_v3.xlsx"  # debe estar en el repo

@st.cache_data(show_spinner=False)
def load_payload():
    if not EXCEL_PATH.exists():
        raise FileNotFoundError(f"No se encontró el Excel en: {EXCEL_PATH}")
    df = pd.read_excel(EXCEL_PATH, sheet_name="Sheet1")
    df = df.loc[:, ~df.columns.astype(str).str.startswith("Unnamed")].copy()

    rename_map = {
        "Sección": "seccion",
        "Categoría": "categoria",
        "Código": "codigo",
        "Item_2025": "item_2025",
        "Monto_2025": "monto_2025",
        "Item_2026": "item_2026",
        "Monto_2026": "monto_2026",
        "Variación %": "variacion_pct",
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    for c in ["monto_2025", "monto_2026"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype("int64")

    if "variacion_pct" in df.columns:
        df["variacion_pct"] = pd.to_numeric(df["variacion_pct"], errors="coerce")

    return {"records": df.fillna("").to_dict(orient="records"), "meta": {"row_count": int(df.shape[0])}}

st.title("PGN Dashboard Paraguay 2025-2026")
st.caption("Streamlit Cloud: React + Recharts via CDN embebido (sin Babel/JSX, para evitar bloqueos de CSP).")

try:
    payload = load_payload()
except Exception as e:
    st.error(f"Error leyendo el Excel: {e}")
    st.stop()

data_json = json.dumps(payload, ensure_ascii=False)

# IMPORTANTE:
# - NO usamos Babel (porque requiere eval y Streamlit Cloud/CSP suele bloquearlo), así evitamos pantalla en blanco.
# - Construimos React sin JSX (React.createElement).
html = """
<!doctype html>
<html>
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>PGN Dashboard</title>

    <!-- React (UMD) -->
    <script crossorigin src=\"https://unpkg.com/react@18/umd/react.production.min.js\"></script>
    <script crossorigin src=\"https://unpkg.com/react-dom@18/umd/react-dom.production.min.js\"></script>

    <!-- Recharts (UMD) -->
    <script src=\"https://unpkg.com/recharts/umd/Recharts.min.js\"></script>

    <style>
      body {
        margin: 0;
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, \"Liberation Mono\", \"Courier New\", monospace;
        color: #e2e8f0;
      }
      .wrap { padding: 20px; }
      .card {
        background: rgba(30,41,59,0.8);
        border-radius: 12px;
        padding: 20px;
        border: 1px solid rgba(255,255,255,0.05);
      }
      .header {
        background: linear-gradient(90deg, rgba(14,165,233,0.15) 0%, rgba(139,92,246,0.15) 100%);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        border: 1px solid rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
      }
      .title {
        margin: 0;
        font-size: 28px;
        font-weight: 800;
        background: linear-gradient(90deg, #0ea5e9, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
      }
      .subtitle { margin: 6px 0 0; font-size: 14px; color: #94a3b8; }
      .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(420px, 1fr)); gap: 16px; }
      table { width: 100%; border-collapse: collapse; font-size: 13px; margin-top: 14px; }
      thead tr { border-bottom: 2px solid #334155; }
      th { padding: 10px 8px; text-align: left; color: #94a3b8; font-weight: 800; }
      td { padding: 10px 8px; border-bottom: 1px solid #1e293b; }
      tr:nth-child(even) td { background: rgba(255,255,255,0.02); }
      .pill-green {
        padding: 4px 10px;
        border-radius: 999px;
        background: rgba(16,185,129,0.2);
        color: #10b981;
        font-weight: 800;
        white-space: nowrap;
        display: inline-block;
      }
      .mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, \"Liberation Mono\", \"Courier New\", monospace; }
      select {
        width: 100%;
        padding: 12px 16px;
        font-size: 16px;
        background: #1e293b;
        border: 2px solid #334155;
        border-radius: 8px;
        color: #e2e8f0;
        cursor: pointer;
        outline: none;
      }
      .chips { margin-top: 12px; display: flex; gap: 8px; flex-wrap: wrap; }
      .chip { padding: 4px 12px; border-radius: 999px; font-size: 12px; }
      .chip-blue { background: rgba(14,165,233,0.2); color: #0ea5e9; }
      .chip-purple { background: rgba(139,92,246,0.2); color: #8b5cf6; }
      .btnrow { display: flex; gap: 8px; margin-bottom: 16px; }
      button {
        padding: 8px 16px;
        border-radius: 8px;
        cursor: pointer;
        font-size: 13px;
        font-weight: 700;
        color: #e2e8f0;
        background: transparent;
        border: 1px solid #334155;
      }
      button.active { background: linear-gradient(135deg, #0ea5e9, #8b5cf6); border: none; }
      .footer { text-align: center; margin-top: 18px; padding: 16px; color: #64748b; font-size: 12px; }
      .small { margin: 12px 0 0; font-size: 12px; color: #64748b; }
    </style>
  </head>
  <body>
    <div id=\"root\"></div>

    <script id=\"pgn-data\" type=\"application/json\">__PGN_DATA_JSON__</script>

    <script>
      const h = React.createElement;
      const { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, PieChart, Pie, Cell } = Recharts;

      function parseData() {
        try {
          const el = document.getElementById("pgn-data");
          return JSON.parse(el.textContent || "{}");
        } catch (e) {
          return { records: [], meta: { error: String(e) } };
        }
      }

      function formatGs(num) {
        const n = Number(num || 0);
        if (n >= 1e12) return "₲ " + (n / 1e12).toFixed(2) + " B";
        if (n >= 1e9) return "₲ " + (n / 1e9).toFixed(1) + " MM";
        if (n >= 1e6) return "₲ " + (n / 1e6).toFixed(0) + " M";
        return "₲ " + n.toLocaleString();
      }

      function clampText(s, max = 60) {
        const str = String(s || "");
        return str.length > max ? str.slice(0, max - 1) + "…" : str;
      }

      const entidadesData = {
        "Ministerio de Educación y Ciencias": {
          codigo: "20",
          nivel: "Poder Ejecutivo",
          pgn2025: { 100: 6310000000000, 200: 485000000000, 300: 2350000000000, 400: 165000000000, 500: 285000000000, 800: 105000000000, 900: 0 },
          pgn2026: { 100: 6850000000000, 200: 545000000000, 300: 2580000000000, 400: 185000000000, 500: 320000000000, 800: 120000000000, 900: 0 }
        },
        "Ministerio de Salud Pública": {
          codigo: "21",
          nivel: "Poder Ejecutivo",
          pgn2025: { 100: 4150000000000, 200: 720000000000, 300: 3280000000000, 400: 485000000000, 500: 680000000000, 800: 185000000000, 900: 0 },
          pgn2026: { 100: 4650000000000, 200: 850000000000, 300: 3520000000000, 400: 540000000000, 500: 780000000000, 800: 220000000000, 900: 0 }
        },
        "Ministerio de Economía y Finanzas": {
          codigo: "12",
          nivel: "Poder Ejecutivo",
          pgn2025: { 100: 520000000000, 200: 145000000000, 300: 92000000000, 400: 38000000000, 500: 65000000000, 800: 16300000000000, 900: 4840000000000 },
          pgn2026: { 100: 555000000000, 200: 158000000000, 300: 98000000000, 400: 42000000000, 500: 72000000000, 800: 17500000000000, 900: 5275000000000 }
        }
      };

      const objetosGasto = {
        100: { nombre: "Servicios Personales", color: "#0ea5e9" },
        200: { nombre: "Servicios No Personales", color: "#8b5cf6" },
        300: { nombre: "Bienes de Consumo e Insumos", color: "#10b981" },
        400: { nombre: "Bienes de Cambio", color: "#f59e0b" },
        500: { nombre: "Inversión Física", color: "#ef4444" },
        800: { nombre: "Transferencias", color: "#ec4899" },
        900: { nombre: "Otros Gastos", color: "#6b7280" }
      };

      function sumObj(obj) {
        return Object.values(obj || {}).reduce((a, b) => a + (Number(b) || 0), 0);
      }

      function RankTable(props) {
        const { title, subtitle, rows, type } = props;
        return h("div", { className: "card" },
          h("div", { style: { display: "flex", justifyContent: "space-between", alignItems: "baseline", gap: 12 } },
            h("div", null,
              h("h3", { style: { margin: 0, fontSize: 16, fontWeight: 800 } }, title),
              h("p", { style: { margin: "6px 0 0", fontSize: 12, color: "#64748b" } }, subtitle)
            )
          ),
          h("table", null,
            h("thead", null,
              h("tr", null,
                h("th", { style: { textAlign: "right" } }, "#"),
                h("th", { style: { textAlign: "center" } }, "Código"),
                h("th", null, "Organismo"),
                type === "var" ? h("th", { style: { textAlign: "right" } }, "Var. %") : null,
                h("th", { style: { textAlign: "right" } }, "Monto 2026")
              )
            ),
            h("tbody", null,
              rows.map((r, idx) =>
                h("tr", { key: (r.codigo || "NA") + "-" + idx },
                  h("td", { style: { textAlign: "right", color: "#94a3b8" } }, String(idx + 1)),
                  h("td", { style: { textAlign: "center" } }, h("span", { className: "mono" }, r.codigo || "—")),
                  h("td", null, clampText(r.organismo, 60)),
                  type === "var"
                    ? h("td", { style: { textAlign: "right" } }, h("span", { className: "pill-green" }, "+" + Number(r.variacion_pct || 0).toFixed(1) + "%"))
                    : null,
                  h("td", { style: { textAlign: "right", color: "#8b5cf6" } }, h("span", { className: "mono" }, formatGs(r.monto_2026)))
                )
              )
            )
          )
        );
      }

      function App() {
        const dataset = parseData();
        const records = Array.isArray(dataset.records) ? dataset.records : [];

        const [selectedEntity, setSelectedEntity] = React.useState("Ministerio de Educación y Ciencias");
        const [comparisonMode, setComparisonMode] = React.useState("absoluto");

        const top15Monto2026 = React.useMemo(() => {
          return records
            .map(r => ({ codigo: r.codigo, organismo: r.item_2026 || r.item_2025 || "", monto_2026: Number(r.monto_2026 || 0) }))
            .sort((a, b) => b.monto_2026 - a.monto_2026)
            .slice(0, 15);
        }, [records]);

        const top15VarPos = React.useMemo(() => {
          return records
            .map(r => ({ codigo: r.codigo, organismo: r.item_2026 || r.item_2025 || "", monto_2026: Number(r.monto_2026 || 0), variacion_pct: Number(r.variacion_pct) }))
            .filter(r => Number.isFinite(r.variacion_pct) && r.variacion_pct > 0)
            .sort((a, b) => b.variacion_pct - a.variacion_pct)
            .slice(0, 15);
        }, [records]);

        const entityKeys = React.useMemo(() => Object.keys(entidadesData).sort(), []);
        const entityData = entidadesData[selectedEntity];

        const comparisonData = React.useMemo(() => {
          if (!entityData) return [];
          return Object.keys(objetosGasto)
            .map((key) => {
              const pgn2025 = (entityData.pgn2025 && entityData.pgn2025[key]) ? entityData.pgn2025[key] : 0;
              const pgn2026 = (entityData.pgn2026 && entityData.pgn2026[key]) ? entityData.pgn2026[key] : 0;
              const variacion = pgn2025 > 0 ? ((pgn2026 - pgn2025) / pgn2025) * 100 : 0;
              return {
                objeto: key,
                nombre: objetosGasto[key].nombre,
                nombreCorto: objetosGasto[key].nombre.split(" ").slice(0,2).join(" "),
                pgn2025,
                pgn2026,
                variacion: Number.isFinite(variacion) ? Number(variacion.toFixed(1)) : 0,
                color: objetosGasto[key].color
              };
            })
            .filter(d => d.pgn2025 > 0 || d.pgn2026 > 0);
        }, [entityData]);

        const totalData = React.useMemo(() => {
          if (!entityData) return { total2025: 0, total2026: 0, variacion: 0 };
          const total2025 = sumObj(entityData.pgn2025);
          const total2026 = sumObj(entityData.pgn2026);
          const variacion = total2025 > 0 ? ((total2026 - total2025) / total2025) * 100 : 0;
          return { total2025, total2026, variacion: Number(variacion.toFixed(1)) };
        }, [entityData]);

        const pieData2025 = comparisonData.map(d => ({ name: d.nombreCorto, value: d.pgn2025, color: d.color }));
        const pieData2026 = comparisonData.map(d => ({ name: d.nombreCorto, value: d.pgn2026, color: d.color }));

        const btn = (key, label) => h(
          "button",
          { className: comparisonMode === key ? "active" : "", onClick: () => setComparisonMode(key) },
          label
        );

        return h("div", { className: "wrap" },
          h("div", { className: "header" },
            h("div", { style: { display: "flex", alignItems: "center", gap: 16 } },
              h("div", { style: {
                width: 48, height: 48, borderRadius: 12,
                background: "linear-gradient(135deg,#0ea5e9,#8b5cf6)",
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: 24
              }}, "🇵🇾"),
              h("div", null,
                h("h1", { className: "title" }, "Dashboard PGN Paraguay"),
                h("p", { className: "subtitle" }, "Análisis Comparativo del Presupuesto General de la Nación 2025 vs 2026")
              )
            ),
            h("p", { className: "small" }, "Fuente: MEF | SITUFIN — Rankings desde el Excel (presup_py_v3.xlsx)")
          ),

          h("div", { className: "grid", style: { marginBottom: 24 } },
            h(RankTable, { title: "Top 15 — Organismos con mayor gasto asignado (2026)", subtitle: "Ranking institucional (monto 2026)", rows: top15Monto2026, type: "monto" }),
            h(RankTable, { title: "Top 15 — Mayor variación positiva (2026 vs 2025)", subtitle: "Ranking institucional (variación %)", rows: top15VarPos, type: "var" })
          ),

          h("div", { className: "card", style: { marginBottom: 24 } },
            h("label", { style: { display: "block", marginBottom: 8, fontSize: 14, color: "#94a3b8", fontWeight: 800 } }, "📊 Seleccionar Organismo (mock para desglose por objeto)"),
            h("select", { value: selectedEntity, onChange: (e) => setSelectedEntity(e.target.value) },
              entityKeys.map(k => h("option", { key: k, value: k }, k))
            ),
            h("div", { className: "chips" },
              h("span", { className: "chip chip-blue" }, "Código: " + (entityData ? entityData.codigo : "—")),
              h("span", { className: "chip chip-purple" }, entityData ? entityData.nivel : "—")
            )
          ),

          h("div", { className: "grid", style: { marginBottom: 24, gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))" } },
            h("div", { className: "card", style: { border: "1px solid rgba(14,165,233,0.3)", background: "linear-gradient(135deg, rgba(14,165,233,0.2) 0%, rgba(14,165,233,0.05) 100%)" } },
              h("div", { style: { fontSize: 12, color: "#0ea5e9", fontWeight: 900, letterSpacing: 1, textTransform: "uppercase" } }, "PGN 2025"),
              h("div", { style: { fontSize: 28, fontWeight: 900, marginTop: 8 } }, formatGs(totalData.total2025))
            ),
            h("div", { className: "card", style: { border: "1px solid rgba(139,92,246,0.3)", background: "linear-gradient(135deg, rgba(139,92,246,0.2) 0%, rgba(139,92,246,0.05) 100%)" } },
              h("div", { style: { fontSize: 12, color: "#8b5cf6", fontWeight: 900, letterSpacing: 1, textTransform: "uppercase" } }, "PGN 2026"),
              h("div", { style: { fontSize: 28, fontWeight: 900, marginTop: 8 } }, formatGs(totalData.total2026))
            ),
            h("div", { className: "card", style: {
              border: "1px solid " + (totalData.variacion >= 0 ? "rgba(16,185,129,0.3)" : "rgba(239,68,68,0.3)"),
              background: "linear-gradient(135deg, " + (totalData.variacion >= 0 ? "rgba(16,185,129,0.2)" : "rgba(239,68,68,0.2)") + " 0%, " + (totalData.variacion >= 0 ? "rgba(16,185,129,0.05)" : "rgba(239,68,68,0.05)") + " 100%)"
            } },
              h("div", { style: { fontSize: 12, color: (totalData.variacion >= 0 ? "#10b981" : "#ef4444"), fontWeight: 900, letterSpacing: 1, textTransform: "uppercase" } }, "Variación"),
              h("div", { style: { fontSize: 28, fontWeight: 900, marginTop: 8 } }, (totalData.variacion >= 0 ? "+" : "") + totalData.variacion + "%")
            )
          ),

          h("div", { className: "card", style: { marginBottom: 24 } },
            h("h2", { style: { margin: "0 0 20px", fontSize: 18, fontWeight: 900 } }, "📈 Desglose por tipo de gasto (objeto) — mock"),
            h("div", { className: "btnrow" }, btn("absoluto", "Valores"), btn("variacion", "Variación %")),
            h("div", { style: { height: 360 } },
              h(ResponsiveContainer, { width: "100%", height: "100%" },
                comparisonMode === "absoluto"
                  ? h(BarChart, { data: comparisonData, margin: { top: 20, right: 30, left: 20, bottom: 70 } },
                      h(CartesianGrid, { strokeDasharray: "3 3", stroke: "#334155" }),
                      h(XAxis, { dataKey: "nombreCorto", angle: -45, textAnchor: "end", fontSize: 11, stroke: "#64748b", height: 90 }),
                      h(YAxis, { stroke: "#64748b", fontSize: 11, tickFormatter: (v) => v >= 1e12 ? (v/1e12).toFixed(1) + "B" : v >= 1e9 ? (v/1e9).toFixed(0) + "MM" : (v/1e6).toFixed(0) + "M" }),
                      h(Tooltip, { contentStyle: { background: "#1e293b", border: "1px solid #334155", borderRadius: 10 }, formatter: (value) => formatGs(value) }),
                      h(Legend, null),
                      h(Bar, { dataKey: "pgn2025", name: "PGN 2025", fill: "#0ea5e9", radius: [4,4,0,0] }),
                      h(Bar, { dataKey: "pgn2026", name: "PGN 2026", fill: "#8b5cf6", radius: [4,4,0,0] })
                    )
                  : h(BarChart, { data: comparisonData, margin: { top: 20, right: 30, left: 20, bottom: 70 } },
                      h(CartesianGrid, { strokeDasharray: "3 3", stroke: "#334155" }),
                      h(XAxis, { dataKey: "nombreCorto", angle: -45, textAnchor: "end", fontSize: 11, stroke: "#64748b", height: 90 }),
                      h(YAxis, { stroke: "#64748b", fontSize: 11, unit: "%" }),
                      h(Tooltip, { contentStyle: { background: "#1e293b", border: "1px solid #334155", borderRadius: 10 }, formatter: (value) => String(value) + "%" }),
                      h(Bar, { dataKey: "variacion", name: "Variación %", radius: [4,4,0,0] },
                        comparisonData.map((entry, index) =>
                          h(Cell, { key: "c-" + index, fill: entry.variacion >= 0 ? "#10b981" : "#ef4444" })
                        )
                      )
                    )
              )
            )
          ),

          h("div", { className: "grid", style: { marginBottom: 24, gridTemplateColumns: "repeat(auto-fit, minmax(350px, 1fr))" } },
            h("div", { className: "card" },
              h("h3", { style: { margin: "0 0 16px", fontSize: 16, fontWeight: 900, color: "#0ea5e9" } }, "🥧 Distribución PGN 2025"),
              h("div", { style: { height: 280 } },
                h(ResponsiveContainer, { width: "100%", height: "100%" },
                  h(PieChart, null,
                    h(Pie, { data: pieData2025, cx: "50%", cy: "50%", innerRadius: 60, outerRadius: 100, paddingAngle: 2, dataKey: "value" },
                      pieData2025.map((entry, index) => h(Cell, { key: "p25-" + index, fill: entry.color }))
                    ),
                    h(Tooltip, { contentStyle: { background: "#1e293b", border: "1px solid #334155", borderRadius: 10, fontSize: 12 }, formatter: (value) => formatGs(value) })
                  )
                )
              )
            ),
            h("div", { className: "card" },
              h("h3", { style: { margin: "0 0 16px", fontSize: 16, fontWeight: 900, color: "#8b5cf6" } }, "🥧 Distribución PGN 2026"),
              h("div", { style: { height: 280 } },
                h(ResponsiveContainer, { width: "100%", height: "100%" },
                  h(PieChart, null,
                    h(Pie, { data: pieData2026, cx: "50%", cy: "50%", innerRadius: 60, outerRadius: 100, paddingAngle: 2, dataKey: "value" },
                      pieData2026.map((entry, index) => h(Cell, { key: "p26-" + index, fill: entry.color }))
                    ),
                    h(Tooltip, { contentStyle: { background: "#1e293b", border: "1px solid #334155", borderRadius: 10, fontSize: 12 }, formatter: (value) => formatGs(value) })
                  )
                )
              )
            )
          ),

          h("div", { className: "footer" },
            h("div", null, "✅ Rankings salen del Excel del repo (", h("span", { className: "mono" }, "presup_py_v3.xlsx"), ")."),
            h("div", { style: { marginTop: 6, fontSize: 11, color: "#475569" } }, "Si querés, conectamos el desglose real por objeto cuando tengas esa tabla.")
          )
        );
      }

      const root = ReactDOM.createRoot(document.getElementById("root"));
      root.render(h(App));
    </script>
  </body>
</html>
""".replace("__PGN_DATA_JSON__", data_json)

components.html(html, height=1650, scrolling=True)
