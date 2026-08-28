CHEAT_KEYWORDS = [
    "Akrien",
    "Celestial",
    "Calestial",
    "Impact",
    "Meteor",
    "LiquidBounce",
    "Wurst",
    "Inertia",
    "Neverhook",
    "Delta",
    "Expensive",
    "Minced",
    "ThunderHack",
    "Aristois",
    "Bleachhack",
    "VenusFree",
]


def is_cheat_filename(filename: str) -> bool:
    """Проверяет, содержит ли имя файла ключевые слова читов"""
    for keyword in CHEAT_KEYWORDS:
        if keyword in filename:
            return True
    return False


def get_detected_cheat(filename: str) -> str | None:
    """Возвращает название обнаруженного чита или None"""
    for keyword in CHEAT_KEYWORDS:
        if keyword in filename:
            return keyword
    return None