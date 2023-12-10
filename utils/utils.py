import json
import os
from typing import Dict, Any
from typeguard import typechecked
from logging import Logger
from .consts import Config
from datetime import date


@typechecked
def load_messages(message_path: str, logger: Logger) -> Dict[str, Any]:
    if not os.path.exists(message_path):
        raise FileNotFoundError("Messages are not found")

    try:
        with open(message_path, "r", encoding="utf-8") as file:
            messages: Dict[str, Any] = json.load(file)
            logger.info(f"Successfully loaded messages from {message_path}")
        return messages
    except Exception as e:
        logger.error(f"Failed to load messages from {message_path} due to error: {e}")
        return {}


@typechecked
def convert_json_personal_training_to_human_readable(data: Dict[str, Any]) -> str:
    output = []
    # Извлекаем общие данные
    in_gym: bool = data["inGym"]
    year: int = int(data["Year"])
    week: int = int(data["Week"])
    day: int = int(data["Day"])

    # Форматируем заголовок
    title = f"День {day} КД {week} Год {year} - еще одна тренировочка, солнышко!!! 🌞\n"
    output.append(title)

    # Форматируем зал или улица
    gym_or_outdoor: str = (
        "🏋️‍♀️ Ой, как здорово! Сегодня тренировочка в тренажерном зале! 💪\n"
        if in_gym
        else "🌳 Ура! Сегодня тренируемся на свежем воздухе! 🍃\n"
    )
    output.append(gym_or_outdoor)

    output.append("Твои упражнения на сегодня:\n")

    # Извлекаем и форматируем каждое упражнение
    for index, exercise in enumerate(data["Exercises"], 1):
        name = exercise["Name"]
        n_sets = int(exercise["nSets"])
        n_reps = int(exercise["nReps"])
        time = exercise["Time"]
        time_units = "мин" if exercise["TimeUnits"] == "мин" else "сек"
        comments = exercise["Comments"]

        if time and time != 0.0:
            time = int(time)
            exercise_info = (
                f"{index}. {name} - {n_sets} серии по {time} {time_units}. 🌟"
            )
        else:
            exercise_info = (
                f"{index}. {name} - {n_sets} серии по {n_reps} повторений. ✨"
            )

        if comments:
            exercise_info += f"\n    💬 Комментарии: {comments}\n"

        output.append(exercise_info)

    # Извлекаем итоговые статистики
    total_exercises = int(data["TotalNumberExercises"])
    total_time = int(data["TotalTime"] / 60)  # Конвертируем секунды в минуты
    output.append(f"\n🔥 Всего упражнений сегодня: {total_exercises} - ты молодец!")
    output.append(
        f"⏱ Общее время тренировки: примерно {total_time} минут - замечательно!"
    )

    return "\n".join(output)

    # return "Yet such."


@typechecked
def is_admin(cfg: Config, user_chat_id: str) -> bool:
    return user_chat_id == cfg.ADMIN_CHAT_ID


@typechecked
def is_client(cfg: Config, user_chat_id: str) -> bool:
    return user_chat_id in cfg.CLIENT_CHAT_ID


@typechecked
def fetch_calender_week() -> int:
    return date.today().isocalendar()[1]
