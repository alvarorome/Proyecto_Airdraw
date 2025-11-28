import cv2
import numpy as np


def crear_kalman():
    """
    Crea e inicializa un filtro de Kalman configurado para rastrear objetos en 2D (posición y velocidad).

    Args:
        None

    Returns:
        cv2.KalmanFilter: Instancia del filtro de Kalman configurado con un estado de 4 variables (x, y, vx, vy)
                          y un vector de medida de 2 variables (x, y).

    Function Details:
        - Define el modelo de transición del sistema dinámico:
            [1 0 1 0]
            [0 1 0 1]
            [0 0 1 0]
            [0 0 0 1]
          donde:
            (x, y) representan la posición,
            (vx, vy) representan la velocidad.
        - Configura la matriz de observación (solo mide posición real (x, y)).
        - Ajusta las matrices de covarianza:
            - processNoiseCov: incertidumbre del modelo de movimiento.
            - measurementNoiseCov: ruido de la medición recibida.
            - errorCovPost: incertidumbre inicial del estado posterior.
        - Inicializa el estado posterior con ceros.
        - Devuelve el filtro listo para usar en predicciones y correcciones.
    """
    kf = cv2.KalmanFilter(4, 2)

    kf.transitionMatrix = np.array([[1, 0, 1, 0],
                                    [0, 1, 0, 1],
                                    [0, 0, 1, 0],
                                    [0, 0, 0, 1]], np.float32)

    kf.measurementMatrix = np.array([[1, 0, 0, 0],
                                     [0, 1, 0, 0]], np.float32)

    kf.processNoiseCov = np.eye(4, dtype=np.float32) * 1e-2
    kf.measurementNoiseCov = np.eye(2, dtype=np.float32) * 1e-1
    kf.errorCovPost = np.eye(4, dtype=np.float32)
    kf.statePost = np.zeros((4, 1), np.float32)

    return kf


def inicializar_estado(kf, x, y):
    """
    Inicializa el estado del filtro de Kalman con una posición inicial conocida.

    Args:
        kf (cv2.KalmanFilter): Filtro de Kalman previamente creado.
        x (float): Coordenada inicial en el eje X.
        y (float): Coordenada inicial en el eje Y.

    Returns:
        None

    Function Details:
        - Asigna manualmente un estado inicial de la forma:
            [x, y, vx, vy]
          donde vx y vy (velocidades) se inicializan en 0.
        - De esta forma, el filtro puede comenzar a hacer predicciones coherentes
          desde la primera medición disponible.
    """
    kf.statePost = np.array([[np.float32(x)],
                             [np.float32(y)],
                             [0.0],
                             [0.0]], np.float32)


def paso_kalman(kf, medida):
    """
    Realiza un ciclo completo de estimación en el filtro de Kalman: predicción y actualización (corrección).

    Args:
        kf (cv2.KalmanFilter): Instancia del filtro de Kalman utilizada para el seguimiento.
        medida (tuple or None): Coordenadas observadas del objeto (x, y).
                                Si es None, el filtro solo predice sin corregir.

    Returns:
        tuple: (x_pred, y_pred)
               - Coordenadas enteras de la posición predicha tras la estimación.

    Function Details:
        - Realiza la fase de **predicción**: estima la nueva posición (x_pred, y_pred) usando el modelo interno.
        - Si se proporciona una medida:
            - Construye un vector de observación (measurement).
            - Ejecuta la fase de **corrección**, actualizando el estado interno según la medición real.
        - Devuelve las coordenadas predichas para poder visualizarlas o utilizarlas como entrada
          en un sistema de dibujo, seguimiento o control.
    """
    # Predicción del estado futuro
    pred = kf.predict()
    x_pred, y_pred = int(pred[0][0]), int(pred[1][0])

    # Corrección si hay medición disponible
    if medida is not None:
        mx, my = medida
        measurement = np.array([[np.float32(mx)],
                                [np.float32(my)]])
        kf.correct(measurement)

    return x_pred, y_pred