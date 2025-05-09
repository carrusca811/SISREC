import bcrypt

def hash_password(password: str) -> str:
    """ Hash a password for storing """
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    """ Verify a stored password against one provided by the user """
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
