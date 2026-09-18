import flet.testing as ftt


async def test_enviar_mensaje(flet_app: ftt.FletTestApp):
    """Selecciona un destino, envía un mensaje y verifica que aparezca en el chat."""
    tester = flet_app.tester

    await tester.pump_and_settle()

    assert (await tester.find_by_text("Enviar")).count == 1
    assert (await tester.find_by_key("destino-127.0.0.1:9000")).count == 1

    await tester.tap(await tester.find_by_key("destino-127.0.0.1:9000"))
    await tester.pump_and_settle()

    await tester.enter_text(
        await tester.find_by_key("campo-mensaje"), "hola desde la prueba"
    )
    await tester.pump_and_settle()

    await tester.tap(await tester.find_by_key("enviar"))
    await tester.pump_and_settle()

    assert (await tester.find_by_text("hola desde la prueba")).count == 1
