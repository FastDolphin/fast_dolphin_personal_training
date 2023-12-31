from utils import convert_json_to_human_readable, separator
from utils.utils import handle_coordination, CoordinationType
import pytest
from typing import Dict, Any, Literal
import os
import json


@pytest.fixture
def legs() -> Dict[str, Any]:
    return {
        "Volume": 200,
        "VolumeUnits": "m",
        "Time": None,
        "TimeUnits": "min",
        "Stroke": "кроль",
        "Speed": 1,
        "Legs": True,
        "Arms": False,
        "Comments": "разминка, свободные упражнения",
    }


@pytest.fixture
def arms() -> Dict[str, Any]:
    return {
        "Volume": 200,
        "VolumeUnits": "m",
        "Time": None,
        "TimeUnits": "min",
        "Stroke": "кроль",
        "Speed": 1,
        "Legs": False,
        "Arms": True,
        "Comments": "разминка, свободные упражнения",
    }


@pytest.fixture
def neither_arms_nor_legs() -> Dict[str, Any]:
    return {
        "Volume": 200,
        "VolumeUnits": "m",
        "Time": None,
        "TimeUnits": "min",
        "Stroke": "кроль",
        "Speed": 1,
        "Legs": False,
        "Arms": False,
        "Comments": "разминка, свободные упражнения",
    }


@pytest.fixture
def both_arms_and_legs() -> Dict[str, Any]:
    return {
        "Volume": 200,
        "VolumeUnits": "m",
        "Time": None,
        "TimeUnits": "min",
        "Stroke": "кроль",
        "Speed": 1,
        "Legs": True,
        "Arms": True,
        "Comments": "разминка, свободные упражнения",
    }


@pytest.fixture
def standard_separator() -> str:
    return separator()


@pytest.fixture
def test_files_dir() -> str:
    tests: Literal["tests"] = "tests"
    test_files_dir: Literal["test_data"] = "test_data"
    return os.path.join(tests, test_files_dir)


@pytest.fixture
def single_fitness_training(test_files_dir) -> Dict[str, Any]:
    file_path: str = os.path.join(test_files_dir, "single_fitness_training.json")
    with open(file_path) as f:
        fitness_training: Dict[str, Any] = json.load(f)
    return fitness_training


@pytest.fixture
def double_fitness_training(test_files_dir) -> Dict[str, Any]:
    file_path: str = os.path.join(test_files_dir, "double_fitness_training.json")
    with open(file_path) as f:
        fitness_training: Dict[str, Any] = json.load(f)
    return fitness_training


@pytest.fixture
def double_swimming_training(test_files_dir) -> Dict[str, Any]:
    file_path: str = os.path.join(test_files_dir, "double_swimming_training.json")
    with open(file_path) as f:
        swimming_training: Dict[str, Any] = json.load(f)
    return swimming_training


def test_convert_json_to_human_readable_single_fitness(
    single_fitness_training, standard_separator
):
    converted: str = convert_json_to_human_readable(
        single_fitness_training["Resources"]
    )
    assert standard_separator in converted
    assert "День 1" in converted


def test_convert_json_to_human_readable_double_fitness(
    double_fitness_training, standard_separator
):
    converted: str = convert_json_to_human_readable(
        double_fitness_training["Resources"]
    )
    assert standard_separator in converted
    assert "День 1" in converted
    assert "День 2" in converted


def test_convert_json_to_human_readable_double_swimming(
    double_swimming_training, standard_separator
):
    converted: str = convert_json_to_human_readable(
        double_swimming_training["Resources"]
    )
    assert standard_separator in converted
    assert "День 1" in converted
    assert "День 2" in converted


def test_handle_coordination_arms(arms):
    coordination: CoordinationType = handle_coordination(arms)
    assert coordination == "н/р"


def test_handle_coordination_legs(legs):
    coordination: CoordinationType = handle_coordination(legs)
    assert coordination == "н/н"


def test_handle_coordination_neither(neither_arms_nor_legs):
    coordination: CoordinationType = handle_coordination(neither_arms_nor_legs)
    assert coordination == "упр."


def test_handle_coordination_both(both_arms_and_legs):
    coordination: CoordinationType = handle_coordination(both_arms_and_legs)
    assert coordination == "в/к"
