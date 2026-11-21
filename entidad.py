"""
PARTE 1: Clase abstracta Entidad
Autor: Jose Yimy Palacio Lucumi (digitextosyisercarepa-pixel)

Clase base abstracta del sistema (Cliente, Servicio y Reserva heredan de ella).
Cada entidad recibe automáticamente un id único.
"""

import itertools
from abc import ABC, abstractmethod


class Entidad(ABC):

    # CONTADOR COMPARTIDO: cada entidad creada recibe el siguiente número
    _contador = itertools.count(1)

    def __init__(self):
        self.id = next(Entidad._contador)

    # TODA ENTIDAD DEBE PODER DESCRIBIRSE EN TEXTO
    @abstractmethod
    def describir(self):
        pass
