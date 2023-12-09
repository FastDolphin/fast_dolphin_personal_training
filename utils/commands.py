from typing import Dict
from pydantic import BaseModel


class Commands(BaseModel):
    ADMIN: Dict[str, str] = {"/start": "Начать", "/menu": "Меню"}

    CLIENT: Dict[str, str] = {"/start": "Начать", "/menu": "Меню"}

    USER: Dict[str, str] = {"/start": "Начать", "/menu": "Меню"}
