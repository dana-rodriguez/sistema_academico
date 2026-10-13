from datetime import date


class ModeloBase:
    """Clase padre: contiene el id y los métodos comunes."""

    def __init__(self, id_registro):
        self.id = int(id_registro)

    @classmethod
    def desde_diccionario(cls, datos):
        # cls permite crear Estudiante, Materia o Matricula.
        datos = dict(datos)
        id_registro = datos.pop("id")
        return cls(id_registro, **datos)

    def a_diccionario(self):
        return {"id": self.id}

    def etiqueta(self):
        return f"Registro {self.id}"

    def __str__(self):
        # Polimorfismo: cada modelo aporta su propia etiqueta.
        return f"[{self.id}] {self.etiqueta()}"


class Persona(ModeloBase):
    """Agrupa los datos comunes de las personas."""

    def __init__(self, id_registro, nombre, apellido, email):
        super().__init__(id_registro)
        self.nombre = str(nombre)
        self.apellido = str(apellido)
        self.email = str(email).strip().lower()

    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos.update({
            "nombre": self.nombre,
            "apellido": self.apellido,
            "email": self.email,
        })
        return datos

    def etiqueta(self):
        return self.nombre_completo()


class Estudiante(Persona):
    """Un estudiante es una persona con carnet y carrera."""

    def __init__(
        self, id_registro, nombre, apellido, email,
        carnet="", carrera=""
    ):
        super().__init__(id_registro, nombre, apellido, email)
        self.carnet = str(carnet).strip().upper()
        self.carrera = str(carrera).strip().title()

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos["carnet"] = self.carnet
        datos["carrera"] = self.carrera
        return datos

    def etiqueta(self):
        return (
            f"{super().etiqueta()} · "
            f"{self.carnet} · {self.carrera}"
        )


class Materia(ModeloBase):
    """Materia: administra cupos y reglas académicas."""

    CUPOS_MAXIMOS = 30
    NOTA_APROBACION = 14

    def __init__(
        self, id_registro, nombre, codigo,
        creditos=1, cupos=0
    ):
        super().__init__(id_registro)
        self.nombre = str(nombre).strip().title()
        self.codigo = str(codigo).strip().upper()
        self.creditos = int(creditos)
        self.cupos = int(cupos)

    @staticmethod
    def es_nota_valida(valor):
        # Método estático: no necesita una materia concreta.
        try:
            nota = float(valor)
            return 0 <= nota <= 20
        except (TypeError, ValueError):
            return False

    def hay_cupo(self):
        return self.cupos > 0

    def ocupar_cupo(self):
        if not self.hay_cupo():
            return False
        self.cupos -= 1
        return True

    def liberar_cupo(self):
        if self.cupos < self.CUPOS_MAXIMOS:
            self.cupos += 1
            return True
        return False

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos.update({
            "nombre": self.nombre,
            "codigo": self.codigo,
            "creditos": self.creditos,
            "cupos": self.cupos,
        })
        return datos

    def etiqueta(self):
        estado = "SIN CUPOS" if not self.hay_cupo() else f"{self.cupos} cupos"
        return (
            f"{self.nombre} · {self.codigo} · "
            f"{self.creditos} créditos · {estado}"
        )


class Matricula(ModeloBase):
    """Relaciona un estudiante con una materia."""

    def __init__(
        self, id_registro, estudiante_id, materia_id,
        periodo, nota=0, fecha=""
    ):
        super().__init__(id_registro)
        self.estudiante_id = int(estudiante_id)
        self.materia_id = int(materia_id)
        self.periodo = str(periodo).strip()
        self.nota = float(nota)
        self.fecha = fecha or date.today().isoformat()

    def esta_aprobada(self):
        return self.nota >= Materia.NOTA_APROBACION

    def estado(self):
        return "Aprobado" if self.esta_aprobada() else "Reprobado"

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos.update({
            "estudiante_id": self.estudiante_id,
            "materia_id": self.materia_id,
            "periodo": self.periodo,
            "nota": self.nota,
            "fecha": self.fecha,
        })
        return datos

    def etiqueta(self):
        return (
            f"{self.fecha} · estudiante {self.estudiante_id} · "
            f"materia {self.materia_id} · {self.periodo} · "
            f"nota {self.nota:.2f} · {self.estado()}"
        )
