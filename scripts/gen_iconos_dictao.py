# -*- coding: utf-8 -*-
"""
Generador parametrico de los iconos de la marca "Dictao".

Dibuja el isotipo (chevron ">" + waveform de 4 barras) sobre un fondo squircle
carbon y produce TODOS los assets que consume el build de Tauri:
  - src-tauri/icons/*        (icono de app: png/ico/icns + tiles de Windows)
  - src-tauri/resources/*    (iconos del tray, en sus 3 temas)

Todo se dibuja en un canvas SS veces mas grande y se reduce con LANCZOS para
lograr un antialiasing limpio.

Herramienta: Pillow. Uso:
    python scripts/gen_iconos_dictao.py

OJO con la convencion del tray (verificada en src-tauri/src/tray.rs):
  - Los archivos SIN "_dark" los usa el tema Dark (barra OSCURA) -> glifo CLARO.
  - Los archivos CON "_dark" los usa el tema Light (barra CLARA) -> glifo OSCURO.
El nombre "_dark" se refiere al color del ICONO... al reves de lo intuitivo.
Por eso los colores de abajo respetan el USO real, no el nombre del archivo.
"""

import io
import os
import struct
from PIL import Image, ImageDraw

# --------------------------------------------------------------------------
# Paleta de la marca Dictao
# --------------------------------------------------------------------------
CARBON = (11, 14, 20, 255)        # #0B0E14  fondo squircle
BORDE = (31, 41, 55, 255)         # #1F2937  borde interior / glifo oscuro (barra clara)
LIMA = (163, 230, 53, 255)        # #A3E635  verde lima (color primario)
BLANCO = (248, 250, 252, 255)     # #F8FAFC  casi blanco (cursor / glifo en barra oscura)
LIMA_CLARO = (77, 124, 15, 255)   # #4D7C0F  lima apagado (para leerse en barra CLARA)
AMBAR_BARRA_OSCURA = (251, 191, 36, 255)  # #FBBF24  ambar brillante (barra oscura)
AMBAR_BARRA_CLARA = (180, 83, 9, 255)     # #B45309  ambar quemado (barra clara)

# Supersampling: dibujamos a SS veces el tamano final y reducimos con LANCZOS.
SS = 8

# Alturas relativas de las 4 barras del waveform (fraccion del alto del glifo).
# La ultima (mas baja) es el "cursor" del terminal: color distinto y mas separada.
ALTURAS_IDLE = [0.45, 0.75, 1.0, 0.40]
# Variante "grabando": barras mas altas para dar sensacion de senal activa.
ALTURAS_REC = [0.65, 0.90, 1.0, 0.55]

# En el tray el icono se ve a ~16-24px: 4 barras finas se empastan.
# Usamos 3 barras (chevron + waveform simplificado) para que lea nitido.
# La ultima sigue siendo el "cursor" (mas separada).
ALTURAS_TRAY_IDLE = [0.55, 1.0, 0.45]
ALTURAS_TRAY_REC = [0.72, 1.0, 0.60]

# Geometria del glifo, en fracciones del lado del canvas supersampleado (S).
# Define la FORMA; luego el glifo se escala a la fraccion de canvas deseada.
_STROKE = 0.075   # grosor de los trazos del chevron
_CW = 0.16        # ancho horizontal del chevron
_GH = 0.36        # alto del glifo (= alto del chevron y de la barra mas alta)
_G1 = 0.05        # separacion entre la punta del chevron y la 1a barra
_BW = 0.058       # ancho de cada barra
_SP = 0.045       # separacion entre barras
_CURSOR_GAP = 0.028  # separacion EXTRA antes de la barra-cursor


# --------------------------------------------------------------------------
# Helpers de dibujo
# --------------------------------------------------------------------------
def _linea_gruesa(draw, p0, p1, grosor, color):
    """Traza una linea gruesa con extremos redondeados (round caps)."""
    draw.line([p0, p1], fill=color, width=int(round(grosor)))
    r = grosor / 2.0
    for (x, y) in (p0, p1):
        draw.ellipse([x - r, y - r, x + r, y + r], fill=color)


def _barra(draw, x0, y0, x1, y1, color):
    """Barra vertical con extremos totalmente redondeados (forma de pildora)."""
    rad = min(x1 - x0, y1 - y0) / 2.0
    draw.rounded_rectangle([x0, y0, x1, y1], radius=rad, fill=color)


