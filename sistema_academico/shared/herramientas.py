import os

RESPUESTAS_SI = ("si", "sí", "s", "yes", "y")


def limpiar_pantalla():
    os.system("cls" if os.name == "nt" else "clear")


def imprimir_color(texto, color="BLANCO"):
    colores = {
        "ROJO": "\033[91m",
        "VERDE": "\033[92m",
        "AZUL": "\033[94m",
        "AMARILLO": "\033[93m",
        "CYAN": "\033[96m",
        "BLANCO": "\033[97m",
    }
    codigo = colores.get(color, colores["BLANCO"])
    print(f"{codigo}{texto}\033[0m")


def imprimir_titulo(texto):
    limpiar_pantalla()
    imprimir_color("=" * 55, "AZUL")
    imprimir_color(texto.center(55), "AZUL")
    imprimir_color("=" * 55, "AZUL")
    print()


def imprimir_exito(mensaje):
    imprimir_color(f"✓ {mensaje}", "VERDE")


def imprimir_error(mensaje):
    imprimir_color(f"✗ {mensaje}", "ROJO")


def imprimir_info(mensaje):
    imprimir_color(f"ℹ {mensaje}", "CYAN")


def confirmar(pregunta):
    respuesta = input(f"{pregunta} (si/no): ").strip().lower()
    return respuesta in RESPUESTAS_SI


def es_email_valido(texto):
    texto = texto.strip()

    if texto.count("@") != 1:
        return False

    usuario, dominio = texto.split("@")

    return (
        bool(usuario)
        and "." in dominio
        and not dominio.startswith(".")
        and not dominio.endswith(".")
        and " " not in texto
    )
