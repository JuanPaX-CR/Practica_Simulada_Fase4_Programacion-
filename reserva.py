# PARTE 3: RESERVAS
# DESARROLLADO POR: JUANPABLO


# IMPORTACIONES: se traen las clases y funciones de las otras partes del proyecto
from datetime import datetime

from cliente import Cliente
from entidad import Entidad
from excepciones import (ErrorSoftwareFJ, OperacionNoPermitidaError, ReservaError)
from logger import registrar_evento, registrar_advertencia, registrar_error
from servicios import Servicio


# CLASE RESERVA


class Reserva(Entidad):

    # ESTADOS POSIBLES DE LA RESERVA (constantes, así no se escriben a mano y no hay errores de ortografía)
    PENDIENTE = "PENDIENTE"
    CONFIRMADA = "CONFIRMADA"
    CANCELADA = "CANCELADA"

    def __init__(self, cliente, servicio, duracion):
        # VALIDACIONES: si el cliente, el servicio o la duración no son válidos, la reserva no se crea
        if not isinstance(cliente, Cliente):
            raise ReservaError("Cliente no válido")
        if not isinstance(servicio, Servicio):
            raise ReservaError("Servicio no válido")
        if not isinstance(duracion, (int, float)) or isinstance(duracion, bool) or duracion <= 0:
            raise ReservaError("La duración debe ser un número mayor a cero")

        # SE CREA LA ENTIDAD (Y SU ID) SOLO SI LAS VALIDACIONES PASARON
        super().__init__()
        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        # TODA RESERVA NACE PENDIENTE
        self.estado = Reserva.PENDIENTE
        self.fecha = datetime.now()

    # CONFIRMAR: solo se puede confirmar una reserva que esté pendiente
    def confirmar(self):
        if self.estado != Reserva.PENDIENTE:
            raise OperacionNoPermitidaError(
                f"Solo se confirma una reserva pendiente (estado actual: {self.estado})")
        self.estado = Reserva.CONFIRMADA

    # CANCELAR: no se puede cancelar una reserva que ya está cancelada
    def cancelar(self):
        if self.estado == Reserva.CANCELADA:
            raise OperacionNoPermitidaError("La reserva ya estaba cancelada")
        self.estado = Reserva.CANCELADA
        registrar_advertencia(f"Reserva {self.id} cancelada por {self.cliente.nombre}")

    # PROCESAR: calcula el costo y confirma la reserva, controlando los errores con try/except/else/finally
    def procesar(self, **opciones):
        try:
            # 1. SE VERIFICA QUE EL SERVICIO ESTÉ DISPONIBLE
            self.servicio.verificar_disponibilidad()
            # 2. SE CALCULA EL COSTO (primero el costo y después se confirma: si el cálculo falla, la reserva sigue pendiente)
            costo = self.servicio.calcular_costo(self.duracion, **opciones)
            # 3. SE CONFIRMA LA RESERVA
            self.confirmar()
        # EXCEPT: si hubo un error propio del sistema, se guarda en el log
        except ErrorSoftwareFJ as e:
            registrar_error(f"No se pudo procesar la reserva {self.id}", e)
            # ENCADENAMIENTO DE EXCEPCIONES: se lanza un error nuevo pero se conserva la causa original (from e)
            raise ReservaError(f"No se pudo procesar la reserva {self.id}: {e}") from e
        # EXCEPT: parámetros mal escritos al llamar a procesar()
        except TypeError as e:
            registrar_error(f"Parámetros incorrectos en la reserva {self.id}", e)
            raise ReservaError(f"Parámetros incorrectos al procesar la reserva {self.id}") from e
        # ELSE: solo se ejecuta si NO hubo ningún error
        else:
            registrar_evento(f"Reserva {self.id} confirmada para {self.cliente.nombre}. Costo: {costo}")
            return costo
        # FINALLY: se ejecuta siempre, haya o no haya error
        finally:
            registrar_evento(f"Fin del procesamiento de la reserva {self.id}")

    # DESCRIBIR: devuelve un resumen de la reserva en texto
    def describir(self):
        return (f"Reserva {self.id} | Cliente: {self.cliente.nombre} | "
                f"Servicio: {self.servicio.nombre} | Estado: {self.estado}")
