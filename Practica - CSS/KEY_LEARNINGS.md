# Recopilación de Aprendizajes Clave (Key Learnings)
## Actividad Práctica de CSS: Cartelera del Curso

Este documento sintetiza los conceptos, aprendizajes técnicos y decisiones de diseño implementados a lo largo de la práctica de desarrollo de la cartelera de actividades.

---

### 1. Normalización y Portabilidad del Entorno
* **Rutas relativas**: Los archivos exportados o compartidos desde sistemas locales suelen arrastrar referencias absolutas (e.g. `file:///C:/Users/...`). Normalizar estas rutas a enlaces relativos limpios (`styles.css`, anclas `#actividades`) es un paso indispensable antes de comenzar cualquier maquetación para asegurar que el proyecto funcione en cualquier máquina o servidor.
* **Separación de responsabilidades**: Mantener el archivo HTML estático e inmutable mientras se resuelve la totalidad del diseño visual a través de una hoja de estilos externa (`styles.css`) demuestra la potencia y flexibilidad de CSS bien estructurado.

---

### 2. Variables CSS y Consistencia Cromática
* **Definición en `:root`**: Centralizar los valores de la paleta en propiedades personalizadas (`--color-mist`, `--color-stone`, `--color-shadow`, `--color-autumn`) simplifica el mantenimiento, facilita ajustes globales en tiempo de ejecución y garantiza consistencia armónica en toda la interfaz.
* **Roles claros**: Asignar funciones semánticas a cada color (e.g. `stone` para encabezados y enlaces, `shadow` para texto de lectura, `autumn` para acentos e insignias, `mist` para bordes tenues) evita la arbitrariedad visual.

---

### 3. Modelo de Caja y Dimensionamiento (`box-sizing`)
* **`box-sizing: border-box` universal**: Aplicado en `*, *::before, *::after`, asegura que las propiedades `padding` y `border` queden contenidas dentro del `width` y `height` calculados para cada elemento. Esto previene desbordamientos inesperados y simplifica el cálculo de cuadrículas.
* **Inspección de capas**: En DevTools, distinguir claramente entre el área de contenido (`width`/`height`), el relleno interior (`padding`), el límite visual (`border`) y la distancia respecto a otros elementos (`margin`).

---

### 4. Metodología BEM (Block, Element, Modifier)
* **Estructura predecible**: 
  - **Bloque (`.tarjeta`)**: Define la entidad independiente con su propio contexto y estilos base.
  - **Elementos (`.tarjeta__titulo`, `.tarjeta__enlace`, `.tarjeta__etiqueta`)**: Representan partes constitutivas del bloque cuya existencia depende del mismo.
  - **Modificador (`.tarjeta--destacada`)**: Modifica la apariencia o estado del bloque sin duplicar todas las declaraciones existentes, aplicando únicamente los acentos diferenciales (borde cálido, fondo sutil, elevación).
* **Propiedad `display` en elementos inline**: Asignar `display: inline-block` en `.tarjeta__enlace` es necesario para que un hipervínculo acepte `padding` vertical, bordes redondeados y transformaciones espaciales comportándose como un botón interactivo.

---

### 5. Layout Moderno: Flexbox (1D) vs. CSS Grid (2D)
* **Flexbox para `.cabecera`**: Ideal para distribuciones unidimensionales. Mediante `display: flex`, `justify-content: space-between` y `align-items: center`, se logra alinear automáticamente el título y la navegación en extremos opuestos sin necesidad de floats ni posicionamientos manuales.
* **CSS Grid para `.cartelera`**: El sistema óptimo para galerías bidimensionales. Utilizar `grid-template-columns: repeat(auto-fit, minmax(260px, 1fr))` permite una distribución fluida de tarjetas que se reacomodan según el ancho del viewport, mientras que `gap: 1.5rem` gestiona los espacios inter-tarjetas de forma nativa sin ensuciar los márgenes de los componentes.
* **Flex interno en tarjetas**: Dentro de cada tarjeta de la grilla, aplicar `display: flex; flex-direction: column;` y `flex-grow: 1;` sobre el párrafo asegura que los botones `.tarjeta__enlace` queden perfectamente alineados en la parte inferior, independientemente de la longitud del texto.

---

