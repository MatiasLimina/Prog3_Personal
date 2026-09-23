# Trabajo Práctico 1: Despliegue en un VPS
## Programación III (2PROG3) — Tecnicatura Universitaria en Programación (UTN FRM)

---

## 1. Carátula y Datos Institucionales

* **Institución:** Universidad Tecnológica Nacional – Facultad Regional Mendoza (UTN FRM)
* **Carrera:** Tecnicatura Universitaria en Programación
* **Cátedra:** Programación III (Código: 2PROG3)
* **Comisión:** Comisión 2
* **Trabajo Práctico:** TP 1 — Despliegue en un VPS: "La Aplicación en Internet"
* **Integrantes del Grupo:**
  * Nicolas Monjelardi (Legajo: 53842)
  * Lautaro Agüero (Legajo: 53867)
  * Matias Limina (Legajo: 54008)
* **Dominio Principal:** `matiaslimina.me`
* **Fecha de Entrega:** 21 de Septiembre de 2026

---

## 2. Datos del Despliegue e Infraestructura

El despliegue productivo del sistema distribuido se realizó sobre una arquitectura desacoplada de microservicios contenerizados, orquestados mediante Easypanel sobre un servidor privado virtual dedicado.

| Parámetro | Valor / Proveedor |
| :--- | :--- |
| **Proveedor VPS** | Hostinger |
| **Dirección IPv4 Pública** | `179.199.130.181` |
| **Proveedor DNS** | Namecheap (GitHub Student Developer Pack) |
| **Autoridad de Certificados TLS** | Let's Encrypt (Emisión y renovación automatizada vía reto HTTP-01) |
| **Panel de Orquestación** | Easypanel sobre Docker Swarm / Engine |

### Tabla de Servicios Públicos y Privados

| Servicio | Rol / Tecnología | Alcance de Red | URL / Endpoint Resoluble |
| :--- | :--- | :--- | :--- |
| **Frontend (`web`)** | Servidor Nginx (HTML5 / Vanilla JS) | Público (Internet) | `https://calculadora.matiaslimina.me/` |
| **Backend (`api`)** | FastAPI / Python (Lógica de cálculo) | Público (Internet) | `https://calculadora.api.limina.me/` |
| **Base de Datos (`db`)** | PostgreSQL 16 (Persistencia de historial) | Privado (Red interna Docker) | `calculadora_db:5432` *(Sin exposición pública)* |

### Variables de Entorno del Sistema

| Servicio | Variable | Valor Configurado | Justificación Técnica |
| :--- | :--- | :--- | :--- |
| `web` | `API_URL` | `https://calculadora.api.limina.me` | Permite al frontend en el navegador dirigir las peticiones HTTP al endpoint público seguro del backend sin hardcodear IPs. |
| `api` | `ORIGENES_PERMITIDOS` | `https://calculadora.matiaslimina.me` | Configura el middleware CORS de FastAPI para autorizar exclusivamente peticiones originadas en el dominio oficial del frontend. |
| `api` | `DATABASE_URL` | `postgres://usuario:clave@calculadora_db:5432/calculadora` | Cadena de conexión hacia el hostname interno del contenedor en la red bridge/overlay aislada de Docker. |

---

## 3. Evidencia de Verificación de Requisitos (R1 a R7)

### R1 — Dominio propio con resolución DNS correcta

**Fundamento:** La utilización de un nombre de dominio propio bajo gobernanza del equipo elimina la dependencia de dominios efímeros autogenerados, garantiza la persistencia del servicio ante migraciones de infraestructura y posibilita la emisión automatizada de certificados TLS reconocidos globalmente.

**Implementación y Verificación:**
Se configuraron registros de tipo **A** en la zona DNS autoritativa de Namecheap apuntando a la IP pública de la VPS (`179.199.130.181`):
1. `calculadora.matiaslimina.me` $\rightarrow$ `179.199.130.181`
2. `calculadora.api.limina.me` $\rightarrow$ `179.199.130.181`

```bash
# Verificación de resolución mediante dig
dig +short calculadora.matiaslimina.me
# Salida esperada: 179.199.130.181

dig +short calculadora.api.limina.me
# Salida esperada: 179.199.130.181
```

