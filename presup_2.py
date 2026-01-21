import json
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="PGN Dashboard Paraguay 2025-2026", layout="wide")

EXCEL_PATH = Path(__file__).parent / "presup_py_v3.xlsx"  # está en tu repo

@st.cache_data(show_spinner=False)
def load_budget_rows():
    if not EXCEL_PATH.exists():
        raise FileNotFoundError(f"No se encontró el Excel en: {EXCEL_PATH}")
    df = pd.read_excel(EXCEL_PATH, sheet_name="Sheet1")
    # Limpieza básica
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

    # Payload que consume el frontend
    payload = {
        "records": df.fillna("").to_dict(orient="records"),
        "meta": {"row_count": int(df.shape[0])},
    }
    return payload

try:
    payload = load_budget_rows()
except Exception as e:
    st.error(f"Error leyendo el Excel: {e}")
    st.stop()

# UI Streamlit (simple) + embed del frontend
st.markdown(
    """
    <style>
      .small-note { color:#64748b; font-size: 12px; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("PGN Dashboard Paraguay 2025-2026")
st.caption("Deploy en Streamlit Cloud (sin Vite/CRA/Next): React + Recharts via CDN embebido en un iframe.")

# Inyectamos el dataset dentro del HTML para evitar fetch/rutas
data_json = json.dumps(payload, ensure_ascii=False)

html = f"""
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>PGN Dashboard</title>

    <!-- React (UMD) -->
    <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>

    <!-- Recharts (UMD) -->
    <script src="https://unpkg.com/recharts/umd/Recharts.min.js"></script>

    <!-- Babel para JSX en el browser (evita build toolchain) -->
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>

    <style>
      body {{
        margin: 0;
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
        color: #e2e8f0;
      }}
      .wrap {{
        padding: 20px;
      }}
      .card {{
        background: rgba(30,41,59,0.8);
        border-radius: 12px;
        padding: 20px;
        border: 1px solid rgba(255,255,255,0.05);
      }}
      .header {{
        background: linear-gradient(90deg, rgba(14,165,233,0.15) 0%, rgba(139,92,246,0.15) 100%);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        border: 1px solid rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
      }}
      .title {{
        margin: 0;
        font-size: 28px;
        font-weight: 800;
        background: linear-gradient(90deg, #0ea5e9, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
      }}
      .subtitle {{
        margin: 6px 0 0;
        font-size: 14px;
        color: #94a3b8;
      }}
      .grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(420px, 1fr));
        gap: 16px;
      }}
      table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
        margin-top: 14px;
      }}
      thead tr {{
        border-bottom: 2px solid #334155;
      }}
      th {{
        padding: 10px 8px;
        text-align: left;
        color: #94a3b8;
        font-weight: 800;
      }}
      td {{
        padding: 10px 8px;
        border-bottom: 1px solid #1e293b;
      }}
      tr:nth-child(even) td {{
        background: rgba(255,255,255,0.02);
      }}
      .pill-green {{
        padding: 4px 10px;
        border-radius: 999px;
        background: rgba(16,185,129,0.2);
        color: #10b981;
        font-weight: 800;
        white-space: nowrap;
        display: inline-block;
      }}
      .mono {{
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
      }}
      select {{
        width: 100%;
        padding: 12px 16px;
        font-size: 16px;
        background: #1e293b;
        border: 2px solid #334155;
        border-radius: 8px;
        color: #e2e8f0;
        cursor: pointer;
        outline: none;
      }}
      .chips {{
        margin-top: 12px;
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
      }}
      .chip {{
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 12px;
      }}
      .chip-blue {{ background: rgba(14,165,233,0.2); color: #0ea5e9; }}
      .chip-purple {{ background: rgba(139,92,246,0.2); color: #8b5cf6; }}
      .btnrow {{ display: flex; gap: 8px; margin-bottom: 16px; }}
      button {{
        padding: 8px 16px;
        border-radius: 8px;
        cursor: pointer;
        font-size: 13px;
        font-weight: 700;
        color: #e2e8f0;
        background: transparent;
        border: 1px solid #334155;
      }}
      button.active {{
        background: linear-gradient(135deg, #0ea5e9, #8b5cf6);
        border: none;
      }}
      .footer {{
        text-align: center;
        margin-top: 18px;
        padding: 16px;
        color: #64748b;
        font-size: 12px;
      }}
    </style>
  </head>
  <body>
    <div id="root"></div>

    <script>
      window.__PGN_DATA__ = {data_json};
    </script>

    <script type="text/babel">
      const {{
        ResponsiveContainer,
        BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
        PieChart, Pie, Cell,
      }} = Recharts;

      const MILLION = 1_000_000;

      const formatGs = (num) => {{
        const n = Number(num || 0);
        if (n >= 1e12) return `₲ ${(n / 1e12).toFixed(2)} B`;
        if (n >= 1e9) return `₲ ${(n / 1e9).toFixed(1)} MM`;
        if (n >= 1e6) return `₲ ${(n / 1e6).toFixed(0)} M`;
        return `₲ ${n.toLocaleString()}`;
      }};

      const clampText = (s, max = 60) => {{
        const str = String(s || "");
        return str.length > max ? str.slice(0, max - 1) + "…" : str;
      }};

      // Desglose por objeto (mock, igual que veníamos usando)
      const entidadesData = {{
        "Ministerio de Educación y Ciencias": {{
          codigo: "20",
          nivel: "Poder Ejecutivo",
          pgn2025: {{ 100: 6310000000000, 200: 485000000000, 300: 2350000000000, 400: 165000000000, 500: 285000000000, 800: 105000000000, 900: 0 }},
          pgn2026: {{ 100: 6850000000000, 200: 545000000000, 300: 2580000000000, 400: 185000000000, 500: 320000000000, 800: 120000000000, 900: 0 }}
        }},
        "Ministerio de Salud Pública": {{
          codigo: "21",
          nivel: "Poder Ejecutivo",
          pgn2025: {{ 100: 4150000000000, 200: 720000000000, 300: 3280000000000, 400: 485000000000, 500: 680000000000, 800: 185000000000, 900: 0 }},
          pgn2026: {{ 100: 4650000000000, 200: 850000000000, 300: 3520000000000, 400: 540000000000, 500: 780000000000, 800: 220000000000, 900: 0 }}
        }},
        "Ministerio de Economía y Finanzas": {{
          codigo: "12",
          nivel: "Poder Ejecutivo",
          pgn2025: {{ 100: 520000000000, 200: 145000000000, 300: 92000000000, 400: 38000000000, 500: 65000000000, 800: 16300000000000, 900: 4840000000000 }},
          pgn2026: {{ 100: 555000000000, 200: 158000000000, 300: 98000000000, 400: 42000000000, 500: 72000000000, 800: 17500000000000, 900: 5275000000000 }}
        }},
      }};

      const objetosGasto = {{
        100: {{ nombre: "Servicios Personales", color: "#0ea5e9" }},
        200: {{ nombre: "Servicios No Personales", color: "#8b5cf6" }},
        300: {{ nombre: "Bienes de Consumo e Insumos", color: "#10b981" }},
        400: {{ nombre: "Bienes de Cambio", color: "#f59e0b" }},
        500: {{ nombre: "Inversión Física", color: "#ef4444" }},
        800: {{ nombre: "Transferencias", color: "#ec4899" }},
        900: {{ nombre: "Otros Gastos", color: "#6b7280" }},
      }};

      function sumObj(obj) {{
        return Object.values(obj || {{}}).reduce((a, b) => a + (Number(b) || 0), 0);
      }}

      function RankTable({{ title, subtitle, rows, type }}) {{
        return (
          <div className="card">
            <div style={{{{ display:"flex", justifyContent:"space-between", alignItems:"baseline", gap:12 }}}}>
              <div>
                <h3 style={{{{ margin:0, fontSize:16, fontWeight:800 }}}}>{title}</h3>
                <p style={{{{ margin:"6px 0 0", fontSize:12, color:"#64748b" }}}}>{subtitle}</p>
              </div>
            </div>

            <table>
              <thead>
                <tr>
                  <th style={{{{ textAlign:"right" }}}}>#</th>
                  <th style={{{{ textAlign:"center" }}}}>Código</th>
                  <th>Organismo</th>
                  {{type === "var" ? <th style={{{{ textAlign:"right" }}}}>Var. %</th> : null}}
                  <th style={{{{ textAlign:"right" }}}}>Monto 2026</th>
                </tr>
              </thead>
              <tbody>
                {{rows.map((r, idx) => (
                  <tr key={{`${r.codigo}-${idx}`}}>
                    <td style={{{{ textAlign:"right", color:"#94a3b8" }}}}>{{idx+1}}</td>
                    <td style={{{{ textAlign:"center" }}}}><span className="mono">{{r.codigo || "—"}}</span></td>
                    <td>{{clampText(r.organismo, 60)}}</td>
                    {{type === "var" ? (
                      <td style={{{{ textAlign:"right" }}}}><span className="pill-green">+{{Number(r.variacion_pct || 0).toFixed(1)}}%</span></td>
                    ) : null}}
                    <td style={{{{ textAlign:"right", color:"#8b5cf6" }}}}><span className="mono">{{formatGs(r.monto_2026)}}</span></td>
                  </tr>
                ))}}
              </tbody>
            </table>
          </div>
        );
      }}

      function App() {{
        const [selectedEntity, setSelectedEntity] = React.useState("Ministerio de Educación y Ciencias");
        const [comparisonMode, setComparisonMode] = React.useState("absoluto");

        const records = (window.__PGN_DATA__ && window.__PGN_DATA__.records) ? window.__PGN_DATA__.records : [];

        const top15Monto2026 = React.useMemo(() => {{
          return records
            .map(r => ({{
              codigo: r.codigo,
              organismo: r.item_2026 || r.item_2025 || "",
              monto_2026: Number(r.monto_2026 || 0),
            }}))
            .sort((a,b) => b.monto_2026 - a.monto_2026)
            .slice(0, 15);
        }}, [records]);

        const top15VarPos = React.useMemo(() => {{
          return records
            .map(r => ({{
              codigo: r.codigo,
              organismo: r.item_2026 || r.item_2025 || "",
              monto_2026: Number(r.monto_2026 || 0),
              variacion_pct: Number(r.variacion_pct),
            }}))
            .filter(r => Number.isFinite(r.variacion_pct) && r.variacion_pct > 0)
            .sort((a,b) => b.variacion_pct - a.variacion_pct)
            .slice(0, 15);
        }}, [records]);

        const entityKeys = React.useMemo(() => Object.keys(entidadesData).sort(), []);
        const entityData = entidadesData[selectedEntity];

        const comparisonData = React.useMemo(() => {{
          if (!entityData) return [];
          return Object.keys(objetosGasto)
            .map((key) => {{
              const pgn2025 = entityData.pgn2025?.[key] || 0;
              const pgn2026 = entityData.pgn2026?.[key] || 0;
              const variacion = pgn2025 > 0 ? ((pgn2026 - pgn2025) / pgn2025) * 100 : 0;
              return {{
                objeto: key,
                nombre: objetosGasto[key].nombre,
                nombreCorto: objetosGasto[key].nombre.split(" ").slice(0,2).join(" "),
                pgn2025,
                pgn2026,
                variacion: Number.isFinite(variacion) ? Number(variacion.toFixed(1)) : 0,
                color: objetosGasto[key].color,
              }};
            }})
            .filter(d => d.pgn2025 > 0 || d.pgn2026 > 0);
        }}, [entityData]);

        const totalData = React.useMemo(() => {{
          if (!entityData) return {{ total2025: 0, total2026: 0, variacion: 0 }};
          const total2025 = sumObj(entityData.pgn2025);
          const total2026 = sumObj(entityData.pgn2026);
          const variacion = total2025 > 0 ? ((total2026 - total2025) / total2025) * 100 : 0;
          return {{ total2025, total2026, variacion: Number(variacion.toFixed(1)) }};
        }}, [entityData]);

        const pieData2025 = comparisonData.map(d => ({{ name: d.nombreCorto, value: d.pgn2025, color: d.color }}));
        const pieData2026 = comparisonData.map(d => ({{ name: d.nombreCorto, value: d.pgn2026, color: d.color }}));

        return (
          <div className="wrap">
            <div className="header">
              <div style={{{{ display:"flex", alignItems:"center", gap:16 }}}}>
                <div style={{{{
                  width:48, height:48, borderRadius:12,
                  background:"linear-gradient(135deg,#0ea5e9,#8b5cf6)",
                  display:"flex", alignItems:"center", justifyContent:"center",
                  fontSize:24
                }}}}>🇵🇾</div>
                <div>
                  <h1 className="title">Dashboard PGN Paraguay</h1>
                  <p className="subtitle">Análisis Comparativo del Presupuesto General de la Nación 2025 vs 2026</p>
                </div>
              </div>
              <p style={{{{ margin:"12px 0 0", fontSize:12, color:"#64748b" }}}}>
                Fuente: MEF | SITUFIN — Rankings desde el Excel (presup_py_v3.xlsx)
              </p>
            </div>

            <div className="grid" style={{{{ marginBottom:24 }}}}>
              <RankTable
                title="Top 15 — Organismos con mayor gasto asignado (2026)"
                subtitle="Ranking institucional (monto 2026)"
                rows={top15Monto2026}
                type="monto"
              />
              <RankTable
                title="Top 15 — Mayor variación positiva (2026 vs 2025)"
                subtitle="Ranking institucional (variación %)"
                rows={top15VarPos}
                type="var"
              />
            </div>

            <div className="card" style={{{{ marginBottom:24 }}}}>
              <label style={{{{ display:"block", marginBottom:8, fontSize:14, color:"#94a3b8", fontWeight:800 }}}}>
                📊 Seleccionar Organismo (mock para desglose por objeto)
              </label>
              <select value={selectedEntity} onChange={(e) => setSelectedEntity(e.target.value)}>
                {entityKeys.map((k) => <option key={k} value={k}>{k}</option>)}
              </select>
              <div className="chips">
                <span className="chip chip-blue">Código: {entityData?.codigo || "—"}</span>
                <span className="chip chip-purple">{entityData?.nivel || "—"}</span>
              </div>
            </div>

            <div className="grid" style={{{{ marginBottom:24, gridTemplateColumns:"repeat(auto-fit, minmax(280px, 1fr))" }}}}>
              <div className="card" style={{{{ border:"1px solid rgba(14,165,233,0.3)", background:"linear-gradient(135deg, rgba(14,165,233,0.2) 0%, rgba(14,165,233,0.05) 100%)" }}}}>
                <div style={{{{ fontSize:12, color:"#0ea5e9", fontWeight:900, letterSpacing:1, textTransform:"uppercase" }}}}>PGN 2025</div>
                <div style={{{{ fontSize:28, fontWeight:900, marginTop:8 }}}}>{formatGs(totalData.total2025)}</div>
              </div>
              <div className="card" style={{{{ border:"1px solid rgba(139,92,246,0.3)", background:"linear-gradient(135deg, rgba(139,92,246,0.2) 0%, rgba(139,92,246,0.05) 100%)" }}}}>
                <div style={{{{ fontSize:12, color:"#8b5cf6", fontWeight:900, letterSpacing:1, textTransform:"uppercase" }}}}>PGN 2026</div>
                <div style={{{{ fontSize:28, fontWeight:900, marginTop:8 }}}}>{formatGs(totalData.total2026)}</div>
              </div>
              <div className="card" style={{{{
                border:`1px solid ${totalData.variacion >= 0 ? "rgba(16,185,129,0.3)" : "rgba(239,68,68,0.3)"}`,
                background:`linear-gradient(135deg, ${totalData.variacion >= 0 ? "rgba(16,185,129,0.2)" : "rgba(239,68,68,0.2)"} 0%, ${totalData.variacion >= 0 ? "rgba(16,185,129,0.05)" : "rgba(239,68,68,0.05)"} 100%)`
              }}}}>
                <div style={{{{ fontSize:12, color: totalData.variacion >= 0 ? "#10b981" : "#ef4444", fontWeight:900, letterSpacing:1, textTransform:"uppercase" }}}}>Variación</div>
                <div style={{{{ fontSize:28, fontWeight:900, marginTop:8 }}}}>
                  {totalData.variacion >= 0 ? "+" : ""}{totalData.variacion}%
                </div>
              </div>
            </div>

            <div className="card" style={{{{ marginBottom:24 }}}}>
              <h2 style={{{{ margin:"0 0 20px", fontSize:18, fontWeight:900 }}}}>📈 Desglose por tipo de gasto (objeto) — mock</h2>
              <div className="btnrow">
                <button className={comparisonMode === "absoluto" ? "active" : ""} onClick={() => setComparisonMode("absoluto")}>Valores</button>
                <button className={comparisonMode === "variacion" ? "active" : ""} onClick={() => setComparisonMode("variacion")}>Variación %</button>
              </div>

              <div style={{{{ height:360 }}}}>
                <ResponsiveContainer width="100%" height="100%">
                  {comparisonMode === "absoluto" ? (
                    <BarChart data={comparisonData} margin={{{{ top:20, right:30, left:20, bottom:70 }}}}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                      <XAxis dataKey="nombreCorto" angle={-45} textAnchor="end" fontSize={11} stroke="#64748b" height={90} />
                      <YAxis stroke="#64748b" fontSize={11}
                        tickFormatter={(v) => v >= 1e12 ? `${(v/1e12).toFixed(1)}B` : v >= 1e9 ? `${(v/1e9).toFixed(0)}MM` : `${(v/1e6).toFixed(0)}M`}
                      />
                      <Tooltip contentStyle={{{{ background:"#1e293b", border:"1px solid #334155", borderRadius:10 }}}} formatter={(value) => formatGs(value)} />
                      <Legend />
                      <Bar dataKey="pgn2025" name="PGN 2025" fill="#0ea5e9" radius={[4,4,0,0]} />
                      <Bar dataKey="pgn2026" name="PGN 2026" fill="#8b5cf6" radius={[4,4,0,0]} />
                    </BarChart>
                  ) : (
                    <BarChart data={comparisonData} margin={{{{ top:20, right:30, left:20, bottom:70 }}}}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                      <XAxis dataKey="nombreCorto" angle={-45} textAnchor="end" fontSize={11} stroke="#64748b" height={90} />
                      <YAxis stroke="#64748b" fontSize={11} unit="%" />
                      <Tooltip contentStyle={{{{ background:"#1e293b", border:"1px solid #334155", borderRadius:10 }}}} formatter={(value) => `${value}%`} />
                      <Bar dataKey="variacion" name="Variación %" radius={[4,4,0,0]}>
                        {comparisonData.map((entry, index) => (
                          <Cell key={`c-${index}`} fill={entry.variacion >= 0 ? "#10b981" : "#ef4444"} />
                        ))}
                      </Bar>
                    </BarChart>
                  )}
                </ResponsiveContainer>
              </div>
            </div>

            <div className="grid" style={{{{ marginBottom:24, gridTemplateColumns:"repeat(auto-fit, minmax(350px, 1fr))" }}}}>
              <div className="card">
                <h3 style={{{{ margin:"0 0 16px", fontSize:16, fontWeight:900, color:"#0ea5e9" }}}}>🥧 Distribución PGN 2025</h3>
                <div style={{{{ height:280 }}}}>
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie data={pieData2025} cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={2} dataKey="value">
                        {pieData2025.map((entry, index) => <Cell key={`p25-${index}`} fill={entry.color} />)}
                      </Pie>
                      <Tooltip contentStyle={{{{ background:"#1e293b", border:"1px solid #334155", borderRadius:10, fontSize:12 }}}} formatter={(value) => formatGs(value)} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className="card">
                <h3 style={{{{ margin:"0 0 16px", fontSize:16, fontWeight:900, color:"#8b5cf6" }}}}>🥧 Distribución PGN 2026</h3>
                <div style={{{{ height:280 }}}}>
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie data={pieData2026} cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={2} dataKey="value">
                        {pieData2026.map((entry, index) => <Cell key={`p26-${index}`} fill={entry.color} />)}
                      </Pie>
                      <Tooltip contentStyle={{{{ background:"#1e293b", border:"1px solid #334155", borderRadius:10, fontSize:12 }}}} formatter={(value) => formatGs(value)} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>

            <div className="footer">
              <div>✅ Rankings salen del Excel del repo (<span className="mono">presup_py_v3.xlsx</span>).</div>
              <div style={{{{ marginTop:6, fontSize:11, color:"#475569" }}}}>
                Próximo paso: reemplazar el desglose “mock” por el desglose real por objeto si lo tenés.
              </div>
            </div>
          </div>
        );
      }}

      const root = ReactDOM.createRoot(document.getElementById("root"));
      root.render(<App />);
    </script>
  </body>
</html>
"""

# Render: height grande y sin scrolling extra (ya hay scroll del browser)
components.html(html, height=1600, scrolling=True)
