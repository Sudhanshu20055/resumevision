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
Fill in the response fields based on this resume. Be specific to THIS
resume's actual content. Do not invent experience that isn't there. If
information is genuinely absent, say so plainly rather than guessing.
Keep every string field free of unescaped quotes or line breaks that could
break JSON formatting."""

_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "candidate_name": {"type": "string", "nullable": True},
        "ats_score": {"type": "integer"},
        "ats_score_reasoning": {"type": "string"},
        "extracted_skills": {
            "type": "object",
            "properties": {
                "technical": {"type": "array", "items": {"type": "string"}},
                "soft": {"type": "array", "items": {"type": "string"}},
                "tools_and_technologies": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["technical", "soft", "tools_and_technologies"],
        },
        "sections_found": {"type": "array", "items": {"type": "string"}},
        "missing_sections": {"type": "array", "items": {"type": "string"}},
        "weak_sections": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "section": {"type": "string"},
                    "issue": {"type": "string"},
                    "suggestion": {"type": "string"},
                },
                "required": ["section", "issue", "suggestion"],
            },
        },
        "improvement_suggestions": {"type": "array", "items": {"type": "string"}},
        "keyword_gaps": {"type": "array", "items": {"type": "string"}},
        "estimated_experience_level": {
            "type": "string",
            "enum": ["Entry-level", "Mid-level", "Senior", "Lead/Executive"],
        },
        "strengths": {"type": "array", "items": {"type": "string"}},
        "interview_questions": {
            "type": "object",
            "properties": {
                "technical": {"type": "array", "items": {"type": "string"}},
                "behavioral": {"type": "array", "items": {"type": "string"}},
                "role_specific": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["technical", "behavioral", "role_specific"],
        },
        "overall_summary": {"type": "string"},
    },
    "required": [
        "ats_score", "ats_score_reasoning", "extracted_skills", "sections_found",
        "missing_sections", "weak_sections", "improvement_suggestions",
        "keyword_gaps", "estimated_experience_level", "strengths",
        "interview_questions", "overall_summary",
    ],
}


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
            "response_schema": _RESPONSE_SCHEMA,
            "max_output_tokens": 8192,
        },
    )


def _strip_code_fences(text: str) -> str:
    """Defensive cleanup in case the model wraps JSON in ``` fences anyway."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    return text


def _repair_json(text: str) -> str:
    """Best-effort cleanup for near-valid JSON (trailing commas, stray text)."""
    text = re.sub(r",\s*([\]}])", r"\1", text)
    last_brace = text.rfind("}")
    if last_brace != -1:
        text = text[: last_brace + 1]
    return text


def analyze_resume(resume_text: str, job_description: str | None = None) -> dict:
    """
    Send resume text to Gemini and return a parsed analysis dict.
    """
    model = _get_model()

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

    last_error = None
    for attempt in range(2):
        try:
            response = model.generate_content(prompt)
            raw_text = response.text
        except Exception as exc:
            raise GeminiAnalysisError(f"Gemini API request failed: {exc}") from exc

        if not raw_text:
            last_error = "Gemini returned an empty response."
            continue

        cleaned = _strip_code_fences(raw_text)

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        try:
            return json.loads(_repair_json(cleaned))
        except json.JSONDecodeError as exc:
            last_error = str(exc)
            continue

    raise GeminiAnalysisError(
        f"Couldn't parse Gemini's response as JSON: {last_error}"
    )