> [!NOTE]
> La resolución directa de ambos subdominios retorna unívocamente la dirección IP pública del servidor VPS sin saltos intermedios no autorizados ni discrepancias de propagación.

---

### R2 — Aseguramiento del Servidor VPS (Hardening & Firewall)

**Fundamento:** Todo servidor expuesto directamente a Internet está sujeto a escaneos automatizados y ataques de fuerza bruta continuos. Siguiendo el principio de menor privilegio y valores predeterminados seguros (*default deny*), se clausuró toda superficie de ataque innecesaria y se neutralizó la autenticación débil.

#### 1. Configuración Estricta de Firewall (UFW)
Se estableció una política global de denegación entrante y se abrieron únicamente los tres puertos requeridos para la operación del sistema:

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp   # SSH - Gestión y administración remota
sudo ufw allow 80/tcp   # HTTP - Validación de retos ACME (Let's Encrypt) y redirección
sudo ufw allow 443/tcp  # HTTPS - Tráfico cifrado de producción
sudo ufw enable
```

![Estado de Firewall UFW](imagenes/r2_ufw_status.png)
*Figura 1: Habilitación de UFW y verificación del estado activo (`sudo ufw status verbose`) con únicamente los puertos 22, 80 y 443 permitidos.*

#### 2. Blindaje del Demonio SSH (`sshd_config`)
Se editó `/etc/ssh/sshd_config` para deshabilitar por completo la autenticación por contraseña y mitigar ataques de diccionario:

```text
PasswordAuthentication no
PermitRootLogin prohibit-password
```

![Configuración segura de SSH](imagenes/r2_sshd_config.png)
*Figura 2: Edición de `/etc/ssh/sshd_config` con `PasswordAuthentication no` y `PermitRootLogin prohibit-password`.*

*Se aplicaron los cambios en caliente mediante `sudo systemctl reload ssh`.*

#### 3. Verificación de Rechazo de Autenticación Insegura
Se comprobó desde un cliente externo que el servidor rechaza de inmediato cualquier intento de conexión SSH que intente utilizar autenticación por contraseña:

```powershell
ssh -o PubkeyAuthentication=no root@179.199.130.181
```

![Rechazo de conexión sin clave pública](imagenes/r2_ssh_rechazo.png)
*Figura 3: Verificación externa demostrando que el servidor no admite acceso por clave y exige llave criptográfica autorizada.*

---

### R3 — Construcción de Imágenes desde Repositorios de Código

**Fundamento:** La reproducibilidad del software exige que cada versión provenga estrictamente de un Dockerfile versionado en el sistema de control de código fuente (Git), eliminando alteraciones manuales (*drift de configuración*) o transferencia opaca de binarios por SFTP.

**Evidencia de Compilación Automatizada en Easypanel:**
El motor de orquestación clonó directamente los repositorios oficiales de la cátedra para el backend y el frontend, ejecutando los builds multicapa de forma aislada:

#### 1. Compilación del Backend (`calc-back`):
![Build logs backend](imagenes/r3_build_backend.png)
*Figura 4: Registro de exportación de capas y generación del contenedor `calc-back:latest` con resultado exitoso.*

#### 2. Compilación del Frontend (`calc-front`):
![Build logs frontend](imagenes/r3_build_frontend.png)
*Figura 5: Registro de exportación de capas y generación del contenedor `calc-front:latest` con resultado exitoso.*

---

### R4 — Publicación con HTTPS Válido y Redirección Obligatoria

**Fundamento:** La privacidad e integridad de los datos en tránsito se garantizan mediante TLS. El tráfico en texto plano (HTTP) debe ser automáticamente elevado a HTTPS mediante códigos de estado de redirección permanente (301/308).

#### 1. Verificación de Respuesta HTTPS Segura (200 OK)
Se inspeccionaron los encabezados de respuesta mediante `curl.exe -I` confirmando la entrega válida bajo TLS sin requerir banderas de omisión como `--insecure`:

![Respuesta HTTPS 200 OK](imagenes/r4_curl_https.png)
*Figura 6: Verificación de respuesta HTTP/1.1 200 OK a través de conexión segura HTTPS en `https://calculadora.matiaslimina.me/`.*

