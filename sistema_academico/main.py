from shared.herramientas import (
    imprimir_titulo,
    imprimir_exito,
    imprimir_error,
    imprimir_info,
    confirmar,
)
from views import (
    EstudianteController,
    MateriaController,
    MatriculaController,
)


# Un solo controlador de cada tipo durante la ejecución.
estudiantes = EstudianteController()
materias = MateriaController()
matriculas = MatriculaController(estudiantes, materias)


def pausa():
    input("\nPresione Enter para continuar...")


def pedir_entero(mensaje):
    try:
        return int(input(mensaje))
    except ValueError:
        imprimir_error("Debe escribir un número entero")
        return None


def mostrar_resultado(resultado):
    exito, mensaje = resultado
    if exito:
        imprimir_exito(mensaje)
    else:
        imprimir_error(mensaje)


def mostrar_lista(objetos, mensaje_vacio="No hay registros"):
    if not objetos:
        imprimir_info(mensaje_vacio)
        return

    # Polimorfismo: cada objeto decide cómo se muestra.
    for objeto in objetos:
        print(f"  {objeto}")

    imprimir_info(f"Total: {len(objetos)}")


def mostrar_detalle(objeto):
    if objeto is None:
        imprimir_error("Registro no encontrado")
        return

    for campo, valor in objeto.a_diccionario().items():
        print(f"  {campo.replace('_', ' ').capitalize():<18}: {valor}")


def pedir_cambios(objeto, campos):
    """Devuelve solo los campos que el usuario desea cambiar."""
    cambios = {}

    for campo in campos:
        actual = getattr(objeto, campo)
        nuevo = input(f"{campo.capitalize()} [{actual}]: ").strip()

        if nuevo:
            cambios[campo] = nuevo

    return cambios


# ---------------------------------------------------------
# FUNCIONES GENERALES PARA ESTUDIANTES Y MATERIAS
# ---------------------------------------------------------

def crear_estudiante():
    imprimir_titulo("CREAR ESTUDIANTE")

    datos = {
        "nombre": input("Nombre: "),
        "apellido": input("Apellido: "),
        "email": input("Email: "),
        "carnet": input("Carnet: "),
        "carrera": input("Carrera: "),
    }

    mostrar_resultado(estudiantes.crear(datos))
    pausa()


def listar_estudiantes():
    imprimir_titulo("ESTUDIANTES")
    mostrar_lista(estudiantes.leer(), "No hay estudiantes")
    pausa()


def buscar_estudiante():
    imprimir_titulo("BUSCAR ESTUDIANTE")
    termino = input("Nombre, email, carnet o carrera: ")
    mostrar_lista(estudiantes.buscar(termino), "Sin coincidencias")
    pausa()


def ver_estudiante():
    imprimir_titulo("ESTUDIANTE POR ID")
    id_registro = pedir_entero("ID: ")

    if id_registro is not None:
        mostrar_detalle(estudiantes.obtener(id_registro))
    pausa()


def actualizar_estudiante():
    imprimir_titulo("ACTUALIZAR ESTUDIANTE")
    id_registro = pedir_entero("ID: ")

    if id_registro is None:
        return pausa()

    objeto = estudiantes.obtener(id_registro)
    if objeto is None:
        imprimir_error("Estudiante no encontrado")
        return pausa()

    cambios = pedir_cambios(
        objeto, ("nombre", "apellido", "email", "carnet", "carrera")
    )
    mostrar_resultado(estudiantes.actualizar(id_registro, cambios))
    pausa()


def eliminar_estudiante():
    imprimir_titulo("ELIMINAR ESTUDIANTE")
    id_registro = pedir_entero("ID: ")

    if id_registro is not None and confirmar("¿Confirma la eliminación?"):
        mostrar_resultado(estudiantes.eliminar(id_registro))
    pausa()


