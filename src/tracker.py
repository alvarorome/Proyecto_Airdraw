import cv2
import numpy as np
from collections import deque

pts = deque(maxlen=200)


def segmentar_piel(frame):
    """
    Segmenta las regiones de piel presentes en la imagen utilizando el espacio
    de color YCrCb.

    Args:
        frame (np.ndarray): Imagen en formato BGR obtenida de la cámara.

    Returns:
        np.ndarray: Máscara binaria donde se resaltan las regiones clasificadas
        como piel.

    Descripción:
        - Convierte la imagen de BGR a YCrCb.
        - Aplica un umbral para aislar tonos de piel.
        - Aplica suavizado Gaussiano y mediana para reducir ruido.
        - Realiza erosión y dilatación para limpiar la máscara.
    """
    ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
    lower = np.array([0, 135, 85], np.uint8)
    upper = np.array([255, 180, 135], np.uint8)

    mask = cv2.inRange(ycrcb, lower, upper)
    mask = cv2.GaussianBlur(mask, (7, 7), 0)
    mask = cv2.medianBlur(mask, 7)

    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.erode(mask, kernel, iterations=1)
    mask = cv2.dilate(mask, kernel, iterations=2)

    return mask


def detectar_centro_mano(frame):
    """
    Localiza el punto más alto de la mano detectada en la imagen.

    Args:
        frame (np.ndarray): Imagen en formato BGR.

    Returns:
        tuple:
            - (x_top, y_top): Coordenadas del punto más alto de la mano.
            - mask (np.ndarray): Máscara de piel utilizada.
        En caso de no detectar mano: (None, mask)

    Descripción:
        - Obtiene la máscara de piel mediante segmentación.
        - Encuentra contornos y selecciona el más grande como la mano.
        - Ignora contornos pequeños que se interpretan como ruido.
        - Busca el punto cuya coordenada 'y' sea mínima dentro del contorno,
          interpretándolo como la punta superior de la mano.
        - Dibuja el contorno en verde y el punto detectado en azul sobre el frame.
    """
    mask = segmentar_piel(frame)

    contours, _ = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    if not contours:
        return None, mask

    c = max(contours, key=cv2.contourArea)
    if cv2.contourArea(c) < 1000:
        return None, mask

    topmost = tuple(c[c[:, :, 1].argmin()][0])
    x_top, y_top = int(topmost[0]), int(topmost[1])

    cv2.drawContours(frame, [c], -1, (0, 255, 0), 2)
    cv2.circle(frame, (x_top, y_top), 6, (255, 0, 0), -1)

    return (x_top, y_top), mask


def actualizar_trayectoria(frame, punto):
    """
    Actualiza y dibuja la trayectoria seguida por la mano en los últimos frames.

    Args:
        frame (np.ndarray): Imagen actual de la cámara.
        punto (tuple or None): Punto predicho o medido (x, y). Si es None,
                               se considera que la mano no está visible.

    Returns:
        np.ndarray: El frame con la trayectoria dibujada.

    Descripción:
        - Añade el punto actual al historial (deque) de posiciones.
        - Conecta los puntos consecutivos mediante líneas rojas para trazar
          el "air drawing".
        - Si el punto es None, añade un hueco para evitar líneas discontinuas.
    """
    if punto is None:
        pts.appendleft(None)
    else:
        pts.appendleft(punto)

    for i in range(1, len(pts)):
        if pts[i] is None or pts[i - 1] is None:
            continue
        cv2.line(frame, pts[i], pts[i - 1], (0, 0, 255), 3)

    return frame
