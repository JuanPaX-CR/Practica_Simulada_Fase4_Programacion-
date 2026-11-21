"""
PARTE 2: Servicios
Autor: Jhonatan David Cardenas Sanchez (John367219)

Clase abstracta Servicio y sus tres implementaciones:
- ReservaSala:           tarifa x horas
- AlquilerEquipo:        tarifa x horas + seguro fijo de 20
- AsesoriaEspecializada: tarifa x horas + IVA 19 % por defecto

Todas calculan el costo con la misma firma (sobrecarga):
    calcular_costo(horas)
    calcular_costo(horas, impuesto)
    calcular_costo(horas, impuesto, descuento)
"""

from abc import abstractmethod

from entidad import Entidad
from excepciones import ServicioError, ServicioNoDisponibleError


# FUNCIÓN AUXILIAR: valida que un valor sea un número real (no bool)


def _es_numero(valor):
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


# CLASE ABSTRACTA SERVICIO


class Servicio(Entidad):

    def __init__(self, nombre, tarifa_base, disponible=True):
        # VALIDACIONES: si algo es inválido, el servicio no se crea
        if not isinstance(nombre, str) or not nombre.strip():
            raise ServicioError("El nombre del servicio no puede estar vacío")
        if not _es_numero(tarifa_base) or tarifa_base <= 0:
            raise ServicioError("La tarifa debe ser un número mayor a cero")

        # SE CREA LA ENTIDAD (Y SU ID) SOLO SI LAS VALIDACIONES PASARON
        super().__init__()
        self.nombre = nombre.strip()
        self.tarifa_base = tarifa_base
        self.disponible = bool(disponible)

    # VERIFICAR DISPONIBILIDAD: lo llama Reserva.procesar()
    def verificar_disponibilidad(self):
        if not self.disponible:
            raise ServicioNoDisponibleError(
                f"El servicio '{self.nombre}' no está disponible")

    # VALIDACIONES COMUNES PARA EL CÁLCULO DEL COSTO
    @staticmethod
    def _validar_horas(horas):
        if not _es_numero(horas) or horas <= 0:
            raise ServicioError("Las horas deben ser un número mayor a cero")

    @staticmethod
    def _validar_porcentajes(impuesto, descuento):
        if not _es_numero(impuesto) or impuesto < 0:
            raise ServicioError("El impuesto debe ser un número mayor o igual a cero")
        if not _es_numero(descuento) or not 0 <= descuento <= 1:
            raise ServicioError("El descuento debe estar entre 0 y 1")

    # SE APLICA PRIMERO EL DESCUENTO Y DESPUÉS EL IMPUESTO
    @staticmethod
    def _total(base, impuesto, descuento):
        return round(base * (1 - descuento) * (1 + impuesto), 2)

    @abstractmethod
    def calcular_costo(self, horas, impuesto=0, descuento=0):
        pass

    @abstractmethod
    def descripcion(self):
        pass

    # DESCRIBIR: resumen en texto (lo exige Entidad y lo usan main.py e interfaz.py)
    def describir(self):
        return (f"Servicio {self.id} | {type(self).__name__}: {self.nombre} | "
                f"Tarifa/hora: {self.tarifa_base} | "
                f"Disponible: {'Sí' if self.disponible else 'No'}")


# SERVICIO: RESERVA DE SALAS


class ReservaSala(Servicio):

    def calcular_costo(self, horas, impuesto=0, descuento=0):
        self._validar_horas(horas)
        self._validar_porcentajes(impuesto, descuento)
        return self._total(self.tarifa_base * horas, impuesto, descuento)

    def descripcion(self):
        return "Servicio de reserva de salas empresariales"


# SERVICIO: ALQUILER DE EQUIPOS


class AlquilerEquipo(Servicio):

    SEGURO = 20

    def calcular_costo(self, horas, impuesto=0, descuento=0):
        self._validar_horas(horas)
        self._validar_porcentajes(impuesto, descuento)
        base = self.tarifa_base * horas + AlquilerEquipo.SEGURO
        return self._total(base, impuesto, descuento)

    def descripcion(self):
        return "Servicio de alquiler de equipos tecnológicos"


# SERVICIO: ASESORÍA ESPECIALIZADA


class AsesoriaEspecializada(Servicio):

    IVA = 0.19

    # SI NO SE ENVÍA IMPUESTO, LA ASESORÍA COBRA IVA POR DEFECTO
    def calcular_costo(self, horas, impuesto=None, descuento=0):
        if impuesto is None:
            impuesto = AsesoriaEspecializada.IVA
        self._validar_horas(horas)
        self._validar_porcentajes(impuesto, descuento)
        return self._total(self.tarifa_base * horas, impuesto, descuento)

    def descripcion(self):
        return "Servicio de asesoría especializada"
