/**
 * Aplica configuración al proyecto Vercel vía API (sin abrir el panel).
 *
 * Prerrequisito: token en https://vercel.com/account/tokens
 *
 * Uso (PowerShell):
 *   $env:VERCEL_TOKEN="tu_token"
 *   $env:API_URL="https://TU-BACKEND.onrender.com/api"
 *   node scripts/vercel-apply-config.mjs
 *
 * API_URL es la URL pública de tu API FastAPI en Render (termina en /api).
 *
 * Referencia API: https://vercel.com/docs/rest-api/reference/endpoints/projects/update-an-existing-project
 */

const API = 'https://api.vercel.com';

const TEAM_SLUG = process.env.VERCEL_TEAM_SLUG || 'maxlive-hotmailes-projects';
const PROJECT = process.env.VERCEL_PROJECT_NAME || 'marketing-copilot';
const TOKEN = process.env.VERCEL_TOKEN;
const API_URL = (process.env.API_URL || '').trim();

async function api(path, opts = {}) {
  const res = await fetch(`${API}${path}`, {
    ...opts,
    headers: {
      Authorization: `Bearer ${TOKEN}`,
      'Content-Type': 'application/json',
      ...opts.headers,
    },
  });
  const text = await res.text();
  let data;
  try {
    data = text ? JSON.parse(text) : {};
  } catch {
    data = { raw: text };
  }
  if (!res.ok) {
    const err = new Error(`${opts.method || 'GET'} ${path} → ${res.status}`);
    err.body = data;
    throw err;
  }
  return data;
}

async function getTeamId() {
  const { teams } = await api('/v2/teams');
  const t = teams?.find((x) => x.slug === TEAM_SLUG);
  if (!t) {
    console.error('Equipos disponibles:', teams?.map((x) => x.slug).join(', ') || 'ninguno');
    throw new Error(`No se encontró el equipo con slug "${TEAM_SLUG}"`);
  }
  return t.id;
}

async function main() {
  if (!TOKEN) {
    console.error(`
Falta VERCEL_TOKEN.

1) Crea un token: https://vercel.com/account/tokens
2) En PowerShell:
   $env:VERCEL_TOKEN="tu_token"
   $env:API_URL="https://xxxx.onrender.com/api"
   node scripts/vercel-apply-config.mjs
`);
    process.exit(1);
  }

  const teamId = await getTeamId();
  console.log(`Equipo: ${TEAM_SLUG} (${teamId})`);
  const q = new URLSearchParams({ teamId });

  const patchBody = {
    rootDirectory: 'frontend',
    framework: 'angular',
    installCommand: 'npm install',
    buildCommand: 'npm run build:vercel',
    outputDirectory: 'dist/marketing-copilot/browser',
  };

  console.log(`Actualizando proyecto "${PROJECT}"…`);
  await api(`/v9/projects/${encodeURIComponent(PROJECT)}?${q}`, {
    method: 'PATCH',
    body: JSON.stringify(patchBody),
  });
  console.log('  ✓ Root Directory = frontend, build Angular, output dist/...');

  if (API_URL) {
    console.log(`Creando variable API_URL (production + preview)…`);
    await api(`/v10/projects/${encodeURIComponent(PROJECT)}/env?${q}&upsert=true`, {
      method: 'POST',
      body: JSON.stringify({
        key: 'API_URL',
        value: API_URL,
        type: 'encrypted',
        target: ['production', 'preview'],
      }),
    });
    console.log(`  ✓ API_URL = ${API_URL}`);
  } else {
    console.log(
      '\n  Omitido API_URL (no estaba definido). Cuando tengas la URL de Render:\n  $env:API_URL="https://tu-servicio.onrender.com/api"\n  node scripts/vercel-apply-config.mjs\n'
    );
  }

  console.log(`
Listo. Falta solo (una vez) conectar Git en la web si aún no está:
  https://vercel.com/${TEAM_SLUG}/${PROJECT}/settings/git

Luego en Vercel → Deployments → "Redeploy" el último deployment (o haz un commit push).
`);
}

main().catch((e) => {
  console.error(e.message);
  if (e.body) console.error(JSON.stringify(e.body, null, 2));
  process.exit(1);
});
