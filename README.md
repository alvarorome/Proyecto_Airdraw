Airdraw – Sistema de Dibujo en el Aire con Visión por Computador

Airdraw implementa un sistema completo de visión por computador que combina:

Calibración de cámara

Autenticación visual mediante patrones geométricos

Seguimiento de mano en tiempo real

Filtrado de trayectoria con Kalman

Air drawing: dibujar en el aire usando solo la mano

Diseñado con OpenCV y filtros de Kalman, el proyecto permite un flujo fluido desde la calibración hasta el dibujo en tiempo real, agregando un modo de seguridad previo basado en detección de secuencias y formas geométricas.

Tabla de Contenidos

Descripción General

Estructura del Proyecto

Características

Dependencias

Pasos para la Ejecución

Calibración

Ejecución del Sistema Principal

Pruebas

Funciones Clave

Ejemplo de Salida

Configuración

Notas Prácticas

Futuros Desarrollos

Descripción General

Airdraw permite al usuario dibujar en el aire tras superar una autenticación visual basada en la detección de una secuencia de patrones geométricos.
Después del desbloqueo, el sistema rastrea la mano en tiempo real mediante segmentación de piel y filtrado con Kalman para obtener un movimiento estable.
El resultado se muestra superpuesto en directo sobre el vídeo.

Estructura del Proyecto
PROYECTO_FINAL/
│
├── data/
│   ├── calibration_chess/            # Imágenes del tablero para calibración
│   │   ├── WIN_20251127_11_34_35_Pro.jpg
│   │   ├── WIN_20251127_11_34_40_Pro.jpg
│   │   ├── WIN_20251127_11_34_44_Pro.jpg
│   │   └── ...                       # Más imágenes del patrón
│   │
│   └── calibration_detected/
│       ├── esquinas_detectadas.png   # Tablero con esquinas detectadas
│       └── calibration_data.npz      # Matriz K, distorsión, extrínsecos
│
├── demo/                             # Material demostrativo
│   ├── airdraw.png
│   ├── DEMO.mkv
│   ├── secuencia.png
│   └── secuencia_forma_geométrica.png
│
├── src/
│   ├── calibration.py                # Calibración de la cámara
│   ├── main.py                       # Ejecución del flujo completo del sistema
│   ├── seguridad.py                  # Lógica de desbloqueo y patrones
│   ├── tracker_kalman.py             # Implementación del filtro de Kalman
│   ├── tracker.py                    # Seguimiento de mano
│   └── test.py                       # Tests de cámara, segmentación y tracking
│
├── diagrama_bloques.drawio           # Diagrama de arquitectura
├── diagrama.txt                      # Descripción textual del diagrama
└── Lab_Project.pdf                   # Informe técnico del proyecto

Características
Calibración de cámara

Utiliza un tablero de ajedrez para obtener parámetros intrínsecos y extrínsecos, corrigiendo la distorsión y mejorando la precisión del tracking.

Modo de seguridad

El sistema permanece bloqueado hasta detectar correctamente una secuencia de figuras geométricas y una forma específica.

Seguimiento de mano

Segmentación en espacio YCrCb y detección del punto superior del contorno.

Filtro de Kalman

Suaviza el movimiento detectado y reduce saltos o ruido.

Air Drawing

Dibujo en el aire con trayectoria en tiempo real sobre el vídeo.

Dependencias

Instalar mediante pip:

pip install numpy opencv-python imageio mediapipe colorama

Pasos para la Ejecución
1. Calibración

Coloca las imágenes del tablero en data/calibration_chess/ y ejecuta:

python src/calibration.py


Esto generará:

calibration_data.npz

esquinas_detectadas.png

2. Ejecución del Sistema Principal
python src/main.py


El flujo incluye:

Carga de parámetros de calibración

Activación del modo seguridad y detección del patrón

Seguimiento de mano

Kalman filter

Visualización del air drawing sobre el vídeo

3. Pruebas

Para probar la cámara o componentes por separado:

python src/test.py

Funciones Clave
calibration.py

calibrar(): Ejecuta la calibración y guarda calibration_data.npz.

seguridad.py

detectar_patron(frame): Detecta figuras geométricas.

autenticacion_visual(): Control principal del desbloqueo.

tracker.py

seguir_mano(frame): Detecta la mano y genera contornos.

punto_superior(contorno): Extrae el punto más alto del contorno.

tracker_kalman.py

kalman_update(point): Actualiza y suaviza la trayectoria.

main.py

Controla la ejecución completa del sistema.

Ejemplo de Salida

Modo seguridad: el sistema detecta una secuencia de figuras geométricas y desbloquea el modo dibujo.
Modo dibujo: se detecta la mano, se aplica el filtro de Kalman y se dibuja sobre el vídeo en tiempo real.

Puedes incluir capturas o vídeos almacenados en la carpeta demo/.

Configuración

Archivo de calibración:
data/calibration_detected/calibration_data.npz

Imágenes del tablero:
data/calibration_chess/*.jpg

Requisitos recomendados:

buena iluminación

fondo uniforme

mínima variación de luz

Notas Prácticas

La calibración mejora significativamente el seguimiento.

El filtro de Kalman reduce el ruido y los movimientos bruscos.

El patrón de desbloqueo puede modificarse en seguridad.py.

Futuros Desarrollos

Reconocimiento avanzado de gestos.

Clasificación automática del dibujo realizado.

Mejora del sistema de autenticación visual.

Herramientas interactivas como borrador, colores, zoom.
