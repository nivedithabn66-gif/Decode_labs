from typing import Dict, Any

def recommend_priority_and_team(title: str, description: str, category: str = "") -> Dict[str, Any]:
    """
    Transparent Heuristic & Keyword Recommendation Module.
    Generates priority ratings and engineering team assignments based on signal weights.
    """
    text = f"{title} {description}".lower()

    # --- 1. Priority Recommendation ---
    critical_signals = ["crash", "security", "data loss", "production down", "vulnerability", "fatal", "out of memory", "overflow", "leak", "kernel panic"]
    high_signals = ["exception", "error", "fails", "fail", "blocking", "500", "broken", "timeout", "nullpointer", "unhandled"]
    medium_signals = ["feature", "enhancement", "ui", "slow", "add", "support", "button", "modal", "page"]
    
    if any(sig in text for sig in critical_signals):
        priority = "Critical"
        p_reason = "Contains severe fault indicators (crash, data loss, security, kernel/memory panic)."
    elif any(sig in text for sig in high_signals) or category.lower() == "bug":
        priority = "High"
        p_reason = "Identified functional error, exception, or blocking defect."
    elif any(sig in text for sig in medium_signals) or category.lower() == "feature":
        priority = "Medium"
        p_reason = "Standard feature request or functional improvement."
    else:
        priority = "Low"
        p_reason = "General inquiry, documentation question, or minor update."

    # --- 2. Team Recommendation ---
    team_signals = {
        "Frontend": ["ui", "css", "button", "mobile", "react", "navbar", "flexbox", "view", "theme", "dark mode", "layout", "tab", "display", "font", "component"],
        "Backend": ["api", "rest", "endpoint", "500", "auth", "jwt", "python", "json", "handler", "service", "route", "http", "controller", "payload"],
        "Database": ["sql", "postgres", "connection pool", "query", "database", "orm", "migration", "table", "nullpointer", "row", "column", "exhausted"],
        "DevOps": ["docker", "kubernetes", "helm", "nginx", "ingress", "deployment", "ci/cd", "celery", "timeout", "yaml", "config", "server", "worker"],
        "Security": ["vulnerability", "token", "auth", "session", "cors", "xss", "csrf", "sso", "security", "permission", "leak", "exposure"],
        "QA / Testing": ["test", "coverage", "mock", "pytest", "unit", "e2e", "cypress", "assertion"],
        "Documentation": ["docs", "readme", "guide", "tutorial", "howto", "question", "how do i", "example"]
    }

    team_scores = {team: 0 for team in team_signals}
    for team, keywords in team_signals.items():
        for kw in keywords:
            if kw in text:
                team_scores[team] += 1

    best_team = max(team_scores, key=team_scores.get)
    if team_scores[best_team] == 0:
        best_team = "Backend" if category.lower() == "bug" else "Frontend" if category.lower() == "feature" else "Documentation"

    return {
        "priority_recommendation": {
            "level": priority,
            "type": "Heuristic Rule Recommendation",
            "rationale": p_reason
        },
        "suggested_team": {
            "name": best_team,
            "type": "Keyword Rule Recommendation",
            "confidence_score": min(1.0, (team_scores[best_team] + 1) * 0.25)
        }
    }
