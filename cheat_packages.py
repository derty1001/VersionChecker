import zipfile

# Пакеты (папки) внутри JAR, наличие которых считается читом
CHEAT_PACKAGES = [
    "baritone/",
    "ViaVersion/",
]

# Точные имена .class файлов, наличие которых считается читом
# Требуется полное совпадение имени (без частичных совпадений)
CHEAT_CLASSES = [
    "AimAssist.class",
    "AimAssistModule.class",
    "ShiftTap.class",
    "ShiftTapModule.class",
    "AutoShiftTap.class",
    "AutoShiftTapModule.class",
    "ESP.class",
    "ESPModule.class",
    "ElytraSwap.class",
    "ElytraSwapModule.class",
    "FreeCam.class",
    "FreeCamModule.class",
]

# Специальные хеши файлов с кастомными сообщениями
SPECIAL_HASHES = {
    "83B1AE75C38055FB3B199065F6F023EB0D6F9D92CEAB8EB9F00A20AF969866E1": "Визуал, надо запустить и проверить вручную.",
}


def _normalize_path(path: str) -> str:
    """Нормализация пути внутри ZIP/JAR"""
    return path.replace("\\", "/")


def scan_jar_for_cheats(jar_path: str) -> list[str]:
    """
    Сканирует JAR на наличие чит-пакетов и чит-классов.
    Возвращает список строк с описанием найденного.
    """
    found = []
    try:
        with zipfile.ZipFile(jar_path, 'r') as zf:
            for info in zf.infolist():
                name = _normalize_path(info.filename)
                lower_name = name.lower()

                # Проверка по папкам (регистр не важен для путей)
                for pkg in CHEAT_PACKAGES:
                    pkg_lower = pkg.lower()
                    if lower_name.startswith(pkg_lower) or ("/" + pkg_lower) in lower_name:
                        desc = f"Найден пакет: {pkg.rstrip('/')}"
                        if desc not in found:
                            found.append(desc)
                        break

                # Проверка по точному имени класса (регистр важен)
                if "/" in name:
                    basename = name[name.rfind("/") + 1 :]
                else:
                    basename = name

                if basename in CHEAT_CLASSES:
                    desc = f"Найден класс: {basename}"
                    if desc not in found:
                        found.append(desc)

    except Exception:
        # При ошибке чтения JAR возвращаем пустой список
        pass

    return found


def check_special_hash(file_hash: str) -> str | None:
    """
    Проверяет хеш файла на специальные метки.
    Возвращает сообщение или None.
    """
    if not file_hash:
        return None
    return SPECIAL_HASHES.get(file_hash.upper())