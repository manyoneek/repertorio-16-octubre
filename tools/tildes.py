#!/usr/bin/env python3
"""Restaura tildes en el copy en castellano de data/*.json.

Varias tandas de investigación llegaron con el texto sin acentos. Este script
corrige sólo lo que no admite otra lectura: sustantivos, adjetivos y adverbios,
más un puñado de casos con contexto suficiente. Las URLs quedan intactas.

    python3 tools/tildes.py [--dry-run]
"""
import json, re, sys

# Sin ambigüedad: la forma sin tilde no es una palabra válida en castellano.
PALABRAS = """
aca acompanamiento acustica acusticas acustico ademas afinacion ahi analisis analogico
animo ano anos armonia armonica armonicamente armonico atras bateria britanico cancion
caracter caracteristico catalogo clasica clasico compas compresion comun confirmacion
creditos cromatico demas desafio detras diatonico dieciseis dificil digitacion dinamica
dorico dramatico electrica electrico epoca escuchandola especifico especificamente
estan estereo estandar explicitamente funcion identica interes leccion lider linea
logicas magico mastil maximo melancolico melodia melodico metodo metronomo modulacion
moviendose muchisimo muneca musica musico ningun organo patron pentatonica percusion
posicion practicamente presion produccion progresion proposito pua rapidas rapido
recien resolucion ritmica ritmico saturacion seccion segun senal sensacion septima
septimas sesion tambien tecnica tecnico tension tipico todavia tremolo triadas tonica
util unica unico vaiven venia version distorsion grabacion habia melodica sinfonico
""".split()

