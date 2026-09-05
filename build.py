#!/usr/bin/env python3
"""Genera el sitio estático del repertorio.

Lee data/songs.json (lista base), data/resources.json (tabs + videos) y
data/theory.json (análisis armónico), data/gear.json (setup original) y
data/spotify.json (links), y escribe el sitio en docs/ listo
para GitHub Pages.

    python3 build.py
"""
import html
import json
import os
import re
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "docs")


def load(name, default):
    path = os.path.join(DATA, name)
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def slugify(title):
    s = title.lower()
    for a, b in [("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"), ("ñ", "n")]:
        s = s.replace(a, b)
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def md(text):
    """Markdown mínimo: **negrita**, *itálica*, `código`, párrafos y listas."""
    if not text:
        return ""
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\*\w])\*([^\*\n]+?)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    blocks = []
    for block in re.split(r"\n\s*\n", text.strip()):
        lines = [ln.strip() for ln in block.strip().split("\n") if ln.strip()]
        if lines and all(ln.startswith(("- ", "* ")) for ln in lines):
            items = "".join(f"<li>{ln[2:]}</li>" for ln in lines)
            blocks.append(f"<ul>{items}</ul>")
        elif lines:
            blocks.append("<p>" + "<br>".join(lines) + "</p>")
    return "\n".join(blocks)


def yt_id(url):
    m = re.search(r"(?:v=|youtu\.be/|embed/)([A-Za-z0-9_-]{11})", url or "")
    return m.group(1) if m else None


def sources_html(urls):
    """Lista de fuentes por dominio: más corta de leer que la URL entera."""
    if not urls:
        return ""
    links = []
    for u in urls:
        host = re.sub(r"^www\.", "", (re.split(r"/+", u, maxsplit=2) + ["", ""])[1])
        links.append(f'<a href="{html.escape(u)}" target="_blank" rel="noopener">{html.escape(host)}</a>')
    return f'<div class="srcs">Fuentes: {" · ".join(links)}</div>'