def _dibujar_glifo(draw, S, cy, color_glifo, color_cursor, alturas):
    """
    Dibuja el glifo (chevron + barras) sobre un canvas SxS.
    Lo posiciona hacia la izquierda; luego quien llama lo recorta y centra.
    'cy' es el centro vertical. Devuelve nada (dibuja in-place).
    """
    st = _STROKE * S
    cw = _CW * S
    gh = _GH * S
    g1 = _G1 * S
    bw = _BW * S
    sp = _SP * S
    cursor_gap = _CURSOR_GAP * S

    x_ini = 0.12 * S  # arranque tentativo; el recentrado posterior lo corrige

    # --- Chevron ">" : dos trazos gruesos que se juntan en la punta derecha ---
    top = (x_ini, cy - gh / 2.0)
    apex = (x_ini + cw, cy)
    bot = (x_ini, cy + gh / 2.0)
    _linea_gruesa(draw, top, apex, st, color_glifo)
    _linea_gruesa(draw, apex, bot, st, color_glifo)

    # --- Barras (waveform) a la derecha de la punta ---
    x = x_ini + cw + g1 + st / 2.0
    n = len(alturas)
    for i, frac in enumerate(alturas):
        if i == n - 1:            # barra-cursor: mas separada y de otro color
            x += cursor_gap
            col = color_cursor
        else:
            col = color_glifo
        h = gh * frac
        _barra(draw, x, cy - h / 2.0, x + bw, cy + h / 2.0, col)
        x += bw + sp


def _fondo_squircle(base, S, con_borde):
    """Pinta el fondo squircle carbon (con borde interior sutil opcional)."""
    d = ImageDraw.Draw(base)
    r = int(round(0.22 * S))  # radio de esquina ~22% del lado
    if con_borde:
        bw = max(1, int(round(0.015 * S)))  # borde interior ~1.5% del lado
        d.rounded_rectangle([0, 0, S - 1, S - 1], radius=r, fill=BORDE)
        d.rounded_rectangle(
            [bw, bw, S - 1 - bw, S - 1 - bw],
            radius=max(1, r - bw),
            fill=CARBON,
        )
    else:
        d.rounded_rectangle([0, 0, S - 1, S - 1], radius=r, fill=CARBON)


def render_icono(lado, con_fondo=True, color_glifo=LIMA, color_cursor=BLANCO,
                 con_borde=True, alturas=None, frac_ancho=0.60):
    """
    Renderiza un icono cuadrado de 'lado' px (RGBA).

    con_fondo   -> dibuja el squircle carbon detras del glifo.
    color_glifo -> color del chevron y de las 3 primeras barras.
    color_cursor-> color de la barra-cursor (la mas baja). En tray monocromo
                   se pasa igual a color_glifo.
    con_borde   -> borde interior del squircle.
    frac_ancho  -> ancho del glifo como fraccion del lado (marge de respiro).
    """
    if alturas is None:
        alturas = ALTURAS_IDLE
    S = lado * SS
    base = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    if con_fondo:
        _fondo_squircle(base, S, con_borde)

    # 1) Dibujamos el glifo en su propia capa transparente.
    capa = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    _dibujar_glifo(ImageDraw.Draw(capa), S, S / 2.0, color_glifo, color_cursor, alturas)

    # 2) Recortamos al contenido real y lo escalamos al ancho objetivo.
    bbox = capa.getbbox()
    sub = capa.crop(bbox)
    objetivo = frac_ancho * S
    ratio = objetivo / sub.width
    nuevo = (max(1, int(round(sub.width * ratio))), max(1, int(round(sub.height * ratio))))
    sub = sub.resize(nuevo, Image.LANCZOS)

    # 3) Lo centramos optica y geometricamente sobre el canvas.
    ox = (S - sub.width) // 2
    oy = (S - sub.height) // 2
    base.alpha_composite(sub, (ox, oy))

    # 4) Reducimos al tamano final con LANCZOS.
    return base.resize((lado, lado), Image.LANCZOS)


# --------------------------------------------------------------------------
# Escritura de contenedores multi-resolucion (.ico / .icns)
# --------------------------------------------------------------------------
def guardar_ico(path, render_fn, tamanos):
    """
    Escribe un .ico multi-resolucion usando Pillow.
    render_fn(size) -> Image RGBA de ese tamano (render nitido, no reescalado).
    Pillow codifica los <256 como BMP y el 256 como PNG (maxima compatibilidad).
    """
    imgs = [render_fn(s) for s in tamanos]
    base = imgs[-1]  # el mas grande
    base.save(
        path,
        format="ICO",
        sizes=[(s, s) for s in tamanos],
        append_images=imgs[:-1],
    )


def guardar_icns(path, render_fn):
    """
    Escribe un .icns a mano (Pillow no lo genera de forma fiable en Windows).
    Formato: 'icns' + longitud total (BE) y luego, por cada icono,
    OSType(4) + longitud(BE, incluye cabecera de 8) + PNG data.

    Tabla de OSTypes usada (todos aceptan PNG):
      ic07=128, ic08=256, ic09=512, ic10=1024,
      ic11=32, ic12=64, ic13=256(retina), ic14=512(retina)
    """
    tabla = [
        (b"ic07", 128),
        (b"ic08", 256),
        (b"ic09", 512),
        (b"ic10", 1024),
        (b"ic11", 32),
        (b"ic12", 64),
        (b"ic13", 256),
        (b"ic14", 512),
    ]
    cuerpo = b""
    for ostype, size in tabla:
        buf = io.BytesIO()
        render_fn(size).save(buf, format="PNG")
        data = buf.getvalue()
        cuerpo += ostype + struct.pack(">I", len(data) + 8) + data
    total = 8 + len(cuerpo)
    with open(path, "wb") as f:
        f.write(b"icns" + struct.pack(">I", total) + cuerpo)