TILDE = {
    "articulo": "artículo", "minima": "mínima", "minimo": "mínimo",
    "asi": "así", "despues": "después", "encontre": "encontré", "aparecio": "apareció",
    "cortisimos": "cortísimos", "cortisimas": "cortísimas", "muchisimas": "muchísimas",
    "muchisimos": "muchísimos", "muchisima": "muchísima",
    "aclaracion": "aclaración", "adaptacion": "adaptación", "alteracion": "alteración",
    "anticipacion": "anticipación", "aproximacion": "aproximación", "armonias": "armonías",
    "armonicas": "armónicas", "armonicos": "armónicos", "articulacion": "articulación",
    "autentica": "auténtica", "autentico": "auténtico", "autoria": "autoría",
    "basicamente": "básicamente", "basico": "básico", "basica": "básica",
    "benefica": "benéfica", "combinacion": "combinación", "complicacion": "complicación",
    "confusion": "confusión", "cromatica": "cromática", "cromaticas": "cromáticas",
    "cromaticamente": "cromáticamente", "cromaticos": "cromáticos", "deberia": "debería",
    "decoracion": "decoración", "diatonicos": "diatónicos", "diatonicas": "diatónicas",
    "diatonica": "diatónica", "dinamico": "dinámico", "dinamicos": "dinámicos",
    "dinamicas": "dinámicas", "documentacion": "documentación", "economia": "economía",
    "eleccion": "elección", "electricas": "eléctricas", "electricos": "eléctricos",
    "elegantisimo": "elegantísimo", "energia": "energía", "estatico": "estático",
    "estatica": "estática", "estrofico": "estrófico", "exhibicion": "exhibición",
    "fotografia": "fotografía", "identicas": "idénticas", "identico": "idéntico",
    "informacion": "información", "interpretacion": "interpretación",
    "inyeccion": "inyección", "larguisimos": "larguísimos", "larguisimas": "larguísimas",
    "mayoria": "mayoría", "melancolica": "melancólica", "melodias": "melodías",
    "metalico": "metálico", "metalica": "metálica", "microfono": "micrófono",
    "microfonos": "micrófonos", "observacion": "observación", "opcion": "opción",
    "plastico": "plástico", "recibia": "recibía", "tecnicamente": "técnicamente",
    "tecnicas": "técnicas", "tecnicos": "técnicos", "teorico": "teórico",
    "teorica": "teórica", "teoricamente": "teóricamente", "tragico": "trágico",
    "variacion": "variación", "variaciones": "variaciones", "acusticos": "acústicos",
    "canciones": "canciones", "clasicos": "clásicos", "clasicas": "clásicas",
    "epocas": "épocas", "lineas": "líneas", "musicos": "músicos", "puas": "púas",
    "sesiones": "sesiones", "tonicas": "tónicas", "unicas": "únicas", "unicos": "únicos",
    "versiones": "versiones", "septimo": "séptimo", "septimos": "séptimos",
    "aca": "acá", "acompanamiento": "acompañamiento", "acustica": "acústica",
    "acusticas": "acústicas", "acustico": "acústico", "ademas": "además",
    "afinacion": "afinación", "ahi": "ahí", "analisis": "análisis",
    "analogico": "analógico", "animo": "ánimo", "ano": "año", "anos": "años",
    "armonia": "armonía", "armonica": "armónica", "armonicamente": "armónicamente",
    "armonico": "armónico", "atras": "atrás", "bateria": "batería",
    "britanico": "británico", "cancion": "canción", "caracter": "carácter",
    "caracteristico": "característico", "catalogo": "catálogo", "clasica": "clásica",
    "clasico": "clásico", "compas": "compás", "compresion": "compresión",
    "comun": "común", "confirmacion": "confirmación", "creditos": "créditos",
    "cromatico": "cromático", "demas": "demás", "desafio": "desafío",
    "detras": "detrás", "diatonico": "diatónico", "dieciseis": "dieciséis",
    "dificil": "difícil", "digitacion": "digitación", "dinamica": "dinámica",
    "distorsion": "distorsión", "dorico": "dórico", "dramatico": "dramático",
    "electrica": "eléctrica", "electrico": "eléctrico", "epoca": "época",
    "escuchandola": "escuchándola", "especifico": "específico",
    "especificamente": "específicamente", "estan": "están", "estereo": "estéreo",
    "estandar": "estándar", "explicitamente": "explícitamente", "funcion": "función",
    "grabacion": "grabación", "habia": "había", "identica": "idéntica",
    "interes": "interés", "leccion": "lección", "lider": "líder", "linea": "línea",
    "logicas": "lógicas", "magico": "mágico", "mastil": "mástil", "maximo": "máximo",
    "melancolico": "melancólico", "melodia": "melodía", "melodica": "melódica",
    "melodico": "melódico", "metodo": "método", "metronomo": "metrónomo",
    "modulacion": "modulación", "moviendose": "moviéndose", "muchisimo": "muchísimo",
    "muneca": "muñeca", "musica": "música", "musico": "músico", "ningun": "ningún",
    "organo": "órgano", "patron": "patrón", "pentatonica": "pentatónica",
    "percusion": "percusión", "posicion": "posición", "practicamente": "prácticamente",
    "presion": "presión", "produccion": "producción", "progresion": "progresión",
    "proposito": "propósito", "pua": "púa", "rapidas": "rápidas", "rapido": "rápido",
    "recien": "recién", "resolucion": "resolución", "ritmica": "rítmica",
    "ritmico": "rítmico", "saturacion": "saturación", "seccion": "sección",
    "segun": "según", "senal": "señal", "sensacion": "sensación", "septima": "séptima",
    "septimas": "séptimas", "sesion": "sesión", "sinfonico": "sinfónico",
    "tambien": "también", "tecnica": "técnica", "tecnico": "técnico",
    "tension": "tensión", "tipico": "típico", "todavia": "todavía", "tonica": "tónica",
    "tremolo": "trémolo", "triadas": "tríadas", "util": "útil", "unica": "única",
    "unico": "único", "vaiven": "vaivén", "venia": "venía", "version": "versión",
}

