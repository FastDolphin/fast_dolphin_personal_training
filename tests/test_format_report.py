from utils import Config, Prompts, format_report_with_gpt, ReportWithMetadata, MetaData
import os
from typeguard import typechecked
import pytest


@pytest.fixture
def config() -> Config:
    return Config()


@pytest.fixture
def prompts() -> Prompts:
    return Prompts()


@pytest.fixture
def client_report() -> str:
    return (
        "Я сделал все тренировочные дни и все упражнения. На ягодичном мостике у меня очень уставали"
        "икроножные мышцы и мне пришлось сделать 10 повторений, вместо 20. Остальное сделал по плану"
    )


@typechecked
def test_format_report(config, prompts, client_report) -> None:
    metadata: MetaData = MetaData(TgId=os.environ["ADMIN_CHAT_ID"], Year=2023, Week=1)
    report: ReportWithMetadata = format_report_with_gpt(
        config, prompts, metadata, client_report
    )
    assert report.allDaysDone
    assert report.allExercisesDone
    assert report.ProblematicExercises