### 6. Posicionamiento en Capas (`relative` / `absolute` / `z-index`)
* **Contexto de apilamiento**: Un elemento con `position: absolute` se posiciona respecto al ancestro posicionado más cercano (`position: relative`, `absolute` o `fixed`). Asignar `position: relative` a `.tarjeta` crea el marco de referencia exacto para que `.tarjeta__etiqueta` pueda situarse en la esquina (`top: 1rem; right: 1rem;`) de su propia tarjeta.
* **Capas con `z-index`**: Al configurar `z-index: 2` en la etiqueta "Nueva", se garantiza que la insignia flote por encima del contenido y de cualquier borde o sombra adyacente.

---

### 7. Selectores Avanzados, Estados y Accesibilidad
* **Combinador descendente**: El selector `.cartelera .tarjeta__enlace` focaliza los estilos exclusivamente en los enlaces que forman parte de la cartelera, evitando efectos secundarios no deseados en enlaces de cabecera o pie.
* **Interactividad con `:hover`**: Brinda retroalimentación inmediata al usuario mediante cambios de color de fondo y una sutil elevación (`transform: translateY(-2px)` con `box-shadow`).
* **Accesibilidad por teclado (`:focus` y `:focus-visible`)**: Definir un contorno destacado (`outline: 3px solid var(--color-autumn)`) con `outline-offset: 3px` garantiza que personas que navegan con la tecla Tab identifiquen sin ambigüedad el elemento activo, cumpliendo pautas de accesibilidad web (WCAG).
* **Selector estructural `:nth-child()`**: `.cartelera .tarjeta:nth-child(2)` permite estilizar un elemento específico basado en su posición en el árbol DOM sin requerir clases adicionales en el HTML, ideal para detalles de laboratorio o elementos secundarios.

---

### 8. Estrategia Responsiva con Media Queries
* **Punto de quiebre (Breakpoint)**: Configurar `@media (max-width: 680px)` permite adaptar la interfaz antes de que los elementos colapsen visualmente.
* **Columna única**: En móvil, forzar `grid-template-columns: 1fr` en `.cartelera` garantiza que cada tarjeta ocupe el ancho completo disponible, evitando textos comprimidos o elementos truncados.
* **Reorganización de cabecera**: Cambiar la dirección del flex a `flex-direction: column` y `align-items: flex-start` en pantallas angostas previene que el menú de navegación se solape con el título principal.

---

### 9. Comparativa Técnica del Experimento de Visibilidad (`.aviso`)
La comparación entre las tres técnicas de ocultamiento en CSS arrojó conclusiones críticas para el desarrollo de interfaces:

| Propiedad | Ocupación de Espacio en Layout | Interactividad con Mouse / Puntero | Accesibilidad y Navegación Tab | Caso de Uso Recomendado |
|---|---|---|---|---|
| **`display: none;`** | **No ocupa espacio** (la caja se retira del render tree) | **Inexistente** (no cliqueable) | **No recibe foco** por teclado | Ocultar menús colapsados, pestañas inactivas o modales cerrados. |
| **`visibility: hidden;`** | **Conserva el espacio original** intacto | **Inexistente** (no cliqueable) | **No recibe foco** por teclado | Ocultar elementos temporalmente sin generar saltos de layout (reflow/layout shifts). |
| **`opacity: 0;`** | **Conserva el espacio original** intacto | **Permanece 100% activo** (se puede cliquear) | **Sigue recibiendo foco Tab** (enlace navegable) | Animaciones y transiciones de desvanecimiento (fade in/out). Requiere combinarse con `pointer-events: none` o `visibility: hidden` si no se desea interacción. |

---

### 10. Justificación de 2 Decisiones de Diseño para la Puesta en Común
Para la defensa y exposición grupal ante la clase, se seleccionaron las siguientes dos justificaciones técnicas:
1. **Elección de CSS Grid adaptable con `auto-fit` y `minmax`**: Se optó por una grilla fluida en lugar de anchos porcentuales fijos porque permite que el navegador calcule matemáticamente la mejor cantidad de columnas según el viewport disponible, combinándolo con una media query en pantallas menores a 680px para garantizar una lectura vertical limpia en dispositivos móviles.
2. **Implementación de navegación accesible mediante `:focus-visible`**: En lugar de suprimir el contorno por defecto (`outline: none`), se diseñó un anillo de enfoque personalizado con `--color-autumn` y `outline-offset: 3px`. Esto asegura que los usuarios que navegan mediante teclado distingan inmediatamente el elemento activo, mejorando la usabilidad universal de la página.
