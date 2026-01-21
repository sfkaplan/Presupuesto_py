import React, { useMemo, useState } from "react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  PieChart, Pie, Cell
} from "recharts";
import pgn from "./data/pgn.json";

// --- Helpers
const formatGs = (num) => {
  const n = Number(num || 0);
  if (n >= 1e12) return `₲ ${(n / 1e12).toFixed(2)} B`;
  if (n >= 1e9) return `₲ ${(n / 1e9).toFixed(1)} MM`;
  if (n >= 1e6) return `₲ ${(n / 1e6).toFixed(0)} M`;
  return `₲ ${n.toLocaleString()}`;
};

const clampText = (s, max = 60) => {
  const str = String(s || "");
  return str.length > max ? str.slice(0, max - 1) + "…" : str;
};

const sumObj = (obj) => Object.values(obj || {}).reduce((a, b) => a + (Number(b) || 0), 0);

// --- MOCK: desglose por objeto (se reemplaza cuando tengamos tabla real)
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

function RankTable({ title, subtitle, rows, type }) {
  return (
    <div className="card">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", gap: 12 }}>
        <div>
          <h3 className="h3">{title}</h3>
          <p className="muted">{subtitle}</p>
        </div>
      </div>

      <table>
        <thead>
          <tr>
            <th style={{ textAlign: "right" }}>#</th>
            <th style={{ textAlign: "center" }}>Código</th>
            <th>Organismo</th>
            {type === "var" ? <th style={{ textAlign: "right" }}>Var. %</th> : null}
            <th style={{ textAlign: "right" }}>Monto 2026</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r, idx) => (
            <tr key={`${r.codigo || "NA"}-${idx}`}>
              <td style={{ textAlign: "right", color: "#94a3b8" }}>{idx + 1}</td>
              <td style={{ textAlign: "center" }}><span className="mono">{r.codigo || "—"}</span></td>
              <td>{clampText(r.organismo, 60)}</td>
              {type === "var" ? (
                <td style={{ textAlign: "right" }}>
                  <span className="pill-green">+{Number(r.variacion_pct || 0).toFixed(1)}%</span>
                </td>
              ) : null}
              <td style={{ textAlign: "right", color: "#8b5cf6" }}><span className="mono">{formatGs(r.monto_2026)}</span></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function App() {
  const records = Array.isArray(pgn?.records) ? pgn.records : [];

  const top15Monto2026 = useMemo(() => {
    return records
      .map((r) => ({
        codigo: r.codigo,
        organismo: r.item_2026 || r.item_2025 || "",
        monto_2026: Number(r.monto_2026 || 0)
      }))
      .sort((a, b) => b.monto_2026 - a.monto_2026)
      .slice(0, 15);
  }, [records]);

  const top15VarPos = useMemo(() => {
    return records
      .map((r) => ({
        codigo: r.codigo,
        organismo: r.item_2026 || r.item_2025 || "",
        monto_2026: Number(r.monto_2026 || 0),
        variacion_pct: Number(r.variacion_pct)
      }))
      .filter((r) => Number.isFinite(r.variacion_pct) && r.variacion_pct > 0)
      .sort((a, b) => b.variacion_pct - a.variacion_pct)
      .slice(0, 15);
  }, [records]);

  const entityKeys = useMemo(() => Object.keys(entidadesData).sort(), []);
  const [selectedEntity, setSelectedEntity] = useState(entityKeys[0] || "");
  const [comparisonMode, setComparisonMode] = useState("absoluto");

  const entityData = entidadesData[selectedEntity];

  const comparisonData = useMemo(() => {
    if (!entityData) return [];
    return Object.keys(objetosGasto)
      .map((key) => {
        const pgn2025 = entityData.pgn2025?.[key] ?? 0;
        const pgn2026 = entityData.pgn2026?.[key] ?? 0;
        const variacion = pgn2025 > 0 ? ((pgn2026 - pgn2025) / pgn2025) * 100 : 0;
        return {
          objeto: key,
          nombre: objetosGasto[key].nombre,
          nombreCorto: objetosGasto[key].nombre.split(" ").slice(0, 2).join(" "),
          pgn2025,
          pgn2026,
          variacion: Number.isFinite(variacion) ? Number(variacion.toFixed(1)) : 0,
          color: objetosGasto[key].color
        };
      })
      .filter((d) => d.pgn2025 > 0 || d.pgn2026 > 0);
  }, [entityData]);

  const totalData = useMemo(() => {
    if (!entityData) return { total2025: 0, total2026: 0, variacion: 0 };
    const total2025 = sumObj(entityData.pgn2025);
    const total2026 = sumObj(entityData.pgn2026);
    const variacion = total2025 > 0 ? ((total2026 - total2025) / total2025) * 100 : 0;
    return { total2025, total2026, variacion: Number(variacion.toFixed(1)) };
  }, [entityData]);

  const pieData2025 = comparisonData.map((d) => ({ name: d.nombreCorto, value: d.pgn2025, color: d.color }));
  const pieData2026 = comparisonData.map((d) => ({ name: d.nombreCorto, value: d.pgn2026, color: d.color }));

  return (
    <div className="wrap">
      <div className="header">
        <div className="headerRow">
          <div className="flag">🇵🇾</div>
          <div>
            <h1 className="title">Dashboard PGN Paraguay</h1>
            <p className="subtitle">Análisis Comparativo del Presupuesto General de la Nación 2025 vs 2026</p>
          </div>
        </div>
        <p className="small">Fuente: MEF | SITUFIN — Rankings desde Excel (presup_py_v3.xlsx → JSON)</p>
      </div>

      <div className="grid">
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

      <div className="card" style={{ marginTop: 16 }}>
        <label className="label">📊 Seleccionar Organismo (mock para desglose por objeto)</label>
        <select value={selectedEntity} onChange={(e) => setSelectedEntity(e.target.value)}>
          {entityKeys.map((k) => (
            <option key={k} value={k}>{k}</option>
          ))}
        </select>

        <div className="chips">
          <span className="chip chip-blue">Código: {entityData?.codigo ?? "—"}</span>
          <span className="chip chip-purple">{entityData?.nivel ?? "—"}</span>
        </div>
      </div>

      <div className="cards3">
        <div className="card cardBlue">
          <div className="kpiLabel blue">PGN 2025</div>
          <div className="kpiValue">{formatGs(totalData.total2025)}</div>
        </div>
        <div className="card cardPurple">
          <div className="kpiLabel purple">PGN 2026</div>
          <div className="kpiValue">{formatGs(totalData.total2026)}</div>
        </div>
        <div className={`card ${totalData.variacion >= 0 ? "cardGreen" : "cardRed"}`}>
          <div className={`kpiLabel ${totalData.variacion >= 0 ? "green" : "red"}`}>Variación</div>
          <div className="kpiValue">{totalData.variacion >= 0 ? "+" : ""}{totalData.variacion}%</div>
        </div>
      </div>

      <div className="card" style={{ marginTop: 16 }}>
        <h2 className="h2">📈 Desglose por tipo de gasto (objeto) — mock</h2>

        <div className="btnrow">
          <button className={comparisonMode === "absoluto" ? "active" : ""} onClick={() => setComparisonMode("absoluto")}>Valores</button>
          <button className={comparisonMode === "variacion" ? "active" : ""} onClick={() => setComparisonMode("variacion")}>Variación %</button>
        </div>

        <div style={{ height: 360 }}>
          <ResponsiveContainer width="100%" height="100%">
            {comparisonMode === "absoluto" ? (
              <BarChart data={comparisonData} margin={{ top: 20, right: 30, left: 20, bottom: 70 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="nombreCorto" angle={-45} textAnchor="end" fontSize={11} stroke="#64748b" height={90} />
                <YAxis stroke="#64748b" fontSize={11} tickFormatter={(v) => v >= 1e12 ? `${(v / 1e12).toFixed(1)}B` : v >= 1e9 ? `${(v / 1e9).toFixed(0)}MM` : `${(v / 1e6).toFixed(0)}M`} />
                <Tooltip contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 10 }} formatter={(v) => formatGs(v)} />
                <Legend />
                <Bar dataKey="pgn2025" name="PGN 2025" fill="#0ea5e9" radius={[4, 4, 0, 0]} />
                <Bar dataKey="pgn2026" name="PGN 2026" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
              </BarChart>
            ) : (
              <BarChart data={comparisonData} margin={{ top: 20, right: 30, left: 20, bottom: 70 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="nombreCorto" angle={-45} textAnchor="end" fontSize={11} stroke="#64748b" height={90} />
                <YAxis stroke="#64748b" fontSize={11} unit="%" />
                <Tooltip contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 10 }} formatter={(v) => `${v}%`} />
                <Bar dataKey="variacion" name="Variación %" radius={[4, 4, 0, 0]}>
                  {comparisonData.map((entry, index) => (
                    <Cell key={`c-${index}`} fill={entry.variacion >= 0 ? "#10b981" : "#ef4444"} />
                  ))}
                </Bar>
              </BarChart>
            )}
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid2">
        <div className="card">
          <h3 className="h3 blue">🥧 Distribución PGN 2025</h3>
          <div style={{ height: 280 }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={pieData2025} cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={2} dataKey="value">
                  {pieData2025.map((entry, index) => (
                    <Cell key={`p25-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 10, fontSize: 12 }} formatter={(v) => formatGs(v)} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card">
          <h3 className="h3 purple">🥧 Distribución PGN 2026</h3>
          <div style={{ height: 280 }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={pieData2026} cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={2} dataKey="value">
                  {pieData2026.map((entry, index) => (
                    <Cell key={`p26-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 10, fontSize: 12 }} formatter={(v) => formatGs(v)} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="footer">
        ✅ UI React real (Vite). Rankings desde JSON. Desglose por objeto aún mock hasta integrar tabla real.
      </div>
    </div>
  );
}
