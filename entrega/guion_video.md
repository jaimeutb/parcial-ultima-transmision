# Naskah video — hanya teks keterangan (tanpa suara)

Target durasi **± 5:30** (batas 6:00). File ini hanya alat bantu: tidak ikut ke ZIP (yang ikut hanya `entrega/video.mp4`).

**Cara pakai:**
- Kolom **Ketik / lakukan** = yang Anda kerjakan saat merekam.
- **⏸** = berhenti 4–5 detik tanpa mengetik, supaya ada waktu membaca keterangan.
- Teks di kotak kutipan (**R1, R2, …**) = keterangan dalam bahasa Spanyol. Salin apa adanya ke Clipchamp, ditaruh di atas momen tersebut.

---

## Persiapan (jangan direkam)

```powershell
.venv\Scripts\Activate.ps1
function prompt { "PS> " }
cls
```

- Atur jendela terminal supaya hanya menempati **±80 % layar bagian atas**. Bagian bawah dibiarkan kosong untuk teks keterangan.
- Perbesar font terminal (Ctrl + `+`). Nyalakan *Do not disturb* (Win+N).
- Siapkan VS Code dengan `docs/arquitectura.md` terbuka di bagian **AD-2** (untuk segmen 6).
- Mulai rekam: **Win+Shift+R** → pilih seluruh layar → Start (mikrofon mati).

---

## Segmen 0 — Pembuka (0:00–0:15)

| Ketik / lakukan | Keterangan |
|---|---|
| Layar terminal kosong ⏸⏸ | R1, lalu R2 |

> **R1** (8 s) — Parcial práctico de Ingeniería de Software · «La última transmisión»
> JAIME MO CHEN · Curso 1206 · Docente: Aisner Jose Marrugo Juliao

> **R2** (6 s) — Motor de historias interactivas en Python (consola). Se muestran: tres finales, segunda historia, validación, pruebas y deshacer.

## Segmen 1 — Tiga ending dan kondisi (0:15–1:40)

| Ketik / lakukan | Keterangan |
|---|---|
| `python -m motor historias/la_ultima_transmision.json` ⏸ | R3 |
| `revisar`, `investigar` | R4 |
| `e` ⏸ | R5 |
| (tunjukkan pilihan di E3) ⏸ | R6 |
| `activar_codigo` ⏸ | R7 |
| `r` | R8 |
| `revisar`, `continuar` ⏸⏸ | R9 |
| `activar_sin_verificar` ⏸ | R10 |
| `r`, `revisar`, `continuar`, `cortar` ⏸ | R11 |

> **R3** — Historia oficial cargada desde un archivo JSON. Solo se muestran las opciones habilitadas.

> **R4** — Se eligió «investigar»: su efecto asigna conoce_origen = verdadero.

> **R5** — Comando «e»: muestra el estado actual de las variables.

> **R6** — Condición: como conoce_origen es verdadero, E3 ofrece «activar_codigo».

> **R7** — Final 1 de 3: E4 Rescate.

> **R8** — «r» reinicia la partida con las variables iniciales.

> **R9** (7 s) — Ahora sin investigar (conoce_origen = falso): E3 ofrece «activar_sin_verificar» en lugar de «activar_codigo».

> **R10** — Final 2 de 3: E5 El eco.

> **R11** — Final 3 de 3: E6 Silencio. «cortar» está disponible se haya investigado o no.

## Segmen 2 — Deshacer, perubahan jam ke-6 (1:40–2:50)

Lanjutkan di sesi yang sama. **Catat menit awal segmen ini** untuk `docs/analisis_impacto_cambio.md`.

| Ketik / lakukan | Keterangan |
|---|---|
| ⏸ | R12 |
| `r`, `revisar`, `investigar`, `e` ⏸ | R13 |
| `d`, `e` ⏸ | R14 |
| `d` ⏸ | R15 |
| `continuar` ⏸⏸ | R16 |
| `activar_sin_verificar`, `d` ⏸ | R17 |
| `q` | — |

> **R12** — Solicitud de cambio (hora 6): deshacer la última elección válida, con un solo nivel.

> **R13** — Ejemplo del docente: desde E2, «investigar» lleva a E3 con conoce_origen = verdadero.

