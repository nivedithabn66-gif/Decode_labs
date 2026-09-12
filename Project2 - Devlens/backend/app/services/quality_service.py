import re
from typing import Dict, Any, List

def calculate_issue_quality_score(title: str, description: str, steps: str = "", expected: str = "", actual: str = "", environment: str = "", logs: str = "") -> Dict[str, Any]:
    """
    Transparent Issue Quality Evaluator.
    Scores 0-100 based on presence of key developer triage elements and returns missing suggestions.
    """
    full_text = f"{title}\n{description}\n{steps}\n{expected}\n{actual}\n{environment}\n{logs}".lower()
    
    score = 0
    breakdown = {}
    missing_items = []

    # 1. Clear Title (20 pts)
    title_words = title.strip().split()
    if len(title_words) >= 4 and len(title) >= 12 and not any(vague in title.lower() for vague in ["help", "bug", "issue", "test", "problem"]):
        score += 20
        breakdown["clear_title"] = 20
    elif len(title_words) >= 2:
        score += 10
        breakdown["clear_title"] = 10
        missing_items.append("Make the title more descriptive (at least 4-5 words detailing the symptom).")
    else:
        breakdown["clear_title"] = 0
        missing_items.append("Provide a clear title summarizing the problem.")

    # 2. Detailed Description (25 pts)
    desc_words = description.strip().split()
    if len(desc_words) >= 30:
        score += 25
        breakdown["detailed_description"] = 25
    elif len(desc_words) >= 10:
        score += 15
        breakdown["detailed_description"] = 15
        missing_items.append("Expand the description with more context (aim for >30 words).")
    else:
        breakdown["detailed_description"] = 0
        missing_items.append("Provide a comprehensive description of the issue or feature request.")

    # 3. Steps to Reproduce (20 pts)
    has_steps_section = bool(steps.strip())
    has_steps_keywords = any(kw in full_text for kw in ["steps to reproduce", "reproduction steps", "to reproduce", "step 1", "how to reproduce"])
    if has_steps_section or has_steps_keywords:
        score += 20
        breakdown["reproduction_steps"] = 20
    else:
        breakdown["reproduction_steps"] = 0
        missing_items.append("Reproduction steps")

    # 4. Expected & Actual Behavior (15 pts)
    has_exp_act = (bool(expected.strip()) or bool(actual.strip())) or any(kw in full_text for kw in ["expected", "instead of", "actual behavior", "should happen", "behavior"])
    if has_exp_act:
        score += 15
        breakdown["expected_actual_behavior"] = 15
    else:
        breakdown["expected_actual_behavior"] = 0
        missing_items.append("Expected vs Actual behavior details")

    # 5. Environment & Version Information (10 pts)
    has_env = bool(environment.strip()) or any(kw in full_text for kw in ["os:", "version", "browser", "python 3", "v1.", "node", "environment", "windows", "linux", "mac"])
    if has_env:
        score += 10
        breakdown["environment_info"] = 10
    else:
        breakdown["environment_info"] = 0
        missing_items.append("Environment or version information (OS, version, browser, runtime)")

    # 6. Error Logs or Stacktrace (10 pts)
    has_logs = bool(logs.strip()) or any(kw in full_text for kw in ["traceback", "exception", "error:", "nullpointer", "stacktrace", "log", "500 internal", "400 bad"])
    if has_logs:
        score += 10
        breakdown["error_logs"] = 10
    else:
        breakdown["error_logs"] = 0
        # Only suggest logs if it looks like a bug
        if any(b in full_text for b in ["crash", "fail", "error", "bug"]):
            missing_items.append("Error log or stacktrace output")

    # Quality Grade
    if score >= 85:
        grade = "Excellent"
    elif score >= 70:
        grade = "Good"
    elif score >= 50:
        grade = "Moderate"
    else:
        grade = "Needs Improvement"

    return {
        "quality_score": min(score, 100),
        "grade": grade,
        "score_breakdown": breakdown,
        "missing_elements": missing_items,
        "actionable_suggestions": [f"Add missing: {item}" for item in missing_items]
    }
