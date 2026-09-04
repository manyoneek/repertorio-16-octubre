#!/usr/bin/env python3
"""Pasa los nombres de nota del copy a notación americana (Do -> C).

Sólo toca nombres de nota escritos en mayúscula inicial: en minúscula, 'la',
'mi', 'si' y 'sol' son artículo, posesivo, conjunción o sustantivo, y
convertirlos rompería la frase ('la mayor parte' no es A mayor).

    python3 tools/notacion.py [--dry-run]
"""
import json, re, sys

LETRA = {"do": "C", "re": "D", "mi": "E", "fa": "F", "sol": "G", "la": "A", "si": "B"}
NOTA = r"(?:Do|Re|Mi|Fa|Sol|La|Si|DO|RE|MI|FA|SOL|LA|SI)"
CALIDAD = r"(?:mayor|menor|natural|dórico|dórica|mixolidio|eolio|lidio|frigio|locrio|" \
          r"MAYOR|MENOR|NATURAL|DÓRICO|mixolidia)"
CIFRAS = {"Dom": "Cm", "Rem": "Dm", "Mim": "Em", "Fam": "Fm",
          "Solm": "Gm", "Lam": "Am", "Sim": "Bm"}
URL = re.compile(r"https?://\S+")


def convertir(text):
    holes = []
    t = URL.sub(lambda m: (holes.append(m.group(0)), f"\x00{len(holes)-1}\x00")[1], text)

    t = re.sub(r"\b([A-G])\s+(?:sostenido|SOSTENIDO)\b", r"\1#", t)
    t = re.sub(r"\b([A-G])\s+(?:bemol|BEMOL)\b", r"\1b", t)
    # Do#, Lab, Fa#m: con alteración nunca son palabras del castellano.
    t = re.sub(rf"\b({NOTA})(#|b)(m|maj|sus|dim|aug|7|m7)?(?![\w#])",
               lambda m: LETRA[m.group(1).lower()] + m.group(2) + (m.group(3) or ""), t)
    # Nota suelta detrás de preposición, salvo que siga un nombre propio (La Renga).
    t = re.sub(rf"\b([Ee]n|[Dd]e|[Aa]|[Aa]l|[Hh]acia|[Ss]obre|[Hh]asta|[Dd]esde|[Ee]ntre)\s+({NOTA})\b(?!\s+[A-ZÁÉÍÓÚ][a-záéíóú])",
               lambda m: f"{m.group(1)} {LETRA[m.group(2).lower()]}", t)
    # 'el Do', 'ese La': artículo más nota, sin sufijo que la vuelva palabra.
    t = re.sub(rf"\b([Ee]l|[Uu]n|[Ee]se|[Ee]ste|[Dd]el|[Nn]ingún)\s+({NOTA})\b(?![\wáéíóúñ])",
               lambda m: f"{m.group(1)} {LETRA[m.group(2).lower()]}", t)
    t = re.sub(rf"\b([Cc]entro tonal|[Tt]ónica|[Ff]undamental)\s+({NOTA})\b(?![\wáéíóúñ])",
               lambda m: f"{m.group(1)} {LETRA[m.group(2).lower()]}", t)
    # Nota más calificador musical.
    t = re.sub(rf"\b({NOTA})\s+(aumentado|disminuido|abierto|estándar|estandar|dominante)\b",
               lambda m: f"{LETRA[m.group(1).lower()]} {m.group(2)}", t)
    # Secuencias tipo 'Do–Si–La–Sol' o 'Mi-Re#-Do#'.
    def seq(m):
        return re.sub(rf"\b({NOTA})\b", lambda x: LETRA[x.group(1).lower()], m.group(0))
    t = re.sub(rf"\b{NOTA}(?:[#b])?(?:\s*[–\-→]\s*(?:{NOTA})(?:[#b])?){{1,}}", seq, t)
    # Listas entre paréntesis: '(Sol y Re)', '(Sol, A menor, Do, Sol)'.
    t = re.sub(r"\([^()]{0,80}\)", lambda m: re.sub(
        rf"\b({NOTA})\b(?!\s+[a-záéíóú]{{4,}})",
        lambda x: LETRA[x.group(1).lower()], m.group(0)) if re.search(
        rf"\b{NOTA}\b", m.group(0)) and re.search(
        r"[A-G][#b]?|acorde|menor|mayor|aumentado|grado|y ", m.group(0)) else m.group(0), t)
    # Fa sostenido -> F#, Si bemol -> Bb (antes que la calidad, que puede seguir).
    t = re.sub(rf"\b({NOTA})\s+(?:sostenido|SOSTENIDO)\b",
               lambda m: LETRA[m.group(1).lower()] + "#", t)
    t = re.sub(rf"\b({NOTA})\s+(?:bemol|BEMOL)\b",
               lambda m: LETRA[m.group(1).lower()] + "b", t)
    # Do mayor -> C mayor, Mi dórico -> E dórico.
    t = re.sub(rf"\b({NOTA})\s+({CALIDAD})\b",
               lambda m: f"{LETRA[m.group(1).lower()]} {m.group(2)}", t)
    # Cifrado latino suelto: Sim -> Bm.
    t = re.sub(r"\b(" + "|".join(CIFRAS) + r")\b", lambda m: CIFRAS[m.group(1)], t)
    # Nota suelta cuando la frase deja claro que es una nota.
    t = re.sub(rf"\b(acorde de|va a|vuelve a|resuelve a|la nota|la tónica de)\s+({NOTA})\b",
               lambda m: f"{m.group(1)} {LETRA[m.group(2).lower()]}", t)
    # Nota resaltada en negrita: **Do**, **Sol**.
    t = re.sub(rf"\*\*({NOTA})\*\*", lambda m: f"**{LETRA[m.group(1).lower()]}**", t)
    t = re.sub(rf"\*\*({NOTA})\s+\(", lambda m: f"**{LETRA[m.group(1).lower()]} (", t)
    # 'Re (D)' decía dos veces la misma nota.
    t = re.sub(rf"\b({NOTA})\s*\(([A-G][#b]?)\)",
               lambda m: m.group(2) if LETRA[m.group(1).lower()] == m.group(2) else m.group(0), t)
    # 'La como tónica', 'La pasa a funcionar'.
    t = re.sub(rf"\b({NOTA})\s+(como\s+(?:tónica|centro|casa)|pasa a|funciona|se convierte)",
               lambda m: f"{LETRA[m.group(1).lower()]} {m.group(2)}", t)
    t = re.sub(rf"\b({NOTA})\s+(en el bajo)",
               lambda m: f"{LETRA[m.group(1).lower()]} {m.group(2)}", t)
    # Enumeraciones: basta con que una del grupo ya sea nota para convertir el resto.
    TOKEN = rf"(?:[A-G][#b]?|{NOTA})"
    t = re.sub(rf"\b{TOKEN}(?:\s*(?:,|y|–|-|→)\s*{TOKEN})+\b",
               lambda m: re.sub(rf"\b({NOTA})\b",
                                lambda x: LETRA[x.group(1).lower()], m.group(0)), t)
    # 'E menor (Em)' quedaba diciendo dos veces lo mismo.
    t = re.sub(r"\b([A-G][#b]?) (?:mayor|MAYOR)\s*\(\1\)", r"\1", t)
    t = re.sub(r"\b([A-G][#b]?) (?:menor|MENOR)\s*\(\1m\)", r"\1m", t)

    return re.sub(r"\x00(\d+)\x00", lambda m: holes[int(m.group(1))], t)


TEXT_KEYS = {"analysis_md", "key_note", "tip", "progression_degrees", "guitarist",
             "guitar", "amp", "effects", "signature_move", "diy", "note",
             "quality_note", "key_verified"}


def walk(node, changes):
    if isinstance(node, dict):
        for k, v in node.items():
            if isinstance(v, str) and k in TEXT_KEYS:
                new = convertir(v)
                if new != v:
                    changes.append((k, v, new))
                    node[k] = new
            else:
                walk(v, changes)
    elif isinstance(node, list):
        for v in node:
            walk(v, changes)


def main():
    dry = "--dry-run" in sys.argv
    for f in ["data/theory.json", "data/gear.json", "data/resources.json"]:
        data = json.load(open(f, encoding="utf-8"))
        changes = []
        walk(data, changes)
        print(f"{f}: {len(changes)} campos")
        if dry:
            for k, old, new in changes[:3]:
                print("   ", k, "->", new[:110])
        else:
            json.dump(data, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
