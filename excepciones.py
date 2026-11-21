"""
PARTE 1: Excepciones
Autor: Jose Yimy Palacio Lucumi (digitextosyisercarepa-pixel)

Excepciones personalizadas que usa todo el sistema.
Todas heredan de ErrorSoftwareFJ, así se pueden capturar juntas con un solo except.
"""


class ErrorSoftwareFJ(Exception):
    """Error base de todo el sistema."""
    pass


class ClienteError(ErrorSoftwareFJ):
    """Se lanza cuando los datos de un cliente son inválidos."""
    pass


class ServicioError(ErrorSoftwareFJ):
    """Se lanza cuando un servicio tiene datos inválidos (tarifa, horas)."""
    pass


class ServicioNoDisponibleError(ServicioError):
    """Se lanza cuando se intenta reservar un servicio no disponible."""
    pass


class ReservaError(ErrorSoftwareFJ):
    """Se lanza cuando una reserva no es válida o no se puede confirmar."""
    pass


class OperacionNoPermitidaError(ErrorSoftwareFJ):
    """Se lanza cuando una operación no está permitida en el estado actual."""
    pass
