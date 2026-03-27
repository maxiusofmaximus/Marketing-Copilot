/**
 * Abre Edge (o Chromium) con perfil persistente para iniciar sesión en Vercel o Render.
 * Uso:
 *   npm install
 *   npm run browser:vercel
 *   npm run browser:render
 * Cuando termines de iniciar sesión en el navegador, pulsa ENTER en esta terminal.
 */
import { chromium } from 'playwright';
import readline from 'readline';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.join(__dirname, '..');
const profileDir = path.join(root, '.playwright-user-data');

const TARGETS = {
  vercel: {
    startUrl: 'https://vercel.com/login',
    storageJson: path.join(root, 'playwright-vercel-storage.json'),
  },
  render: {
    startUrl: 'https://dashboard.render.com/login',
    storageJson: path.join(root, 'playwright-render-storage.json'),
  },
};

const name = (process.argv[2] || 'vercel').toLowerCase();
const t = TARGETS[name];
if (!t) {
  console.error('Uso: node scripts/playwright-manual-login.mjs [vercel|render]');
  process.exit(1);
}

fs.mkdirSync(profileDir, { recursive: true });

const useEdge = process.platform === 'win32';
const context = await chromium.launchPersistentContext(profileDir, {
  headless: false,
  ...(useEdge ? { channel: 'msedge' } : {}),
  viewport: { width: 1280, height: 800 },
});

const page = context.pages()[0] || (await context.newPage());
await page.goto(t.startUrl, { waitUntil: 'domcontentloaded' });

console.log('\n========================================');
console.log(`  Navegador abierto → ${name.toUpperCase()}`);
console.log('  Inicia sesión en la ventana del navegador.');
console.log('  Cuando hayas terminado, vuelve aquí y pulsa ENTER.');
console.log('========================================\n');

await new Promise((resolve) => {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  rl.question('Pulsa ENTER cuando el login esté listo... ', () => {
    rl.close();
    resolve();
  });
});

await context.storageState({ path: t.storageJson });
console.log(`\nEstado de cookies guardado en:\n  ${t.storageJson}`);
console.log(`Perfil persistente (próximas ejecuciones):\n  ${profileDir}\n`);

await context.close();
process.exit(0);
