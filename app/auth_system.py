import bcrypt

from database import add_user, get_user


def hash_password(password):
    return bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    ).decode()


def register_user(username, email, password):

    add_user(
        username,
        email,
        hash_password(password)
    )


def login_user(username, password):

    user = get_user(username)

    if user is None:
        return False

    stored_password = user[3]

    if not stored_password:
        return False

    return bcrypt.checkpw(
        password.encode(),
        stored_password.encode()
    )