CSS = """*{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#0f1115;--card:#171a21;--line:#252a34;--tx:#e8eaed;--dim:#9aa3b2;--acc:#ff8a4c;--acc2:#4cc2ff}
body{background:var(--bg);color:var(--tx);font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;padding:0 0 5rem}
a{color:var(--acc2);text-decoration:none}a:hover{text-decoration:underline}
.wrap{max-width:860px;margin:0 auto;padding:0 1.25rem}
header{border-bottom:1px solid var(--line);padding:2.5rem 0 2rem;margin-bottom:2rem;background:linear-gradient(180deg,#171a21,transparent)}
h1{font-size:2rem;letter-spacing:-.02em}
h2{font-size:1.25rem;margin:2.5rem 0 1rem;padding-bottom:.4rem;border-bottom:1px solid var(--line)}
h3{font-size:1rem;margin:1.5rem 0 .6rem;color:var(--acc)}
.sub{color:var(--dim);margin-top:.4rem;font-size:.95rem}
.back{display:inline-block;margin-bottom:1.5rem;color:var(--dim);font-size:.9rem}
ol.songs{list-style:none}
ol.songs li{border:1px solid var(--line);background:var(--card);border-radius:10px;margin-bottom:.6rem;transition:border-color .15s}
ol.songs li:hover{border-color:var(--acc)}
ol.songs li[hidden]{display:none}
ol.songs a{display:flex;align-items:center;gap:1rem;padding:.85rem 1.1rem;color:var(--tx)}
ol.songs a:hover{text-decoration:none}
/* El número es la posición en el setlist, así que no se renumera al filtrar. */
ol.songs a::before{content:attr(data-n);color:var(--dim);font-variant-numeric:tabular-nums;font-size:.85rem;min-width:1.6rem}
.find{position:relative;margin:0 0 1.2rem}
.find input{width:100%;background:var(--card);border:1px solid var(--line);border-radius:10px;
color:var(--tx);font:inherit;font-size:1rem;padding:.75rem 2.4rem .75rem 2.5rem;outline:none}
.find input:focus{border-color:var(--acc)}
.find input::placeholder{color:var(--dim)}
/* La X nativa de type=search duplicaría nuestro botón de limpiar. */
.find input::-webkit-search-cancel-button{-webkit-appearance:none;appearance:none}
.find .ico{position:absolute;left:.9rem;top:50%;transform:translateY(-50%);color:var(--dim);font-size:.95rem}
.find .clr{position:absolute;right:.5rem;top:50%;transform:translateY(-50%);background:none;border:0;
color:var(--dim);font-size:1.2rem;cursor:pointer;padding:.2rem .5rem;line-height:1}
.find .clr:hover{color:var(--tx)}
.count{color:var(--dim);font-size:.88rem;margin:-.6rem 0 1rem}
.t{font-weight:600}.a{color:var(--dim);font-size:.9rem}
.k{margin-left:auto;background:#20242d;border:1px solid var(--line);color:var(--acc);border-radius:6px;padding:.15rem .55rem;font-size:.8rem;font-weight:600}
.meta{display:flex;flex-wrap:wrap;gap:.5rem;margin:1rem 0 2rem}
.pill{background:var(--card);border:1px solid var(--line);border-radius:999px;padding:.3rem .8rem;font-size:.85rem;color:var(--dim)}
.pill b{color:var(--tx);font-weight:600}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:1rem 1.15rem;margin-bottom:.7rem}
.card .src{font-size:.78rem;color:var(--dim);text-transform:uppercase;letter-spacing:.05em;margin-bottom:.2rem}
.note{color:var(--dim);font-size:.88rem;margin-top:.35rem}
.vid{aspect-ratio:16/9;width:100%;border:0;border-radius:10px;margin:.5rem 0}
.warn{background:#2a1f14;border:1px solid #5c3d1e;color:#ffcb91;border-radius:8px;padding:.8rem 1rem;font-size:.9rem;margin-bottom:1rem}
.deg{background:#12151b;border-left:3px solid var(--acc);padding:.7rem 1rem;border-radius:0 8px 8px 0;font-family:ui-monospace,Menlo,monospace;font-size:.95rem;margin:.8rem 0;overflow-x:auto}
.ear{background:#131a15;border-left:3px solid #4caf7d;padding:.8rem 1rem;border-radius:0 8px 8px 0;margin:1rem 0}
.ear b{color:#7fd6a5}
.keynote{color:var(--dim);font-size:.88rem;margin:-.5rem 0 1.5rem;padding-left:.75rem;border-left:2px solid var(--line)}
.spot{display:inline-flex;align-items:center;gap:.45rem;background:#1db954;color:#08130c;font-weight:600;font-size:.88rem;border-radius:999px;padding:.4rem .95rem;margin:.2rem 0 1rem}
.spot:hover{text-decoration:none;background:#1ed760}
.gear dt{color:var(--acc);font-size:.78rem;text-transform:uppercase;letter-spacing:.05em;margin-top:1rem}
.gear dt:first-child{margin-top:0}
.gear dd{margin:.25rem 0 0}
.srcs{font-size:.82rem;color:var(--dim);margin-top:1rem;word-break:break-all}
.srcs a{color:var(--dim)}
footer{color:var(--dim);font-size:.85rem;border-top:1px solid var(--line);margin-top:3rem;padding-top:1.5rem}
p{margin:.7rem 0}ul{margin:.7rem 0 .7rem 1.3rem}li{margin:.3rem 0}
"""


def page(title, body, depth=0, script=""):
    up = "../" * depth
    js = f"<script>{script}</script>" if script else ""
    return f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<link rel="stylesheet" href="{up}style.css"></head>
