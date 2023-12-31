import json
import os

import requests
from requests import Response
from pydantic import BaseModel, validator
from typing import Dict, Any, Optional, List, Literal, Union, Final
from typeguard import typechecked
from logging import Logger
from .consts import Config
from datetime import date
from .prompts import Prompts

CoordinationType = Union[
    Literal["в/к"], Literal["н/р"], Literal["н/н"], Literal["упр."]
]


class CommonTrainingInfo(BaseModel):
    trainingType: Union[Literal["fitness"], Literal["swimming"]]
    inGym: bool
    inSwimmingPool: bool
    Year: int
    Week: int
    Day: int

    @validator("inGym")
    def validate_in_gym(cls, in_gym, values):
        if in_gym and values.get("trainingType") != "fitness":
            raise ValueError("inGym can only be True if trainingType is 'fitness'")
        return in_gym

    @validator("inSwimmingPool")
    def validate_in_swimming_pool(cls, in_swimming_pool, values):
        if in_swimming_pool and values.get("trainingType") != "swimming":
            raise ValueError(
                "inSwimmingPool can only be True if trainingType is 'swimming'"
            )
        return in_swimming_pool


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
def convert_json_to_human_readable(resources: List[Dict[str, Any]]) -> str:
    week_output: List[str] = []
    if not resources:
        raise ValueError("Нет тренировок для форматирования")
    for data in resources:
        common_info: CommonTrainingInfo = CommonTrainingInfo(**data)
        day_output: List[str] = []
        # Форматируем заголовок
        title: str = format_title(common_info)
        day_output.append(title)
        day_output.append("Твои упражнения на сегодня:\n")

        converted: str
        if common_info.trainingType == "fitness":
            converted = convert_fitness_exercises(data["Exercises"])
        elif common_info.trainingType == "swimming":
            converted = convert_swimming_exercises(data["Exercises"])
        else:
            raise ValueError(
                "This training type is not supported! Supported: ['fitness', 'swimming']"
            )

        day_output.append(converted)

        # Извлекаем итоговые статистики
        total_exercises = int(data["TotalNumberExercises"])
        total_day_time = int(data["TotalTime"] / 60)  # Конвертируем секунды в минуты
        day_output.append(
            f"\n🔥 Всего упражнений сегодня: {total_exercises} - ты молодец!"
        )
        if total_day_time != 0:
            day_output.append(
                f"⏱ Общее время тренировки: примерно {total_day_time} мин - замечательно! \n"
            )
        total_day_volume: int = int(data["TotalVolume"])
        if total_day_volume != 0:
            day_output.append(
                f"⏱Объем тренировки: {total_day_volume} {data['TotalVolumeUnits']} - круто! \n"
            )
        week_output.append("\n".join(day_output))
        week_output.append("\n" + separator())

    total_trainings_week: str = (
        f" 🔥 На неделе {common_info.Week} всего {len(resources)} трен."
    )
    week_output.append(total_trainings_week)
    return "\n".join(week_output)


@typechecked
def convert_fitness_exercises(exercises: List[Dict[str, Any]]) -> str:
    converted: List[str] = []
    for index, exercise in enumerate(exercises, 1):
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
            exercise_info += f"\n💬 Комментарии: {comments}\n"

        converted.append(exercise_info)
    return "\n".join(converted)


@typechecked
def convert_swimming_exercises(exercises: List[Dict[str, Any]]) -> str:
    max_speed: int = 6
    converted: List[str] = []

    # iterate over each exercise
    for i, exercise in enumerate(exercises, start=1):
        volume = exercise["Volume"]
        time = exercise["Time"]
        volume_units = exercise["VolumeUnits"]
        time_units = exercise["TimeUnits"]
        stroke = exercise["Stroke"]
        speed = exercise["Speed"]
        comments = exercise["Comments"].capitalize()

        # use Volume if it's not None, otherwise use Time
        volume_or_time = (
            f"{volume:.0f}{adjust_units(volume_units)}"
            if is_volume_provided(volume)
            else f"{time:.0f}{adjust_units(time_units)}"
        )

        coordination: CoordinationType = handle_coordination(exercise)
        equipment: str = handle_equipment(exercise)

        exercise_info = (
            f"{i}. {volume_or_time} {stroke} "
            f"{coordination}, {equipment}"
            f" скорость {speed}/{max_speed}"
        )
        if comments:
            exercise_info += f"\n💬 Комментарии: {comments}\n"

        converted.append(exercise_info)
    converted.append(swim_ending())
    return "\n".join(converted)


