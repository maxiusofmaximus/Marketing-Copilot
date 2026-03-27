/**
 * Escribe environment.prod.ts antes del build usando API_URL (Vercel / CI).
 * En Vercel: Project Settings → Environment Variables → API_URL = https://xxx.onrender.com/api
 */
const fs = require('fs');
const path = require('path');

const apiUrl =
  process.env.API_URL ||
  process.env.NG_APP_API_URL ||
  '';

const finalUrl =
  apiUrl.trim() ||
  'https://REPLACE_WITH_YOUR_RENDER_API_URL/api';

const out = `// Generado por scripts/inject-env.cjs — no editar a mano en CI
export const environment = {
  production: true,
  apiUrl: ${JSON.stringify(finalUrl)},
};
`;

const target = path.join(__dirname, '..', 'src', 'environments', 'environment.prod.ts');
fs.writeFileSync(target, out, 'utf8');
console.log('[inject-env] apiUrl =', finalUrl);
if (!apiUrl.trim()) {
  console.warn('[inject-env] API_URL no definida; usando placeholder. Configura API_URL en Vercel.');
}
