import socket
import threading
import json

from config import SERVER_HOST, SERVER_PORT


# ==================================
# VARIABLES GLOBALES
# ==================================

cliente_nombre = ""
puerto_escucha = 0

conexion_servidor = None
lector_servidor = None

lock_servidor = threading.Lock()

servidor_listo = threading.Event()


# ==================================
# UTILIDADES JSON
# ==================================

def enviar_json_socket(sock, datos):
    mensaje = json.dumps(datos) + "\n"
    sock.sendall(mensaje.encode("utf-8"))


def recibir_json_socket():
    """
    Lee una respuesta utilizando SIEMPRE
    el mismo lector asociado al servidor.
    """

    linea = lector_servidor.readline()

    if not linea:
        return None

    return json.loads(linea)


# ==================================
# COMUNICACIÓN CON SERVIDOR
# ==================================

def conectar_servidor():

    global conexion_servidor
    global lector_servidor

    conexion_servidor = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    conexion_servidor.connect(
        (SERVER_HOST, SERVER_PORT)
    )

    # Creamos UN SOLO lector permanente
    lector_servidor = conexion_servidor.makefile(
        "r",
        encoding="utf-8"
    )


def registrar():

    with lock_servidor:

        enviar_json_socket(
            conexion_servidor,
            {
                "type": "register",
                "cliente": cliente_nombre,
                "port": puerto_escucha
            }
        )

        respuesta = recibir_json_socket()

    if respuesta is None:
        print("El servidor cerró la conexión.")
        return

    if respuesta["type"] == "register_ok":

        print("\nRegistro exitoso.")
        print(
            f"{respuesta['cliente']} -> "
            f"{respuesta['ip']}:{respuesta['port']}\n"
        )

    else:

        print("No fue posible registrarse.")


def listar_clientes():

    with lock_servidor:

        enviar_json_socket(
            conexion_servidor,
            {
                "type": "list"
            }
        )

        respuesta = recibir_json_socket()

    if respuesta is None:
        print("\nNo hubo respuesta del servidor.\n")
        return

    if respuesta["type"] == "list_ok":

        print("\nCLIENTES REGISTRADOS")

        for c in respuesta["clients"]:

            print(
                f"- {c['cliente']} "
                f"({c['ip']}:{c['port']})"
            )

        print()


def buscar_cliente(nombre):

    with lock_servidor:

        enviar_json_socket(
            conexion_servidor,
            {
                "type": "lookup",
                "cliente": nombre
            }
        )

        respuesta = recibir_json_socket()

    if respuesta is None:
        print("\nNo hubo respuesta del servidor.\n")
        return None

    if respuesta["type"] == "lookup_ok":

        return (
            respuesta["ip"],
            respuesta["port"]
        )

    print("\nCliente no encontrado.\n")

    return None


def desregistrar():

    try:

        with lock_servidor:

            enviar_json_socket(
                conexion_servidor,
                {
                    "type": "unregister",
                    "cliente": cliente_nombre
                }
            )

            recibir_json_socket()

    except Exception:
        pass


# ==================================
# RECEPTOR DE MENSAJES
# ==================================

def manejar_chat(conn, addr):

    file = conn.makefile(
        "r",
        encoding="utf-8"
    )

    try:

        while True:

            linea = file.readline()

            if not linea:
                break

            datos = json.loads(linea)

            if datos["type"] == "chat":

                remitente = datos["cliente"]
                mensaje = datos["message"]

                print("\n" + "=" * 45)
                print(f"Mensaje de {remitente}")
                print(mensaje)
                print("=" * 45)
                print(">> ", end="", flush=True)

    except Exception as e:

        print(f"\nError recibiendo mensaje: {e}")

    finally:

        conn.close()


def escuchar_mensajes():

    servidor_cliente = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    servidor_cliente.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    servidor_cliente.bind(
        ("0.0.0.0", puerto_escucha)
    )

    servidor_cliente.listen()

    print(
        f"Escuchando mensajes en puerto {puerto_escucha}..."
    )

    # Avisamos que ya está listo
    servidor_listo.set()

    while True:

        conn, addr = servidor_cliente.accept()

        hilo = threading.Thread(
            target=manejar_chat,
            args=(conn, addr),
            daemon=True
        )

        hilo.start()


# ==================================
# ENVÍO DE MENSAJES
# ==================================

def enviar_mensaje(destinatario, mensaje):

    destino = buscar_cliente(destinatario)

    if destino is None:
        return

    ip, puerto = destino

    try:

        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        sock.connect(
            (ip, puerto)
        )

        enviar_json_socket(
            sock,
            {
                "type": "chat",
                "cliente": cliente_nombre,
                "message": mensaje
            }
        )

        sock.close()

        print("\nMensaje enviado.\n")

    except Exception as e:

        print(
            f"\nNo fue posible enviar el mensaje: {e}\n"
        )


# ==================================
# MENÚ
# ==================================

def mostrar_menu():

    print("=" * 45)
    print("CHAT CON SOCKETS")
    print("=" * 45)
    print("1. Listar clientes")
    print("2. Enviar mensaje")
    print("3. Salir")
    print("=" * 45)


# ==================================
# PROGRAMA PRINCIPAL
# ==================================

def iniciar_cliente():

    global cliente_nombre
    global puerto_escucha

    print("\nBienvenido al chat\n")

    cliente_nombre = input(
        "Ingrese su identificador: "
    ).strip()

    puerto_escucha = int(
        input(
            "Ingrese su puerto de escucha: "
        )
    )

    # --------------------------
    # Hilo receptor
    # --------------------------

    hilo_escucha = threading.Thread(
        target=escuchar_mensajes,
        daemon=True
    )

    hilo_escucha.start()

    # Esperamos hasta que realmente
    # el puerto esté escuchando
    servidor_listo.wait()

    # --------------------------
    # Conexión con servidor
    # --------------------------

    conectar_servidor()

    registrar()

    # --------------------------
    # Menú
    # --------------------------

    while True:

        mostrar_menu()

        opcion = input(
            "Seleccione una opción: "
        )

        if opcion == "1":

            listar_clientes()

        elif opcion == "2":

            destinatario = input(
                "Cliente destinatario: "
            ).strip()

            mensaje = input(
                "Mensaje: "
            )

            enviar_mensaje(
                destinatario,
                mensaje
            )

        elif opcion == "3":

            desregistrar()

            conexion_servidor.close()

            print(
                "\nCliente cerrado correctamente."
            )

            break

        else:

            print("\nOpción inválida.\n")


if __name__ == "__main__":
    iniciar_cliente()