#### 2. Verificación de Redirección HTTP a HTTPS (308 Permanent Redirect)
Se constató que cualquier solicitud entrante por HTTP en el puerto 80 es redirigida inmediatamente hacia la variante segura HTTPS:

![Redirección HTTP a HTTPS](imagenes/r4_curl_redirect.png)
*Figura 7: Verificación de respuesta HTTP/1.1 308 Permanent Redirect hacia `https://calculadora.matiaslimina.me/`.*

---

### R5 — Funcionamiento del Contrato de Punta a Punta

**Fundamento:** La arquitectura desacoplada requiere que el frontend consuma la API a través de la red respetando las políticas de seguridad del navegador (*Cross-Origin Resource Sharing - CORS*) y que el backend gestione explícitamente tanto el camino feliz como los casos de error de negocio y validación.

#### 1. Intercambio CORS y Flujo Normal (Camino Feliz)
Al efectuar una operación matemática desde la interfaz web (por ejemplo, `5 + 5`):
* El navegador emite la solicitud preflight `OPTIONS` que recibe los encabezados `Access-Control-Allow-Origin: https://calculadora.matiaslimina.me`.
* La petición principal `POST /api/calcular` devuelve exitosamente HTTP `200 OK` con el resultado y la expresión correspondiente.

![Contrato exitoso y DevTools Network](imagenes/r5_contrato_exito.png)
*Figura 8: Operación `5 + 5 = 10` ejecutada desde el frontend, evidenciando en la pestaña Network los intercambios OPTIONS y POST con código 200 y sin errores de CORS.*

#### 2. Validación de Casos de Error del Contrato

* **División por Cero (Regla de Negocio $\rightarrow$ HTTP 400 Bad Request):**
  * Petición: `{"a": 5, "b": 0, "operacion": "division"}`
  * Respuesta: HTTP `400 Bad Request` — `{"detail": "No se puede dividir por cero."}`.
  * La interfaz captura el error y notifica en pantalla al usuario de forma clara sin romper la aplicación.

![Error 400 División por cero](imagenes/r5_contrato_error_400.png)
*Figura 9: Validación de división por cero (`5 / 0`) mostrando el mensaje de error en la interfaz y la respuesta HTTP 400 en el panel de red.*

* **Operación Inexistente / Tipo Inválido (Validación Pydantic $\rightarrow$ HTTP 422 Unprocessable Entity):**
  * Petición: `{"a": 1, "b": 2, "operacion": "hackear"}`
  * Respuesta: HTTP `422 Unprocessable Entity` — La API rechaza el esquema no admitido protegiendo la integridad del servicio.

---

### R6 — Persistencia en Base de Datos PostgreSQL Aislada

**Fundamento:** El principio de defensa en profundidad exige que los motores de bases de datos operen en redes privadas no enrutables desde internet. La persistencia debe residir en volúmenes Docker duraderos que sobrevivan al ciclo de vida de los contenedores de aplicación.

#### 1. Aislamiento Perimetral (Escaneo Nmap Externo)
Se ejecutó un barrido perimetral de puertos con Nmap desde un host externo hacia la dirección IP de la VPS para corroborar que el puerto estándar de PostgreSQL (`5432`) no está expuesto:

![Escaneo Nmap puerto 5432](imagenes/r6_nmap_db_aislada.png)
*Figura 10: Salida del escaneo Nmap externo reportando el puerto 5432/tcp como `filtered`, inaccesible desde internet.*

#### 2. Supervivencia de Datos ante Redespliegues
1. Se realizaron operaciones aritméticas sucesivas en el frontend (`5.0 * 4.0 = 20.0`, `5.0 + 4.0 = 9.0`, etc.), registrándose en el historial de base de datos.
2. Se forzó el redespliegue y reinicio completo del contenedor del backend (`calculadora_api`) desde el panel de control.
3. Al consultar el historial (`GET /api/historial`) tras el reinicio, los registros persistieron íntegramente gracias al volumen persistente de PostgreSQL montado en el contenedor `db`.

![Historial de operaciones persistidas](imagenes/r6_historial_persistencia.png)
*Figura 11: Panel de últimas operaciones mostrando el historial persistido en la base de datos PostgreSQL.*

---

### R7 — Degradación Elegante

