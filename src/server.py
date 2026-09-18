
import socket
import threading
import json

from config import SERVER_HOST, SERVER_PORT


# =========================
# DIRECTORIO DE CLIENTES
# =========================

directorio = {}

lock_directorio = threading.Lock()


# =========================
# UTILIDADES JSON
# =========================

def enviar_json(conn, datos):
    mensaje = json.dumps(datos) + "\n"
    conn.sendall(mensaje.encode("utf-8"))


def recibir_json(file):
    linea = file.readline()

    if not linea:
        return None

    return json.loads(linea)


# =========================
# MANEJO DE CADA CLIENTE
# =========================

def manejar_cliente(conn, addr):

    print(f"[NUEVA CONEXIÓN] {addr}")

    file = conn.makefile("r", encoding="utf-8")

    try:
        while True:

            datos = recibir_json(file)

            if datos is None:
                break

            tipo = datos.get("type")

            # =========================
            # REGISTER
            # =========================

            if tipo == "register":

                cliente = datos.get("cliente")
                puerto = datos.get("port")

                if not cliente or not puerto:
                    enviar_json(
                        conn,
                        {
                            "type": "error",
                            "message": "invalid_register"
                        }
                    )
                    continue

                ip = addr[0]

                with lock_directorio:
                    directorio[cliente] = {
                        "ip": ip,
                        "port": puerto
                    }

                print(
                    f"[REGISTRO] {cliente} -> {ip}:{puerto}"
                )

                enviar_json(
                    conn,
                    {
                        "type": "register_ok",
                        "cliente": cliente,
                        "ip": ip,
                        "port": puerto
                    }
                )

            # =========================
            # LOOKUP
            # =========================

            elif tipo == "lookup":

                cliente = datos.get("cliente")

                with lock_directorio:
                    info = directorio.get(cliente)

                if info is None:

                    enviar_json(
                        conn,
                        {
                            "type": "error",
                            "message": "client_not_found"
                        }
                    )

                else:

                    enviar_json(
                        conn,
                        {
                            "type": "lookup_ok",
                            "cliente": cliente,
                            "ip": info["ip"],
                            "port": info["port"]
                        }
                    )

            # =========================
            # LIST
            # =========================

            elif tipo == "list":

                with lock_directorio:

                    clientes = []

                    for cliente, info in directorio.items():

                        clientes.append(
                            {
                                "cliente": cliente,
                                "ip": info["ip"],
                                "port": info["port"]
                            }
                        )

                enviar_json(
                    conn,
                    {
                        "type": "list_ok",
                        "clients": clientes
                    }
                )

            # =========================
            # UNREGISTER
            # =========================

            elif tipo == "unregister":

                cliente = datos.get("cliente")

                with lock_directorio:

                    if cliente in directorio:
                        del directorio[cliente]

                print(f"[SALIDA] {cliente}")

                enviar_json(
                    conn,
                    {
                        "type": "unregister_ok"
                    }
                )

            else:

                enviar_json(
                    conn,
                    {
                        "type": "error",
                        "message": "unknown_command"
                    }
                )

    except Exception as e:

        print(f"[ERROR] {addr}: {e}")

    finally:

        conn.close()

        print(f"[CONEXIÓN CERRADA] {addr}")


# =========================
# SERVIDOR PRINCIPAL
# =========================

def iniciar_servidor():

    servidor = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    servidor.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    servidor.bind(
        (SERVER_HOST, SERVER_PORT)
    )

    servidor.listen()

    print("=" * 45)
    print(" SERVIDOR DIRECTORIO INICIADO")
    print("=" * 45)
    print(f"IP: {SERVER_HOST}")
    print(f"Puerto: {SERVER_PORT}")
    print("Esperando clientes...\n")

    while True:

        conn, addr = servidor.accept()

        hilo = threading.Thread(
            target=manejar_cliente,
            args=(conn, addr),
            daemon=True
        )

        hilo.start()


if __name__ == "__main__":
    iniciar_servidor()