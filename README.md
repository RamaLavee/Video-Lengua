# Emilia — cortometraje animado sobre *Kentukis* (Samanta Schweblin)

Video animado de unos cuatro minutos que cuenta, solo con imágenes, la historia de **Emilia**: la jubilada de
Lima que «es» una conejita kentuki en el departamento de Eva, en Erfurt. Está pensado para acompañar una
exposición oral: no tiene voz en off, diálogos ni subtítulos, y la música queda a volumen bajo.

**Video final:** [`output/kentukis_emilia_video_final.mp4`](output/kentukis_emilia_video_final.mp4)
(MP4 H.264, 1920×1080, 24 fps, audio AAC estéreo).

## Documentos

| Archivo | Contenido |
|---|---|
| [`docs/01_analisis_novela.md`](docs/01_analisis_novela.md) | Lectura de las seis secciones de Emilia, personajes, cronología y decisiones de fidelidad. |
| [`docs/02_guion_tecnico.md`](docs/02_guion_tecnico.md) | Guion técnico de las 20 escenas: tiempos, composición, cámara, luz, sonido y función narrativa. |
| [`docs/03_guia_de_estilo.md`](docs/03_guia_de_estilo.md) | Diseño de personajes, kentuki, espacios, paleta y gramática visual Lima / Erfurt. |
| [`storyboard/`](storyboard/README.md) | Storyboard con tres fotogramas por escena. |
| [`docs/04_control_de_calidad.md`](docs/04_control_de_calidad.md) | Verificaciones técnicas y narrativas del video final. |

## Cómo se hizo

Todo es generado por código, sin imágenes ni sonidos externos:

- **Dibujo y animación:** Python + [Skia](https://skia.org/) (`skia-python`). Cada personaje es un *rig* 2D
  (cabeza con giro 3/4, expresiones, brazos con cinemática inversa, caminata) definido una sola vez, por eso
  conserva su aspecto en todas las escenas.
- **Música y efectos:** síntesis con NumPy/SciPy (piano de fieltro, caja de música, pads, cuerdas pulsadas,
  campanas, agua, ruedas, chillidos, timbre, etc.).
- **Video:** FFmpeg (libx264), renderizado en paralelo por segmentos de 5 s.
- **Tipografía de rótulos:** Lora (licencia SIL OFL, incluida en `assets/fonts/`).

## Estructura

```
engine/        motor: núcleo, dibujo, personajes (people.py), kentuki (rabbit.py), objetos (props.py),
               interfaz del controlador y montaje (ui.py), escenarios de Lima y Erfurt, efectos (fx.py)
scenes/        meta.py (guion técnico y línea de tiempo), common.py y una escena por archivo (s01…s20)
scripts/       render.py (video), audio.py (banda sonora), sheets.py (hojas de modelo), make_docs.py
assets/        hojas de modelo de personajes y kentuki, tipografías, textura de papel
docs/          análisis, guion técnico, guía de estilo y control de calidad
storyboard/    fotogramas por escena
output/        video final
```

## Regenerar el video

Requisitos: Python 3.11+, FFmpeg con libx264 y los paquetes `skia-python`, `numpy`, `scipy`, `pillow`
(en Linux, `skia-python` necesita `libegl1`).

```bash
pip install skia-python numpy scipy pillow
python3 scripts/audio.py                 # banda sonora -> build/audio.wav
python3 scripts/render.py video          # video -> output/kentukis_emilia_video_final.mp4
python3 scripts/make_docs.py             # guion técnico y storyboard
```

`render.py` guarda cada segmento con un hash del código que lo afecta: al modificar una escena, solo se
vuelven a renderizar los segmentos donde aparece. Para revisar sin renderizar todo:

```bash
python3 scripts/render.py still 125.0 cuadro.png       # un fotograma (segundo 125)
python3 scripts/render.py sheet s10 12 hoja.png        # hoja de contacto de la escena 10
```
