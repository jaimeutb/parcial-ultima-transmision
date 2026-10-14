# Capturas del tablero

Tablero en Trello creado a partir de `docs/backlog.md`. Las tarjetas están en `tarjetas_trello.txt`
(una por línea; al pegarlas en «Añadir una tarjeta», Trello ofrece crear una tarjeta por línea).

| Archivo | Contenido |
|---|---|
| `tablero_inicial.png` | Estado de partida reconstruido: todas las tarjetas en «Por hacer», con responsable y etiqueta «Hora 6» en B13–B17. Reloj del sistema visible. |
| `tablero_final.png` | Estado real al cerrar: tarjetas en «Hecho» / «En curso» / «Por hacer» según `docs/backlog.md`. Reloj del sistema visible. |

El tablero se creó al final del trabajo; el anexo lo declara así y muestra la fecha de cada archivo.

Después de guardar las capturas:

```bash
python scripts/generar_anexo.py
python scripts/generar_pdfs.py
```
