# Control de calidad

Verificaciones hechas sobre `output/kentukis_emilia_video_final.mp4` (versión final). Las técnicas se
reproducen con `python3 scripts/qa.py --sheets`.

## C. Calidad técnica (medida)

| Control | Resultado |
|---|---|
| Archivo | MP4, 88,2 MB, se abre y se decodifica completo **sin errores** (`ffmpeg -f null`) |
| Duración | **4:08.08** (248,08 s), dentro del margen de 3:45–4:15 |
| Video | H.264 High, **1920×1080**, 16:9, `yuv420p`, BT.709 |
| Fotogramas | **24 fps constantes**: 5.954 fotogramas con intervalos regulares (ninguno irregular) |
| Audio | AAC estéreo 48 kHz, 196 kb/s; dura 248,06 s (desfase de 19 ms con el video, imperceptible) |
| Sonoridad | **−23,8 LUFS** integrados, rango 9,9 LU, pico verdadero −4,6 dBFS (sin saturación) |
| Tramos negros | Uno solo, intencional: 2:52.9–2:53.9 (pantalla negra antes del timbre de Gloria) |
| Congelamientos | **Ninguno** de 1,5 s o más (en la primera versión había tres planos fijos; se les agregó movimiento) |
| Contenido | Sin voces, diálogos hablados ni subtítulos. Todo el audio es instrumental y ambiental, sintetizado |

## D. Revisión del contenido visual

- Se revisaron **hojas de contacto con un fotograma cada 2 segundos** de todo el video (125 fotogramas) en
  dos rondas, más fotogramas a resolución completa para controlar nitidez y artefactos de compresión.
- La versión final se armó después de **tres rondas de correcciones**:
  1. Pose sentada de Emilia, escala del café, caja del kentuki que tapaba a Eva, primeros planos fuera de
     cuadro, pies descalzos poco legibles, Emilia acostada en la cama.
  2. Encuadres que cortaban la cabeza de Eva, Klaus mal sentado en el sofá, franjas negras en la pantalla
     dividida, planos fijos sin movimiento, apagado de la luz verde superpuesto con el fundido final, peso del
     archivo (199 MB → 88 MB, reduciendo el grano fino del papel).
  3. Fidelidad: se quitaron las fotos de Klaus de la heladera de Emilia (en el libro están en la mesita de luz).
- **Limitación:** la revisión visual se hizo con fotogramas muestreados (cada 2 s y en puntos clave), no
  mirando la reproducción completa en tiempo real. El audio se verificó con mediciones (niveles por escena,
  sonoridad, picos, silencios y sincronía construida desde la misma línea de tiempo), pero **no fue escuchado**.
  Conviene mirarlo y escucharlo una vez completo antes de la exposición.

## B. Calidad visual

| Pregunta | Resultado |
|---|---|
| ¿Los personajes conservan su apariencia? | Sí: cada uno se dibuja siempre con el mismo rig y la misma paleta (hojas en `assets/characters/`). |
| ¿Estética uniforme? | Sí: mismo trazo, sombreado y textura de papel en todas las escenas. |
| ¿Se percibe animación? | Sí: parpadeos, respiración, gestos, caminatas, ruedas y orejas del kentuki, cámara con paneos, acercamientos y paralaje. |
| ¿Transiciones fluidas? | Fundidos, barridos de página, fundidos a negro, zoom continuo hacia el monitor y un corte por coincidencia de gesto. |
| ¿Rótulos legibles? | «Lima, Perú», «Erfurt, Alemania», «Hong Kong» en tipografía Lora, con sombra suave. |
| ¿Amabilidad visual e inquietud? | La paleta se enfría y desatura desde la llegada de Klaus. Sus ojos pálidos, la cámara tirada, la sombra en la huida y la luz verde que se apaga sostienen la inquietud sin recurrir al terror. |

## A. Fidelidad narrativa

| Pregunta | Resultado |
|---|---|
| ¿Se entiende quién es Emilia? | Jubilada sola en Lima, con regalos de un hijo en Hong Kong y una computadora vieja. |
| ¿Se distingue Lima de Erfurt? | Paleta cálida o fría, rótulos y el controlador del kentuki enmarcando todo lo que se ve desde la conejita. |
| ¿Se entiende la conexión? | La tarjeta, el ojo «despertar», el zoom dentro del monitor, la pantalla dividida y la caja de la conejita. |
| ¿Orden correcto de los hechos? | Sigue la cronología de las seis secciones del libro (ver `docs/01_analisis_novela.md`). |
| ¿Relaciones fieles? | Hijo lejano, Eva como ama cariñosa y luego cruel, Klaus como intruso, Gloria entusiasta e Inés desconfiada. |
| ¿Conflictos relevantes? | Intruso, robo, agua, mensaje a Klaus, espejo, bañera, el kentuki del hijo y la llamada de Eva. |
| ¿Desenlace fiel? | Desconexión con el botón rojo; Emilia ahoga a su conejita bajo la canilla hasta que la luz verde deja de titilar. No se agrega moraleja y no se revela quién maneja la conejita de Lima. |
| ¿Invenciones? | No se agregan hechos. Hay simplificaciones visuales (la desnudez sugerida, el insulto del espejo como garabato, el kentuki del hijo sin especie). Se omitieron detalles secundarios por duración, como la cámara que Gloria le presta a Emilia y la escena de yoga frente al espejo. |
