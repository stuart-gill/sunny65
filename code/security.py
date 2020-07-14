from models.user import UserModel

# users = [User(1, "stuart", "asdf")]

# # username_mapping = {"stuart": {"id": 1, "username": "stuart", "password": "asdf"}}
# username_mapping = {u.username: u for u in users}

# userid_mapping = {u.id: u for u in users}


def authenticate(username, password):
    user = UserModel.find_by_username(username)
    if user and user.password == password:
        return user


def identity(payload):
    user_id = payload["identity"]
    return UserModel.find_by_id(user_id)

