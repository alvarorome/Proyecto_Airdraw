import cv2
import mediapipe as mp
import time
from colorama import Fore, Style, init

init(autoreset=True)

#VARIABLES
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

SECUENCIA = [3, 2, 1, 5]
mem = []
desbloqueado = False
cuadrado_detectado = False
contador_cuadrado = 0
FRAMES_CONFIRMACION = 8

ultimo_valor = None
tiempo_inicio_valor = 0
UMBRAL_ESTABILIDAD = 1.0

COLOR_FONDO = (40, 40, 40)
COLOR_TEXTO_PRINCIPAL = (0, 255, 0)
COLOR_TEXTO_SECUNDARIO = (255, 255, 0)
COLOR_VALIDADO = (0, 255, 100)
COLOR_ALERTA = (0, 0, 255)

hands = None

#FUNCIONES

def inicializar_detector():
    """
    Inicializa el modelo de detección de manos de Mediapipe.

    Args:
        None

    Returns:
        None

    Function Details:
        - Crea una instancia global del modelo mp.solutions.hands.Hands.
        - Establece umbrales de confianza para la detección y el seguimiento.
        - Permite posteriormente analizar frames con hands.process().
    """
    global hands
    hands = mp_hands.Hands(min_detection_confidence=0.7,
                           min_tracking_confidence=0.6)


def contar_dedos(hand_landmarks):
    """
    Cuenta la cantidad de dedos levantados en una mano detectada.

    Args:
        hand_landmarks (mediapipe.framework.formats.landmark_pb2.NormalizedLandmarkList):
            Lista de landmarks de la mano detectada por Mediapipe.

    Returns:
        int: Número de dedos levantados (0-5).

    Function Details:
        - Evalúa el dedo pulgar comparando posiciones horizontales (x).
        - Evalúa los otros dedos comparando posiciones verticales (y).
        - Considera un dedo “levantado” si la punta está por encima de la articulación proximal.
        - Retorna el número total de dedos levantados.
    """
    dedos = 0
    tips = [4, 8, 12, 16, 20]
    lm = hand_landmarks.landmark
    if lm[tips[0]].x < lm[tips[0] - 1].x:
        dedos += 1
    for i in range(1, 5):
        if lm[tips[i]].y < lm[tips[i] - 2].y:
            dedos += 1
    return dedos


def actualizar_secuencia(valor):
    """
    Gestiona y valida la secuencia de gestos de desbloqueo basada en el número de dedos levantados.

    Args:
        valor (int): Número de dedos levantados detectado actualmente.

    Returns:
        bool: 
            - True si la secuencia completa (3-2-1-5) fue correctamente realizada.
            - False en cualquier otro caso.

    Function Details:
        - Añade los valores de dedos detectados en orden a la lista mem.
        - Compara mem con la secuencia esperada SECUENCIA.
        - Si coincide, establece desbloqueado = True e imprime un mensaje de confirmación.
        - Si se detecta un valor incorrecto, reinicia la secuencia.
        - Muestra en consola el progreso actual de la secuencia.
    """
    global mem, desbloqueado

    if valor is None:
        return False

    if len(mem) == 0 or valor != mem[-1]:
        mem.append(valor)
        if mem == SECUENCIA:
            desbloqueado = True
            print(Fore.GREEN + Style.BRIGHT +
                  "\nSECUENCIA CORRECTA: Sistema DESBLOQUEADO\n")
            mem.clear()
            return True
        if mem[-1] != SECUENCIA[len(mem) - 1]:
            print(Fore.RED + "Secuencia incorrecta. Reiniciando.")
            mem = []
    progreso = " - ".join(str(n) for n in mem) if mem else "Esperando inicio..."
    print(Fore.CYAN + f"Progreso: {progreso}")
    return False


def dibujar_texto(frame, texto, posicion=(30, 80), color=(255, 255, 255),
                  font_scale=1, thickness=2, bg_color=COLOR_FONDO):
    """
    Escribe texto en pantalla con un recuadro de fondo opaco.

    Args:
        frame (numpy.ndarray): Imagen actual del video donde se dibujará el texto.
        texto (str): Contenido textual a colocar.
        posicion (tuple): Coordenadas (x, y) de la esquina inferior izquierda del texto.
        color (tuple): Color del texto en formato BGR.
        font_scale (float): Escala del texto.
        thickness (int): Grosor de las letras.
        bg_color (tuple): Color de fondo del rectángulo.

    Returns:
        None

    Function Details:
        - Calcula el tamaño del texto a renderizar.
        - Dibuja un rectángulo sólido detrás del texto para mejorar la visibilidad.
        - Superpone el texto sobre el frame usando `cv2.putText`.
    """
    x, y = posicion
    font = cv2.FONT_HERSHEY_SIMPLEX
    (w, h), _ = cv2.getTextSize(texto, font, font_scale, thickness)
    cv2.rectangle(frame, (x - 10, y - h - 10),
                  (x + w + 10, y + 10), bg_color, -1)
    cv2.putText(frame, texto, (x, y), font, font_scale, color, thickness)


