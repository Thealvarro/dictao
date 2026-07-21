# Guía de publicación — Dictao

Guía paso a paso para publicar Dictao **hoy**: subir el repo, generar los instaladores y dejar la landing online. Escrita para usar **GitHub Desktop** y **Vercel**, con la alternativa por consola (`gh` / `vercel`) donde hace falta.

Orden recomendado:

1. Crear el repo en GitHub y subir esta carpeta.
2. Generar los instaladores con GitHub Actions.
3. Deployar la landing en Vercel.
4. Checklist final.

Al final: **"Pendientes conscientes"** — lo que queda para después, con nombre y apellido.

---

## 1. Crear el repo `Thealvarro/dictao` y subir la carpeta

**Ojo con esto, es lo más importante de entender:** la carpeta `dictao/` **ya es su propio repo git**, y hoy su `origin` apunta al proyecto original (`cjpais/Handy`). O sea, todavía "cree" que es Handy. Hay que hacer dos cosas:

- Apuntar `origin` a **tu** repo nuevo (`Thealvarro/dictao`).
- **Conservar** el repo original como `upstream`, para poder traer mejoras de Handy más adelante.

### 1.1. Crear el repo vacío en GitHub

1. Ve a https://github.com/new
2. **Owner:** `Thealvarro` · **Repository name:** `dictao`
3. Visibilidad: **Public**
4. **NO** marques "Add a README", ni `.gitignore`, ni licencia. La carpeta ya trae todo eso; si GitHub crea archivos, el push choca.
5. **Create repository.**

Te va a quedar un repo vacío en `https://github.com/Thealvarro/dictao`.

### 1.2. Cambiar los remotos (esto va por consola, es rápido)

Buena noticia: `upstream` ya quedó configurado apuntando al proyecto original (`cjpais/Handy`), así que más adelante puedes traer sus mejoras sin drama (ver el paso 1.4). Lo único que falta es agregar `origin` apuntando a **tu** repo nuevo.

Abre una consola **dentro de la carpeta `dictao/`** y corre:

```bash
# Apuntar "origin" a tu repo nuevo
git remote add origin https://github.com/Thealvarro/dictao.git

# Verificar que quedó bien
git remote -v
```

Tienes que ver algo así:

```
origin    https://github.com/Thealvarro/dictao.git (fetch/push)
upstream  https://github.com/cjpais/Handy (fetch/push)
```

### 1.3. Subir el código

**Opción A — GitHub Desktop:**
1. `File → Add local repository…` y elige la carpeta `dictao/`.
2. Arriba te va a mostrar la rama `main`.
3. Botón **"Publish branch"** (o "Push origin"). Como `origin` ya apunta a tu repo, sube ahí.

**Opción B — consola:**
```bash
git push -u origin main
```

**Opción C — con `gh` CLI** (hace todo de una: crea el repo y sube):
```bash
gh repo create Thealvarro/dictao --public --source=. --remote=origin --push
```
> Si usas esta opción, hazla **en vez** del paso 1.1 y 1.2. Como `upstream` ya está configurado (ver 1.2), no tienes que renombrar nada: `gh` crea `origin` apuntando a tu repo nuevo y con eso quedan los dos remotos listos.

### 1.4. Traer mejoras de Handy en el futuro

Cuando el proyecto original saque algo bueno, lo traes así:

```bash
git fetch upstream
git merge upstream/main
```

Resuelves los conflictos que salgan (nuestros cambios de branding vs los suyos), y listo.

---

## 2. Generar los instaladores (GitHub Actions)

Los instaladores de todas las plataformas se compilan en la nube con GitHub Actions. **No necesitas compilar nada en tu máquina.** El workflow `release.yml` ya está adaptado.

1. En tu repo, ve a la pestaña **Actions**.
2. Si te pide habilitar los workflows, dale **"I understand my workflows, go ahead and enable them"**.
3. En la lista de la izquierda, elige el workflow **"Release"**.
4. Botón **"Run workflow"** (arriba a la derecha) → confirma con **"Run workflow"**. Se dispara a mano (`workflow_dispatch`).
5. **Espera ~30-40 min.** Compila para Windows (x64 + ARM64), macOS (Intel + Apple Silicon) y Linux (deb, AppImage, RPM). Puedes cerrar la pestaña, sigue solo.
6. Cuando termina, va a existir un **release en borrador** (`draft`) llamado `v1.0.0`, con todos los instaladores adjuntos.
7. Ve a la pestaña **Releases** (o `.../releases`), abre el borrador, revisa que estén los archivos, y dale **"Publish release"**.