@typechecked
def handle_coordination(exercise: Dict[str, Any]) -> CoordinationType:
    if exercise["Arms"] and exercise["Legs"]:
        return "в/к"
    elif not exercise["Arms"] and not exercise["Legs"]:
        return "упр."
    elif exercise["Arms"] and not exercise["Legs"]:
        return "н/р"
    else:
        return "н/н"


@typechecked
def handle_equipment(exercise: Dict[str, Any]) -> str:
    equipment: str = ""
    ###MAIN EQUIPMENT####
    if exercise["Equipment"]["KickBoard"]:
        equipment: str = equipment + "с доской"
    elif exercise["Equipment"]["PullBuoy"]:
        equipment: str = equipment + "с колобашкой"

    ###ADDITIONAL EQUIPMENT####
    if exercise["Equipment"]["Paddles"]:
        equipment: str = equipment + "с лопатками"
    if exercise["Equipment"]["Snorkel"]:
        equipment: str = equipment + "с трубкой"

    return equipment


@typechecked
def handle_total_duration(total_week_time: int) -> str:
    if total_week_time == 0.0:
        return ""
    total_duration: str = (
        f"⏱ Общая продолжительность (+/-): {total_week_time // 60} ч "
        f"{round((total_week_time / 60) * 60 - (total_week_time // 60) * 60)} мин "
    )
    return total_duration


@typechecked
def is_volume_provided(volume: float) -> bool:
    return (volume is not None) and (volume != 0)


@typechecked
def adjust_units(unit: str) -> str:
    units: Dict[str, str] = {"m": "м", "min": "мин"}
    return units.get(unit, unit)


@typechecked
def format_title(common_info: CommonTrainingInfo, separator: str = "") -> str:
    title: str
    if common_info.trainingType == "swimming" and common_info.inSwimmingPool:
        title = (
            f"🏊‍ День {common_info.Day}, Неделя {common_info.Week} (в бассейне) 🏊‍️\n"
        )
    elif common_info.trainingType == "swimming" and not common_info.inSwimmingPool:
        title = f"🌊 День {common_info.Day}, Неделя {common_info.Week} (на открытой воде) 🌊\n"
    elif common_info.trainingType == "fitness" and common_info.inGym:
        title = f"🏋️ День {common_info.Day}, Неделя {common_info.Week} (в тренажерном зале) 🏋️\n"

    elif common_info.trainingType == "fitness" and not common_info.inGym:
        title = f"🏡 День {common_info.Day}, Неделя {common_info.Week} (дома или на улице) 🏡\n"

    else:
        raise NotImplementedError

    return title + separator


@typechecked
def separator(
    n_seps: int = 20, sep: str = "-", n_endl: int = 1, endl: str = "\n"
) -> str:
    return sep * n_seps + n_endl * endl


@typechecked
def swim_ending(
    n_waves: int = 3, wave: str = "🌊", n_endl: int = 0, endl: str = "\n"
) -> str:
    return n_waves * wave + n_endl * endl


@typechecked
def is_admin(cfg: Config, user_chat_id: str) -> bool:
    return user_chat_id == cfg.ADMIN_CHAT_ID


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


@typechecked
def has_access(cfg: Config, api_token: str) -> bool:
    params: Dict[str, str] = {"api_key": api_token}
    get_request: Response = requests.get(
        f"{cfg.BACKEND_API}/{cfg.VERSION}/{cfg.ALLOWED_PERSONAL_TRAINING}",
        params=params,
    )
    if get_request.status_code != 403:
        get_request.raise_for_status()
    else:
        return False
    result: Dict[str, Any] = get_request.json()
    is_allowed: bool = result["Resources"][0]["Allowed"]
    return is_allowed