# --------------------------------------------------------------------------
# Generacion de todos los assets
# --------------------------------------------------------------------------
def main():
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dir_icons = os.path.join(raiz, "src-tauri", "icons")
    dir_res = os.path.join(raiz, "src-tauri", "resources")

    # ---- Icono de app (con squircle, glifo lima, cursor blanco) ----
    def app(lado):
        return render_icono(lado, con_fondo=True, color_glifo=LIMA,
                            color_cursor=BLANCO, con_borde=True, frac_ancho=0.60)

    pngs_icons = {
        "icon.png": 512,          # fuente (se respeta el tamano existente)
        "logo.png": 1024,
        "32x32.png": 32,
        "64x64.png": 64,
        "128x128.png": 128,
        "128x128@2x.png": 256,
        "StoreLogo.png": 50,
        "Square30x30Logo.png": 30,
        "Square44x44Logo.png": 44,
        "Square71x71Logo.png": 71,
        "Square89x89Logo.png": 89,
        "Square107x107Logo.png": 107,
        "Square142x142Logo.png": 142,
        "Square150x150Logo.png": 150,
        "Square284x284Logo.png": 284,
        "Square310x310Logo.png": 310,
    }
    for nombre, lado in pngs_icons.items():
        app(lado).save(os.path.join(dir_icons, nombre), format="PNG")
        print(f"[icons] {nombre:24s} {lado}x{lado}")

    # ---- icon.ico multi-resolucion ----
    guardar_ico(os.path.join(dir_icons, "icon.ico"), app,
                [16, 24, 32, 48, 64, 128, 256])
    print("[icons] icon.ico            16/24/32/48/64/128/256")

    # ---- icon.icns (macOS) ----
    guardar_icns(os.path.join(dir_icons, "icon.icns"), app)
    print("[icons] icon.icns           128/256/512/1024 (+retina)")

    # ---- Tray: temas Dark (barra oscura) y Light (barra clara) ----
    # Monocromo: el glifo entero de un solo color (cursor = mismo color).
    # Usa 3 barras (ALTURAS_TRAY_*) para leerse nitido a 16-24px.
    def tray(color, alturas=ALTURAS_TRAY_IDLE):
        return render_icono(64, con_fondo=False, color_glifo=color,
                            color_cursor=color, con_borde=False,
                            alturas=alturas, frac_ancho=0.82)

    tray_specs = {
        # Archivos SIN "_dark" -> tema Dark (barra OSCURA) -> glifo CLARO
        "tray_idle.png": BLANCO,
        "tray_recording.png": LIMA,
        "tray_transcribing.png": AMBAR_BARRA_OSCURA,
        # Archivos CON "_dark" -> tema Light (barra CLARA) -> glifo OSCURO
        "tray_idle_dark.png": BORDE,
        "tray_recording_dark.png": LIMA_CLARO,
        "tray_transcribing_dark.png": AMBAR_BARRA_CLARA,
    }
    alturas_por_estado = {
        "recording": ALTURAS_TRAY_REC,
    }
    for nombre, color in tray_specs.items():
        estado = "recording" if "recording" in nombre else "idle"
        alt = alturas_por_estado.get(estado, ALTURAS_TRAY_IDLE)
        tray(color, alt).save(os.path.join(dir_res, nombre), format="PNG")
        print(f"[resources] {nombre}")

    # ---- Tema "Colored" (Linux): CON squircle carbon de fondo ----
    # handy.png = idle (glifo lima, cursor blanco)
    render_icono(64, con_fondo=True, color_glifo=LIMA, color_cursor=BLANCO,
                 con_borde=True, alturas=ALTURAS_IDLE, frac_ancho=0.60
                 ).save(os.path.join(dir_res, "handy.png"), format="PNG")
    # recording.png = grabando (barras mas altas)
    render_icono(64, con_fondo=True, color_glifo=LIMA, color_cursor=BLANCO,
                 con_borde=True, alturas=ALTURAS_REC, frac_ancho=0.60
                 ).save(os.path.join(dir_res, "recording.png"), format="PNG")
    # transcribing.png = transcribiendo (glifo ambar)
    render_icono(64, con_fondo=True, color_glifo=AMBAR_BARRA_OSCURA, color_cursor=BLANCO,
                 con_borde=True, alturas=ALTURAS_IDLE, frac_ancho=0.60
                 ).save(os.path.join(dir_res, "transcribing.png"), format="PNG")
    print("[resources] handy.png / recording.png / transcribing.png (tema Colored)")

    print("\nListo. Iconos de Dictao regenerados.")


if __name__ == "__main__":
    main()
