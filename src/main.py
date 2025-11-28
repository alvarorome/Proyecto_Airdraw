import cv2
import seguridad  # módulo de autenticación por gestos
from tracker import detectar_centro_mano, actualizar_trayectoria
from tracker_kalman import crear_kalman, inicializar_estado, paso_kalman
import calibration


def main():
    """
    Ejecuta el pipeline principal de AirDraw Secure: calibración, autenticación por gestos y tracking de mano.

    Args:
        None

    Returns:
        None

    Function Details:
        - Realiza la calibración de la cámara, obteniendo sus parámetros intrínsecos y de distorsión.
        - Inicia la captura de video desde la cámara web mediante OpenCV.
        - Inicializa el filtro de Kalman que se utilizará para estimar trayectorias suaves de la mano.
        - Llama al módulo seguridad para ejecutar el sistema de autenticación en dos fases:
            1. Secuencia de gestos con los dedos (3 → 2 → 1 → 5)
            2. Validación visual mostrando un cuadrado frente a la cámara
        - Una vez completada la autenticación, cambia al modo Tracker (AirDraw):
            - Detecta la posición de la mano con `detectar_centro_mano`.
            - Inicializa y actualiza el filtro de Kalman para suavizar la trayectoria.
            - Dibuja las predicciones y la trayectoria de la mano en tiempo real sobre el video.
        - Muestra los resultados en una ventana única (AirDraw Secure) que combina ambos modos.
        - Permite salir del programa presionando la tecla q.
        - Al finalizar, libera los recursos de cámara y cierra todas las ventanas de OpenCV.
    """

    # Calibración de cámara
    print("Calibrando cámara...")
    (
        rms_calibration,
        intrinsics_calibration,
        extrinsics_calibration,
        dist_coeffs_calibration,
    ) = calibration.calibrar()

    print(f"RMS calibración: {rms_calibration:.4f}")
    print("Matriz intrínseca:\n", intrinsics_calibration)
    print("Coeficientes de distorsión:\n", dist_coeffs_calibration.ravel())

    # Inicialización cámara
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: no se pudo abrir la cámara.")
        return

    # Filtro de Kalman
    kf = crear_kalman()
    kalman_inicializado = False

    # Detector de seguridad
    seguridad.inicializar_detector()

    modo_tracker = False

    # Bucle principal de captura de video
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # modo seguridad
        if not modo_tracker:
            frame = seguridad.procesar_frame(frame)
            cv2.putText(frame, "Modo Seguridad", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)

            if seguridad.desbloqueado and seguridad.cuadrado_detectado:
                print(">> Seguridad completada. Activando tracker...")
                modo_tracker = True

        # modo airdraw
        else:
            medida, mask = detectar_centro_mano(frame)

            if medida is not None and not kalman_inicializado:
                inicializar_estado(kf, medida[0], medida[1])
                kalman_inicializado = True

            if kalman_inicializado:
                x_pred, y_pred = paso_kalman(kf, medida)

                if medida is not None:
                    cv2.circle(frame, medida, 6, (0, 255, 0), -1)
                cv2.circle(frame, (x_pred, y_pred), 6, (0, 0, 255), -1)

                frame = actualizar_trayectoria(frame, (x_pred, y_pred))
            else:
                frame = actualizar_trayectoria(frame, None)

            cv2.putText(frame, "Tracker Mano (AirDraw)", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)

        # mostrar la salida
        cv2.imshow("AirDraw Secure", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    # limpieza final de recursos
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()