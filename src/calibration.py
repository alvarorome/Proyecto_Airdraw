from typing import List
import numpy as np
import cv2
import glob
import os
import imageio


CHESSBOARD_COLS = 7
CHESSBOARD_ROWS = 7

SQUARE_SIZE_X = 30.0
SQUARE_SIZE_Y = 30.0


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CALIB_IMAGES_GLOB = os.path.join(BASE_DIR, "..", "data", "calibration_chess", "*.jpg")
OUTPUT_DIR = os.path.join(BASE_DIR, "..", "data", "calibration_detected")


def load_images(filenames: List[str]) -> List[np.ndarray]:
    """
    Carga una lista de imágenes desde disco utilizando OpenCV.

    Args:
        filenames (List[str]): Lista con rutas a imágenes.

    Returns:
        List[np.ndarray]: Lista de imágenes en formato BGR.

    Descripción:
        - Itera por la lista de rutas.
        - Intenta cargar cada imagen con cv2.imread.
        - Devuelve una lista con todas las imágenes cargadas, pudiendo contener None si alguna falla.
    """
    return [cv2.imread(fname) for fname in filenames]


def write_image(filename: str, img: np.ndarray) -> None:
    """
    Guarda una imagen en disco asegurando una extensión válida.

    Args:
        filename (str): Ruta de salida donde se guardará la imagen.
        img (np.ndarray): Imagen en formato BGR.

    Descripción:
        - Comprueba si el nombre tiene una extensión válida.
        - Si no la tiene, añade '.jpg' por defecto.
        - Guarda la imagen en disco con calidad JPEG 90.
    """
    if not filename.lower().endswith((".jpg", ".jpeg", ".png")):
        filename += ".jpg"
    cv2.imwrite(filename, img, [cv2.IMWRITE_JPEG_QUALITY, 90])


def get_chessboard_points(chessboard_shape, dx: float, dy: float) -> np.ndarray:
    """
    Genera los puntos 3D del tablero en coordenadas reales.

    Args:
        chessboard_shape (tuple): Número de esquinas interiores (cols, rows).
        dx (float): Distancia real entre esquinas en el eje X.
        dy (float): Distancia real entre esquinas en el eje Y.

    Returns:
        np.ndarray: Matriz Nx3 con los puntos 3D del tablero.

    Descripción:
        - Construye una rejilla de puntos sobre el plano Z = 0.
        - Los puntos se usan como referencia 3D durante la calibración.
    """
    cols, rows = chessboard_shape
    chessboard = []
    for y in range(rows):
        for x in range(cols):
            chessboard.append([x * dx, y * dy, 0])
    return np.array(chessboard, dtype=np.float32)


def calibrar():
    """
    Realiza la calibración de la cámara usando imágenes de un tablero de ajedrez.

    Returns:
        tuple:
            rms_calibration (float): Error RMS de reproyección.
            intrinsics_calibration (np.ndarray): Matriz intrínseca K.
            extrinsics_calibration (List[np.ndarray]): Matrices [R|t] por imagen válida.
            dist_coeffs_calibration (np.ndarray): Coeficientes de distorsión.

    Descripción:
        - Busca las imágenes del tablero en la carpeta correspondiente.
        - Carga las imágenes utilizando imageio para evitar problemas de codificación.
        - Convierte cada imagen a escala de grises.
        - Detecta las esquinas interiores del tablero con findChessboardCorners.
        - Refina las esquinas detectadas a subpíxel.
        - Genera los puntos 3D correspondientes al tablero físico.
        - Llama a cv2.calibrateCamera para obtener los parámetros intrínsecos y extrínsecos.
        - Guarda imágenes con las esquinas detectadas para depuración.
        - Almacena los parámetros calibrados en un archivo NPZ.
    """

    img_paths = sorted(glob.glob(CALIB_IMAGES_GLOB))

    if not img_paths:
        return None, None, None, None

    imgs = []
    valid_paths = []

    for p in img_paths:
        try:
            img_rgb = imageio.imread(p)
            img = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
        except Exception:
            continue

        if img is None or img.size == 0:
            continue

        imgs.append(img)
        valid_paths.append(p)

    if not imgs:
        return None, None, None, None

    corners_all = []
    imgs_gray = []

    for img in imgs:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        imgs_gray.append(gray)

        ret, corners = cv2.findChessboardCorners(
            gray,
            patternSize=(CHESSBOARD_COLS, CHESSBOARD_ROWS),
            flags=cv2.CALIB_CB_ADAPTIVE_THRESH +
                  cv2.CALIB_CB_NORMALIZE_IMAGE +
                  cv2.CALIB_CB_FAST_CHECK
        )

        corners_all.append((ret, corners))

    criteria = (
        cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
        30,
        0.01
    )

    corners_refined = []
    for gray, (found, corners) in zip(imgs_gray, corners_all):
        if found:
            corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            corners_refined.append((True, corners2))
        else:
            corners_refined.append((False, None))

    draw_corners_imgs = []
    for img, (found, corners) in zip(imgs, corners_refined):
        if found and corners is not None:
            img_drawn = cv2.drawChessboardCorners(
                img.copy(),
                patternSize=(CHESSBOARD_COLS, CHESSBOARD_ROWS),
                corners=corners,
                patternWasFound=True
            )
        else:
            img_drawn = img
        draw_corners_imgs.append(img_drawn)

    for i, img_drawn in enumerate(draw_corners_imgs):
        out_path = os.path.join(OUTPUT_DIR, f"Image_{i}_corners.jpg")
        write_image(out_path, img_drawn)

    objp = get_chessboard_points(
        (CHESSBOARD_COLS, CHESSBOARD_ROWS),
        SQUARE_SIZE_X,
        SQUARE_SIZE_Y
    )

    objpoints = []
    imgpoints = []

    for found, corners in corners_refined:
        if found:
            objpoints.append(objp)
            imgpoints.append(corners)

    if len(objpoints) < 3:
        return None, None, None, None

    image_size = imgs_gray[0].shape[::-1]

    (
        rms_calibration,
        intrinsics_calibration,
        dist_coeffs_calibration,
        rvecs_calibration,
        tvecs_calibration,
    ) = cv2.calibrateCamera(
        objpoints,
        imgpoints,
        image_size,
        None,
        None,
    )

    extrinsics_calibration = [
        np.hstack((cv2.Rodrigues(rvec)[0], tvec))
        for rvec, tvec in zip(rvecs_calibration, tvecs_calibration)
    ]

    np.savez(
        os.path.join(BASE_DIR, "..", "calibration_data.npz"),
        K=intrinsics_calibration,
        dist=dist_coeffs_calibration,
        rms=rms_calibration,
        rvecs=rvecs_calibration,
        tvecs=tvecs_calibration,
    )

    return (
        rms_calibration,
        intrinsics_calibration,
        extrinsics_calibration,
        dist_coeffs_calibration,
    )

if __name__ == "__main__":
    calibrar()