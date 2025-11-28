# Proyecto_Airdraw

VISIÓN GENERAL
Airdraw implementa un sistema de visión por ordenador que combina calibración de cámara, autenticación visual mediante detección de patrones y seguimiento de mano en tiempo real, permitiendo realizar dibujo en el aire tras un proceso de desbloqueo basado en una secuencia y una detección de una forma geométrica.

El proyecto emplea OpenCV y filtros de Kalman para obtener un seguimiento estable del movimiento de la mano, generando trayectorias suaves sobre el vídeo en tiempo real.
Además, integra un modo de seguridad que utiliza detección de contornos y patrones geométricos para autenticar al usuario antes de habilitar el modo de dibujo.
