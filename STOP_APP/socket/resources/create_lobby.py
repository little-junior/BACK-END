from flask_socketio import join_room
from STOP_APP.sql.services import LobbyService
from STOP_APP.sql.models import User
from STOP_APP.socket.models import storage_stop, validations, lobby_users
from sqlalchemy import and_
import random


def handle_create_lobby(socketio, data):
    # Make a list of all the letters drawn
    drawn_letters = random_letters(int(data["rounds"]))

    # Persist lobby
    result = LobbyService().create_lobby(data, drawn_letters)

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

    # Return data for Front-End
    socketio.emit("create_lobby", {
        "code_lobby": result.code_lobby,
        "host": data["id_user"],
        "themes": result.themes.replace("'", "").split(", "),
        "letters": str(drawn_letters).replace("'", "")
        },
        to=result.code_lobby
    )

def random_letters(quantidade=10):
    # Most common and simple letters to fill in
    letras_faceis = list("ABCDEGHIJLMNOPRSTV")

    # Ensure that the quantity does not exceed the total number of letters available.
    quantidade = min(quantidade, len(letras_faceis))

    # Carry out the draw
    return random.sample(letras_faceis, k=quantidade)
