import flet as ft

DESTINOS_INICIALES = [
    "192.168.1.10:5000",
    "192.168.1.20:5000",
    "192.168.1.30:6000",
    "10.0.0.5:7000",
    "127.0.0.1:9000",
]


def burbuja(autor: str, texto: str, propio: bool) -> ft.Control:
    return ft.Row(
        alignment=ft.MainAxisAlignment.END if propio else ft.MainAxisAlignment.START,
        controls=[
            ft.Container(
                bgcolor=ft.Colors.PRIMARY_CONTAINER
                if propio
                else ft.Colors.SECONDARY_CONTAINER,
                border_radius=14,
                padding=ft.Padding.symmetric(horizontal=14, vertical=8),
                content=ft.Column(
                    spacing=2,
                    tight=True,
                    controls=[
                        ft.Text(
                            autor,
                            size=11,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.ON_PRIMARY_CONTAINER
                            if propio
                            else ft.Colors.ON_SECONDARY_CONTAINER,
                        ),
                        ft.Text(texto, selectable=True),
                    ],
                ),
            )
        ],
    )


def main(page: ft.Page):
    page.title = "Chat"
    page.window.width = 960
    page.window.height = 640

    seleccionado: str | None = None

    titulo_conversacion = ft.Text(
        "Selecciona un destino para comenzar a hablar",
        size=18,
        weight=ft.FontWeight.BOLD,
    )

    mensajes = ft.ListView(expand=True, spacing=6, padding=10, auto_scroll=True)

    campo_mensaje = ft.TextField(
        key="campo-mensaje",
        hint_text="Escribe un mensaje...",
        expand=True,
        filled=True,
        border_radius=24,
    )

    aviso = ft.Text(
        "Selecciona primero un destino en el panel izquierdo",
        color=ft.Colors.ERROR,
        size=12,
        visible=False,
    )

    def recibir_mensaje(remitente: str, texto: str) -> None:
        pass

    def seleccionar(destino: str):
        nonlocal seleccionado
        seleccionado = destino
        titulo_conversacion.value = f"Chat con {destino}"
        lista_destinos.controls = [crear_tile(d) for d in DESTINOS_INICIALES]
        mensajes.controls.clear()
        aviso.visible = False
        page.update()
        campo_mensaje.focus()

    def crear_tile(destino: str) -> ft.Control:
        activo = destino == seleccionado

        def al_hacer_clic(_e):
            seleccionar(destino)

        return ft.ListTile(
            key=f"destino-{destino}",
            leading=ft.Icon(ft.Icons.LAN),
            title=ft.Text(
                destino, weight=ft.FontWeight.BOLD if activo else ft.FontWeight.NORMAL
            ),
            selected=activo,
            on_click=al_hacer_clic,
        )

    def enviar(_e=None):
        texto = (campo_mensaje.value or "").strip()
        if not texto:
            campo_mensaje.focus()
            return
        if seleccionado is None:
            aviso.visible = True
            page.update()
            return
        aviso.visible = False
        mensajes.controls.append(burbuja("Tú", texto, propio=True))
        campo_mensaje.value = ""
        page.update()
        campo_mensaje.focus()

    campo_mensaje.on_submit = enviar

    lista_destinos = ft.ListView(
        expand=True,
        spacing=2,
        controls=[crear_tile(d) for d in DESTINOS_INICIALES],
    )

    panel_destinos = ft.Container(
        width=280,
        padding=12,
        content=ft.Column(
            spacing=8,
            controls=[
                ft.Row(
                    [
                        ft.Icon(ft.Icons.DEVICES),
                        ft.Text("Destinos", weight=ft.FontWeight.BOLD),
                    ]
                ),
                ft.Text("IP:Puerto — selecciona con quién hablar", size=12),
                ft.Divider(height=1),
                lista_destinos,
            ],
        ),
    )

    panel_chat = ft.Container(
        expand=True,
        padding=12,
        content=ft.Column(
            spacing=8,
            controls=[
                titulo_conversacion,
                ft.Divider(height=1),
                mensajes,
                aviso,
                ft.Row(
                    spacing=8,
                    controls=[
                        campo_mensaje,
                        ft.FilledButton(
                            key="enviar",
                            content="Enviar",
                            icon=ft.Icons.SEND,
                            on_click=enviar,
                        ),
                    ],
                ),
            ],
        ),
    )

    page.add(
        ft.Row(
            expand=True,
            spacing=0,
            vertical_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[panel_destinos, ft.VerticalDivider(width=1), panel_chat],
        )
    )


if __name__ == "__main__":
    ft.run(main)
