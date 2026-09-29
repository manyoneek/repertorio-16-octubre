# Reglas del proyecto

## Notación musical

- **Siempre usar notación americana para notas, acordes, tonalidades y afinaciones: C, D, E, F, G, A, B.** Es una preferencia explícita de Andy.
- Usar también letras en el texto explicativo: `en G`, `de Bb a B`, `E–F–F#–G`. No escribir nombres de solfeo ni equivalencias redundantes como `G (Sol)`.
- Conservar las alteraciones y la calidad del acorde: `F#`, `Bb`, `Am`, `D7`. Las explicaciones siguen en español rioplatense.
- Aplicar la regla a todas las fichas, recomendaciones de equipo y Quad Cortex, diagramas y datos fuente, incluidos los parciales `data/_gear_g*.json`.
- No confundir notas con palabras comunes o nombres propios. No modificar «La Renga», «Mi» como posesivo, «Si» como conjunción ni títulos originales. Revisar cualquier conversión automática antes de guardarla.

## Edición y publicación

- El contenido debe explicar la música, no el proceso de edición: evitar frases como «la referencia ahora es» y comparaciones con versiones que ya se reemplazaron.
- No poner avisos de que no hace falta transponer. Aclarar diferencias de tonalidad o afinación sólo cuando aporten una indicación para tocar.
- Editar `data/` y `build.py`, no los HTML generados a mano. Si se cambia `gear.json`, mantener alineada la entrada del parcial `_gear_g*.json` correspondiente.
- Ejecutar `python3 build.py`, revisar el diff y verificar que no se alteraron títulos, artistas ni enlaces por convertir notas. Publicar los cambios autorizados mediante commit y push y verificar GitHub Pages.