def detectar_cuadrado(frame):
    """
    Busca y valida la presencia de un cuadrado en la imagen.

    Args:
        frame (numpy.ndarray): Frame actual de la cámara en formato BGR.

    Returns:
        bool: 
            - True si se detecta un cuadrado.
            - False en caso contrario.

    Function Details:
        - Convierte la imagen a escala de grises y aplica suavizado gaussiano.
        - Detecta bordes con el algoritmo Canny.
        - Obtiene contornos externos en la imagen binarizada.
        - Evalúa cada contorno:
            - Si tiene 4 vértices, es convexo y tiene una proporción (w/h) cercana a 1,
              lo considera cuadrado.
            - Debe además tener un área dentro de un rango específico.
        - Dibuja el cuadrado encontrado sobre el frame y devuelve True.
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 60, 160)
    contornos, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for c in contornos:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4 and cv2.isContourConvex(approx):
            x, y, w, h = cv2.boundingRect(approx)
            area = cv2.contourArea(approx)
            aspect_ratio = w / float(h)
            if 0.9 < aspect_ratio < 1.1 and 3000 < area < 80000:
                cv2.drawContours(frame, [approx], -1, (255, 255, 0), 3)
                return True
    return False


def procesar_frame(frame):
    """
    Procesa cada frame de la cámara para controlar el flujo de seguridad y desbloqueo.

    Args:
        frame (numpy.ndarray): Frame actual leído desde la cámara.

    Returns:
        numpy.ndarray: Frame procesado con anotaciones y estados visuales del proceso.

    Function Details:
        - Invierte la imagen horizontalmente para simular un espejo.
        - Convierte el frame a RGB y se lo pasa a Mediapipe para la detección de manos.
        - Si aún no está desbloqueado:
            - Detecta la cantidad de dedos levantados y actualiza la secuencia de desbloqueo.
            - Dibuja los landmarks de las manos y muestra el progreso del gesto.
        - Si la secuencia se completó:
            - Pide al usuario mostrar un cuadrado frente a la cámara.
            - Verifica su presencia durante varios frames consecutivos.
            - Cuando se cumple la condición, marca `cuadrado_detectado = True`.
        - Devuelve el frame anotado, listo para mostrar en pantalla por el bucle principal.
    """
    global ultimo_valor, tiempo_inicio_valor, desbloqueado
    global cuadrado_detectado, contador_cuadrado

    frame = cv2.flip(frame, 1)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    resultados = hands.process(frame_rgb)
    dedos_levantados = None

    # Secuencia de dedos
    if not desbloqueado:
        if resultados.multi_hand_landmarks:
            for hand_landmarks in resultados.multi_hand_landmarks:
                dedos_levantados = contar_dedos(hand_landmarks)
                mp_drawing.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        now = time.time()
        if dedos_levantados is not None:
            if dedos_levantados != ultimo_valor:
                ultimo_valor = dedos_levantados
                tiempo_inicio_valor = now
            elif now - tiempo_inicio_valor > UMBRAL_ESTABILIDAD:
                actualizar_secuencia(dedos_levantados)
                tiempo_inicio_valor = now + 1.5

        dibujar_texto(frame,
                      f"Dedos detectados: {dedos_levantados if dedos_levantados is not None else '-'}",
                      (30, 80), COLOR_TEXTO_PRINCIPAL, font_scale=1.1)
        secuencia_txt = "Secuencia: " + " - ".join(map(str, mem)) if mem else "Esperando inicio..."
        dibujar_texto(frame, secuencia_txt, (30, 140), COLOR_TEXTO_SECUNDARIO)

    # Validación cuadrado
    elif desbloqueado and not cuadrado_detectado:
        dibujar_texto(frame, "Sistema desbloqueado",
                      (30, 70), COLOR_TEXTO_PRINCIPAL)
        dibujar_texto(frame, "Muestra un cuadrado",
                      (30, 120), COLOR_TEXTO_SECUNDARIO)
        encontrado = detectar_cuadrado(frame)
        contador_cuadrado = contador_cuadrado + 1 if encontrado else 0

        if contador_cuadrado >= FRAMES_CONFIRMACION:
            cuadrado_detectado = True
            print(Fore.GREEN + Style.BRIGHT +
                  "\nVALIDACIÓN COMPLETADA: Cuadrado detectado.\n")

        if encontrado:
            dibujar_texto(frame, f"Cuadrado detectado ({contador_cuadrado}/{FRAMES_CONFIRMACION})",
                          (30, 180), COLOR_TEXTO_PRINCIPAL)
        else:
            dibujar_texto(frame, "Buscando figura cuadrada...",
                          (30, 180), COLOR_ALERTA)

    return frame