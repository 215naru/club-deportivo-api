# Club Deportivo API

API REST para el sistema de reservas de un club deportivo (canchas, socios y reservas), implementada en Flask + MySQL.

## Integrantes

- Nimer Rodriguez
- Shelby Cadillo

## Versiones utilizadas

- Python 3
- Flask 3.1.3
- mysql-connector-python 26.7.0
- python-dotenv 1.2.3

Ver el detalle completo de dependencias en `requirements.txt`.

## Instalación

1. Clonar el repositorio y ubicarse en la carpeta del proyecto.
2. Crear y activar un entorno virtual:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
4. Copiar el archivo de configuración de ejemplo y completar los valores reales:
   ```bash
   cp .env.example .env
   ```
5. Crear la base de datos en MySQL (el nombre debe coincidir con `DB_NAME` en `.env`):
   ```sql
   CREATE DATABASE club_deportivo;
   ```
6. Ejecutar el script de creación de tablas (crea las tablas y carga los deportes iniciales):
   ```bash
   mysql -u <usuario> -p club_deportivo < sql/init_db.sql
   ```

## Configuración

La aplicación lee la configuración desde variables de entorno (archivo `.env`, no versionado). Las claves esperadas están documentadas en `.env.example`:

| Variable      | Descripción                          |
|---------------|---------------------------------------|
| `DB_HOST`     | Host del servidor MySQL               |
| `DB_PORT`     | Puerto del servidor MySQL              |
| `DB_USER`     | Usuario de conexión a la base de datos |
| `DB_PASSWORD` | Contraseña del usuario                 |
| `DB_NAME`     | Nombre de la base de datos             |

## Ejecución

```bash
python run.py
```

El servidor queda disponible en `http://127.0.0.1:5001`.

## Ejemplos de requests

### Deportes

```bash
curl http://127.0.0.1:5001/deportes
```

### Canchas

```bash
# Crear una cancha
curl -X POST http://127.0.0.1:5001/canchas \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Cancha 1 - Fútbol 5","id_deporte":1,"precio_hora":1000000,"techada":false}'

# Listar canchas con filtros
curl "http://127.0.0.1:5001/canchas?id_deporte=1&activa=true&_limit=10&_offset=0"

# Consultar disponibilidad
curl "http://127.0.0.1:5001/canchas/disponibles?fecha=2026-10-15&hora_inicio=18:00:00&hora_fin=20:00:00"

# Actualizar parcialmente
curl -X PATCH http://127.0.0.1:5001/canchas/1 \
  -H "Content-Type: application/json" \
  -d '{"precio_hora":1200000}'

# Eliminar (falla con 409 si tiene reservas asociadas)
curl -X DELETE http://127.0.0.1:5001/canchas/1
```

### Socios

```bash
# Crear un socio
curl -X POST http://127.0.0.1:5001/socios \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Juan Pérez","email":"juan.perez@example.com"}'

# Listar socios con filtros
curl "http://127.0.0.1:5001/socios?nombre=juan&activo=true"
```

### Reservas

```bash
# Crear una reserva
curl -X POST http://127.0.0.1:5001/reservas \
  -H "Content-Type: application/json" \
  -d '{"id_socio":1,"id_cancha":1,"fecha_hora_inicio":"2026-10-15T18:00:00.000000-03:00","fecha_hora_fin":"2026-10-15T20:00:00.000000-03:00"}'

# Listar reservas con filtros y paginación
curl "http://127.0.0.1:5001/reservas?id_cancha=1&_limit=10&_offset=0"

# Cambiar el estado de una reserva
curl -X PUT http://127.0.0.1:5001/reservas/1/estado \
  -H "Content-Type: application/json" \
  -d '{"estado":"cancelada"}'
```

## Supuestos adoptados

- Las fechas/horas se interpretan siempre en GMT-3 fijo (sin manejo de husos horarios reales); se valida explícitamente que el string recibido incluya el offset `-03:00`.
- La verificación de superposición y el alta de la reserva se resuelven dentro del mismo request sin una transacción explícita de base de datos; se considera una simplificación aceptable para el alcance de este trabajo.
- `PUT /reservas/{id}/estado` responde `204 Sin contenido`, siguiendo la definición de `swagger.yaml` (el contrato tomado como referencia principal).
- `GET /canchas/disponibles` exige las mismas reglas de horario, duración (1 a 3 horas) y fecha futura que una reserva nueva.
- `DELETE /canchas/{id}` rechaza la eliminación si la cancha tiene alguna reserva asociada, sin importar su estado; para dejar de ofrecerla se recomienda usar `PATCH` con `activa: false`.
- Los cuerpos de creación/actualización rechazan campos desconocidos y los `PATCH` rechazan cuerpos vacíos.
- Los parámetros de consulta (`query params`) desconocidos en los listados se rechazan con `400`.