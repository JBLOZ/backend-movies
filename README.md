[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/PBsONbu3)
# Práctica 2 - Backend de aplicación

# Implementación de un sistema de gestión de películas y comentarios

## Introducción  

El objetivo de esta práctica es implementar el *backend* de una aplicación para gestionar los datos de películas y comentarios de usuarios. El sistema integrará un modelo IA capaz de categorizar los comentarios de los usuarios como positivos, negativos o neutros (*sentiment analysis*).

## Evaluación

Esta práctica **se puede realizar de forma individual o en grupos de dos personas**. En caso de realizarla en grupo, ambos miembros deberán participar activamente en el desarrollo de la práctica y conocer en detalle el código implementado, y su participación deberá quedar reflejada en el repositorio.

La evaluación de la práctica se realizará mediante **pruebas automáticas** y una **revisión manual** del código que valorará el diseño de las clases y métodos, la claridad y organización del código, y el uso de buenas prácticas de programación siguiendo los conceptos vistos en la asignatura.

| Concepto                                                                        | Peso |
|---------------------------------------------------------------------------------|------|
| Implementación de los endpoints (pruebas automáticas)                           |  40% |
| Diseño de clases (controladores, servicios, modelos)                            |  15% |
| Organización del código en paquetes                                             |   5% |
| Documentación de los endpoints                                                  |   5% |
| Otros criterios de calidad (nombres de variables y funciones, comentarios, ...) |  10% |
| Despliegue de la aplicación con Docker                                          |   5% |
| Autenticación con tokens JWT                                                    |  10% |
| Creación de un servicio de inferencia                                           |  10% |

**NO ESTÁ PERMITIDO modificar las pruebas automatizadas**. Si lo haces obtendrás un 0 en la práctica.

## Ejecución

Instala las dependencias necesarias con el siguiente comando:

```bash
pip install -r requirements.txt
```

Se proporciona un fichero `docker-compose.yml` con un servicio de base de datos MariaDB y un cliente de administración de la base de datos (Adminer) para que puedas probar tu aplicación con una base de datos real. Para poner en marcha la aplicación, ejecuta el siguiente comando en la raíz del repositorio:

```bash
docker compose up
```

El código base proporcionado en `src/main.py` se conecta a la base de datos y ofrece un servicio `/users` para probar la conexión.

## Implementación de los endpoints

El código debe superar las pruebas automáticas proporcionadas en el repositorio. Para ello deberás implementar los endpoints descritos en en documento [ENDPOINTS.md](ENDPOINTS.md).

Aunque tienes libertad para estructurar tu código, para superar las pruebas es imprescindible crear los modelos `User`, `Movie` y `Comment` usando `SQLModel`. Estos modelos deberán estar disponibles en el paquete `db` (se proporciona la implementación de `User`). Deberás crearlos de acuerdo al siguiente diagrama:

![](docs/uml.svg)

En el código proporcionado se incluye una clase `SentimentModel` que se encarga de categorizar los comentarios de los usuarios como positivos, negativos o neutros. Deberás usar esta clase en tu aplicación para etiquetar los comentarios de los usuarios en el endpoint `POST /movies/{movie_id}/comments`.

Esta clase usa por defecto un generador aleatorio de predicciones, pero está preparada para usar un modelo preentrenado de Hugging Face. **El uso de este modelo preentrenado no es obligatorio** para evitar problemas de compatibilidad que puedan surgir en diferentes entornos, y **su uso no afecta al funcionamiento de las pruebas automáticas**, pero puedes activarlo si quieres probarlo y obtener predicciones realistas en tus pruebas, [siguiendo estas instrucciones](DEPENDENCIES.md).

El resto del código puedes estructurarlo a tu conveniencia, aunque deberás seguir las recomendaciones vistas en la asignatura.

El resto de funcionalidades descritas a continuación no son necesarias para superar las pruebas automáticas, pero se deben implementar para obtener la máxima puntuación en la práctica. **Deberás documentarte y buscar información adicional para implementarlas**. En caso de implementarlas, **las pruebas automáticas deberán seguir funcionando correctamente**.

## Despliegue con Docker

Deberás proporcionar un fichero `Dockerfile` para construir la imagen de tu aplicación, y modificar el fichero `docker-compose.yml` para desplegar la aplicación con Docker Compose. La aplicación deberá estar disponible en el puerto 8000.

Deberás añadir también un nuevo servicio al fichero `docker-compose.yml` proporcionado.

