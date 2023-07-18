from fastapi import FastAPI, HTTPException
from enum import Enum
from pydantic import BaseModel
import sqlite3

app = FastAPI()

games = {}
history = []


class status(str, Enum):
    Finished: "Finished"
    Inprogress: "Inprogress"


class Request(BaseModel):
    type: str
    position: int


conn = sqlite3.connect(':memory:')
c = conn.cursor()
c.execute("""CREATE TABLE MovesHistory (
            game_id integer,
            type text,
            position integer
            )""")


@app.post("/start")
async def start():
    game_id = len(games) + 1
    games[game_id] = [[" " for i in range(3)] for i in range(3)]
    return {"game_id": game_id}


@app.post("/move/{game_id}")
async def move(game_id: int, request: Request):
    arr = games[game_id]
    row, col = request.position // 3, request.position % 3
    if arr[row][col] != " ":
        raise HTTPException(status_code=400, detail={"result": "error", "error_code": "invalid_position"})
    arr[row][col] = request.type
    history.append({"game_id": game_id,
                    "move": request})
    c.execute("INSERT INTO MovesHistory VALUES (:game_id , :type, :position)",
              {'game_id': game_id, 'type': request.type,
               'position': request.position})
    return {"result": "success"}


@app.get("/check/{game_id}")
async def check_status(game_id: int):
    if game_id not in games:
        return {"game Id not in games!!!"}
    arr = games[game_id]

    for row in arr:
        if row[0] == row[1] == row[2] != " ":
            return {"game": "finished", "winner": row[0]}

    for column in range(0, 3):
        if arr[0][column] == arr[1][column] == arr[2][column] != " ":
            return {"game": "finished", "winner": arr[0][column]}

    if arr[0][0] == arr[1][1] == arr[2][2] != " ":
        return {"game": "finished", "winner": arr[0][0]}

    if arr[0][2] == arr[1][1] == arr[2][0] != " ":
        return {"game": "finished", "winner": arr[0][2]}

    if all(arr[i][j] != " " for i in range(3) for j in range(3)):
        return {"game": "finished", "winner": "null"}

    return {"game": "in_progress"}


@app.get("/history")
async def get_history():
    return history
