/**
 * Reutiliza la sesión guardada (playwright-vercel-storage.json) y abre tu workspace en Vercel.
 * Ejecutar desde la raíz del repo: npm run browser:vercel:dashboard
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
  console.error('No existe playwright-vercel-storage.json. Ejecuta antes: npm run browser:vercel');
  process.exit(1);
}

const browser = await chromium.launch({
  headless: false,
  channel: process.platform === 'win32' ? 'msedge' : undefined,
});

const context = await browser.newContext({
  storageState: storage,
  viewport: { width: 1400, height: 900 },
});

const page = await context.newPage();

// Tu equipo en Vercel (ajusta si cambia el slug)
await page.goto('https://vercel.com/maxlive-hotmailes-projects', {
  waitUntil: 'domcontentloaded',
});

const importUrl = 'https://vercel.com/new/import';
const p2 = await context.newPage();
await p2.goto(importUrl, { waitUntil: 'domcontentloaded' });

console.log('\nVentanas abiertas:');
console.log('  1) Equipo / proyectos');
console.log('  2) Importar repositorio (conecta maxiusofmaximus/Marketing-Copilot si aún no está)');
console.log('\nChecklist rápido:');
console.log('  • Root Directory: frontend');
console.log('  • Build: npm run build:vercel (o el default si vercel.json ya lo define)');
console.log('  • Env (Build): API_URL = https://<tu-backend>.onrender.com/api');
console.log('\nPulsa ENTER aquí para cerrar el navegador.\n');

await new Promise((resolve) => {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  rl.question('', () => {
    rl.close();
    resolve();
  });
});

await browser.close();
process.exit(0);
