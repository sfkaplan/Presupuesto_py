import React, { useMemo, useState } from "react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  PieChart, Pie, Cell
} from "recharts";
import pgn from "./data/pgn.json";

/* =========================
   Helpers
========================= */
const formatGs = (num) => {
  const n = Number(num || 0);
  if (n >= 1e12) return `₲ ${(n / 1e12).toFixed(2)} Bill.`;
  if (n >= 1e9) return `₲ ${(n / 1e9).toFixed(1)} MM`;
  if (n >= 1e6) return `₲ ${(n / 1e6).toFixed(0)} M`;
  return `₲ ${n.toLocaleString()}`;
};

const sumObj = (obj) =>
  Object.values(obj || {}).reduce((a, b) => a + (Number(b) || 0), 0);

/* =========================
   Objetos de Gasto (FUENTE ÚNICA)
========================= */
const objetosGasto = {
  100: {
    nombre: "Servicios Personales",
    descripcion: "Sueldos, salarios, beneficios sociales del personal",
    color: "#3b82f6"
  },
  200: {
    nombre: "Servicios No Personales",
    descripcion: "Servicios básicos, alquileres, mantenimiento, seguros",
    color: "#10b981"
  },
  300: {
    nombre: "Bienes de Consumo e Insumos",
    descripcion: "Alimentos, medicamentos, útiles de oficina, combustibles",
    color: "#f59e0b"
  },
  400: {
    nombre: "Bienes de Cambio",
    descripcion: "Equipos, muebles, vehículos, construcciones",
    color: "#8b5cf6"
  },
  500: {
    nombre: "Inversión Física",
    descripcion: "Obras, infraestructura, equipamiento de capital",
    color: "#ef4444"
  },
  600: {
    nombre: "Inversión Financiera",
    descripcion: "Adquisición de activos financieros",
    color: "#14b8a6"
  },
  700: {
    nombre: "Servicio de Deuda Pública",
    descripcion: "Pago de intereses y amortización de la deuda pública",
    color: "#f43f5e"
  },
  800: {
    nombre: "Transferencias",
    descripcion: "Transferencias a gobiernos, ONGs, subsidios sociales",
    color: "#ec4899"
  },
  900: {
    nombre: "Otros Gastos",
    descripcion: "Otros gastos no clasificados en categorías anteriores",
    color: "#6b7280"
  }
};

/* =========================
   MOCK – Desglose por organismo
========================= */
const entidadesData = {
  "Ministerio de Educación y Ciencias": {
    codigo: "20",
    nivel: "Poder Ejecutivo",
    pgn2025: { 100: 5900000000000, 200: 2500000000000, 300: 735000000000, 400: 490000000000, 500: 220000000000, 700: 25000000000 },
    pgn2026: { 100: 6100000000000, 200: 2500000000000, 300: 763000000000, 400: 508000000000, 500: 229000000000, 700: 25000000000 }
  }
};

/* =========================
   Componentes
========================= */
function ObjetoGastoDetalleTable({ data }) {
  return (
    <div className="card" style={{ marginTop: 16 }}>
      <h2 className="h2">Detalle por Objeto de Gasto</h2>

      <table>
        <thead>
          <tr>
            <th>Objeto</th>
            <th style={{ textAlign: "right" }}>2025</th>
            <th style={{ textAlign: "right" }}>2026</th>
            <th style={{ textAlign: "right" }}>Var %</th>
          </tr>
        </thead>
        <tbody>
          {data.map((d) => (
            <tr key={d.objeto}>
              <td>
                <span
                  style={{
                    display: "inline-block",
                    width: 12,
                    height: 12,
                    borderRadius: 4,
                    background: d.color,
                    marginRight: 8
                  }}
                />
                <strong>{d.objeto}</strong> – {objetosGasto[d.objeto].nombre}
              </td>
              <td style={{ textAlign: "right" }}>{formatGs(d.pgn2025)}</td>
              <td style={{ textAlign: "right", color: "#6366f1" }}>
                {formatGs(d.pgn2026)}
              </td>
              <td
                style={{
                  textAlign: "right",
                  color: d.variacion >= 0 ? "#16a34a" : "#dc2626",
                  fontWeight: 700
                }}
              >
                {d.variacion >= 0 ? "+" : ""}
                {d.variacion}%
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ClasificacionObjetoGasto() {
  return (
    <div className="card" style={{ marginTop: 16 }}>
      <h2 className="h2">Clasificación por Objeto del Gasto</h2>

      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        {Object.entries(objetosGasto).map(([codigo, obj]) => (
          <div
            key={codigo}
            style={{
              display: "flex",
              gap: 16,
              alignItems: "center",
              padding: 16,
              borderRadius: 12,
              background: "rgba(255,255,255,0.03)"
            }}
          >
            <div
              style={{
                width: 36,
                height: 36,
                borderRadius: 8,
                background: obj.color
              }}
            />
            <div>
              <strong>
                {codigo} – {obj.nombre}
              </strong>
              <div style={{ fontSize: 13, color: "#94a3b8", marginTop: 4 }}>
                {obj.descripcion}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

/* =========================
   App principal
========================= */
export default function App() {
  const records = pgn.records || [];

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

  const selectedEntity = "Ministerio de Educación y Ciencias";
  const entityData = entidadesData[selectedEntity];

  const comparisonData = useMemo(() => {
    if (!entityData) return [];
    return Object.keys(entityData.pgn2025).map((key) => {
      const p2025 = entityData.pgn2025[key] || 0;
      const p2026 = entityData.pgn2026[key] || 0;
      const varPct = p2025 > 0 ? ((p2026 - p2025) / p2025) * 100 : 0;

      return {
        objeto: key,
        pgn2025: p2025,
        pgn2026: p2026,
        variacion: Number(varPct.toFixed(1)),
        color: objetosGasto[key].color
      };
    });
  }, [entityData]);

  return (
    <div className="wrap">
      <h1 className="title">PGN Dashboard Paraguay 2025–2026</h1>

      <ObjetoGastoDetalleTable data={comparisonData} />
      <ClasificacionObjetoGasto />
    </div>
  );
}
