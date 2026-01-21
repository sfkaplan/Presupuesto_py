# PGN Dashboard Paraguay (React + Vite)

Este frontend replica la UI en React y usa **Recharts**.

## Datos
Los rankings (Top 15) se leen desde `src/data/pgn.json` (generado desde tu Excel).

> El desglose por objeto (100/200/...) está en **mock** por ahora hasta integrar la tabla real.

## Desarrollo local
```bash
npm install
npm run dev
```

## Deploy gratis (recomendado)
### Opción A: Cloudflare Pages (gratis)
- Build command: `npm run build`
- Build output: `dist`

### Opción B: Vercel (gratis)
Importás el repo y Vercel detecta Vite automáticamente.
