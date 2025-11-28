# Proyecto Airdraw
## Visión General

Airdraw implementa un sistema de visión por ordenador que combina calibración de cámara, autenticación visual mediante detección de patrones y seguimiento de mano en tiempo real, permitiendo realizar dibujo en el aire tras un proceso de desbloqueo basado en una secuencia y una detección de una forma geométrica.

El proyecto emplea OpenCV y filtros de Kalman para obtener un seguimiento estable del movimiento de la mano, generando trayectorias suaves sobre el vídeo en tiempo real.
Además, integra un modo de seguridad que utiliza detección de contornos y patrones geométricos para autenticar al usuario antes de habilitar el modo de dibujo.

---

## ESTRUCTURA

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

---

## CARACTERÍSTICAS GENERALES

### Calibración de cámara:
Se usa un patrón de tablero de ajedrez para corregir la distorsión y asegurar medidas confiables.

### Modo seguridad:
El sistema permanece bloqueado hasta que el usuario muestra una secuencia correcta frente a la cámara y después detecta una forma geométrica.

### Seguimiento de mano en tiempo real:
Una vez autenticado, se segmenta la piel en el espacio YCrCb y se localiza el punto más alto del contorno para rastrear la mano.

### Filtro de Kalman:
Suaviza las trayectorias detectadas para obtener un movimiento estable y continuo.

### Air Drawing:
Permite al usuario dibujar con el movimiento de su mano, generando un trazo sobre el vídeo en tiempo real.

### Salida en vídeo:
Muestra en pantalla el flujo de vídeo anotado con el dibujo y la trayectoria del movimiento.

---

## Dependencias
Es necesaria la instalación de las siguientes dependencias antes de ejecutar el proyecto:

pip install numpy opencv-python imageio mediapipe colorama

## Pasos para ejecución

### 1. Calibración de la cámara
Antes de usar el sistema, se debe calibrar la cámara.
Es necesario tener las imágenes del tablero de ajedrez en data/calibration_chess/.

Ejecuta:

python src/calibration.py

Esto generará o actualizará el archivo calibration_data.npz con los parámetros de cámara:

Matriz intrínseca
Coeficientes de distorsión
Parámetros extrínsecos

### 2. Ejecución del sistema principal
Para ejecutar todo el flujo del sistema, ejecuta:

python src/main.py

El script realizará los siguientes pasos:

Cargar datos de calibración.
Esperar al desbloqueo mediante detección de patrones (modo de seguridad).
Una vez autenticado, iniciar el air drawing con seguimiento de mano y Kalman filter.
Mostrar el resultado en tiempo real con la trayectoria dibujada.

### 3. Pruebas de cámara y componentes
   
Para probar la cámara o verificar las segmentaciones:

python src/test.py


## Key Functions

calibration.py
calibrar(): Realiza la calibración de la cámara usando un tablero de ajedrez y guarda los parámetros en un archivo .npz.

seguridad.py
detectar_patron(frame): Detecta figuras geométricas y verifica la secuencia de desbloqueo.
autenticacion_visual(): Controla la lógica de desbloqueo visual.

tracker.py
seguir_mano(frame): Detecta la mano mediante segmentación de piel y extracción de contornos.
punto_superior(contorno): Obtiene el punto más alto del contorno (punta de los dedos).

tracker_kalman.py
kalman_update(point): Aplica el filtro de Kalman para suavizar el movimiento detectado.

main.py
Controla el flujo completo del sistema:

## Calibración.
Modo de autenticación visual.
Tracking y dibujo en tiempo real.

## Ejemplo de salida
1️ Modo seguridad:
El sistema detecta la secuencia de patrones geométricos (por ejemplo, líneas y cuadrados).
Si la secuencia es correcta, aparece un mensaje de desbloqueo.

 Aquí puedes insertar las capturas de la detección del patrón.

2️ Modo dibujo:
El tracker detecta la mano y traza la trayectoria del movimiento con Kalman filter.
Se muestra la trayectoria sobre el vídeo en tiempo real, generando el air drawing.

 Aquí puedes insertar las capturas del vídeo con la trayectoria dibujada.

Configuración

Archivos de calibración:
data/calibration_data.npz

Imágenes de tablero:
data/calibration_chess/*.jpg

Se recomienda buena iluminación y fondo uniforme para mejorar la detección de piel.

Usage Notes
La calibración mejora sustancialmente la precisión del seguimiento.
El filtro de Kalman reduce el ruido por movimientos bruscos o iluminación variable.
El modo de seguridad puede ajustarse cambiando el patrón objetivo en seguridad.py.

Futuros Desarrollos

Implementar reconocimiento de gestos para control sin contacto.
Integrar modelos de IA para reconocer lo que el usuario dibuja.
Utilizar el desbloqueo por patrones como sistema de autenticación visual.
Añadir herramientas interactivas como cambio de color, borrado o zoom.
