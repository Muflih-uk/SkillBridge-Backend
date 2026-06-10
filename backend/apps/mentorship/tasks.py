import json
import logging

from celery import shared_task
from django.conf import settings
from google import genai

from .models import AIMatchResult, LearningPath

logger = logging.getLogger(__name__)

client = genai.Client(api_key=settings.GEMINI_API_KEY)


def extract_json(text: str):
    """
    Extract JSON from Gemini responses that may contain markdown.
    """
    text = text.strip()

    if text.startswith("```json"):
        text = text.replace("```json", "", 1)

    if text.startswith("```"):
        text = text.replace("```", "", 1)

    if text.endswith("```"):
        text = text[:-3]

    return json.loads(text.strip())


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=300,
    retry_kwargs={"max_retries": 5},
)
def generate_learning_path_task(self, path_id, goal):
    try:
        prompt = f"""
        Act as a professional technical mentor.

        Generate a structured week-by-week learning roadmap
        for the following goal:

        {goal}

        Return ONLY valid JSON.

        Example:
        {{
            "weeks": [
                {{
                    "week": 1,
                    "topics": ["Topic A", "Topic B"]
                }}
            ]
        }}
        """

        logger.info(
            "Generating learning path | path_id=%s | goal_length=%s",
            path_id,
            len(goal),
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
        )

        logger.info("Gemini response received")

        cleaned_json = extract_json(response.text)

        path = LearningPath.objects.get(id=path_id)
        path.title = f"AI Pathway: {goal[:30]}"
        path.content = cleaned_json
        path.save()

        logger.info("Learning path saved successfully")

    except Exception as e:
        logger.exception(
            "Failed generating learning path. path_id=%s error=%s",
            path_id,
            str(e),
        )

        raise


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=300,
    retry_kwargs={"max_retries": 5},
)
def generate_ai_mentor_matches_task(
    self,
    result_id,
    goal,
    structural_mentors_list,
):
    try:
        prompt = f"""
        Compare this learner goal:

        {goal}

        Against these mentors:

        {json.dumps(structural_mentors_list, ensure_ascii=False)}

        Rank the top 5 mentors.

        Return ONLY valid JSON.

        Example:
        [
            {{
                "mentor_id": "uuid",
                "score": 95,
                "rationale": "reason"
            }}
        ]
        """

        logger.info(
            "Generating mentor matches | result_id=%s | mentors=%s",
            result_id,
            len(structural_mentors_list),
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
        )

        parsed_results = extract_json(response.text)

        result = AIMatchResult.objects.get(id=result_id)
        result.results = parsed_results
        result.save()

        logger.info("Mentor matches saved successfully")

    except Exception as e:
        logger.exception(
            "Failed mentor matching. result_id=%s error=%s",
            result_id,
            str(e),
        )

        raise
