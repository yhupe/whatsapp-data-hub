from fastapi import FastAPI
from enum import Enum

app = FastAPI()

class UserName(str, Enum):
    hannes = "Hannes"
    anna = "Anna"
    teifi = "Teifi"



@app.get("/users/{user_name}")
async def read_users(user_name: UserName):
    if user_name is UserName.hannes:
        return {"Who is the coolest guy?": user_name}

    if user_name is UserName.anna:
        return {"Who is the most beautiful girlfriend?": user_name}

    if user_name.value == "Teifi":
        return {"Who is a good boy?": user_name, "user_name.value": user_name.value}

