# Publicar Olvido para jugar en el navegador

Este proyecto usa Python + pygame-ce. GitHub Pages no ejecuta Python por sí mismo; por eso la acción de GitHub Actions usa **Pygbag** para empaquetar el juego para WebAssembly y publica el contenido estático generado en `build/web/`.

## Pasos

1. Sube el contenido de esta carpeta (`olvido_py`) a la rama `main` de un repositorio de GitHub.
2. Abre **Settings → Pages** y, en **Build and deployment**, selecciona **GitHub Actions** como fuente.
3. Entra en la pestaña **Actions** y espera a que termine el flujo **Build and publish Olvido for web**.
4. Al completarse, abre la URL que aparece en **Settings → Pages** o en el resumen del despliegue.

Cada nuevo `push` a `main` vuelve a construir y publicar la versión web.

## Importante

- La primera carga puede tardar porque el navegador descarga el runtime WebAssembly de Pygbag.
- La versión web debe probarse en escritorio y móvil. Algunas funciones del sistema de archivos y audio pueden comportarse distinto en navegador.
- El guardado actual usa un archivo JSON local. **No se garantiza que el progreso persista después de cerrar la pestaña**; el guardado en navegador necesita una prueba y posiblemente una adaptación a almacenamiento web.
- La acción automatiza la compilación, pero un despliegue verde no sustituye una prueba de juego completa.
- Si la compilación falla, abre el trabajo fallido en **Actions** y revisa el paso `Build Pygbag web version`.
