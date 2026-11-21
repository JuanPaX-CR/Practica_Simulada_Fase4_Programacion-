# PARTE 3: SIMULACIÓN DEL SISTEMA
# DESARROLLADO POR: JUANPABLO


# IMPORTACIONES: se traen las clases de las otras partes del proyecto
from cliente import Cliente
from excepciones import ClienteError, ErrorSoftwareFJ
from logger import registrar_error, registrar_evento
from reserva import Reserva
from servicios import AlquilerEquipo, AsesoriaEspecializada, ReservaSala


# CLASE SISTEMA


class SistemaGestion:

    def __init__(self):
        # LISTAS INTERNAS: aquí se guarda todo (no se usa base de datos)
        self.clientes = []
        self.servicios = []
        self.reservas = []

    # AGREGAR CLIENTE: si no es un objeto Cliente, lanza ClienteError
    def agregar_cliente(self, cliente):
        if not isinstance(cliente, Cliente):
            raise ClienteError("Objeto cliente inválido")
        self.clientes.append(cliente)
        registrar_evento(f"Cliente agregado: {cliente.nombre}")

    def agregar_servicio(self, servicio):
        self.servicios.append(servicio)
        registrar_evento(f"Servicio agregado: {servicio.nombre}")

    # CREAR RESERVA: procesa la reserva y solo la guarda en la lista si todo salió bien
    def crear_reserva(self, reserva, **opciones):
        costo = reserva.procesar(**opciones)
        self.reservas.append(reserva)
        return costo


# EJECUCIÓN DE CADA OPERACIÓN


def ejecutar(numero, descripcion, accion):
    # CADA OPERACIÓN SE EJECUTA DENTRO DE SU PROPIO try/except,
    # ASÍ UN ERROR NUNCA DETIENE EL PROGRAMA
    print(f"\n[{numero}] {descripcion}")
    try:
        resultado = accion()
    # ERRORES PROPIOS DEL SISTEMA: se muestran en pantalla y se guardan en el log
    except ErrorSoftwareFJ as error:
        registrar_error(f"Operación {numero} falló: {descripcion}", error)
        print(f"   ERROR controlado ({type(error).__name__}): {error}")
        if error.__cause__ is not None:
            print(f"   Causa original: {error.__cause__}")
    # CUALQUIER OTRO ERROR INESPERADO: también se controla y el programa sigue
    except Exception as error:
        registrar_error(f"Error inesperado en la operación {numero}", error)
        print(f"   ERROR inesperado ({type(error).__name__}): {error}")
    # ELSE: la operación salió bien
    else:
        registrar_evento(f"Operación {numero} exitosa: {descripcion}")
        print(f"   OK: {resultado}")


# SIMULACIONES DEL SISTEMA


