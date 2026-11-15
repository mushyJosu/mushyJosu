"""Genera stats.svg y langs.svg para el README del perfil.
Solo usa la librería estándar de Python (no hay que instalar nada)."""
import json
import os
import urllib.request

USER = os.environ.get("GH_USER", "mushyJosu")
TOKEN = os.environ.get("GITHUB_TOKEN", "")

ROJO = "#cc0000"
BLANCO = "#ffffff"
GRIS = "#cccccc"
GRIS_OSCURO = "#333333"
FUENTE = "'Courier New', monospace"
ANCHO, ALTO = 420, 205


# ---------- 1. PEDIR DATOS A LA API DE GITHUB ----------
def api(ruta):
    req = urllib.request.Request("https://api.github.com" + ruta)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "profile-stats")
    if TOKEN:
        req.add_header("Authorization", "Bearer " + TOKEN)
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def intentar(ruta, campo):
    """Si una consulta falla, devuelve '-' en lugar de romper todo."""
    try:
        return api(ruta)[campo]
    except Exception:
        return "-"


usuario = api(f"/users/{USER}")
repos = [r for r in api(f"/users/{USER}/repos?per_page=100&type=owner")
         if not r["fork"]]

estrellas = sum(r["stargazers_count"] for r in repos)
commits = intentar(f"/search/commits?q=author:{USER}&per_page=1", "total_count")
prs = intentar(f"/search/issues?q=author:{USER}+type:pr&per_page=1", "total_count")

# bytes de código por lenguaje, sumando todos los repos
lenguajes = {}
for r in repos:
    if r["language"]:
        try:
            for lang, b in api(f"/repos/{USER}/{r['name']}/languages").items():
                lenguajes[lang] = lenguajes.get(lang, 0) + b
        except Exception:
            pass


# ---------- 2. DIBUJAR LAS TARJETAS (SVG) ----------
def marco(titulo, contenido):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {ANCHO} {ALTO}" width="{ANCHO}" height="{ALTO}">
  <rect x="1" y="1" width="{ANCHO-2}" height="{ALTO-2}" fill="#000000" stroke="{BLANCO}" stroke-width="1"/>
  <text x="20" y="32" font-family="{FUENTE}" font-size="16" font-weight="bold">
    <tspan fill="{BLANCO}">&gt; </tspan><tspan fill="{ROJO}">{titulo}</tspan>
  </text>
  <line x1="20" y1="44" x2="{ANCHO-20}" y2="44" stroke="{GRIS_OSCURO}" stroke-width="1"/>
{contenido}
</svg>
'''


# Tarjeta 1: números generales
filas = [
    ("Repositorios públicos", usuario["public_repos"]),
    ("Estrellas recibidas", estrellas),
    ("Commits", commits),
    ("Pull requests", prs),
    ("Seguidores", usuario["followers"]),
]
txt = ""
for i, (etiqueta, valor) in enumerate(filas):
    y = 72 + i * 28
    txt += (f'  <text x="20" y="{y}" font-family="{FUENTE}" font-size="14" fill="{GRIS}">{etiqueta}</text>\n'
            f'  <text x="{ANCHO-20}" y="{y}" font-family="{FUENTE}" font-size="14" font-weight="bold" '
            f'fill="{ROJO}" text-anchor="end">{valor}</text>\n')
open("stats.svg", "w", encoding="utf-8").write(marco("estadísticas", txt))

# Tarjeta 2: lenguajes más usados (top 5 con barras)
total = sum(lenguajes.values()) or 1
top = sorted(lenguajes.items(), key=lambda x: x[1], reverse=True)[:5]
txt = ""
for i, (nombre, b) in enumerate(top):
    y = 72 + i * 28
    pct = b / total * 100
    largo = round(pct / 100 * 180, 1)
    txt += (f'  <text x="20" y="{y}" font-family="{FUENTE}" font-size="14" fill="{GRIS}">{nombre}</text>\n'
            f'  <rect x="140" y="{y-9}" width="180" height="8" fill="{GRIS_OSCURO}"/>\n'
            f'  <rect x="140" y="{y-9}" width="{largo}" height="8" fill="{ROJO}"/>\n'
            f'  <text x="{ANCHO-20}" y="{y}" font-family="{FUENTE}" font-size="13" fill="{BLANCO}" '
            f'text-anchor="end">{pct:.1f}%</text>\n')
open("langs.svg", "w", encoding="utf-8").write(marco("lenguajes", txt))
print("Listo: stats.svg y langs.svg generados para", USER)
