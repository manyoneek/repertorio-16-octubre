#!/usr/bin/env python3
"""Crea la playlist del repertorio en Spotify.

Uso:
    python3 tools/crear_playlist.py "<url de callback pegada del navegador>"

La URL de callback es la que queda en la barra de direcciones después de
autorizar (arranca con http://127.0.0.1:8888/callback?code=...). El navegador
va a mostrar un error de conexión: es esperado, nadie está escuchando en ese
puerto. Lo único que importa es la URL.

Credenciales: salen de 1Password (vault "manny", item "Spotify app - Bands In
Trip"). No se pasan por argumento ni quedan en el historial del shell.
"""
import base64
import json
import os
import subprocess
import sys
import urllib.parse
import urllib.request

VAULT = "manny"
ITEM = "pbpitblwdhlyzivuglvllwfmki"
REDIRECT = "http://127.0.0.1:8888/callback"
DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "songs.json")
TOKENS = os.path.expanduser("~/.config/bands-in-trip/tokens-write.json")


def op_field(label):
    return subprocess.run(
        ["op", "item", "get", ITEM, "--vault", VAULT, "--fields", f"label={label}", "--reveal"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()


def api(url, token, method="GET", body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    if data:
        req.add_header("Content-Type", "application/json")
    return json.loads(urllib.request.urlopen(req).read() or b"{}")


def get_token():
    cid, csec = op_field("client id"), op_field("client secret")
    basic = base64.b64encode(f"{cid}:{csec}".encode()).decode()

    if os.path.exists(TOKENS):
        with open(TOKENS) as f:
            saved = json.load(f)
        if saved.get("refresh_token"):
            payload = urllib.parse.urlencode({
                "grant_type": "refresh_token",
                "refresh_token": saved["refresh_token"],
            }).encode()
            req = urllib.request.Request("https://accounts.spotify.com/api/token", data=payload)
            req.add_header("Authorization", f"Basic {basic}")
            return json.loads(urllib.request.urlopen(req).read())["access_token"]

    if len(sys.argv) < 2:
        sys.exit("Falta la URL de callback. Ver el docstring de este archivo.")
    code = urllib.parse.parse_qs(urllib.parse.urlparse(sys.argv[1]).query).get("code", [None])[0]
    if not code:
        sys.exit("Esa URL no tiene ?code=. Copiá la barra de direcciones entera.")

    payload = urllib.parse.urlencode({
        "grant_type": "authorization_code", "code": code, "redirect_uri": REDIRECT,
    }).encode()
    req = urllib.request.Request("https://accounts.spotify.com/api/token", data=payload)
    req.add_header("Authorization", f"Basic {basic}")
    tok = json.loads(urllib.request.urlopen(req).read())

    os.makedirs(os.path.dirname(TOKENS), exist_ok=True)
    with open(TOKENS, "w") as f:
        json.dump(tok, f)
    os.chmod(TOKENS, 0o600)
    return tok["access_token"]


def find_track(token, song):
    for q in (f"track:{song['title']} artist:{song['artist']}", f"{song['title']} {song['artist']}"):
        url = "https://api.spotify.com/v1/search?" + urllib.parse.urlencode(
            {"q": q, "type": "track", "limit": 5, "market": "UY"})
        items = api(url, token).get("tracks", {}).get("items", [])
        for t in items:
            artists = " ".join(a["name"].lower() for a in t.get("artists", []))
            if song["artist"].lower().split()[0] in artists:
                return t
        if items:
            return items[0]
    return None


def main():
    token = get_token()
    me = api("https://api.spotify.com/v1/me", token)
    print(f"cuenta: {me.get('display_name')} ({me.get('id')})")

    with open(DATA, encoding="utf-8") as f:
        songs = json.load(f)

    uris, missing = [], []
    for s in songs:
        t = find_track(token, s)
        if t:
            uris.append(t["uri"])
            print(f"  ok   {s['title'][:34]:36s} -> {t['artists'][0]['name']}")
        else:
            missing.append(s["title"])
            print(f"  MISS {s['title']}")

    pl = api(f"https://api.spotify.com/v1/users/{me['id']}/playlists", token, "POST", {
        "name": "Repertorio 16 de octubre",
        "description": "Temas del concierto del 16 de octubre. Armada automáticamente.",
        "public": False,
    })
    for i in range(0, len(uris), 100):
        api(f"https://api.spotify.com/v1/playlists/{pl['id']}/tracks", token, "POST",
            {"uris": uris[i:i + 100]})

    print(f"\nplaylist creada: {pl['external_urls']['spotify']}")
    print(f"{len(uris)} temas agregados" + (f", faltaron: {missing}" if missing else ""))


if __name__ == "__main__":
    main()