def simular():
    sistema = SistemaGestion()
    # DICCIONARIO PARA GUARDAR LOS OBJETOS CREADOS Y USARLOS EN LAS OPERACIONES SIGUIENTES
    d = {}

    # 1. CLIENTE VÁLIDO
    # SE CREA UN CLIENTE CON DATOS CORRECTOS Y SE GUARDA EN LA LISTA

    def op1():
        d["cliente"] = Cliente("Juan Pérez", "1010", "juan@gmail.com")
        sistema.agregar_cliente(d["cliente"])
        return d["cliente"].describir()

    # 2. CLIENTE CON CORREO INVÁLIDO
    # EL CORREO NO TIENE FORMATO VÁLIDO: DEBE DAR ClienteError

    def op2():
        return Cliente("Ana Torres", "2020", "correo_invalido")

    # 3. CLIENTE CON NOMBRE VACÍO
    # EL NOMBRE ESTÁ VACÍO: DEBE DAR ClienteError

    def op3():
        return Cliente("   ", "3030", "vacio@gmail.com")

    # 4. CLIENTE CON IDENTIFICACIÓN NO NUMÉRICA
    # LA IDENTIFICACIÓN TIENE LETRAS: DEBE DAR ClienteError

    def op4():
        return Cliente("Luis Gómez", "abc", "luis@gmail.com")

    # 5. CLIENTE CON CORREO NONE
    # EL CORREO ES None (ANTES DABA TypeError): DEBE DAR ClienteError

    def op5():
        return Cliente("Eva Ríos", "4040", None)

    # 6. SERVICIO VÁLIDO
    # SE CREA UNA SALA CON TARIFA VÁLIDA

    def op6():
        d["sala"] = ReservaSala("Sala de juntas", 50)
        sistema.agregar_servicio(d["sala"])
        return d["sala"].describir()

    # 7. SERVICIO CON TARIFA INVÁLIDA
    # LA TARIFA ES NEGATIVA: DEBE DAR ServicioError

    def op7():
        return ReservaSala("Sala inválida", -10)

    # 8. RESERVA EXITOSA
    # RESERVA CORRECTA: SE CONFIRMA Y SE CALCULA EL COSTO

    def op8():
        d["reserva1"] = Reserva(d["cliente"], d["sala"], 3)
        costo = sistema.crear_reserva(d["reserva1"])
        return f"{d['reserva1'].describir()} | Costo: ${costo}"

    # 9. RESERVA CON HORAS INVÁLIDAS
    # LA DURACIÓN ES NEGATIVA: DEBE DAR ReservaError

    def op9():
        return Reserva(d["cliente"], d["sala"], -5)

    # 10. SERVICIO DE ALQUILER CON IMPUESTO Y DESCUENTO
    # SE RESERVA UN EQUIPO CON IMPUESTO DEL 19% Y DESCUENTO DEL 10% (SOBRECARGA)

    def op10():
        d["equipo"] = AlquilerEquipo("Portátil Gamer", 80)
        sistema.agregar_servicio(d["equipo"])
        reserva = Reserva(d["cliente"], d["equipo"], 2)
        costo = sistema.crear_reserva(reserva, impuesto=0.19, descuento=0.10)
        return f"{reserva.describir()} | Costo con impuesto y descuento: ${costo}"

    # 11. SERVICIO DE ASESORÍA
    # LA ASESORÍA COBRA IVA POR DEFECTO

    def op11():
        d["asesoria"] = AsesoriaEspecializada("Asesoría Python", 120)
        sistema.agregar_servicio(d["asesoria"])
        d["reserva4"] = Reserva(d["cliente"], d["asesoria"], 4)
        costo = sistema.crear_reserva(d["reserva4"])
        return f"{d['reserva4'].describir()} | Costo: ${costo}"

    # 12. SERVICIO NO DISPONIBLE
    # EL SERVICIO NO ESTÁ DISPONIBLE: DEBE DAR ReservaError CAUSADO POR ServicioNoDisponibleError

    def op12():
        proyector = AlquilerEquipo("Proyector", 60, disponible=False)
        reserva = Reserva(d["cliente"], proyector, 2)
        return sistema.crear_reserva(reserva)

    # 13. CANCELACIÓN DE RESERVA
    # SE CANCELA LA RESERVA DE LA ASESORÍA

    def op13():
        d["reserva4"].cancelar()
        return d["reserva4"].describir()

    # 14. CANCELACIÓN REPETIDA
    # SE INTENTA CANCELAR OTRA VEZ: DEBE DAR OperacionNoPermitidaError

    def op14():
        d["reserva4"].cancelar()

    # 15. RESERVA CON CLIENTE INVÁLIDO
    # EL CLIENTE NO ES UN OBJETO Cliente: DEBE DAR ReservaError

    def op15():
        return Reserva("cliente falso", d["sala"], 2)

    # 16. RESERVA CON SERVICIO INVÁLIDO
    # EL SERVICIO NO ES UN OBJETO Servicio: DEBE DAR ReservaError

    def op16():
        return Reserva(d["cliente"], "servicio falso", 2)

    # 17. POLIMORFISMO Y SOBRECARGA
    # SE LLAMA calcular_costo() EN TRES SERVICIOS DISTINTOS

    def op17():
        resumen = []
        # POLIMORFISMO: LA MISMA LLAMADA calcular_costo() DA UN RESULTADO DISTINTO SEGÚN EL SERVICIO
        for servicio in (d["sala"], d["equipo"], d["asesoria"]):
            # SOBRECARGA: calcular_costo SE LLAMA CON 1, 2 Y 3 PARÁMETROS
            resumen.append(
                f"{servicio.nombre}: "
                f"2h=${servicio.calcular_costo(2)} | "
                f"con impuesto 19%=${servicio.calcular_costo(2, 0.19)} | "
                f"con impuesto y 10% desc.=${servicio.calcular_costo(2, 0.19, 0.10)}")
        return "\n      " + "\n      ".join(resumen)

    # LISTA DE OPERACIONES: (número, descripción, función que se ejecuta)
    operaciones = [
        (1, "Registrar cliente válido", op1),
        (2, "Registrar cliente con correo inválido", op2),
        (3, "Registrar cliente con nombre vacío", op3),
        (4, "Registrar cliente con identificación no numérica", op4),
        (5, "Registrar cliente con correo None", op5),
        (6, "Crear servicio de sala válido", op6),
        (7, "Crear servicio con tarifa negativa", op7),
        (8, "Reserva exitosa de la sala", op8),
        (9, "Reserva con duración negativa", op9),
        (10, "Alquiler de equipo con impuesto y descuento", op10),
        (11, "Asesoría especializada", op11),
        (12, "Reserva de un servicio no disponible", op12),
        (13, "Cancelar una reserva", op13),
        (14, "Cancelar la misma reserva otra vez", op14),
        (15, "Reserva con cliente falso", op15),
        (16, "Reserva con servicio falso", op16),
        (17, "Polimorfismo y sobrecarga de calcular_costo", op17),
    ]
    # SE EJECUTAN TODAS LAS OPERACIONES EN ORDEN, UNA POR UNA
    for numero, descripcion, accion in operaciones:
        ejecutar(numero, descripcion, accion)

    # RESUMEN FINAL DE LO QUE QUEDÓ GUARDADO EN LAS LISTAS
    print("\n========== RESUMEN ==========")
    print(f"Clientes registrados: {len(sistema.clientes)}")
    print(f"Servicios creados:    {len(sistema.servicios)}")
    print(f"Reservas guardadas:   {len(sistema.reservas)}")
    for reserva in sistema.reservas:
        print(f"  - {reserva.describir()}")
    print("\nSistema ejecutado sin interrupciones.")
    print("Revisar logs/eventos.log para ver los eventos y errores.")


# EJECUCIÓN DEL PROGRAMA


if __name__ == "__main__":
    # SE EJECUTA SOLO SI SE CORRE ESTE ARCHIVO DIRECTAMENTE (python main.py)
    simular()
