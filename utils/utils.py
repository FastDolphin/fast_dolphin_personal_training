import json
import os

import requests
from requests import Response
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from typeguard import typechecked
from logging import Logger
from .consts import Config
from datetime import date
from .prompts import Prompts


class Report(BaseModel):
    isInjured: bool = False
    allDaysDone: bool = True
    allExercisesDone: bool = True
    ProblematicExercises: List[str] = []
    Comments: Optional[str] = None


class MetaData(BaseModel):
    TgId: int
    Year: int
    Week: int


class ReportWithMetadata(Report):
    TgId: int
    Year: int
    Week: int

    @classmethod
    def from_report_and_metadata(
        cls, report: Report, metadata: MetaData
    ) -> "ReportWithMetadata":
        return cls(
            TgId=metadata.TgId,
            Year=metadata.Year,
            Week=metadata.Week,
            isInjured=report.isInjured,
            allDaysDone=report.allDaysDone,
            allExercisesDone=report.allExercisesDone,
            ProblematicExercises=report.ProblematicExercises,
            Comments=report.Comments,
        )


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
    title: str = (
        f"День {day} КД {week} Год {year} - еще одна тренировочка, солнышко!!! 🌞\n"
    )
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


@typechecked
def fetch_current_year() -> int:
    return date.today().year


@typechecked
def format_report_with_gpt(
    cfg: Config, prompts: Prompts, metadata: MetaData, client_report: str
) -> ReportWithMetadata:
    messages: List[Dict[str, str]] = [
        {"role": "system", "content": prompts.System},
        {"role": "user", "content": client_report},
    ]

    headers: Dict[str, str] = {
        "Authorization": f"Bearer {cfg.OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    data: Dict[str, Any] = {"model": cfg.MODEL_TYPE, "messages": messages}

    response: Response = requests.post(cfg.OPENAI_API_URL, json=data, headers=headers)
    response.raise_for_status()
    json_response: Dict[str, Any] = response.json()

    # Process the last response from the assistant to create the Report object
    # Assuming the last message contains the response in JSON format
    last_response: str = json_response["choices"][0]["message"]["content"]
    last_response = last_response.replace("False", "false").replace("True", "true")
    try:
        report_data: Dict[str, Any] = json.loads(last_response)
    except json.decoder.JSONDecodeError:
        cleaned_response = last_response.strip("`")
        report_data = json.loads(cleaned_response)
    report: Report = Report(**report_data)
    return ReportWithMetadata.from_report_and_metadata(report=report, metadata=metadata)
