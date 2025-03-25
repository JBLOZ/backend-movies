# Descripción de los endpoints

## Usuarios

- GET /users
    - Devuelve una lista con todos los usuarios registrados en la base de datos.
    - De cada usuario se devolverán los campos `id` y `username`.
    - Códigos de respuesta:
        - 200: lista de usuarios

- GET /users/{id}
    - Devuelve los datos del usuario con el id especificado.
    - De cada usuario se devolverán los campos `id`, `username` y `email`.
    - Códigos de respuesta:
        - 200: usuario
        - 404: "User not found"


## Películas

- GET /movies
    - Devuelve una lista con todas las películas registradas en la base de datos.
    - De cada película se devolverán los campos `id` y `title`.
    - Códigos de respuesta:
        - 200: lista de películas

- GET /movies/search
    - Busca películas por título, devolverá todas las películas que contengan la cadena a buscar en el título (en cualquier posición y sin distinción de mayúsculas y minúsculas).
    - Parámetros de consulta (*query string*):
        - `title`: título de la película a buscar.
    - De cada película se devolverán los campos `id` y `title`.
    - Si no hay ninguna película que coincida con el título, se devolverá una lista vacía.
    - Códigos de respuesta:
        - 200: lista de películas

- GET /movies/{id}
    - Devuelve los datos de la película con el id especificado.
    - De cada película se devolverán los campos `id`, `title`, `director`, `year` y `genre`.
    - Códigos de respuesta:
        - 200: película
        - 404: "Movie not found"

- POST /movies
    - Crea una nueva película en la base de datos.
    - Parámetros en el cuerpo de la petición (*request body* en formato JSON):
        - `title`: título de la película (cadena de texto).
        - `director`: director de la película (cadena de texto).
        - `year`: año de estreno de la película (número entero).
        - `genre`: género de la película (cadena de texto).
    - Códigos de respuesta:
        - 201: película creada (`id`, `title`, `director`, `year`, `genre`)
        - 422: error de validación generado por Pydantic

- DELETE /movies/{id}
    - Elimina la película con el id especificado de la base de datos.
    - **Si la película tiene comentarios asociados, también se eliminarán.**
    - Códigos de respuesta:
        - 200: no devuelve contenido
        - 404: "Movie not found"

## Comentarios

- GET /users/{id}/comments
    - Devuelve una lista con todos los comentarios del usuario con el id especificado.
    - De cada comentario se devolverán los campos `movie_id`, `title` (título de la película), `user_id`, `username` (usuario que hizo el comentario), `text` (texto del comentario) y `sentiment`.
    - Códigos de respuesta:
        - 200: lista de comentarios
        - 404: "User not found"

- GET /movies/{id}/comments
    - Devuelve una lista con todos los comentarios de la película con el id especificado.
    - De cada comentario se devolverán los campos `movie_id`, `title` (título de la película), `user_id`, `username` (usuario que hizo el comentario), `text` (texto del comentario) y `sentiment`.
        - Códigos de respuesta:
        - 200: lista de comentarios
        - 404: "Movie not found"

- POST /movies/{id}/comments
    - Añade un nuevo comentario a la película con el id especificado.
    - Parámetros en el cuerpo de la petición (*request body* en formato JSON):
        - `user_id`: id del usuario que hace el comentario (número entero).
        - `text`: texto del comentario (cadena de texto).
    - El campo `sentiment` se rellenará automáticamente usando el modelo de análisis de sentimiento.
    - Códigos de respuesta:
        - 201: comentario creado (`movie_id`, `title`, `user_id`, `username`, `text`, `sentiment`)
        - 404: "Movie not found"
        - 404: "User not found"
        - 422: error de validación generado por Pydantic
