/**
 * Abre el proyecto marketing-copilot en Vercel (sesión guardada).
 * npm run browser:vercel:project
 */
import readline from 'readline';
import { chromium } from 'playwright';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.join(__dirname, '..');
const storage = path.join(root, 'playwright-vercel-storage.json');

if (!fs.existsSync(storage)) {
  console.error('No existe playwright-vercel-storage.json. Ejecuta: npm run browser:vercel');
  process.exit(1);
}

const TEAM = 'maxlive-hotmailes-projects';
const PROJECT = 'marketing-copilot';
const urls = [
  `https://vercel.com/${TEAM}/${PROJECT}`,
  `https://vercel.com/${TEAM}/${PROJECT}/settings/environment-variables`,
  `https://vercel.com/${TEAM}/${PROJECT}/settings/git`,
];

const browser = await chromium.launch({
  headless: false,
  channel: process.platform === 'win32' ? 'msedge' : undefined,
});

const context = await browser.newContext({
  storageState: storage,
  viewport: { width: 1400, height: 900 },
});

for (const u of urls) {
  const p = await context.newPage();
  await p.goto(u, { waitUntil: 'domcontentloaded' });
}

console.log('\nPestañas abiertas: Overview, Environment Variables, Git.');
console.log('Añade API_URL (Build) = https://TU-SERVICIO.onrender.com/api');
console.log('Si aún no está conectado el repo: pestaña Git → Connect Git Repository.');
console.log('\nPulsa ENTER para cerrar el navegador.\n');

await new Promise((resolve) => {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  rl.question('', () => {
    rl.close();
    resolve();
  });
});

await browser.close();
process.exit(0);
