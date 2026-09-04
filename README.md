# Repertorio · 16 de octubre

Material de estudio para el concierto del 16 de octubre. Guitarra eléctrica.

36 temas, cada uno con tablaturas, videos de lección y análisis armónico.

## Sitio

👉 **https://manyoneek.github.io/repertorio-16-octubre/**

- Lista de temas con la tonalidad del chart de la banda
- Una página por tema: tabs, videos embebidos y análisis
- Sección de teoría musical agrupada por tonalidad

## Estructura

```
data/songs.json      lista base: título, artista, tonalidad del chart
data/resources.json  tablaturas y videos por tema
data/theory.json     análisis armónico verificado
build.py             genera docs/ a partir de los tres JSON
docs/                sitio estático (GitHub Pages)
```

## Regenerar el sitio

```bash
python3 build.py
```

Sin dependencias: sólo Python 3 de sistema. `build.py` borra y reescribe `docs/`.

## Cómo agregar o corregir un tema

Editá el JSON correspondiente en `data/` y volvé a correr `build.py`.
No edites `docs/` a mano: se sobreescribe en cada build.

## Sobre las tonalidades

La tonalidad que aparece en la lista es **la del chart de la banda**, que no
siempre coincide con la del disco. Cuando difieren, la ficha del tema lo aclara
arriba de todo — importa para saber si podés tocar junto al video o si primero
tenés que transportar.

## Verificación

El análisis armónico se contrastó contra varias fuentes independientes por tema
(Ultimate-Guitar, Chordify, Hooktheory, Songsterr, Cifra Club, lacuerda).
Donde las fuentes no coincidían o no se pudo verificar, el tema queda marcado
con una advertencia en vez de afirmar algo sin respaldo.
