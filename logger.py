"""
PARTE 1: Sistema de logs
Autor: Jose Yimy Palacio Lucumi (digitextosyisercarepa-pixel)

Registra eventos, advertencias y errores en logs/eventos.log
(la interfaz lee ese mismo archivo en la pestaña Registro).
La configuración se hace sola al importar este módulo.
"""

import logging
import os

RUTA_LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs", "eventos.log")

_logger = logging.getLogger("software_fj")


def configurar_logs():
    # SE EJECUTA UNA SOLA VEZ: si ya tiene handler no se agrega otro (evita líneas repetidas)
    if _logger.handlers:
        return
    os.makedirs(os.path.dirname(RUTA_LOG), exist_ok=True)
    manejador = logging.FileHandler(RUTA_LOG, encoding="utf-8")
    manejador.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    _logger.addHandler(manejador)
    _logger.setLevel(logging.INFO)
    _logger.propagate = False


configurar_logs()


def registrar_evento(mensaje):
    _logger.info(mensaje)


def registrar_advertencia(mensaje):
    _logger.warning(mensaje)


def registrar_error(mensaje, error=None):
    if error is not None:
        mensaje = f"{mensaje} | {type(error).__name__}: {error}"
    _logger.error(mensaje)
