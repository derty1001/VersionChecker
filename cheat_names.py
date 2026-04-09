# Проверка нечувствительна к регистру

CHEAT_KEYWORDS = [
    # Основные читы
    "akrien",
    "celestial",
    "calestial",  # частая опечатка
    "impact",
    "meteor",
    "liquidbounce",
    "wurst",
    "inertia",
    "neverhook",
    "delta",
    "expensive",
    "minced",
    "thunderhack",

    # Дополнительные
    "aristois",
    "bleachhack",
    "lambda",
]


def is_cheat_filename(filename: str) -> bool:
    """Проверяет, содержит ли имя файла ключевые слова читов"""
    filename_lower = filename.lower()
    for keyword in CHEAT_KEYWORDS:
        if keyword in filename_lower:
            return True
    return False


def get_detected_cheat(filename: str) -> str | None:
    """Возвращает название обнаруженного чита или None"""
    filename_lower = filename.lower()
    for keyword in CHEAT_KEYWORDS:
        if keyword in filename_lower:
            return keyword
    return None