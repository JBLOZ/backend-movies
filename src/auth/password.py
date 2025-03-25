import bcrypt

def hash_password(password: str) -> str:
    """Encripta la contraseña usando bcrypt"""
    # Convertir la contraseña a bytes
    password_bytes = password.encode('utf-8')
    # Generar un salt y hacer hash de la contraseña
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    # Devolver el hash como string
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña coincide con el hash almacenado"""
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)