Recién ahí el link `https://github.com/Thealvarro/dictao/releases/latest` empieza a funcionar de verdad.

> **Nota:** el release sale **sin firma de código** (así está configurado hoy). Los instaladores funcionan igual, pero Windows va a mostrar el aviso de SmartScreen (ver checklist). Eso es esperado, no es un error del build.

---

## 3. Deployar la landing en Vercel

La landing vive en la carpeta `landing/` y es estática (HTML/CSS/JS). Se deploya como sitio estático, sin build.

> **Antes de deployar:** confirma que `landing/` tenga contenido (al menos un `index.html`). Si todavía está vacía porque otro agente la está armando, espera a que esté lista.

### Opción A — Vercel web (recomendada)

1. Entra a https://vercel.com/new
2. **Import Git Repository** → elige `Thealvarro/dictao` (si no aparece, conecta tu cuenta de GitHub y dale acceso al repo).
3. En la config del proyecto:
   - **Root Directory:** `landing`  ← clave, apunta a la subcarpeta.
   - **Framework Preset:** `Other` (sitio estático).
   - **Build Command:** déjalo vacío.
   - **Output Directory:** déjalo por defecto.
4. **Deploy.**
5. En 1-2 min te da un dominio tipo `dictao.vercel.app`. Ese es el link público de la landing.

### Opción B — Vercel CLI

Desde la carpeta `landing/`:

```bash
cd landing
vercel          # primer deploy: te pregunta y linkea el proyecto (preview)
vercel --prod   # deploy a producción
```

---

## 4. Checklist final (antes de compartir)

- [ ] El link `https://github.com/Thealvarro/dictao/releases/latest` abre el release publicado y se ven los instaladores.
- [ ] **Probar el instalador en Windows:** baja el `.exe`/`.msi`, ejecútalo. Va a saltar el aviso azul **"Windows protegió tu PC"** (SmartScreen, porque no está firmado). Es lo esperado → click en **"Más información" → "Ejecutar de todas formas"**. Instala y verifica que dicta bien.
- [ ] Abrir Dictao, apretar el atajo (`Ctrl + Espacio`), hablar y confirmar que el texto aparece.
- [ ] La landing carga en su dominio de Vercel y los links de descarga apuntan al release correcto.
- [ ] Compartir el link. 🚀

---

## Pendientes conscientes

Cosas que **sabemos** que quedan para después. No son bugs, son decisiones de "salir hoy":

**1. Firma de código (Windows/macOS).**
Hoy los binarios salen **sin firmar**, por eso el aviso de SmartScreen. Para sacarlo hace falta un certificado de firma:
- **Windows:** certificado **EV Code Signing** (~USD 250-600/año según proveedor) o **Azure Trusted Signing** (más barato, ~USD 10/mes, pero requiere validación de organización). El EV saca el warning de una; el OV lo reduce con el tiempo.
- **macOS:** cuenta de **Apple Developer** (USD 99/año) para firmar y notarizar.
- *Los precios cambian, confirma antes de comprar.*

**2. Llaves del updater automático.**
El updater está **fail-closed**: no va a actualizar solo hasta que generes tus propias llaves de firma (minisign). Hoy la pubkey en `tauri.conf.json` todavía es la de Handy.
```bash
bun run tauri signer generate
```
Eso te da una **llave privada** (guárdala segura, NO la subas al repo) y una **pública**. Después:
- Reemplaza el valor de `plugins.updater.pubkey` en `src-tauri/tauri.conf.json` por tu pubkey nueva.
- Carga la privada como **secret** en GitHub Actions para que firme los releases.
- Actualiza los `endpoints` del updater para que apunten a tu repo.

**3. Ícono `.icns` de macOS.**
Si el ícono de macOS (`src-tauri/icons/`) no se regeneró con el branding de Dictao, la app puede mostrar todavía el ícono de Handy en el Dock. Revisa que estén los íconos de Dictao antes de un release "serio".

**4. Migrar el CDN de modelos.**
Los modelos (Whisper/Parakeet/VAD) se descargan en runtime desde `blob.handy.computer`, el CDN del **proyecto original**. Funciona, pero dependes de su infra. Pendiente: subir los modelos a un bucket propio (R2/S3/Vercel Blob) y actualizar las URLs en el manager de modelos.

**5. Dominio propio.**
La landing arranca en `*.vercel.app`. Cuando estés listo, compra **`dictao.dev`**, agrégalo en Vercel (**Project → Settings → Domains**) y apunta los DNS. Vercel te da el SSL solo.

---

<sub>Desarrollado por <a href="https://alvarocofre.dev" target="_blank" rel="noopener noreferrer">SICS</a></sub>