def crear_materia():
    imprimir_titulo("CREAR MATERIA")

    datos = {
        "nombre": input("Nombre: "),
        "codigo": input("Código: "),
        "creditos": input("Créditos (1-10): "),
        "cupos": input("Cupos (0-30): "),
    }

    mostrar_resultado(materias.crear(datos))
    pausa()


def listar_materias():
    imprimir_titulo("MATERIAS")
    mostrar_lista(materias.leer(), "No hay materias")
    pausa()


def buscar_materia():
    imprimir_titulo("BUSCAR MATERIA")
    termino = input("Nombre o código: ")
    mostrar_lista(materias.buscar(termino), "Sin coincidencias")
    pausa()


def ver_materia():
    imprimir_titulo("MATERIA POR ID")
    id_registro = pedir_entero("ID: ")

    if id_registro is not None:
        mostrar_detalle(materias.obtener(id_registro))
    pausa()


def actualizar_materia():
    imprimir_titulo("ACTUALIZAR MATERIA")
    id_registro = pedir_entero("ID: ")

    if id_registro is None:
        return pausa()

    objeto = materias.obtener(id_registro)
    if objeto is None:
        imprimir_error("Materia no encontrada")
        return pausa()

    cambios = pedir_cambios(
        objeto, ("nombre", "codigo", "creditos", "cupos")
    )
    mostrar_resultado(materias.actualizar(id_registro, cambios))
    pausa()


def eliminar_materia():
    imprimir_titulo("ELIMINAR MATERIA")
    id_registro = pedir_entero("ID: ")

    if id_registro is not None and confirmar("¿Confirma la eliminación?"):
        mostrar_resultado(materias.eliminar(id_registro))
    pausa()


# ---------------------------------------------------------
# MATRÍCULAS
# ---------------------------------------------------------

def crear_matricula():
    imprimir_titulo("REGISTRAR MATRÍCULA")

    imprimir_info("Estudiantes disponibles:")
    mostrar_lista(estudiantes.leer())

    imprimir_info("Materias disponibles:")
    mostrar_lista(materias.leer())

    estudiante_id = pedir_entero("ID del estudiante: ")
    materia_id = pedir_entero("ID de la materia: ")

    if estudiante_id is None or materia_id is None:
        return pausa()

    periodo = input("Periodo (ej. 2026-1): ").strip()

    datos = {
        "estudiante_id": estudiante_id,
        "materia_id": materia_id,
        "periodo": periodo,
    }

    mostrar_resultado(matriculas.crear(datos))
    pausa()


def listar_matriculas():
    imprimir_titulo("MATRÍCULAS")
    mostrar_lista(matriculas.leer(), "No hay matrículas")
    pausa()


def buscar_matricula():
    imprimir_titulo("BUSCAR MATRÍCULA")
    termino = input("Periodo o fecha: ")
    mostrar_lista(matriculas.buscar(termino), "Sin coincidencias")
    pausa()


def registrar_nota():
    imprimir_titulo("REGISTRAR NOTA")
    id_registro = pedir_entero("ID de la matrícula: ")

    if id_registro is None:
        return pausa()

    nota = input("Nota (0-20): ")
    mostrar_resultado(matriculas.registrar_nota(id_registro, nota))
    pausa()


def ver_certificado():
    imprimir_titulo("CERTIFICADO ACADÉMICO")
    id_registro = pedir_entero("ID de la matrícula: ")

    if id_registro is None:
        return pausa()

    texto = matriculas.certificado(id_registro)

    if texto is None:
        imprimir_error("Matrícula no encontrada")
    else:
        print("\n" + texto)

    pausa()


def retirar_matricula():
    imprimir_titulo("RETIRAR MATRÍCULA")
    id_registro = pedir_entero("ID de la matrícula: ")

    if id_registro is not None and confirmar(
        "¿Confirma el retiro y la devolución del cupo?"
    ):
        mostrar_resultado(matriculas.retirar_matricula(id_registro))
    pausa()