<body>{body}{js}</body></html>"""


# Filtro en el cliente: sin dependencias, para que GitHub Pages lo sirva tal cual.
FIND_JS = """
(function () {
  var q = document.getElementById('q'),
      clr = document.getElementById('clr'),
      out = document.getElementById('count'),
      items = [].slice.call(document.querySelectorAll('ol.songs li'));
  // Sin tildes ni mayúsculas: buscar "flaca" tiene que encontrar "La Flaca".
  function norm(s) {
    return s.normalize('NFD').replace(/[\\u0300-\\u036f]/g, '').toLowerCase();
  }
  items.forEach(function (li) { li.dataset.k = norm(li.innerText); });
  function run() {
    var terms = norm(q.value).split(/\\s+/).filter(Boolean), n = 0;
    items.forEach(function (li) {
      var ok = terms.every(function (t) { return li.dataset.k.indexOf(t) > -1; });
      li.hidden = !ok;
      if (ok) n++;
    });
    clr.hidden = !q.value;
    out.textContent = !q.value ? '' :
      n === 0 ? 'Ningún tema coincide con "' + q.value + '".' :
      n === 1 ? '1 tema' : n + ' temas';
  }
  q.addEventListener('input', run);
  q.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') { q.value = ''; run(); }
    // Enter con un solo resultado entra directo a la ficha.
    if (e.key === 'Enter') {
      var v = items.filter(function (li) { return !li.hidden; });
      if (v.length === 1) v[0].querySelector('a').click();
    }
  });
  clr.addEventListener('click', function () { q.value = ''; run(); q.focus(); });
  document.addEventListener('keydown', function (e) {
    if (e.key === '/' && document.activeElement !== q) { e.preventDefault(); q.focus(); }
  });
  run();
})();
"""


def main():
    songs = load("songs.json", [])
    res = {s["title"]: s for s in load("resources.json", [])}
    th = {s["title"]: s for s in load("theory.json", [])}
    gear = {s["title"]: s for s in load("gear.json", [])}
    spot = load("spotify.json", {})
    spot_tracks = {t["title"]: t for t in spot.get("tracks", [])}

    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(os.path.join(OUT, "temas"), exist_ok=True)
    with open(os.path.join(OUT, "style.css"), "w", encoding="utf-8") as f:
        f.write(CSS)
    open(os.path.join(OUT, ".nojekyll"), "w").close()

    # --- index ---
    items = []
    for n, s in enumerate(songs, 1):
        slug = slugify(s["title"])
        k = f'<span class="k">{html.escape(s["key"])}</span>' if s.get("key") else ""
        items.append(
            f'<li><a data-n="{n}" href="temas/{slug}.html">'
            f'<span><span class="t">{html.escape(s["title"])}</span>'
            f'<br><span class="a">{html.escape(s["artist"])}</span></span>{k}</a></li>'
        )
    playlist_pill = (f'<div class="meta"><a class="pill" href="{html.escape(spot["playlist_url"])}" '
                     f'target="_blank" rel="noopener">🎧 <b>Escuchar el repertorio</b> en Spotify</a></div>'
                     if spot.get("playlist_url") else "")
    buscador = ('<div class="find"><span class="ico">⌕</span>'
                '<input id="q" type="search" autocomplete="off" spellcheck="false" '
                'placeholder="Buscar por tema, artista o tonalidad…" aria-label="Buscar tema">'
                '<button class="clr" id="clr" hidden aria-label="Limpiar búsqueda">×</button></div>'
                '<div class="count" id="count" role="status"></div>')
    idx = f"""<header><div class="wrap"><h1>Repertorio · 16 de octubre</h1></div></header>
