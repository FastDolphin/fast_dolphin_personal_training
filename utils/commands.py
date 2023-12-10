from pydantic import BaseModel


class UserCommands(BaseModel):
    start: str = "Начать"
    menu: str = "🔍 Меню"


class ClientCommands(UserCommands):
    start: str = "Начать"
    menu: str = "🔍 Меню"
    get_personal_training: str = "🦾 Получить персональную тренировку"


class AdminCommands(ClientCommands):
    pass


class Commands(BaseModel):
    User: UserCommands = UserCommands()
    Client: ClientCommands = ClientCommands()
    Admin: AdminCommands = AdminCommands()