def ver_promedio():
    imprimir_titulo("PROMEDIO DEL ESTUDIANTE")
    id_estudiante = pedir_entero("ID del estudiante: ")

    if id_estudiante is None:
        return pausa()

    if estudiantes.obtener(id_estudiante) is None:
        imprimir_error("Estudiante no encontrado")
    else:
        promedio = matriculas.promedio_de_estudiante(id_estudiante)

        if promedio is None:
            imprimir_info("El estudiante todavía no tiene matrículas")
        else:
            print(f"Promedio: {promedio:.2f}/20")

    pausa()


# ---------------------------------------------------------
# RESUMEN
# ---------------------------------------------------------

def resumen():
    imprimir_titulo("RESUMEN ACADÉMICO")

    # Set: elimina carreras repetidas.
    carreras = sorted({
        e.carrera for e in estudiantes.leer() if e.carrera
    })

    print(f"Estudiantes       : {len(estudiantes.leer())}")
    print(f"Carreras distintas: {', '.join(carreras) or '-'}")
    print(f"Materias          : {len(materias.leer())}")
    print(f"Materias sin cupo : {len(materias.materias_sin_cupo())}")
    print(f"Matrículas        : {len(matriculas.leer())}")
    print(f"Aprobadas         : {len(matriculas.aprobadas())}")

    pausa()


# ---------------------------------------------------------
# MENÚS
# ---------------------------------------------------------

MENU_ESTUDIANTES = {
    "1": ("Crear estudiante", crear_estudiante),
    "2": ("Ver todos", listar_estudiantes),
    "3": ("Buscar", buscar_estudiante),
    "4": ("Ver por ID", ver_estudiante),
    "5": ("Actualizar", actualizar_estudiante),
    "6": ("Eliminar", eliminar_estudiante),
    "0": ("Volver", None),
}

MENU_MATERIAS = {
    "1": ("Crear materia", crear_materia),
    "2": ("Ver todas", listar_materias),
    "3": ("Buscar", buscar_materia),
    "4": ("Ver por ID", ver_materia),
    "5": ("Actualizar", actualizar_materia),
    "6": ("Eliminar", eliminar_materia),
    "0": ("Volver", None),
}

MENU_MATRICULAS = {
    "1": ("Matricular estudiante", crear_matricula),
    "2": ("Ver todas", listar_matriculas),
    "3": ("Buscar por periodo o fecha", buscar_matricula),
    "4": ("Registrar nota", registrar_nota),
    "5": ("Ver certificado", ver_certificado),
    "6": ("Retirar matrícula", retirar_matricula),
    "7": ("Consultar promedio", ver_promedio),
    "0": ("Volver", None),
}


def ejecutar_menu(titulo, opciones):
    while True:
        imprimir_titulo(titulo)

        for tecla, (texto, _) in opciones.items():
            print(f"{tecla}. {texto}")

        tecla = input("\nOpción: ").strip()

        if tecla not in opciones:
            imprimir_error("Opción no válida")
            pausa()
            continue

        funcion = opciones[tecla][1]

        if funcion is None:
            break

        funcion()


def main():
    while True:
        imprimir_titulo("SISTEMA ACADÉMICO")
        print("1. Estudiantes")
        print("2. Materias")
        print("3. Matrículas")
        print("4. Resumen")
        print("0. Salir")

        opcion = input("\nOpción: ").strip()

        if opcion == "1":
            ejecutar_menu("ESTUDIANTES", MENU_ESTUDIANTES)
        elif opcion == "2":
            ejecutar_menu("MATERIAS", MENU_MATERIAS)
        elif opcion == "3":
            ejecutar_menu("MATRÍCULAS", MENU_MATRICULAS)
        elif opcion == "4":
            resumen()
        elif opcion == "0":
            imprimir_info("Hasta luego")
            break
        else:
            imprimir_error("Opción no válida")
            pausa()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nPrograma interrumpido.")
