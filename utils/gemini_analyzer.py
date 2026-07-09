"""
gemini_analyzer.py
Sends resume text (and optional job description) to the Google Gemini API
and returns a structured analysis: ATS score, extracted skills, missing/weak
sections, improvement suggestions, and tailored interview questions.
"""
import json
import os
import re

import google.generativeai as genai

DEFAULT_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")

_SYSTEM_INSTRUCTION = """You are an expert technical recruiter and ATS (Applicant \
Tracking System) specialist. You analyze resumes with the same rigor a Fortune \
500 recruiting team and an ATS parser would use. You are precise, honest, and \
constructive - you point out real weaknesses, not generic platitudes. \
You always respond with valid JSON only, no markdown fences, no commentary."""

_ANALYSIS_PROMPT_TEMPLATE = """Analyze the following resume{jd_clause}.

RESUME TEXT:
---
{resume_text}
---
{jd_block}
Return ONLY a valid JSON object (no markdown code fences, no extra text) with
EXACTLY this schema:

{{
  "candidate_name": string or null,
  "ats_score": integer from 0 to 100,
  "ats_score_reasoning": short string explaining the score,
  "extracted_skills": {{
      "technical": [list of strings],
      "soft": [list of strings],
      "tools_and_technologies": [list of strings]
  }},
  "sections_found": [list of resume section names actually present, e.g. "Summary", "Experience"],
  "missing_sections": [list of standard resume sections that are absent or should be added],
  "weak_sections": [
      {{"section": string, "issue": string, "suggestion": string}}
  ],
  "improvement_suggestions": [list of specific, actionable suggestions, at least 5],
  "keyword_gaps": [list of important keywords/skills missing, especially relevant if a job description was provided],
  "estimated_experience_level": one of "Entry-level", "Mid-level", "Senior", "Lead/Executive",
  "strengths": [list of 3-5 genuine strengths of this resume],
  "interview_questions": {{
      "technical": [5 questions tailored to this candidate's stated skills],
      "behavioral": [5 questions tailored to this candidate's experience],
      "role_specific": [3-5 questions tailored to the target role if inferable]
  }},
  "overall_summary": short 2-3 sentence summary of the resume's readiness for job applications
}}

Be specific to THIS resume's actual content. Do not invent experience that
isn't there. If information is genuinely absent, say so plainly rather than
guessing."""


class GeminiAnalysisError(Exception):
    """Raised when the Gemini API call fails or returns unusable content."""
    pass


def _get_model():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise GeminiAnalysisError(
            "GEMINI_API_KEY is not set. Add it to your .env file "
            "(see .env.example)."
        )
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(
        model_name=DEFAULT_MODEL,
        system_instruction=_SYSTEM_INSTRUCTION,
        generation_config={
            "temperature": 0.4,
            "response_mime_type": "application/json",
        },
    )


def _strip_code_fences(text: str) -> str:
    """Defensive cleanup in case the model wraps JSON in ``` fences anyway."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    return text


def analyze_resume(resume_text: str, job_description: str | None = None) -> dict:
    """
    Send resume text to Gemini and return a parsed analysis dict.

    Args:
        resume_text: plain text extracted from the uploaded resume.
        job_description: optional job description to tailor the analysis
                          (keyword gap matching, role-specific questions).

    Returns:
        Parsed JSON response as a Python dict.

    Raises:
        GeminiAnalysisError: on API failure or invalid/unparseable response.
    """
    model = _get_model()

    # Guard against extremely long resumes blowing up the prompt.
    trimmed_resume = resume_text[:15000]

    if job_description and job_description.strip():
        jd_clause = " against the target job description provided below"
        jd_block = f"\nTARGET JOB DESCRIPTION:\n---\n{job_description.strip()[:6000]}\n---\n"
    else:
        jd_clause = ""
        jd_block = ""

    prompt = _ANALYSIS_PROMPT_TEMPLATE.format(
        jd_clause=jd_clause, resume_text=trimmed_resume, jd_block=jd_block
    )

    try:
        response = model.generate_content(prompt)
        raw_text = response.text
    except Exception as exc:
        raise GeminiAnalysisError(f"Gemini API request failed: {exc}") from exc

    if not raw_text:
        raise GeminiAnalysisError("Gemini returned an empty response.")

    cleaned = _strip_code_fences(raw_text)

    try:
        result = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise GeminiAnalysisError(
            f"Couldn't parse Gemini's response as JSON: {exc}"
        ) from exc

    return result
