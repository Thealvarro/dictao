# dictao█

**Tu voz es el prompt.**

[![Licencia MIT](https://img.shields.io/badge/licencia-MIT-F97316?style=for-the-badge)](LICENSE)
[![Plataformas](https://img.shields.io/badge/Windows%20%C2%B7%20macOS%20%C2%B7%20Linux-0B0E14?style=for-the-badge)](#descarga)
[![Última versión](https://img.shields.io/badge/release-1.0.0-F97316?style=for-the-badge)](https://github.com/Thealvarro/dictao/releases/latest)

---

## ¿Qué es esto?

Dictao es dictado por voz para los que programamos con IA. Aprietas un atajo, hablas, y el texto aparece donde tengas el cursor: Cursor, Claude Code, el terminal, el navegador, donde sea. Todo corre **100% local** en tu máquina (GPU o CPU) con modelos Whisper/Parakeet. Nada sale a la nube, nada se sube a ningún lado. Tu voz se queda en tu compu.

Pensado para vibe coders de LATAM: los que dictan prompts en vez de tipearlos, viven entre el editor y la terminal, y trabajan en español. Español por defecto, sin config rara.

## ¿Por qué?

Los que programamos con IA escribimos párrafos de prompt todo el día. Hablarlos es como 3x más rápido que tipearlos, y no te saca del flow. Ya existen apps de dictado, pero ninguna estaba pensada para nosotros ni para trabajar en español de entrada. Dictao es eso: hecho en LATAM, dev a dev, para los que trabajan hablando.

## Características

| | |
|---|---|
| 🎙️ **Local de verdad** | Transcripción en tu máquina, sin nube, sin cuentas, sin telemetría. |
| ⚡ **GPU o CPU** | Usa aceleración por GPU cuando hay; si no, corre en CPU con Parakeet. |
| 🌎 **Español por defecto** | Configurado para trabajar en español desde el arranque. |
| ⌨️ **Aparece donde escribes** | Pega el texto en la app activa vía portapapeles, con acentos y ñ bien puestos. |
| 🔀 **Atajo configurable** | Toggle o push-to-talk, el atajo lo cambias tú. |
| 🧠 **Varios modelos** | Whisper (Small/Medium/Turbo/Large) y Parakeet V3, se descargan cuando los eliges. |
| 🤫 **Filtro de silencio (VAD)** | Silero VAD corta el silencio para que no invente texto. |
| 🖥️ **Multiplataforma** | Windows, macOS y Linux (x64 y ARM64). |

## Descarga

Los instaladores están en la [página de releases](https://github.com/Thealvarro/dictao/releases/latest). Bajas el de tu sistema, instalas, y le das permisos de micrófono (y accesibilidad en macOS, para que pueda pegar el texto).

> **Ojo con Windows SmartScreen:** los binarios todavía **no están firmados** (firmar cuesta plata, va en el roadmap). Windows te va a mostrar el aviso azul de "Windows protegió tu PC". Es esperado. Haz clic en **"Más información" → "Ejecutar de todas formas"**. El código es abierto y está acá mismo: puedes compilarlo tú si quieres cero dudas.

## Cómo se usa

1. **Aprietas el atajo** para empezar a grabar.
2. **Hablas.**
3. **Aprietas de nuevo** (o sueltas, según el modo) y el texto aparece donde esté el cursor.

Atajos por defecto:

| Acción | Windows / Linux | macOS |
|---|---|---|
| Transcribir | `Ctrl + Espacio` | `Option + Espacio` |
| Transcribir + post-procesado IA | `Ctrl + Shift + Espacio` | `Option + Shift + Espacio` |
| Cancelar | `Escape` | `Escape` |
| Menú de debug | `Ctrl + Shift + D` | `Cmd + Shift + D` |

Todos se pueden cambiar desde Ajustes. Vive en la bandeja del sistema, así que lo tienes siempre a mano.

## Modelos

Los modelos se descargan en runtime la primera vez que los eliges, y quedan guardados en tu máquina.

- **Whisper** (Small / Medium / Turbo / Large) — GGML/GGUF, con aceleración por GPU cuando el hardware lo permite.
- **Parakeet V3** — optimizado para CPU, con detección automática de idioma. Anda bien en hardware modesto (~5x tiempo real en un i5).

**Recomendaciones de hardware:**
- **GPU** (Whisper con acelerón): NVIDIA/AMD/Intel en Windows y Linux; Mac M-series o Intel en macOS.
- **Solo CPU** (Parakeet V3): desde un Intel Skylake (6ª gen) o AMD equivalente en adelante.

## Desarrollo

**Requisitos:**
- [Rust](https://rustup.rs/) (stable más reciente)
- [Bun](https://bun.sh/)

**Comandos:**

```bash
bun install            # instalar dependencias
bun run tauri dev      # correr en modo desarrollo
bun run tauri build    # compilar para producción
```

En macOS, si te tira error de cmake:

```bash
CMAKE_POLICY_VERSION_MINIMUM=3.5 bun run tauri dev
```

Para el setup por plataforma (dependencias del sistema, etc.), mira [BUILD.md](BUILD.md). Para publicar tu propia versión, mira [DEPLOY.md](DEPLOY.md).

**Nota para Linux:** para que el pegado ande bien necesitas una herramienta de input según tu servidor gráfico — `xdotool` en X11, `wtype` o `dotool` en Wayland. Sin eso, el texto puede no pegarse. Detalle completo en el [README de upstream](https://github.com/cjpais/Handy#linux-notes).

## Stack técnico

App de escritorio en **Tauri 2** (backend Rust + frontend React/TypeScript con Tailwind).

- **transcribe-cpp** — inferencia local de Whisper (GGML/GGUF) con aceleración por GPU.
- **transcribe-rs** — reconocimiento por ONNX (Parakeet).
- **cpal** — audio multiplataforma · **vad-rs** — detección de voz (Silero) · **rubato** — resampleo · **rdev** — atajos globales.

## Roadmap

- [ ] **Firma de código** (certificado EV) para sacar el aviso de SmartScreen en Windows.
- [ ] **CDN propio de modelos** — hoy se bajan del CDN del proyecto original (`blob.handy.computer`); migrar a infra propia.
- [ ] **Comandos de voz** ("punto aparte", "borra eso", "nueva línea").
- [ ] **Updater automático** con llaves minisign propias (hoy está fail-closed).

## Créditos

> ### Dictao es un fork de [Handy](https://github.com/cjpais/Handy), de CJ Pais.
>
> **Todo el mérito de la ingeniería original es suyo.** Dictao no existiría sin ese trabajo: la arquitectura, el pipeline de audio, la integración con Whisper y Parakeet, el manejo multiplataforma — todo viene de ahí. Nosotros lo reempaquetamos y le pusimos cara latina.
>
> Si Dictao te sirve, **considera apoyar el proyecto original**: 👉 **https://handy.computer/donate**
>
> Repo upstream: https://github.com/cjpais/Handy

Y gracias también a **Whisper** (OpenAI), **ggml / transcribe.cpp**, **Silero** (VAD) y al equipo de **Tauri**.

## Licencia

MIT — mira el archivo [LICENSE](LICENSE). El copyright original de CJ Pais se mantiene intacto, como manda la licencia.

> El nombre, logo e íconos de **Handy** son marca de su autor y **no** son parte de la licencia MIT. Por eso Dictao usa su propia identidad (nombre, wordmark, paleta) y no implica respaldo ni afiliación con Handy.

---

<sub>Desarrollado por <a href="https://alvarocofre.dev" target="_blank" rel="noopener noreferrer">SICS</a></sub>
