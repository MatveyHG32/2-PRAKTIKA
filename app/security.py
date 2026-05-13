import bcrypt


def hash_password(password: str) -> str:
    # bcrypt ограничивает длину до 72 байт — обрезаем заранее для совместимости.
    data = password.encode("utf-8")[:72]
    return bcrypt.hashpw(data, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    data = plain.encode("utf-8")[:72]
    try:
        return bcrypt.checkpw(data, hashed.encode("utf-8"))
    except ValueError:
        return False
