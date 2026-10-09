VALID_LOCATIONS = {"LAB-01", "AULA-201", "BIB-01"}
VALID_CATEGORIES = {"ELECTRICIDAD", "HIDRAULICA", "MOBILIARIO", "TIC"}
VALID_IMPACTS = {"BAJO", "ALTO"}


def parse_boolean(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, int) and value in (0, 1):
        return bool(value)
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "si", "sí", "on"}:
            return True
        if normalized in {"false", "0", "no", "off"}:
            return False
    return None


def validate_new_incident(data):
    location = str(data.get("location", "")).strip()
    category = str(data.get("category", "")).strip()
    description = str(data.get("description", "")).strip()
    impact = str(data.get("impact", "")).strip()
    risk_people = parse_boolean(data.get("risk_people"))

    errors = {}

    if location not in VALID_LOCATIONS:
        errors["location"] = "Ubicación no válida."

    if category not in VALID_CATEGORIES:
        errors["category"] = "Categoría no válida."

    if not 20 <= len(description) <= 500:
        errors["description"] = "La descripción debe tener entre 20 y 500 caracteres."

    if impact not in VALID_IMPACTS:
        errors["impact"] = "Impacto no válido."

    if risk_people is None:
        errors["risk_people"] = "El riesgo para personas debe indicarse como sí o no."

    cleaned = {
        "location": location,
        "category": category,
        "description": description,
        "impact": impact,
        "risk_people": risk_people,
    }
    return cleaned, errors


def calculate_priority(risk_people, impact):
    if bool(risk_people):
        return "CRITICA"
    if impact == "ALTO":
        return "ALTA"
    if impact == "BAJO":
        return "NORMAL"
    raise ValueError("Impacto no válido para calcular prioridad.")


def validate_solution(text):
    cleaned = str(text or "").strip()
    if not 20 <= len(cleaned) <= 800:
        return cleaned, "La solución debe tener entre 20 y 800 caracteres."
    return cleaned, None


def validate_reason(text):
    cleaned = str(text or "").strip()
    if not 10 <= len(cleaned) <= 300:
        return cleaned, "El motivo debe tener entre 10 y 300 caracteres."
    return cleaned, None
