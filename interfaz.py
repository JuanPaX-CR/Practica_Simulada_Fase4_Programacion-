# PARTE 3: INTERFAZ GRÁFICA
# DESARROLLADO POR: JUANPABLO


# IMPORTACIONES: tkinter es la librería de ventanas que viene incluida con Python
import os
import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText

from cliente import Cliente
from excepciones import ErrorSoftwareFJ, ReservaError, ServicioError
from logger import registrar_error
from main import SistemaGestion
from reserva import Reserva
from servicios import AlquilerEquipo, AsesoriaEspecializada, ReservaSala


# CONSTANTES DE LA INTERFAZ


# TIPOS DE SERVICIO QUE SE MUESTRAN EN LA LISTA DESPLEGABLE (texto -> clase)
TIPOS_SERVICIO = {
    "Reserva de sala": ReservaSala,
    "Alquiler de equipo": AlquilerEquipo,
    "Asesoría especializada": AsesoriaEspecializada,
}
# RUTA DEL ARCHIVO DE LOG, SE USA EN LA PESTAÑA REGISTRO
RUTA_LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs", "eventos.log")


# FUNCIÓN AUXILIAR


def leer_numero(texto, nombre, error=ServicioError):
    try:
        return float(texto.strip().replace(",", "."))
    except ValueError as causa:
        # ENCADENAMIENTO DE EXCEPCIONES: el error nuevo conserva la causa original (from)
        raise error(f"{nombre} debe ser un número") from causa


# CLASE VENTANA PRINCIPAL


