import bcrypt

from database import add_user, get_user


def register_user(username, email, password):

    hashed = bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    )

    add_user(
        username,
        email,
        hashed.decode()
    )


def login_user(username, password):

    user = get_user(username)

    if user is None:
        return False

    stored_password = user[3]

    return bcrypt.checkpw(
        password.encode(),
        stored_password.encode()
    )