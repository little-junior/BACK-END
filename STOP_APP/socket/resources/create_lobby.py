from flask_socketio import join_room
from STOP_APP.sql.services import LobbyService
from STOP_APP.sql.models import User
from STOP_APP.socket.models import storage_stop, validations, lobby_users
from sqlalchemy import and_
import random
import string


def handle_create_lobby(socketio, data):
    # Persist lobby
    result = LobbyService().create_lobby(data)

    # Appending client to the room
    join_room(result.code_lobby)

    # Create lobby in storages
    storage_stop.update({f"{result.code_lobby}": []})
    validations.update({f"{result.code_lobby}": []})

    # Get username by "id_user"
    username = User().query.filter(and_(User.id==data["id_user"], User.active==True)).first().username
    # Get users in lobby_users
    lobby_users[f"{result.code_lobby}"] = []
    # Append user data
    lobby_users[f"{result.code_lobby}"].append({
        "id_user": data["id_user"],
        "username": username,
        "host": data["id_user"]
    })

    # Make a list of all the letters drawn
    draw_letters = random_letters()

    # Return data for Front-End
    socketio.emit("create_lobby", {
        "code_lobby": result.code_lobby,
        "host": data["id_user"],
        "themes": result.themes.split(", "),
        "letters": draw_letters
        },
        to=result.code_lobby
    )

def random_letters(quantidade=10):
    # Gera uma lista de letras aleatórias minúsculas
    return random.choices(string.ascii_lowercase, k=quantidade)
