from flask_login import UserMixin

# Realizamos la clase User para la autenticación
class User(UserMixin):
    def __init__(self, username):
        self.id = username

# Generamos un usuario Dummy para la base de datos
VALID_USERNAME_PASSWORD = {
    'admin': 'admin'
}
