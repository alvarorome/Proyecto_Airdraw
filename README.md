# Proyecto_Airdraw

VISIÓN GENERAL
Airdraw implementa un sistema de visión por ordenador que combina calibración de cámara, autenticación visual mediante detección de patrones y seguimiento de mano en tiempo real, permitiendo realizar dibujo en el aire tras un proceso de desbloqueo basado en una secuencia y una detección de una forma geométrica.

El proyecto emplea OpenCV y filtros de Kalman para obtener un seguimiento estable del movimiento de la mano, generando trayectorias suaves sobre el vídeo en tiempo real.
Además, integra un modo de seguridad que utiliza detección de contornos y patrones geométricos para autenticar al usuario antes de habilitar el modo de dibujo.

ESTRUCTURA

PROYECTO_FINAL/
├── data/
│   ├── calibration_chess/           # Imágenes del tablero de ajedrez para la calibración
│   ├── calibration_data.npz         # Datos de calibración guardados (intrínsecos, distorsión, etc.)
│
├── src/
│   ├── calibration.py               # Calibración de cámara con tablero de ajedrez
│   ├── main.py                      # Script principal que ejecuta el flujo completo del sistema
│   ├── seguridad.py                 # Detección de patrones y desbloqueo del sistema
│   ├── tracker_kalman.py            # Implementación del filtro de Kalman para suavizar el seguimiento
│   ├── tracker.py                   # Lógica de seguimiento de la mano mediante segmentación y contornos
│   ├── test.py                      # Scripts de prueba para cámara y funciones auxiliares
│
├── diagrama_bloques.drawio          # Diagrama de bloques del sistema
├── diagrama.txt                     # Descripción textual de la arquitectura del diagrama de bloques

CARACTERÍSTICAS GENERALES

Calibración de cámara:
Se usa un patrón de tablero de ajedrez para corregir la distorsión y asegurar medidas confiables.

Modo seguridad:
El sistema permanece bloqueado hasta que el usuario muestra una secuencia correcta frente a la cámara y después detecta una forma geométrica.

Seguimiento de mano en tiempo real:
Una vez autenticado, se segmenta la piel en el espacio YCrCb y se localiza el punto más alto del contorno para rastrear la mano.

Filtro de Kalman:
Suaviza las trayectorias detectadas para obtener un movimiento estable y continuo.

Air Drawing:
Permite al usuario dibujar con el movimiento de su mano, generando un trazo sobre el vídeo en tiempo real.

Salida en vídeo:
Muestra en pantalla el flujo de vídeo anotado con el dibujo y la trayectoria del movimiento.

Dependencies
Es necesaria la instalación de las siguientes dependencias antes de ejecutar el proyecto:

bash
pip install numpy opencv-python imageio mediapipe colorama
