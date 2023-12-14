from pydantic import BaseModel


class Prompts(BaseModel):
    System: str = (
        "Your job is to analyze a fitness training report and and convert the information into a structured "
        "JSON format. The report details the users training activities, any injuries or issues they faced, "
        "and any exercises they could not complete or found difficult. The response should be in "
        "a JSON format suitable for "
        "direct conversion into a Python dictionary without any additional comments. ```Пример: На этой "
        "неделе я сделала все тренировочные дни, в них я сделала все упражнения, кроме приседаний со "
        "штангой, так как у меня болело правое колено. В остальном все хорошо и проблем не было.``` Ответ: "
        '```{"isInjured": true, "allDaysDone": true, "allExercisesDone": false, "ProblematicExercises": ['
        '"приседания со штангой"], "Comments": null}``` '
    )