class App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Software FJ - Gestión de clientes, servicios y reservas")
        self.geometry("880x620")
        self.minsize(780, 540)

        # EL SISTEMA GUARDA CLIENTES, SERVICIOS Y RESERVAS EN LISTAS (SIN BASE DE DATOS)
        self.sistema = SistemaGestion()
        # GUARDA EL COSTO DE CADA RESERVA (id de la reserva -> costo)
        self.costos = {}
        self.mensaje = tk.StringVar(value="Listo.")

        # PESTAÑAS DE LA VENTANA
        self.pestanas = ttk.Notebook(self)
        self.pestanas.pack(fill="both", expand=True, padx=8, pady=8)
        self.tab_clientes = ttk.Frame(self.pestanas)
        self.tab_servicios = ttk.Frame(self.pestanas)
        self.tab_reservas = ttk.Frame(self.pestanas)
        self.tab_log = ttk.Frame(self.pestanas)
        self.pestanas.add(self.tab_clientes, text="Clientes")
        self.pestanas.add(self.tab_servicios, text="Servicios")
        self.pestanas.add(self.tab_reservas, text="Reservas")
        self.pestanas.add(self.tab_log, text="Registro (log)")

        self._armar_clientes()
        self._armar_servicios()
        self._armar_reservas()
        self._armar_log()

        # BARRA DE ESTADO: muestra en verde si la acción salió bien y en rojo si falló
        self.lbl_mensaje = tk.Label(self, textvariable=self.mensaje, anchor="w")
        self.lbl_mensaje.pack(fill="x", padx=8, pady=(0, 8))
        self.pestanas.bind("<<NotebookTabChanged>>", lambda evento: self._refrescar_log())

    # UTILIDADES
    # CREA UNA TABLA CON BARRA DE DESPLAZAMIENTO (se reutiliza en las pestañas)
    def _crear_tabla(self, padre, columnas, titulos, fila):
        marco = ttk.Frame(padre)
        marco.grid(row=fila, column=0, columnspan=3, sticky="nsew", padx=8, pady=8)
        tabla = ttk.Treeview(marco, columns=columnas, show="headings", height=8)
        for columna, titulo in zip(columnas, titulos):
            tabla.heading(columna, text=titulo)
            tabla.column(columna, width=120, anchor="w")
        barra = ttk.Scrollbar(marco, orient="vertical", command=tabla.yview)
        tabla.configure(yscrollcommand=barra.set)
        tabla.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")
        padre.rowconfigure(fila, weight=1)
        padre.columnconfigure(2, weight=1)
        return tabla

    # MUESTRA UN MENSAJE EN LA BARRA DE ESTADO
    def _mostrar(self, texto, error=False):
        self.mensaje.set(texto)
        self.lbl_mensaje.config(fg="#b00020" if error else "#1b5e20")

    # EJECUTA CUALQUIER ACCIÓN DENTRO DE try/except: SI FALLA, MUESTRA EL ERROR,
    # LO GUARDA EN EL LOG Y LA VENTANA SIGUE ABIERTA
    def _ejecutar(self, accion, exito):
        try:
            resultado = accion()
        except ErrorSoftwareFJ as error:
            registrar_error("Error controlado desde la interfaz", error)
            self._mostrar(f"Error: {error}", error=True)
            messagebox.showerror("No se pudo completar la acción", str(error))
            return None
        except Exception as error:
            registrar_error("Error inesperado desde la interfaz", error)
            self._mostrar(f"Error inesperado: {error}", error=True)
            messagebox.showerror("Error inesperado", str(error))
            return None
        self._mostrar(exito)
        return resultado

    # PESTAÑA CLIENTES
    def _armar_clientes(self):
        marco = self.tab_clientes
        self.v_nombre = tk.StringVar()
        self.v_identificacion = tk.StringVar()
        self.v_correo = tk.StringVar()
        campos = [("Nombre", self.v_nombre), ("Identificación", self.v_identificacion),
                  ("Correo", self.v_correo)]
        for fila, (texto, variable) in enumerate(campos):
            ttk.Label(marco, text=texto).grid(row=fila, column=0, sticky="w", padx=8, pady=4)
            ttk.Entry(marco, textvariable=variable, width=40).grid(
                row=fila, column=1, sticky="w", padx=8, pady=4)
        ttk.Button(marco, text="Registrar cliente", command=self.registrar_cliente).grid(
            row=3, column=1, sticky="w", padx=8, pady=8)
        self.tabla_clientes = self._crear_tabla(
            marco, ("id", "nombre", "identificacion", "correo"),
            ("ID", "Nombre", "Identificación", "Correo"), fila=4)

    # BOTÓN REGISTRAR CLIENTE (las validaciones están en cliente.py)
    def registrar_cliente(self):
        def accion():
            cliente = Cliente(self.v_nombre.get(), self.v_identificacion.get(), self.v_correo.get())
            self.sistema.agregar_cliente(cliente)
            return cliente

        cliente = self._ejecutar(accion, "Cliente registrado correctamente.")
        if cliente is not None:
            for variable in (self.v_nombre, self.v_identificacion, self.v_correo):
                variable.set("")
            self._refrescar_clientes()
            self._refrescar_listas()

    # ACTUALIZA LA TABLA DE CLIENTES
    def _refrescar_clientes(self):
        self.tabla_clientes.delete(*self.tabla_clientes.get_children())
        for c in self.sistema.clientes:
            self.tabla_clientes.insert("", "end", iid=str(c.id),
                                       values=(c.id, c.nombre, c.identificacion, c.correo))

    # PESTAÑA SERVICIOS
    def _armar_servicios(self):
        marco = self.tab_servicios
        self.v_tarifa = tk.StringVar()
        self.v_nombre_servicio = tk.StringVar()
        self.v_disponible = tk.BooleanVar(value=True)

        ttk.Label(marco, text="Tipo").grid(row=0, column=0, sticky="w", padx=8, pady=4)
        self.cb_tipo = ttk.Combobox(marco, values=list(TIPOS_SERVICIO), state="readonly", width=37)
        self.cb_tipo.grid(row=0, column=1, sticky="w", padx=8, pady=4)
        ttk.Label(marco, text="Nombre").grid(row=1, column=0, sticky="w", padx=8, pady=4)
        ttk.Entry(marco, textvariable=self.v_nombre_servicio, width=40).grid(
            row=1, column=1, sticky="w", padx=8, pady=4)
        ttk.Label(marco, text="Tarifa por hora").grid(row=2, column=0, sticky="w", padx=8, pady=4)
        ttk.Entry(marco, textvariable=self.v_tarifa, width=40).grid(
            row=2, column=1, sticky="w", padx=8, pady=4)
        ttk.Checkbutton(marco, text="Disponible", variable=self.v_disponible).grid(
            row=3, column=1, sticky="w", padx=8, pady=4)
        ttk.Button(marco, text="Crear servicio", command=self.crear_servicio).grid(
            row=4, column=1, sticky="w", padx=8, pady=4)
        ttk.Button(marco, text="Cambiar disponibilidad del seleccionado",
                   command=self.cambiar_disponibilidad).grid(
            row=4, column=2, sticky="w", padx=8, pady=4)
        self.tabla_servicios = self._crear_tabla(
            marco, ("id", "tipo", "nombre", "tarifa", "disponible"),
            ("ID", "Tipo", "Nombre", "Tarifa", "Disponible"), fila=5)

    # BOTÓN CREAR SERVICIO
    def crear_servicio(self):
        def accion():
            tipo = self.cb_tipo.get()
            if tipo not in TIPOS_SERVICIO:
                raise ServicioError("Selecciona un tipo de servicio")
            tarifa = leer_numero(self.v_tarifa.get(), "La tarifa", ServicioError)
            servicio = TIPOS_SERVICIO[tipo](self.v_nombre_servicio.get(), tarifa,
                                            self.v_disponible.get())
            self.sistema.agregar_servicio(servicio)
            return servicio

        servicio = self._ejecutar(accion, "Servicio creado correctamente.")
        if servicio is not None:
            self.v_nombre_servicio.set("")
            self.v_tarifa.set("")
            self._refrescar_servicios()
            self._refrescar_listas()

    # BOTÓN CAMBIAR DISPONIBILIDAD: sirve para probar el error de servicio no disponible
    def cambiar_disponibilidad(self):
        def accion():
            seleccion = self.tabla_servicios.selection()
            if not seleccion:
                raise ServicioError("Selecciona un servicio de la tabla")
            servicio = next(s for s in self.sistema.servicios if s.id == int(seleccion[0]))
            servicio.disponible = not servicio.disponible
            return servicio

        servicio = self._ejecutar(accion, "Disponibilidad actualizada.")
        if servicio is not None:
            self._refrescar_servicios()

    # ACTUALIZA LA TABLA DE SERVICIOS
    def _refrescar_servicios(self):
        self.tabla_servicios.delete(*self.tabla_servicios.get_children())
        for s in self.sistema.servicios:
            self.tabla_servicios.insert(
                "", "end", iid=str(s.id),
                values=(s.id, type(s).__name__, s.nombre, s.tarifa_base,
                        "Sí" if s.disponible else "No"))

    # PESTAÑA RESERVAS
    def _armar_reservas(self):
        marco = self.tab_reservas
        self.v_duracion = tk.StringVar()
        self.v_impuesto = tk.StringVar()
        self.v_descuento = tk.StringVar()

        ttk.Label(marco, text="Cliente").grid(row=0, column=0, sticky="w", padx=8, pady=4)
        self.cb_cliente = ttk.Combobox(marco, state="readonly", width=37)
        self.cb_cliente.grid(row=0, column=1, sticky="w", padx=8, pady=4)
        ttk.Label(marco, text="Servicio").grid(row=1, column=0, sticky="w", padx=8, pady=4)
        self.cb_servicio = ttk.Combobox(marco, state="readonly", width=37)
        self.cb_servicio.grid(row=1, column=1, sticky="w", padx=8, pady=4)
        ttk.Label(marco, text="Duración (horas)").grid(row=2, column=0, sticky="w", padx=8, pady=4)
        ttk.Entry(marco, textvariable=self.v_duracion, width=40).grid(
            row=2, column=1, sticky="w", padx=8, pady=4)
        ttk.Label(marco, text="Impuesto (opcional, ej. 0.19)").grid(
            row=3, column=0, sticky="w", padx=8, pady=4)
        ttk.Entry(marco, textvariable=self.v_impuesto, width=40).grid(
            row=3, column=1, sticky="w", padx=8, pady=4)
        ttk.Label(marco, text="Descuento (opcional, ej. 0.10)").grid(
            row=4, column=0, sticky="w", padx=8, pady=4)
        ttk.Entry(marco, textvariable=self.v_descuento, width=40).grid(
            row=4, column=1, sticky="w", padx=8, pady=4)
        ttk.Button(marco, text="Crear y procesar reserva", command=self.crear_reserva).grid(
            row=5, column=1, sticky="w", padx=8, pady=4)
        ttk.Button(marco, text="Cancelar reserva seleccionada",
                   command=self.cancelar_reserva).grid(
            row=5, column=2, sticky="w", padx=8, pady=4)
        self.tabla_reservas = self._crear_tabla(
            marco, ("id", "cliente", "servicio", "duracion", "estado", "costo"),
            ("ID", "Cliente", "Servicio", "Horas", "Estado", "Costo"), fila=6)

    # BOTÓN CREAR RESERVA: junta cliente, servicio y horas, y procesa la reserva
    def crear_reserva(self):
        def accion():
            i = self.cb_cliente.current()
            j = self.cb_servicio.current()
            if i < 0:
                raise ReservaError("Selecciona un cliente")
            if j < 0:
                raise ReservaError("Selecciona un servicio")
            duracion = leer_numero(self.v_duracion.get(), "La duración", ReservaError)
            # EL IMPUESTO Y EL DESCUENTO SOLO SE ENVÍAN SI EL USUARIO LOS ESCRIBIÓ
            opciones = {}
            if self.v_impuesto.get().strip():
                opciones["impuesto"] = leer_numero(self.v_impuesto.get(), "El impuesto", ReservaError)
            if self.v_descuento.get().strip():
                opciones["descuento"] = leer_numero(self.v_descuento.get(), "El descuento", ReservaError)
            reserva = Reserva(self.sistema.clientes[i], self.sistema.servicios[j], duracion)
            costo = self.sistema.crear_reserva(reserva, **opciones)
            self.costos[reserva.id] = costo
            return costo

        costo = self._ejecutar(accion, "Reserva procesada correctamente.")
        if costo is not None:
            self._mostrar(f"Reserva confirmada. Costo total: ${costo}")
            for variable in (self.v_duracion, self.v_impuesto, self.v_descuento):
                variable.set("")
            self._refrescar_reservas()

    # BOTÓN CANCELAR RESERVA: cancela la reserva seleccionada en la tabla
    def cancelar_reserva(self):
        def accion():
            seleccion = self.tabla_reservas.selection()
            if not seleccion:
                raise ReservaError("Selecciona una reserva de la tabla")
            reserva = next(r for r in self.sistema.reservas if r.id == int(seleccion[0]))
            reserva.cancelar()
            return reserva

        reserva = self._ejecutar(accion, "Reserva cancelada.")
        if reserva is not None:
            self._refrescar_reservas()

    # ACTUALIZA LA TABLA DE RESERVAS
    def _refrescar_reservas(self):
        self.tabla_reservas.delete(*self.tabla_reservas.get_children())
        for r in self.sistema.reservas:
            self.tabla_reservas.insert(
                "", "end", iid=str(r.id),
                values=(r.id, r.cliente.nombre, r.servicio.nombre, r.duracion, r.estado,
                        self.costos.get(r.id, "")))

    # ACTUALIZA LAS LISTAS DESPLEGABLES DE LA PESTAÑA RESERVAS
    def _refrescar_listas(self):
        self.cb_cliente["values"] = [f"{c.id} - {c.nombre}" for c in self.sistema.clientes]
        self.cb_servicio["values"] = [f"{s.id} - {s.nombre}" for s in self.sistema.servicios]

    # PESTAÑA REGISTRO
    def _armar_log(self):
        ttk.Button(self.tab_log, text="Actualizar", command=self._refrescar_log).pack(
            anchor="w", padx=8, pady=8)
        self.texto_log = ScrolledText(self.tab_log, height=20, state="disabled")
        self.texto_log.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    # MUESTRA LAS ÚLTIMAS 200 LÍNEAS DE logs/eventos.log
    def _refrescar_log(self):
        try:
            with open(RUTA_LOG, encoding="utf-8") as archivo:
                lineas = archivo.readlines()[-200:]
        except OSError:
            lineas = ["Todavía no hay registros."]
        self.texto_log.config(state="normal")
        self.texto_log.delete("1.0", "end")
        self.texto_log.insert("end", "".join(lineas))
        self.texto_log.see("end")
        self.texto_log.config(state="disabled")


# EJECUCIÓN DEL PROGRAMA


def main():
    App().mainloop()


if __name__ == "__main__":
    main()
