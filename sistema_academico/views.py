from abc import ABC, abstractmethod

from models import Estudiante, Materia, Matricula
from shared.json_manager import GestorJSON
from shared.herramientas import es_email_valido


class CrudBase(ABC):
    """Contrato de operaciones que debe cumplir cada controlador."""

    @abstractmethod
    def crear(self, datos):
        pass

    @abstractmethod
    def actualizar(self, id_registro, datos):
        pass

    @abstractmethod
    def eliminar(self, id_registro):
        pass


class ControladorBase(CrudBase):
    """Operaciones reutilizables para cualquier modelo."""

    CAMPOS_BUSCABLES = ()

    def __init__(self, archivo, clase):
        self.gestor = GestorJSON(archivo)
        self.clase = clase
        self.lista = []

        for datos in self.gestor.leer():
            try:
                self.lista.append(clase.desde_diccionario(datos))
            except (TypeError, ValueError, KeyError):
                # Ignora registros que no coincidan con el modelo.
                continue

    def guardar(self):
        datos = [objeto.a_diccionario() for objeto in self.lista]
        return self.gestor.guardar(datos)

    def leer(self):
        return list(self.lista)

    def obtener(self, id_registro):
        if id_registro is None:
            return None

        for objeto in self.lista:
            if objeto.id == id_registro:
                return objeto
        return None

    def buscar(self, termino):
        termino = str(termino).strip().casefold()

        if not termino:
            return []

        # Tupla: campos fijos que se pueden buscar.
        encontrados = []
        for objeto in self.lista:
            for campo in self.CAMPOS_BUSCABLES:
                valor = str(getattr(objeto, campo, ""))
                if termino in valor.casefold():
                    encontrados.append(objeto)
                    break

        return encontrados

    def siguiente(self):
        return max((objeto.id for objeto in self.lista), default=0) + 1

    def eliminar(self, id_registro):
        objeto = self.obtener(id_registro)

        if objeto is None:
            return False, "Registro no encontrado"

        self.lista.remove(objeto)

        if not self.guardar():
            self.lista.append(objeto)
            return False, "No se pudo guardar el archivo"

        return True, f"Registro {id_registro} eliminado"


class EstudianteController(ControladorBase):
    CAMPOS_BUSCABLES = (
        "nombre", "apellido", "email", "carnet", "carrera"
    )

    def __init__(self, archivo="data/estudiantes.json"):
        super().__init__(archivo, Estudiante)

    def validar(self, datos, id_actual=None):
        obligatorios = ("nombre", "apellido", "email", "carnet")

        if id_actual is None:
            for campo in obligatorios:
                if not str(datos.get(campo, "")).strip():
                    return f"El campo {campo} es obligatorio"

        if "email" in datos:
            email = str(datos["email"]).strip().lower()

            if not es_email_valido(email):
                return "El email no es válido"

            emails = {
                e.email for e in self.lista if e.id != id_actual
            }
            if email in emails:
                return "El email ya está registrado"

        if "carnet" in datos:
            carnet = str(datos["carnet"]).strip().upper()

            # Set: evita carnets duplicados con búsqueda eficiente.
            carnets = {
                e.carnet for e in self.lista if e.id != id_actual
            }
            if not carnet:
                return "El carnet es obligatorio"
            if carnet in carnets:
                return "El carnet ya está registrado"

        return None

    def crear(self, datos):
        error = self.validar(datos)
        if error:
            return False, error

        estudiante = Estudiante(
            self.siguiente(),
            str(datos["nombre"]).strip().title(),
            str(datos["apellido"]).strip().title(),
            str(datos["email"]).strip().lower(),
            str(datos["carnet"]).strip().upper(),
            str(datos.get("carrera", "")).strip().title(),
        )

        self.lista.append(estudiante)

        if not self.guardar():
            self.lista.remove(estudiante)
            return False, "No se pudo guardar el estudiante"

        return True, f"Estudiante creado: {estudiante.etiqueta()}"

    def actualizar(self, id_registro, datos):
        estudiante = self.obtener(id_registro)

        if estudiante is None:
            return False, "Estudiante no encontrado"
        if not datos:
            return False, "No se indicaron cambios"

        permitidos = {
            "nombre", "apellido", "email", "carnet", "carrera"
        }
        desconocidos = set(datos) - permitidos

        if desconocidos:
            return False, f"Campos inválidos: {', '.join(sorted(desconocidos))}"

        error = self.validar(datos, id_registro)
        if error:
            return False, error

        anteriores = estudiante.a_diccionario()

        for campo, valor in datos.items():
            valor = str(valor).strip()

            if campo in ("nombre", "apellido", "carrera"):
                valor = valor.title()
            elif campo == "email":
                valor = valor.lower()
            elif campo == "carnet":
                valor = valor.upper()

            setattr(estudiante, campo, valor)

        if not self.guardar():
            restaurar_estudiante(estudiante, anteriores)
            return False, "No se pudieron guardar los cambios"

        return True, "Estudiante actualizado"