# Con contexto: la regla de arriba no alcanza, pero la frase resuelve la duda.
CONTEXTO = [
    (r"\bgrabo\b", "grabó"), (r"\bmovio\b", "movió"), (r"\bsalio\b", "salió"),
    (r"\bdescribio\b", "describió"), (r"\bconto que\b", "contó que"),
    (r"\bregalo la\b", "regaló la"), (r"\bentro después\b", "entró después"),
    (r"\bque toco este\b", "que tocó este"), (r"\bClapton escucho\b", "Clapton escuchó"),
    (r"\bque escucho nunca\b", "que escuché nunca"),
    (r"\bpaso (?=(la|el|los|las) )", "pasó "),
    (r"\b(documentación|sesión|EMI) publica\b", lambda m: m.group(1) + " pública"),
    (r"\bnunca este del todo\b", "nunca esté del todo"),
    (r"\bdiga cual\b", "diga cuál"), (r"\bse agrego\b", "se agregó"),
    (r"\batandose\b", "atándose"), (r"\bambiguedad\b", "ambigüedad"),
    (r"\bconseguis\b", "conseguís"), (r"\bestas haciendo\b", "estás haciendo"),
    (r"\bacompanar\b", "acompañar"), (r"\bpoeelo\b", "ponelo"),
    (r"\bdonde esta la\b", "donde está la"), (r"\ble sacas\b", "le sacás"),
    (r"\blo escuchas\b", "lo escuchás"), (r"\bmas precisamente\b", "más precisamente"),
    (r"\bla practica\b", "la práctica"),
    (r"\bfuente publica\b", "fuente pública"),
    (r"\bque (?=(guitarra|guitarras|pedal|pedales|amplificador|equipo|modelo|cuerdas|efectos)\b)", "qué "),
    (r"\buso\b(?= [A-Z])", "usó"),
    (r"\bremato\b", "remató"),
    (r"\bmas\b", "más"),                      # el 'mas' adversativo no aparece en estos textos
    (r"\bpor que\b", "por qué"),
    (r"\bque tan\b", "qué tan"),
    (r"\bsi mismo\b", "sí mismo"),
    (r"\bde cuanto\b", "de cuánto"),
    (r"\bcerteza total quien\b", "certeza total quién"),
    (r"\bsino cuanto\b", "sino cuánto"),
    (r"\baun asi\b", "aun así"),
    (r"(?<!más )(?<!mas )\bseria\b", "sería"),
    (r"\besta\s+(?=(en|muy|más|hecho|hecha|grabad|documentad|afinad|tocad|basad|pensad|"
     r"construid|ahí|todo|toda|cerca|lejos|claro|clara|lleno|llena|puesta|al |la clave))", "está "),
    (r"\bNapoli\b", "Nápoli"), (r"\bNarigon\b", "Narigón"),
    # Voseo rioplatense, que es como escribe el resto del sitio.
    (r"\btenes\b", "tenés"), (r"\bpodes\b", "podés"), (r"\bvenis\b", "venís"),
    (r"\btocas\b", "tocás"), (r"\busas\b", "usás"), (r"\bdejas\b", "dejás"),
    (r"\bnecesitas\b", "necesitás"), (r"\bpegas\b", "pegás"), (r"\bllenas\b", "llenás"),
    (r"\bbajas\b", "bajás"), (r"\bquedas\b", "quedás"), (r"\bbuscas\b", "buscás"),
    (r"\bqueres\b", "querés"), (r"\bsentis\b", "sentís"), (r"\bpensas\b", "pensás"),
]

URL = re.compile(r"https?://\S+")


def cap(orig, new):
    if orig.isupper() and len(orig) > 1:
        return new.upper()
    if orig[0].isupper():
        return new[0].upper() + new[1:]
    return new


def fix(text):
    holes = []

    def stash(m):
        holes.append(m.group(0))
        return f"\x00{len(holes) - 1}\x00"

    t = URL.sub(stash, text)
    for plain, acc in TILDE.items():
        t = re.sub(rf"\b{plain}\b",
                   lambda m, a=acc: cap(m.group(0), a), t, flags=re.IGNORECASE)
    for pat, acc in CONTEXTO:
        if callable(acc):
            t = re.sub(pat, acc, t, flags=re.IGNORECASE)
        else:
            t = re.sub(pat, lambda m, a=acc: cap(m.group(0), a), t, flags=re.IGNORECASE)
    return re.sub(r"\x00(\d+)\x00", lambda m: holes[int(m.group(1))], t)


TEXT_KEYS = {"analysis_md", "key_note", "tip", "progression_degrees", "guitarist",
             "guitar", "amp", "effects", "signature_move", "diy", "note",
             "quality_note", "title_es"}


def walk(node, changes):
    if isinstance(node, dict):
        for k, v in node.items():
            if isinstance(v, str) and k in TEXT_KEYS:
                new = fix(v)
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
    total = 0
    for f in ["data/theory.json", "data/gear.json", "data/resources.json"]:
        data = json.load(open(f, encoding="utf-8"))
        changes = []
        walk(data, changes)
        total += len(changes)
        print(f"{f}: {len(changes)} campos corregidos")
        if not dry:
            json.dump(data, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"total: {total}")


if __name__ == "__main__":
    main()