**Fundamento:** El almacenamiento del historial constituye una funcionalidad complementaria y secundaria respecto a la misión central del sistema: calcular. La caída o ausencia de la base de datos debe degradar el servicio de manera controlada y transparente, sin interrumpir la capacidad operativa de la calculadora.

#### 1. Comportamiento ante Ausencia de `DATABASE_URL`
Al remover temporalmente la variable de entorno `DATABASE_URL` del servicio backend y redesplegar:
* **Estado de Salud (`/api/salud`):** Retorna `HTTP 200 OK` informando `{"estado": "ok", "persistencia": false}`.
* **Capacidad de Cálculo (`/api/calcular`):** El endpoint continúa procesando cálculos (`5 - 4 = 1`) retornando `200 OK` en memoria.
* **Consulta de Historial (`/api/historial`):** Retorna `HTTP 503 Service Unavailable`, informando con precisión que el módulo de persistencia está deshabilitado.
* **Comportamiento en Frontend:** La interfaz advierte al usuario con el mensaje: *"Esta API está corriendo sin base de datos, así que no guarda historial. La calculadora funciona..."*.

![Degradación elegante sin base de datos](imagenes/r7_degradacion_sin_db.png)
*Figura 12: Cálculo matemático ejecutado exitosamente con mensaje informativo de degradación elegante al no disponer de base de datos.*

#### 2. Recuperación al Restablecer la Conexión
Al reconfigurar la variable `DATABASE_URL` y redesplegar el backend, la conexión se restablece de inmediato (`persistencia: true`), reactivando el guardado de nuevas operaciones en el historial sin requerir reinicios globales ni pérdida de estado.

![Persistencia restablecida](imagenes/r7_persistencia_restaurada.png)
*Figura 13: Cálculo posterior (`5 + 4 = 9`) con persistencia reactivada y registro de 8 operaciones en el historial.*

---

## 4. Registro y Análisis de Incidentes Reales

