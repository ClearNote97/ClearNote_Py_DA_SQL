# `assets/` — todo lo visual del proyecto

Imágenes, logos, íconos, fuentes y diagramas que usan **los entregables y la documentación**
(README, informes, presentaciones, notebooks). Un solo lugar para no tenerlos regados por el repo.

| Carpeta | Qué va |
|---|---|
| `marca/` | Logo(s) en sus variantes (claro, oscuro, ícono) y la paleta de la marca del proyecto o del cliente |
| `imagenes/` | Fotos, capturas y portadas que se reutilizan |
| `iconos/` | Íconos sueltos (SVG de preferencia) |
| `fuentes/` | Tipografías que el proyecto incrusta (con su licencia al lado) |
| `diagramas/` | Diagramas del proyecto: flujo de trabajo, arquitectura (SVG de preferencia: se ve nítido en GitHub y VS Code) |

**Reglas:**

- **SVG antes que PNG** cuando se pueda: pesa poco, escala sin perder nitidez y se puede editar.
- **Nombres en minúscula y con guiones** (`logo-claro.svg`, `flujo-trabajo.svg`), sin espacios.
- **Licencias:** una fuente o una imagen de terceros va con su licencia o su fuente al lado (`fuentes/LICENCIAS.md`).
- **Material del cliente:** si es confidencial y el repo es público, va en `.gitignore` (como `.env`), no aquí.
- Lo que **genera** el análisis (gráficos de resultados) no va aquí: va al flujo `sandbox/ → output/`.