> **R14** — «d» deshace: vuelve a E2 y conoce_origen vuelve a falso.

> **R15** — Un segundo «d» no cambia nada: solo se guarda un nivel.

> **R16** (7 s) — Al continuar sin investigar, E3 muestra «activar_sin_verificar» y «cortar», como pide la solicitud.

> **R17** — Desde un final, «d» también vuelve a E3 con los valores previos.

## Segmen 3 — Cerita kedua (2:50–3:30)

| Ketik / lakukan | Keterangan |
|---|---|
| `cls`, lalu `python -m motor historias/el_faro.json` ⏸ | R18 |
| `faro_buscar_llave` ⏸ | R19 |
| `faro_abrir_candado`, `faro_encender_lampara` ⏸ | R20 |
| `q` | — |

> **R18** (7 s) — Segunda historia, «El faro de Isla Gris», con el mismo motor: no se modificó el código de motor/.

> **R19** — Con la llave se habilita «faro_abrir_candado»; si se va directo a la puerta, esa opción no aparece.

> **R20** — Final «faro_rescate» alcanzado.

## Segmen 4 — Error destino yang tidak ada (3:30–3:55)

| Ketik / lakukan | Keterangan |
|---|---|
| `cls`, lalu `python -m motor --validar historias/invalidas/destino_inexistente.json` ⏸ | R21 |
| `$LASTEXITCODE` ⏸ | R22 |

> **R21** — Archivo inválido: una opción apunta a la escena E99, que no existe.

> **R22** (7 s) — El validador informa código, ubicación y causa, no abre ninguna partida y termina con código 2.

## Segmen 5 — Tes (3:55–4:35)

| Ketik / lakukan | Keterangan |
|---|---|
| `cls`, lalu `python -m pytest -q` ⏸ | R23 |
| `python -m pytest -v tests/test_deshacer.py` ⏸⏸ | R24 |

> **R23** (7 s) — Pruebas automatizadas: 301 pasan (U1–U6, I1, CLI, RNF y coherencia de la documentación).

> **R24** (7 s) — Las 12 pruebas U6 del cambio: ejemplo del docente, un solo nivel, entradas inválidas y deshacer desde cada final.

## Segmen 6 — Penutup: arsitektur dan dampak perubahan (4:35–5:35)

| Ketik / lakukan | Keterangan |
|---|---|
| Pindah ke VS Code: `docs/arquitectura.md`, bagian AD-2 ⏸⏸⏸ | R25, R26, R27 |
| Kembali ke terminal: `cls`, lalu `git diff --stat v1-inicial v2-cambio -- motor/` ⏸⏸⏸ | R28, R29 |
| ⏸ | R30 |

> **R25** — Decisión de arquitectura AD-2: deshacer con una única instantánea (escena + copia de las variables).

> **R26** — Alternativas descartadas: pila de instantáneas, patrón Command y repetir las elecciones desde el inicio.

> **R27** (7 s) — Motivo: la regla «un solo nivel» se cumple por construcción y no se tocan el modelo, el validador ni las historias.

> **R28** (7 s) — Impacto del cambio: RF17 nuevo; RF06, RF08, RF09 y RF16 ampliados; modelos, trazabilidad y backlog actualizados.

> **R29** (7 s) — Entre v1-inicial y v2-cambio solo cambiaron motor/sesion.py y motor/cli.py. Las 95 pruebas de la versión inicial siguen pasando.

> **R30** — Fin de la demostración.

---

## Menyunting di Clipchamp

1. Buka **Clipchamp** → *Create a new video* → impor MP4 hasil rekaman → seret ke timeline.
2. Potong jeda yang terlalu panjang atau salah ketik: taruh penanda waktu, tekan **S** (*split*), lalu hapus potongannya.
3. Menu **Text** di kiri → pilih gaya sederhana → seret ke timeline **di atas** video, sejajar dengan momennya → tempel teks R-nya.
4. Format teks: putih di atas latar gelap semi-transparan, ukuran besar, posisi di **pita bawah** yang kosong. Durasi sesuai angka di naskah (default 5 s).
5. **Export** → 1080p. Simpan sebagai `entrega\video.mp4`. Pastikan durasinya ≤ 6:00 dan teksnya terbaca saat layar penuh.
