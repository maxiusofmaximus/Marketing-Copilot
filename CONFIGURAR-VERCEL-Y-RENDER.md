# Configuración rápida (Vercel + Render)

El backend **no es Render** escrito “Redos”: la plataforma del API se llama **[Render](https://render.com)**. El frontend va en **[Vercel](https://vercel.com)**.

## 1) Vercel (frontend) — automático con un comando

1. **Crea un token** (solo para tu cuenta): [vercel.com/account/tokens](https://vercel.com/account/tokens)
2. Copia la **URL de tu API en Render** (por ejemplo `https://algo.onrender.com`). La API debe responder en `.../api/health`.
3. **Opción A (sin variables en la terminal):** en la raíz del repo crea el archivo **`.vercel-token`** (no se sube a Git) con exactamente **dos líneas**: línea 1 = token, línea 2 = `https://TU-SERVICIO.onrender.com/api`. Luego ejecuta:

```powershell
cd "ruta\a\Marketing-Copilot"
powershell -ExecutionPolicy Bypass -File scripts/apply-local.ps1
```

3. **Opción B:** en **PowerShell**, en la carpeta raíz del repo:

```powershell
cd "ruta\a\Marketing-Copilot"
$env:VERCEL_TOKEN="PEGA_AQUI_EL_TOKEN"
$env:API_URL="https://TU-SERVICIO.onrender.com/api"
node scripts/vercel-apply-config.mjs
```

Eso deja el proyecto **marketing-copilot** con:

- **Root Directory:** `frontend`
- **Build:** `npm run build:vercel`
- **Salida:** `dist/marketing-copilot/browser`
- Variable **`API_URL`** para producción y preview

4. **Git (solo si aún no está conectado):** entra en [Settings → Git](https://vercel.com/maxlive-hotmailes-projects/marketing-copilot/settings/git), conecta el repo **maxiusofmaximus/Marketing-Copilot** y rama **main**.
5. En Vercel → **Deployments** → **Redeploy** el último deploy (o sube un commit).

---

## 2) Render (backend)

En el [dashboard de Render](https://dashboard.render.com), tu servicio web (Python):

- **Root Directory:** `backend`
- **Build:** `pip install -r requirements.txt`
- **Start:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Variables:

| Nombre | Valor |
|--------|--------|
| `LLM_PROVIDER` | `cerebras` |
| `CEREBRAS_API_KEY` | (tu clave, en secreto) |
| `FRONTEND_ORIGIN` | URL de tu app en Vercel, ej. `https://marketing-copilot-xxx.vercel.app` |

Guarda y espera a que el servicio esté **Live**. Esa URL base (sin `/api`) es la que pones en `FRONTEND_ORIGIN`; la URL con **`/api`** (ej. `https://xxx.onrender.com/api`) es la que pones en `API_URL` en Vercel.

---

## Orden recomendado

1. Deja Render funcionando y copia la URL `https://xxx.onrender.com/api`.
2. Ejecuta `vercel-apply-config.mjs` con `API_URL` y el token.
3. Conecta Git en Vercel si falta y redeploy.
