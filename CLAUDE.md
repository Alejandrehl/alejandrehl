# CLAUDE.md — repo `alejandrehl/alejandrehl`

Este repo es **el README del perfil de GitHub** de Alejandro (`github.com/Alejandrehl`).
GitHub renderiza `README.md` en la portada del perfil. Es marca, no producto: el único "build"
es el workflow del snake. Editar con rigor, commitear directo a `main`, push → se ve en vivo.

## Qué es (y qué NO)

- **Artefactos:** `README.md` (la tarjeta de perfil) · `assets/claude-code.svg` (animación
  hecha a mano: terminal de Claude Code que "escribe" vía SMIL — se anima en GitHub sin servicios
  externos; NO borrar ni convertir a imagen estática) · `.github/workflows/snake.yml` (genera el snake).
- **Idioma:** inglés (audiencia global de GitHub).
- **No** es fuente de verdad de ningún dominio. La data de negocio, salud y personal vive
  en el vault Obsidian; la orquestación multidominio vive en `kainext-hq`.

## Elementos vivos del README (no romper)

- **Contador de repos:** badge dinámico shields.io que lee `public_repos` de la API de GitHub.
  **Nunca** hardcodear un número — se actualiza solo.
- **Snake de contribuciones:** lo genera `.github/workflows/snake.yml` (Platane/snk, paleta coral
  a juego con el terminal; corre en cada push + cada 12h) y lo publica en la branch `output`
  (`github-contribution-grid-snake{,-dark}.svg`), embebido vía `<picture>` dark/light.
- **Railway:** código de referido del operador **`KJa0VN`** → `https://railway.com?referralCode=KJa0VN`.
  Debe permanecer en el README (badge + línea de texto).
- **Typing SVG** (tagline animada): servicio externo `readme-typing-svg.demolab.com`. Si algún
  día renderiza roto, degrada a su `alt`; los stats cards flaky (github-readme-stats / streak)
  se descartaron a propósito por caídas 503 — no re-agregar.

## Identidad (mantener sincronizado con la realidad)

- **Alejandro Exequiel Hernández Lara** — Santiago, Chile. `@alejandrehl` en todas las plataformas.
- **Ale Hernández SpA** — su empresa **principal** (100% suya, constituida 08-07-2026). Sitio de
  marca: alehernandez.cl. Bajo ella construye **NutriCoach** (nutricoach.cl). Datos legales
  (RUT, escritura) viven en el vault, **no** en este repo público.
- **KaiNext Solutions Limitada** — consultora de software (secundaria, con su padre Julio). kainext.cl.
- **Thoughtworks** — Senior Consultant (P4), embedded en Platform Engineering @ LATAM Airlines.

> NutriCoach está en fase de refinamiento pre-lanzamiento (dogfooding), **no** lanzado
> públicamente. No describirlo como "launched"/"live para usuarios" en el README.

## Reglas transversales (heredadas del centro de mando)

- **plan → review → approval → execution.** Nunca ejecutar cambios de fondo sin aprobación.
- **10/10:** sin placeholders, sin claims sin verificar, sin datos desactualizados.
- **Fechas** `DD-MM-YYYY`. Verificar la hora real (`TZ='America/Santiago' date`) antes de escribir cualquier timestamp.
- **Privacidad:** este repo es **público**. Nunca poner aquí datos sensibles, secretos, RUTs de
  terceros, ni detalle interno de clientes/engagements. Solo marca pública.

## Flujo de trabajo

Editar `README.md` → verificar el render (badges, links) → `git commit` → `git push origin main`.
El perfil se actualiza al instante. Los badges usan shields.io (inline, sin dependencias).