def restaurar_estudiante(estudiante, datos):
    estudiante.nombre = datos["nombre"]
    estudiante.apellido = datos["apellido"]
    estudiante.email = datos["email"]
    estudiante.carnet = datos["carnet"]
    estudiante.carrera = datos["carrera"]


class MateriaController(ControladorBase):
    CAMPOS_BUSCABLES = ("nombre", "codigo")

    def __init__(self, archivo="data/materias.json"):
        super().__init__(archivo, Materia)

    def validar(self, datos, id_actual=None):
        if id_actual is None:
            for campo in ("nombre", "codigo"):
                if not str(datos.get(campo, "")).strip():
                    return f"El campo {campo} es obligatorio"

        if "codigo" in datos:
            codigo = str(datos["codigo"]).strip().upper()

            # Set: códigos únicos en todas las materias.
            codigos = {
                m.codigo for m in self.lista if m.id != id_actual
            }
            if not codigo:
                return "El código es obligatorio"
            if codigo in codigos:
                return "El código ya está registrado"

        try:
            creditos = int(datos.get("creditos", 1))
            cupos = int(datos.get("cupos", 0))
        except (TypeError, ValueError):
            return "Créditos y cupos deben ser números enteros"

        if "creditos" in datos or id_actual is None:
            if not 1 <= creditos <= 10:
                return "Los créditos deben estar entre 1 y 10"

        if "cupos" in datos or id_actual is None:
            if not 0 <= cupos <= Materia.CUPOS_MAXIMOS:
                return f"Los cupos deben estar entre 0 y {Materia.CUPOS_MAXIMOS}"

        return None

    def crear(self, datos):
        error = self.validar(datos)
        if error:
            return False, error

        materia = Materia(
            self.siguiente(),
            datos["nombre"],
            datos["codigo"],
            datos.get("creditos", 1),
            datos.get("cupos", 0),
        )

        self.lista.append(materia)

        if not self.guardar():
            self.lista.remove(materia)
            return False, "No se pudo guardar la materia"

        return True, f"Materia creada: {materia.etiqueta()}"

    def actualizar(self, id_registro, datos):
        materia = self.obtener(id_registro)

        if materia is None:
            return False, "Materia no encontrada"
        if not datos:
            return False, "No se indicaron cambios"

        permitidos = {"nombre", "codigo", "creditos", "cupos"}
        desconocidos = set(datos) - permitidos

        if desconocidos:
            return False, f"Campos inválidos: {', '.join(sorted(desconocidos))}"

        error = self.validar(datos, id_registro)
        if error:
            return False, error

        # No se permite reducir cupos por debajo de matrículas existentes
        # en este controlador. La interfaz debe evitar cambios incoherentes.
        anteriores = materia.a_diccionario()

        try:
            if "nombre" in datos:
                materia.nombre = str(datos["nombre"]).strip().title()
            if "codigo" in datos:
                materia.codigo = str(datos["codigo"]).strip().upper()
            if "creditos" in datos:
                materia.creditos = int(datos["creditos"])
            if "cupos" in datos:
                materia.cupos = int(datos["cupos"])
        except (TypeError, ValueError):
            restaurar_materia(materia, anteriores)
            return False, "Datos numéricos inválidos"

        if not self.guardar():
            restaurar_materia(materia, anteriores)
            return False, "No se pudieron guardar los cambios"

        return True, "Materia actualizada"

    def materias_sin_cupo(self):
        return [m for m in self.lista if not m.hay_cupo()]


def restaurar_materia(materia, datos):
    materia.nombre = datos["nombre"]
    materia.codigo = datos["codigo"]
    materia.creditos = datos["creditos"]
    materia.cupos = datos["cupos"]