> **¿Quieres hacerlo aún mejor?** Añade un volumen al nuevo servicio montado en `/var/log/movies` y haz que la aplicación escriba los logs en un fichero en esta carpeta.

Deberás modificar el código de la aplicación para que se conecte a la base de datos usando una variable de entorno proporcionada por Docker Compose (`DB_URL`).

Cuando los servicios arrancan, es habitual que la aplicación se inicie antes de que la base de datos esté lista para aceptar conexiones. Deberás implementar un mecanismo de espera en la aplicación para esperar a que la base de datos esté disponible antes de intentar conectarse. Existen varias alternativas:

- Esperar un tiempo fijo antes de intentar conectarse a la base de datos con `time.sleep()`
- Usar la librería `tenacity` para reintentar la conexión a la base de datos hasta que tenga éxito
- Usar un script `wait-for-it.sh` en el contenedor de la aplicación para esperar a que la base de datos esté disponible

## Autenticación con tokens JWT

Para implementar la autenticación de los usuarios deberás usar tokens JWT. Deberás usar la librería PyJWT para generar y validar los tokens, y deberás implementar la clase `JWTBearer` en el fichero `src/auth/jwt.py`. Esta clase validará los tokens en las peticiones de las rutas protegidas.

En este fichero se declara una variable:
```{python}
authenticator = JWTBearer()
```
que deberás importar y usar como dependencia en todos los endpoints, de la siguiente manera:
```{python}
from auth import authenticator

@app.get("/protected", dependencies=[Depends(authenticator)])
def protected_route():
    return {"message": "This is a protected route"}
```

Además, deberás añadir un endpoint `/login` que permita a los usuarios autenticarse y obtener un token JWT. El endpoint deberá recibir un JSON con los campos `username` y `password`, y deberá devolver un token JWT con un campo `access_token`si las credenciales son correctas. **Este endpoint no debe estar protegido con autenticación**, de lo contrario sería imposible acceder a él para identificarse.

Ten en cuenta además que las contraseñas de los usuarios deberán estar encriptadas en la base de datos, y para comprobar si la contraseña recibida en el login es correcta deberás encriptarla y compararla con la contraseña encriptada almacenada en la base de datos. Se recomienda usar la librería `bcrypt` para encriptar las contraseñas. Deberás encriptar también las contraseñas de los usuarios de prueba que se insertan en la base de datos en el método `seed_users` de `db.py`.

## Creación de un servicio de inferencia

En la implementación básica, el modelo de inferencia está integrado en la propia aplicación. Sin embargo, en un entorno de producción es recomendable separar la lógica de inferencia en un servicio independiente. Deberás crear un servicio de inferencia que ofrezca las predicciones a través de una API REST.

Deberás modificar la clase `SentimentModel`para que el método `analyze_sentiment` haga una petición a este servicio en lugar de realizar la inferencia directamente. El servicio de inferencia deberá estar disponible en el puerto 8001.

Este servicio deberá lanzarse junto con la aplicación principal en el fichero `docker-compose.yml`. Deberás proporcionar un `Dockerfile` para construir la imagen de este servicio.

> Si has añadido un volumen a la aplicación principal, monta el mismo volumen en el nuevo servicio para que también escriba sus logs en la misma carpeta.

## Código base

En el repositorio se proporciona el siguiente código base:

- `src/db/models.py`: contiene la implementación de la clase `User` usando `SQLModel`
- `src/db/db.py`: contiene el código necesario para realizar la conexión con la base de datos, y un método `seed_users` para insertar usuarios de prueba
- `src/ia/sentiment_analysis.py`: contiene la implementación de la clase `SentimentModel` que se encargará de categorizar los comentarios de los usuarios
- `src/auth/jwt.py`: módulo donde deberás implementar la autenticación de los usuarios con tokens JWT
- `src/main.py`: contiene el código principal de la aplicación, con un endpoint de prueba
- `tests/`: contiene las pruebas automáticas que se ejecutarán para evaluar la práctica
- `requirements.txt`: contiene las dependencias necesarias para ejecutar la aplicación y las pruebas
- `postman_collection.json`: contiene una colección de Postman con ejemplos de peticiones a los endpoints de la aplicación. Puedes importarla en Postman para probar los endpoints. Las peticiones que incluye asumen que hay al menos un usuario en la base de datos con id 1, y dos películas con id 1 y 2 para probar los endpoints.
- `docker-compose.yml`: contiene la configuración de Docker Compose para ejecutar una base de datos MariaDB y un cliente de administración de la base de datos (Adminer) en contenedores Docker. Puedes usarlo para probar la aplicación con una base de datos real.


