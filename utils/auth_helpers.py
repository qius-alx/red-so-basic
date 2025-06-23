# from app import bcrypt # Esta importación se hará dentro de las funciones

def hash_password(password_text):
    from app import bcrypt # Importar aquí para evitar importación circular a nivel de módulo
    return bcrypt.generate_password_hash(password_text).decode('utf-8')

def check_password(hashed_password_db, password_text_form):
    from app import bcrypt # Importar aquí
    return bcrypt.check_password_hash(hashed_password_db, password_text_form)