class MatriculaController(ControladorBase):
    CAMPOS_BUSCABLES = ("periodo", "fecha")

    def __init__(
        self, estudiantes, materias,
        archivo="data/matriculas.json"
    ):
        super().__init__(archivo, Matricula)
        self.estudiantes = estudiantes
        self.materias = materias

    def crear(self, datos):
        try:
            estudiante_id = int(datos["estudiante_id"])
            materia_id = int(datos["materia_id"])
        except (KeyError, TypeError, ValueError):
            return False, "Los IDs deben ser números enteros"

        periodo = str(datos.get("periodo", "")).strip()

        if not periodo:
            return False, "El periodo es obligatorio"

        estudiante = self.estudiantes.obtener(estudiante_id)
        materia = self.materias.obtener(materia_id)

        if estudiante is None:
            return False, "El estudiante no existe"
        if materia is None:
            return False, "La materia no existe"
        if not materia.hay_cupo():
            return False, "La materia no tiene cupos disponibles"

        for matricula in self.lista:
            if (
                matricula.estudiante_id == estudiante_id
                and matricula.materia_id == materia_id
                and matricula.periodo == periodo
            ):
                return False, "El estudiante ya está matriculado en esa materia y periodo"

        matricula = Matricula(
            self.siguiente(),
            estudiante_id,
            materia_id,
            periodo,
            0,
        )

        # Primero descontamos el cupo y persistimos ambos cambios.
        materia.ocupar_cupo()

        if not self.materias.guardar():
            materia.liberar_cupo()
            return False, "No se pudo guardar el nuevo cupo"

        self.lista.append(matricula)

        if not self.guardar():
            self.lista.remove(matricula)
            materia.liberar_cupo()
            self.materias.guardar()
            return False, "No se pudo guardar la matrícula"

        return True, f"Matrícula {matricula.id} creada"

    def actualizar(self, id_registro, datos):
        # La nota se cambia con registrar_nota(), no con un CRUD genérico.
        return False, "Use registrar_nota() para actualizar la nota"

    def registrar_nota(self, id_registro, valor):
        matricula = self.obtener(id_registro)

        if matricula is None:
            return False, "Matrícula no encontrada"
        if not Materia.es_nota_valida(valor):
            return False, "La nota debe estar entre 0 y 20"

        nota_anterior = matricula.nota
        matricula.nota = float(valor)

        if not self.guardar():
            matricula.nota = nota_anterior
            return False, "No se pudo guardar la nota"

        return True, f"Nota registrada: {matricula.nota:.2f} ({matricula.estado()})"

    def retirar_matricula(self, id_registro):
        return self.eliminar(id_registro)

    def eliminar(self, id_registro):
        matricula = self.obtener(id_registro)

        if matricula is None:
            return False, "Matrícula no encontrada"

        materia = self.materias.obtener(matricula.materia_id)

        if materia is not None:
            if not materia.liberar_cupo():
                return False, "No se pudo liberar el cupo"
            if not self.materias.guardar():
                materia.cupos -= 1
                return False, "No se pudo guardar el cupo liberado"

        self.lista.remove(matricula)

        if not self.guardar():
            self.lista.append(matricula)
            if materia is not None:
                materia.cupos -= 1
                self.materias.guardar()
            return False, "No se pudo guardar la eliminación"

        return True, "Matrícula retirada y cupo liberado"

    def certificado(self, id_registro):
        matricula = self.obtener(id_registro)

        if matricula is None:
            return None

        # Diccionarios índice: permiten localizar registros por ID.
        estudiantes = {e.id: e for e in self.estudiantes.leer()}
        materias = {m.id: m for m in self.materias.leer()}

        estudiante = estudiantes.get(matricula.estudiante_id)
        materia = materias.get(matricula.materia_id)

        nombre = estudiante.nombre_completo() if estudiante else "Eliminado"
        carnet = estudiante.carnet if estudiante else "-"
        nombre_materia = materia.nombre if materia else "Eliminada"
        codigo = materia.codigo if materia else "-"
        creditos = materia.creditos if materia else 0

        return (
            f"CERTIFICADO #{matricula.id} · Periodo: {matricula.periodo}\n"
            f"Estudiante: {nombre} ({carnet})\n"
            f"Materia: {nombre_materia} ({codigo}) · {creditos} créditos\n"
            f"{'-' * 42}\n"
            f"Nota: {matricula.nota:.2f}\n"
            f"Estado: {matricula.estado()}"
        )

    def matriculas_por_estudiante(self):
        # Diccionario de listas: agrupa todas las matrículas por estudiante.
        agrupadas = {}

        for matricula in self.lista:
            agrupadas.setdefault(matricula.estudiante_id, []).append(matricula)

        return agrupadas

    def promedio_de_estudiante(self, id_estudiante):
        notas = [
            m.nota for m in self.lista
            if m.estudiante_id == id_estudiante
        ]

        if not notas:
            return None

        return round(sum(notas) / len(notas), 2)

    def aprobadas(self):
        return [m for m in self.lista if m.esta_aprobada()]
