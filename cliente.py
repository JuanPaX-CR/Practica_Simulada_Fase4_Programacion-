"""
PARTE 1: Clientes
Autor: Jose Yimy Palacio Lucumi (digitextosyisercarepa-pixel)

Clase Cliente (hereda de Entidad) con validación de nombre,
identificación y correo electrónico.
"""

import re

from entidad import Entidad
from excepciones import ClienteError

# FORMATO MÍNIMO DE CORREO: algo@dominio.ext
PATRON_CORREO = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class Cliente(Entidad):

    def __init__(self, nombre, identificacion, correo):
        # VALIDACIONES: si algo es inválido, el cliente no se crea (ni gasta un id)
        if not isinstance(nombre, str) or not nombre.strip():
            raise ClienteError("El nombre no puede estar vacío")
        identificacion = str(identificacion).strip()
        if not identificacion.isdigit():
            raise ClienteError("La identificación debe ser numérica")

        correo = Cliente._validar_correo(correo)

        super().__init__()
        self.nombre = nombre.strip()
        self.identificacion = identificacion
        self.__correo = correo

    @property
    def correo(self):
        return self.__correo

    @correo.setter
    def correo(self, valor):
        self.__correo = Cliente._validar_correo(valor)

    # VALIDA EL FORMATO DEL CORREO Y LO DEVUELVE SIN ESPACIOS
    @staticmethod
    def _validar_correo(valor):
        if not isinstance(valor, str) or not PATRON_CORREO.match(valor.strip()):
            raise ClienteError("Correo electrónico inválido")
        return valor.strip()

    def describir(self):
        return (f"Cliente {self.id} | {self.nombre} | "
                f"ID: {self.identificacion} | {self.correo}")
