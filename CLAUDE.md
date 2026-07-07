# Proyecto Colibrí — sitio web

Sitio web del **Proyecto Colibrí**, un grupo de investigación (Universidad del Cauca / Pontificia Universidad Javeriana / Queen's University Belfast, entre otros) que estudia las decisiones médicas, de pacientes y de familiares/cuidadores en el final de la vida, con foco en enfermedades crónicas y oncológicas en Colombia.

Sitio en producción: https://proyectocolibri.github.io/ (se publica desde este mismo repo vía GitHub Pages).

Este repo se descargó originalmente como zip desde GitHub (`proyectocolibri.github.io-main`), sin historial git. Se inicializó un repositorio git local (`git init`) con un commit de checkpoint del estado tal cual se descargó, seguido de un commit de limpieza (ver sección "Historial y GitHub" más abajo) — **todavía no tiene remoto configurado** (`git remote -v` vacío).

## Stack técnico

- **Quarto** (`type: website`) — el sitio se genera a partir de archivos `.qmd`, no se edita el HTML de salida directamente.
- Salida renderizada al mismo directorio raíz (`output-dir: .`), por eso conviven `index.qmd`/`index.html`, `search.json`, `sitemap.xml`, `site_libs/`, etc. Todo lo que termine en `.html`, `site_libs/`, `search.json`, `sitemap.xml` es **generado** — no editar a mano, editar el `.qmd` fuente y re-renderizar.
- Tema HTML: `cosmo` + `custom.scss` (paleta de marca del proyecto, ver sección "Convenciones").
- Hay un `webcolibri.Rproj`, es decir se asume entorno RStudio/R, pero el build real lo hace Quarto. `scripts/` solo tiene un script Python en uso (`pre_fetch_scholar_papers.py`, ver más abajo); `requirements.txt` está recortado a sus dependencias reales (`requests`, `beautifulsoup4`).
- **Quarto 1.9.38, R 4.6.1 y Python 3.12 ya están instalados** (vía winget: `Posit.Quarto`, `RProject.R`, `Python.Python.3.12`). R y Python se agregaron manualmente al PATH de usuario (`C:\Program Files\R\R-4.6.1\bin`, `...\Python\Python312` y `...\Python312\Scripts`) porque sus instaladores no siempre lo hacen. Dependencias Python instaladas: `requests`, `beautifulsoup4` (ver `requirements.txt`).
  - `quarto check` pasa OK para pandoc/sass/deno/typst y para R. `knitr`/`rmarkdown` no están instalados en R (no hacen falta: los `.qmd` de este sitio no tienen chunks de R).
  - Comandos útiles: `quarto preview` (servidor local con recarga en vivo, mejor forma de validar cambios de diseño) y `quarto render` (build completo a `_site`/raíz según `output-dir`). **Ojo:** `quarto preview <carpeta-proyecto>` también dispara los `pre-render` scripts al arrancar (no solo `quarto render`).

## Instalación (para nuevas máquinas)

Si se clona el repo en otra máquina Windows, instalar con:
```
winget install --id Posit.Quarto -e --source winget
winget install --id RProject.R -e --source winget
winget install --id Python.Python.3.12 -e --source winget
python -m pip install requests beautifulsoup4
```
Luego agregar `C:\Program Files\R\R-<version>\bin` (y, si el instalador de Python no lo hizo, su carpeta + `Scripts`) al PATH de usuario, y abrir una terminal nueva para que tome el PATH actualizado.

## Estructura

```
_quarto.yml         # config del sitio, navbar, tema
index.qmd           # Home (leyenda del colibrí + presentación del proyecto)
people/index.qmd     # "Nuestro equipo" — bios del equipo, bloques de columnas con foto+texto
papers/index.qmd     # "Publicaciones" — sección "Artículos publicados" AUTO-GENERADA desde Google Scholar (ver abajo); "Posters y presentaciones" y "Tesis" siguen siendo manuales
teaching/index.qmd   # "Enlaces de interes" — lista de recursos externos
talks/               # Presentaciones (listing de Quarto)
media/               # Apariciones en medios (listing de Quarto)
disclaimer/index.qmd # Aviso legal
img/, img/team/      # imágenes, fotos del equipo
styles.css           # actualmente vacío, solo comentario placeholder
scripts/             # scripts Python de pre-render (solo pre_fetch_scholar_papers.py; ver sección de Scholar)
_extensions/         # extensiones Quarto: fontawesome, academicons, social-embeds
```

- Navbar (en `_quarto.yml`): Home, Nuestro equipo, Publicaciones, Videos & Podcast, Enlaces de interes, Presentaciones. Incluye `logo: img/colibri-navbar-logo.png`.
- **Logo de la navbar**: viene de una ilustración de colibrí que envió el usuario (`img/hummingbird-bird.jpg`, fondo gris plano). Se procesó con [`scripts/process_logo.py`](scripts/process_logo.py) (Pillow/numpy) para quitar el fondo (umbral de distancia de color respecto a las esquinas + boost de saturación/contraste), generando `img/colibri-logo.png` (ilustración completa, transparente). Como a 38px la ilustración completa se ve como un borrón de color (demasiado detalle para ese tamaño), se recortó un cuadrado enfocado solo en cabeza+pico → `img/colibri-navbar-logo.png`, que es el que realmente usa la navbar. Si se quiere cambiar el logo por otra imagen, correr de nuevo `process_logo.py` (ajustando `SRC`) y repetir el recorte cuadrado a la cabeza antes de usarlo en `_quarto.yml`.
- `img/colibri-logo.jpg` (foto real) sigue siendo la imagen del bloque "about" en el home (`index.qmd`) — es un uso distinto del logo de la navbar, no se tocó.
- `videos-podcast/index.qmd` — página nueva, clon del contenido de https://sites.google.com/view/p-colibri/podcast-videos (2 episodios de podcast vía Spreaker + 10 videos de YouTube agrupados en 3 secciones). Usa el shortcode nativo `{{< video >}}` de Quarto para los videos y el widget embed de Spreaker (bloques `{=html}`) para el podcast. Los videos se agrupan visualmente con las clases `.video-grid`/`.video-card` (definidas en `custom.scss`), no son un listing de Quarto.
- `talks/` y `media/` son *listings* de Quarto (`contents: .`, autodescubren subcarpetas con un `index.qmd` cada una) — hoy están **vacíos** (solo un mensaje "Próximamente..."), ver "Historial y GitHub" sobre por qué. Para agregar una charla o aparición en medios: crear una subcarpeta nueva (ej. `talks/mi-charla/index.qmd`) con su propio YAML de listing item (`title`, `date`, `categories`, imagen), y Quarto la recoge sola al re-renderizar.
- `media/index.qmd` existe pero **no está enlazado en la navbar** — solo es accesible por URL directa. No se tocó porque no se pidió agregarlo, pero vale la pena preguntarle al usuario si es intencional.

## Convenciones de contenido

- Todo el contenido visible es en **español** (las citas de `papers/` quedan en el idioma original del artículo, eso es normal en Vancouver).
- Los perfiles del equipo en `people/index.qmd` siguen un patrón fijo: bloque `::: columns` con foto (30%) + nombre/título, contacto/ORCID opcional (70%), separados por `---`. **No lleva `number-sections`** — se quitó del YAML porque numeraba automáticamente cada nombre (ej. "1.1 Esther de Vries"); si se vuelve a agregar `number-sections: true` a esta página, ese problema reaparece.
- Las publicaciones en `papers/index.qmd` están agrupadas por año (`# 2024`, `# 2023`, ...) en orden descendente.
- El tono es institucional/académico, propio de un grupo de investigación en salud — evitar informalidad excesiva al redactar contenido nuevo.

## Sincronización de publicaciones con Google Scholar

La sección "Artículos publicados" de `papers/index.qmd` (entre los marcadores `<!-- scholar:auto:start -->` y `<!-- scholar:auto:end -->`) se genera con [`scripts/pre_fetch_scholar_papers.py`](scripts/pre_fetch_scholar_papers.py), que:

1. Scrapea el [perfil público de Google Scholar del grupo](https://scholar.google.com/citations?hl=es&user=m67uDzwAAAAJ&view_op=list_works&sortby=pubdate) (no hay API oficial de Scholar).
2. Por cada publicación, visita también su página de detalle para sacar autores completos, revista, volumen/número/páginas y el enlace externo (de ahí intenta extraer el DOI con una regex; si no lo encuentra, enlaza directo a la página de la publicación).
3. Formatea cada entrada en **Vancouver** (`Apellido AB, Apellido CD, et al. Título. _Revista_. Año;Vol(Núm):Páginas. doi: [10.xxxx](https://doi.org/10.xxxx){target="_blank"}`) y reemplaza el contenido entre los marcadores — **no editar a mano esa sección**, se sobrescribe en la siguiente sincronización.

**Cómo ejecutarlo:** está deliberadamente **desactivado** en `_quarto.yml` (`#pre-render:` con la línea del script comentada) — decisión tomada explícitamente con el usuario porque Google Scholar bloquea temporalmente (CAPTCHA) las IPs que hacen demasiadas solicitudes automatizadas en poco tiempo (~23 publicaciones × 2 requests c/u ya lo disparó una vez durante pruebas). Para refrescar el listado manualmente:

```
set SCHOLAR_SYNC_FORCE=1
python scripts/pre_fetch_scholar_papers.py
```

Ejecutarlo con moderación (no en cada preview/build). El script falla de forma segura: si Scholar bloquea la solicitud o no devuelve nada, dejar el contenido existente intacto en vez de borrarlo. Limitaciones conocidas: el nombre de la revista no siempre se resuelve (formato NLM abreviado no está disponible sin una base de datos de abreviaturas), y el DOI solo se detecta si aparece embebido en la URL externa que da Scholar (algunos editores, ej. `revistas.javeriana.edu.co`, no lo incluyen — en esos casos el enlace cae a "Ver publicación" en vez de "doi:").

## Pendientes / cosas detectadas que probablemente valga la pena revisar

- ~~`custom.scss` no existía~~ — ya se creó con la paleta de marca (verde `#0E7C7B`, magenta `#D81B72`, ámbar `#F2A93B`) y reglas para navbar, footer, encabezados, botones, `hr` y fotos de equipo circulares. Usa la fuente "Poppins" de Google Fonts (dependencia de red externa, cargada vía `@import url(...)` en `scss:rules`).
- `people/index.qmd` y otras páginas de sección declaran `css: styles.css` en el YAML con ruta relativa, por lo que el navegador pide `/people/styles.css` (404) en vez de `/styles.css`. Como `styles.css` está vacío no afecta nada hoy, pero si se le agrega contenido habría que corregir la ruta (usar `/styles.css` o `../styles.css`).
- Importante para futuros ajustes de CSS: **Quarto/bslib neutraliza el CSS flex de Pandoc para `::: columns :::`** — compila `.columns{display:initial}` y `.column{display:inline-block; width:50%}`, ignorando el `display:flex` que Pandoc pone en un `<style>` inline. El layout de dos columnas (foto+texto en `people/index.qmd`) en realidad funciona por `inline-block` + los `width:30%/70%` que Pandoc fija como `style=` inline en cada `.column`, no por flexbox. Por eso el fix de responsive en `custom.scss` tuvo que forzar `.column { display: block !important; width: 100% !important; }` en `@media (max-width: 767px)` — sin el `!important` el estilo inline de Pandoc gana y las columnas no colapsan en móvil.
- ~~`disclaimer/index.qmd` tenía texto genérico de plantilla~~ — reescrito con contenido propio: menciona que el Proyecto Colibrí es una iniciativa conjunta de GRIAN (Universidad del Cauca) y el Grupo de Investigación en Epidemiología y Bioestadística (Pontificia Universidad Javeriana), y aclara que el contenido es informativo, no consejo médico.
- `styles.css` está vacío; si el estilo custom se maneja por `custom.scss` (Sass), aclarar cuál de los dos es el mecanismo real antes de agregar CSS en el que no corresponde.
- ~~El link "Presentaciones" apuntaba a `talks and presentations` (ruta inexistente, 404)~~ — corregido a `href: talks` en `_quarto.yml`.
- Las páginas de listado (`talks/`, `media/`) ahora tienen tarjetas con miniatura redondeada+sombra, título en Poppins, fecha en magenta y categorías como píldoras (clases `.quarto-post`, `.listing-title`, `.listing-category`, `.listing-date` en `custom.scss`) — mismo tratamiento visual que el resto del sitio.
- Nota sobre el tooling de preview: el navegador embebido de `mcp__Claude_Preview` a veces se niega a navegar a `/papers/` específicamente al hacer clic programático (`net::ERR_ABORTED`), aunque la página responde 200 por HTTP y comparte el mismo CSS global ya verificado en otras páginas. Es una rareza de la herramienta de preview, no del sitio — si hace falta verificar `papers/` visualmente, mejor abrirlo a mano en un navegador normal.

## Historial y GitHub

El repo se descargó como zip de una plantilla Quarto personal (de Chris von Csefalvay) que **nunca se terminó de limpiar** al adaptarla a Proyecto Colibrí. Se eliminó todo el contenido de ejemplo ajeno al proyecto y los residuos técnicos, en dos commits:

1. `Checkpoint: estado inicial descargado antes de limpieza` — snapshot completo tal cual llegó el zip (por si hace falta recuperar algo).
2. Commit de limpieza — elimina:
   - `talks/prometheus-unbound/`, `media/euronews-covid/`, `media/fr-disinfectants/`, `media/tech-for-good/` — charla y apariciones de prensa del autor de la plantilla, no del Proyecto Colibrí. Esto dejó los listings de `talks/` y `media/` vacíos (se les agregó un texto "Próximamente...").
   - `papers/bibliography.bib` — bibliografía personal del autor de la plantilla (no se usaba: las publicaciones ahora vienen de Google Scholar, ver arriba).
   - `scripts/pre_create_papers_file.py`, `pre_check_skierg_records.py`, `pre_doi_from_rogue_scholar.py`, `pre_canonicalise_tags.py` — scripts de pre-render de la plantilla, nunca activados en este proyecto.
   - `_site/` — build duplicado y desactualizado (el build real vive en la raíz por `output-dir: .`).
   - `.DS_Store` (raíz, `img/`, `img/team/`), `img/team/esther_de_vries.jpeg` (foto huérfana, no referenciada — la que se usa es `esther.png`), `listings.json`/`talks/index.xml`/`media/index.xml` (metadatos de feed, se regeneran solos con `quarto render`).
   - `requirements.txt` recortado a `beautifulsoup4`+`requests` (las demás — numpy, scipy, pandas, etc. — no las usa ningún script real de este proyecto).
   - `.gitignore` ampliado con `.DS_Store`, `_site/`, `__pycache__/`, `*.pyc`.

**Para publicar en GitHub:** el `site-url` en `_quarto.yml` y el sitio en producción (https://proyectocolibri.github.io/) indican que el repo remoto debe llamarse exactamente `proyectocolibri.github.io` bajo la organización/usuario `proyectocolibri` en GitHub — los repos `<usuario-u-org>.github.io` se publican automáticamente por GitHub Pages sirviendo la raíz del branch por defecto, sin necesidad de Actions ni de habilitar Pages manualmente (aunque vale la pena confirmarlo en Settings → Pages tras el primer push). Pasos:

```
git remote add origin https://github.com/proyectocolibri/proyectocolibri.github.io.git
git push -u origin master   # la rama local se llama "master" (default de este git init)
```

Como no hay GitHub Actions configurado, **hay que correr `quarto render` (full) y comitear el HTML resultante antes de cada push** — Pages sirve los archivos tal cual están en el repo, no renderiza Quarto por ti.

## Objetivo actual

Mejorar el sitio en **diseño** y **contenidos** manteniendo la estructura Quarto existente. Con Quarto ya instalado, usar `quarto preview` para validar visualmente cada cambio antes de darlo por terminado.
