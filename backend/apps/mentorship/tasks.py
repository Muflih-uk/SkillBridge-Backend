import json
import logging

from django.conf import settings
from google import genai

from apps.skills.models import Skill
from apps.users.models import MentorProfile, UserProfile

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


def generate_learning_path(path_id, goal):
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


def generate_ai_mentor_matches(result_id, structural_mentors_list, goal):
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


def generate_mentor_summary(mentor_id_str):
    try:
        user_profile = UserProfile.objects.get(id=mentor_id_str)
        mentor_profile = MentorProfile.objects.get(id=user_profile)

        skills = Skill.objects.filter(mentor=user_profile).values_list(
            "title", flat=True
        )
        skills_csv = (
            ", ".join(list(skills)) if skills else "No specific skills cataloged yet"
        )

        prompt = (
            f"Act as an expert technical recruiter. Generate a concise, high-impact, professional "
            f"one-sentence biography summary (maximum 30 words) for a mentor profile. "
            f"Base it exactly on this data:\n"
            f"- Display Name: {user_profile.display_name}\n"
            f"- Core Bio: {user_profile.bio or 'Experienced professional'}\n"
            f"- Years of Experience: {mentor_profile.experience_yrs} years\n"
            f"- Key Skills/Expertise: {skills_csv}\n"
            f"Return ONLY the raw summary sentence. Do not include quotes, wrappers, or introductory phrases."
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
        )

        cleaned_summary = response.text.strip().replace('"', "")
        mentor_profile.ai_summary = cleaned_summary
        mentor_profile.save()

    except Exception as e:
        logger.exception(
            "Failed to compile AI summary for mentor %s: %s",
            mentor_id_str,
            str(e),
        )
        raise
