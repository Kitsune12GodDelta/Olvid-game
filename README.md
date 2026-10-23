# Olvido

**Olvido** es una novela visual interactiva en Python y Pygame sobre recuerdos, vínculos y seguir adelante. Este repositorio contiene el código del juego, recursos gráficos y herramientas de validación.

> Estado: proyecto en desarrollo. Las comprobaciones estáticas y de recursos pasan; todavía se necesita una prueba manual completa del juego en un equipo con Pygame.

## Características

- Ocho escenas narrativas, incluidos seis recuerdos y el epílogo.
- Exploración mediante clics, objetos interactivos y fragmentos coleccionables.
- Minijuegos narrativos de memoria, ritmo y dibujo.
- Habitación central con objetos y recuerdos desbloqueados.
- Guardado local de progreso.
- Nombres de personajes, idioma español/inglés, volumen y controles configurables.
- Controles de teclado y opciones de interacción en pantalla para dispositivos táctiles.
- Recursos de personajes en hojas PNG transparentes y retratos separados.

## Requisitos

- Python 3.10 o posterior recomendado.
- `pygame-ce` para ejecutar el juego.
- `Pillow` para las herramientas de auditoría de imágenes.

## Ejecutar en Windows, Linux o macOS

Desde la carpeta raíz del repositorio:

```bash
python -m venv .venv
```

Activar el entorno virtual:

- Windows PowerShell: `\.venv\Scripts\Activate.ps1`
- Linux/macOS: `source .venv/bin/activate`

Instalar dependencias e iniciar:

```bash
python -m pip install -r requirements.txt
python main.py
```

## Controles

- Clic: explorar, interactuar y avanzar diálogos.
- Flechas o A/D: moverse en escenas que permiten caminar.
- Los controles táctiles pueden configurarse desde el menú del juego.

## Validar antes de publicar cambios

Estas herramientas no necesitan iniciar el motor gráfico, pero sí Pillow:

```bash
python _fuera_del_juego/tools/validar_proyecto.py   # ahora fuera de la carpeta del juego
python _fuera_del_juego/tools/auditar_sprites.py
python -m compileall -q .
```

La validación comprueba sintaxis, dimensiones y transparencia de las hojas de personajes y algunas referencias de interacciones. **No reemplaza probar el juego** y no puede confirmar por sí sola que cada fotograma esté bien dibujado.

## Jugar en el navegador con GitHub Pages (experimental)

El repositorio incluye `.github/workflows/deploy-pages.yml`. Cuando subas el proyecto a la rama `main`, GitHub Actions construirá la versión web con Pygbag y la publicará en GitHub Pages.

1. En GitHub, abre **Settings → Pages** y selecciona **GitHub Actions** como fuente.
2. Abre la pestaña **Actions** y espera a que termine `Build and publish Olvido for web`.
3. Abre la URL de Pages que aparece en el resumen del despliegue.

Consulta [`WEB_GITHUB_PAGES.md`](WEB_GITHUB_PAGES.md) para ver los pasos y las limitaciones conocidas.

Para probar localmente, instala Pygbag y ejecuta desde esta carpeta:

```bash
python -m pip install pygbag
python -m pygbag .
```

La primera carga en el navegador puede tardar mientras se descarga el runtime WebAssembly. La publicación automatizada todavía debe validarse con una prueba real del juego en escritorio y móvil. El guardado actual escribe un archivo JSON y aún no garantiza persistencia después de cerrar la pestaña.

## Estructura

```text
olvido_py/
├── main.py
├── config.py
├── menus.py
├── controls.py
├── room.py
├── commute.py
├── minigames.py
├── save_system.py
├── scenes.py
├── epilogue.py
├── engine/                 motor, movimiento, dibujo, audio e interfaz
├── assets/
│   ├── backgrounds/        fondos del juego
│   ├── characters/         sprites y retratos
│   └── concept_art/        referencias visuales de desarrollo
(tools/ se movió a ../_fuera_del_juego/tools/)
└── requirements.txt
```

## Recursos y créditos

El arte, los retratos y los fondos se encuentran en `assets/`. Algunas imágenes dentro de `assets/concept_art/` son referencias de diseño y no necesariamente recursos usados directamente durante el juego. Antes de distribuir públicamente el proyecto, confirma que tienes permiso para publicar todos los recursos gráficos, sonidos y textos incluidos.

## Publicar en GitHub

1. Crea un repositorio nuevo en GitHub.
2. Descomprime este proyecto y abre una terminal en su carpeta raíz.
3. Ejecuta:

```bash
git init
git add .
git commit -m "Preparar proyecto Olvido para GitHub"
git branch -M main
git remote add origin https://github.com/TU-USUARIO/TU-REPOSITORIO.git
git push -u origin main
```

Sustituye la URL de ejemplo por la URL real de tu repositorio. No subas archivos de guardado personal, entornos virtuales ni credenciales.

## Estado de desarrollo

El proyecto sigue en desarrollo. Los sprites tienen dimensiones compatibles con el cargador actual, pero su acabado visual y las animaciones deben revisarse en ejecución. La prueba de Pygame depende del entorno local del desarrollador.