Durante las distintas etapas de aprovisionamiento, configuración de red y despliegue de microservicios, el equipo enfrentó y resolvió dos incidentes técnicos significativos:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                          ANÁLISIS DE INCIDENTES                             │
├────────────────────────────────┬────────────────────────────────────────────┤
│ Incidente 1: Ruteo / ISP       │ Solucionado vía diagnóstico con tracert y  │
│                                │ túnel VPN hacia nodo internacional limpio. │
├────────────────────────────────┼────────────────────────────────────────────┤
│ Incidente 2: Desconexión DB    │ Solucionado corrigiendo hostname interno   │
│                                │ en la variable DATABASE_URL del backend.   │
└────────────────────────────────┴────────────────────────────────────────────┘
```

---

### Incidente 1: Pérdida de Conectividad hacia la VPS por Falla de Enrutamiento del ISP

* **Síntoma Observado:** Uno de los integrantes del equipo experimentó la imposibilidad total de establecer conexión SSH hacia `179.199.130.181` y acceder a los subdominios publicados, recibiendo errores de *Connection Timeout*, mientras que el resto del grupo operaba normalmente.
* **Hipótesis Inicial:** Se supuso que el firewall UFW de la VPS había bloqueado la IP pública del integrante por reiterados intentos fallidos o que el proveedor Hostinger presentaba problemas en su interfaz de red.
* **Causa Raíz Identificada:** Se ejecutó un diagnóstico de traza de paquetes mediante `tracert 179.199.130.181`. El reporte evidenció que los paquetes salían del router local pero se descartaban de forma sistemática en un salto intermedio (*hop 8*) perteneciente al proveedor de tránsito internacional del ISP local del estudiante (problema de ruteo BGP / congestión de enlace del carrier).
* **Corrección Aplicada:** El integrante activó una conexión VPN para alterar el punto de salida de su tráfico de red, bordeando el nodo defectuoso del carrier. Esto restauró la conectividad plena a la VPS de forma inmediata y confirmó que la configuración del servidor era correcta.

---

### Incidente 2: Pérdida de Persistencia por Desincronización del Hostname Interno de PostgreSQL

* **Síntoma Observado:** Luego de agregar una nueva funcionalidad y modificar configuraciones en el panel de control, la calculadora realizaba los cálculos correctamente pero el historial dejó de registrar datos, mostrando el aviso `"Esta API está corriendo sin base de datos"`.
* **Hipótesis Inicial:** Se sospechó que el servicio PostgreSQL se había detenido por falta de memoria RAM o que el volumen de datos se había corrompido durante el reinicio.
* **Causa Raíz Identificada:** La inspección de contenedores demostró que PostgreSQL estaba en ejecución saludable (`running`). Sin embargo, en el servicio `calc-back`, la variable de entorno `DATABASE_URL` contenía un nombre de host desactualizado que no resolvía en la red interna de Docker generada tras la recreación de los servicios.
* **Corrección Aplicada:** Se actualizó la variable de entorno `DATABASE_URL` en Easypanel asignando la cadena canónica con el nombre del servicio interno:
  ```text
  DATABASE_URL=postgres://usuario:clave@calculadora_db:5432/calculadora
  ```
  Se forzó un nuevo despliegue del backend. El log de inicialización confirmó la reconexión:
  `"Historial habilitado: conexion a la base establecida"`, normalizándose el registro de operaciones.

---

## 5. Conclusiones y Evaluación de Aprendizaje

El desarrollo del presente trabajo práctico permitió consolidar conceptos fundamentales de infraestructura, DevOps y seguridad en la nube:

1. **Aislamiento y Defensa en Profundidad:** La separación entre servicios públicos (expuestos en puertos 80/443 bajo reverse proxy) y servicios privados (PostgreSQL en red interna aislada y filtrada) reduce radicalmente la superficie de vulnerabilidad.
2. **Resiliencia y Degradación Elegante:** Diseñar el software asumiendo que las dependencias auxiliares pueden fallar previene caídas totales del sistema (*fault isolation*) y preserva la experiencia de usuario.
3. **Automatización y Reproducibilidad:** La integración de Docker y paneles de orquestación garantiza la reproducibilidad completa del ciclo de vida del software, desde el commit en Git hasta la producción.

---

## 6. Anexo — Lista de Control Previa a la Entrega

Verificación exhaustiva de todos los puntos de control exigidos por la cátedra (Sección 10 de la consigna oficial):

### Nombres y Transporte
- [x] `dig +short calculadora.matiaslimina.me` devuelve la IP de la VPS (`179.199.130.181`).
- [x] `dig +short calculadora.api.limina.me` devuelve la IP de la VPS (`179.199.130.181`).
- [x] `https://calculadora.matiaslimina.me/` abre sin advertencias de seguridad del navegador.
- [x] `https://calculadora.api.limina.me/api/salud` responde `{"estado": "ok", ...}`.
- [x] `http://calculadora.matiaslimina.me/` redirige automáticamente a HTTPS (308 Permanent Redirect).

### Servidor y Seguridad
- [x] El barrido de puertos desde afuera (`nmap`) muestra únicamente 22, 80 y 443 abiertos.
- [x] El acceso SSH por contraseña está completamente deshabilitado en `sshd_config`.
- [x] Las claves públicas de los integrantes están cargadas y autorizadas en el servidor.
- [x] El firewall UFW está activo con política restrictiva por defecto (`deny incoming`).

### Aplicación y Persistencia
- [x] Una operación completa funciona desde la página web publicada.
- [x] La consola de red del navegador no muestra errores de CORS en el intercambio.
- [x] División por cero devuelve `400 Bad Request`; operación inválida devuelve `422 Unprocessable Entity`.
- [x] El historial muestra las operaciones registradas, la más reciente primero.
- [x] El historial sobrevive al redespliegue del contenedor del servicio backend (`calc-back`).
- [x] Nmap confirma el puerto de base de datos `5432` cerrado/filtrado desde el exterior.
- [x] Sin `DATABASE_URL`, la calculadora continúa operando y el endpoint de historial devuelve `503 Service Unavailable`.

### Entrega
- [x] El informe incluye las capturas reales de la sección 5, legibles y propias del entorno del grupo.
- [x] El informe describe detalladamente dos incidentes técnicos reales y sus soluciones.
- [x] Las URLs del frontend y de la API están consignadas explícitamente para el envío por el campus.

---
*Informe académico oficial generado conforme a las normativas de la cátedra de Programación III - UTN FRM.*
