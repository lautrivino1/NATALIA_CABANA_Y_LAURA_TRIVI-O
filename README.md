# Aplicación de chat

## Crear ambiente virtual

```bash
python -m venv mi_virtualenv
```

## Instalar librerías


### Interfaz gráfica

```bash
pip install 'flet[all]'

```
## Ejecutar la aplicación

Ejecutar como aplicación de escritorio:

```bash
 flet run
```

Ejecutar como aplicación web:

```bash
flet run --web
```

Para más detalles sobre cómo ejecutar la aplicación, consulta la [Guía de Inicio](https://flet.dev/docs/).

## Construir la aplicación

### Android

```bash
flet build apk -v
```

Para más detalles sobre cómo construir y firmar `.apk` o `.aab`, consulta la [Guía de Empaquetado para Android](https://flet.dev/docs/publish/android/).

### iOS

```bash
flet build ipa -v
```

Para más detalles sobre cómo construir y firmar `.ipa`, consulta la [Guía de Empaquetado para iOS](https://flet.dev/docs/publish/ios/).

### macOS

```bash
flet build macos -v
```

Para más detalles sobre cómo construir el paquete para macOS, consulta la [Guía de Empaquetado para macOS](https://flet.dev/docs/publish/macos/).

### Linux

```bash
flet build linux -v
```

Para más detalles sobre cómo construir el paquete para Linux, consulta la [Guía de Empaquetado para Linux](https://flet.dev/docs/publish/linux/).

### Windows

```bash
flet build windows -v
```

Para más detalles sobre cómo construir el paquete para Windows, consulta la [Guía de Empaquetado para Windows](https://flet.dev/docs/publish/windows/).

### Web

```bash
flet build web -v
```

Para más detalles sobre cómo construir la aplicación web, consulta la [Guía de Empaquetado para Web](https://flet.dev/docs/publish/web/).