<div class="wrap">
{playlist_pill}
{buscador}
<ol class="songs">{''.join(items)}</ol></div>"""
    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
        f.write(page("Repertorio · 16 de octubre", idx, script=FIND_JS))

    # --- página por tema ---
    for s in songs:
        slug = slugify(s["title"])
        r = res.get(s["title"], {})
        t = th.get(s["title"], {})
        b = ['<div class="wrap"><a class="back" href="../index.html">← Volver al repertorio</a>']
        b.append(f'<h1>{html.escape(s["title"])}</h1>')
        b.append(f'<p class="sub">{html.escape(s["artist"])}</p>')

        sp = spot_tracks.get(s["title"])
        if sp and sp.get("url"):
            b.append(f'<a class="spot" href="{html.escape(sp["url"])}" target="_blank" '
                     f'rel="noopener">▶ Escuchar en Spotify</a>')

        # Un solo pill con el tono que se toca; la diferencia con el disco va en la nota corta.
        key = s.get("key") or t.get("key_verified")
        if key:
            b.append(f'<div class="meta"><span class="pill">Tonalidad: '
                     f'<b>{html.escape(key)}</b></span></div>')
        if t.get("key_note"):
            b.append(f'<div class="keynote">{html.escape(t["key_note"])}</div>')

        b.append("<h2>Tablaturas</h2>")
        tabs = r.get("tabs") or []
        if tabs:
            for tab in tabs:
                if not tab.get("url"):
                    continue
                note = f'<div class="note">{html.escape(tab["note"])}</div>' if tab.get("note") else ""
                b.append(
                    f'<div class="card"><div class="src">{html.escape(tab.get("source","Tab"))}</div>'
                    f'<a href="{html.escape(tab["url"])}" target="_blank" rel="noopener">{html.escape(tab["url"])}</a>{note}</div>'
                )
        else:
            b.append('<div class="warn">Sin tab verificada todavía. Buscá en Songsterr o Ultimate-Guitar.</div>')

        b.append("<h2>Videos</h2>")
        vids = r.get("videos") or []
        if vids:
            for v in vids:
                vid = yt_id(v.get("url", ""))
                b.append('<div class="card">')
                b.append(f'<div class="src">{html.escape(v.get("channel","YouTube"))}</div>')
                b.append(f'<a href="{html.escape(v.get("url",""))}" target="_blank" rel="noopener">{html.escape(v.get("title","Ver lección"))}</a>')
                if v.get("quality_note"):
                    b.append(f'<div class="note">{html.escape(v["quality_note"])}</div>')
                if vid:
                    b.append(f'<iframe class="vid" src="https://www.youtube.com/embed/{vid}" loading="lazy" allowfullscreen></iframe>')
                b.append("</div>")
        else:
            b.append('<div class="warn">Sin video verificado todavía.</div>')

        g = gear.get(s["title"])
        if g:
            b.append("<h2>Setup del guitarrista original</h2>")
            rows = [("Guitarrista", g.get("guitarist")), ("Guitarra", g.get("guitar")),
                    ("Amplificador", g.get("amp")), ("Efectos", g.get("effects")),
                    ("La clave del sonido", g.get("signature_move")),
                    ("Cómo acercarte con lo que tenés", g.get("diy"))]
            dl = "".join(f"<dt>{html.escape(k)}</dt><dd>{md(v)}</dd>" for k, v in rows if v)
            # Sólo avisamos cuando el dato es flojo; decir "documentación alta" no aporta.
            warn = {"medio": "Parte de este setup está poco documentado.",
                    "bajo": "Setup poco documentado: tomalo como aproximación."}.get(g.get("confidence"))
            extra = f'<div class="note">{warn}</div>' if warn else ""
            extra += sources_html(g.get("sources"))
            b.append(f'<div class="card"><dl class="gear">{dl}</dl>{extra}</div>')

        if t.get("analysis_md") or t.get("progression_degrees"):
            b.append("<h2>Análisis armónico</h2>")
            if t.get("progression_degrees"):
                b.append(f'<div class="deg">{html.escape(t["progression_degrees"])}</div>')
            b.append(md(t.get("analysis_md", "")))
            if t.get("tip"):
                b.append(f'<div class="ear"><b>Para tocarlo:</b> {html.escape(t["tip"])}</div>')
            b.append(sources_html(t.get("sources")))

        b.append("</div>")
        with open(os.path.join(OUT, "temas", f"{slug}.html"), "w", encoding="utf-8") as f:
            f.write(page(f'{s["title"]} · Repertorio', "\n".join(b), depth=1))

    print(f"OK: {len(songs)} temas | tabs/videos: {len(res)} | teoría: {len(th)}")
    print(f"salida: {OUT}")


if __name__ == "__main__":
    main()
