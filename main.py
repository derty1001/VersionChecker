import os
import sys
import hashlib
import zipfile
import datetime
from datetime import datetime as dt
from pathlib import Path
import time
from collections import defaultdict

# Импорт баз данных
from hashes import MINECRAFT_HASHES
from cheat_names import is_cheat_filename, get_detected_cheat

# Информация о программе
APP_NAME = "Minecraft Version Checker"
APP_VERSION = "1.2.0"
APP_AUTHOR = "holyworld"


def is_frozen():
    """Проверка, скомпилирован ли скрипт в EXE"""
    return hasattr(sys, 'frozen')


def get_base_path():
    """Получение базового пути (рабочая директория для EXE)"""
    if is_frozen():
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def print_colored(text, color_code="\\033[0m"):
    """Цветной вывод в консоль"""
    colors = {
        "red": "\\033[91m",
        "green": "\\033[92m",
        "yellow": "\\033[93m",
        "cyan": "\\033[96m",
        "gray": "\\033[90m",
        "reset": "\\033[0m"
    }
    print(f"{colors.get(color_code, '')}{text}{colors['reset']}")


def main_menu():
    """Главное меню для выбора программы"""
    print(" ╔══════════════════════════════════════════════════╗")
    print(" ║             Minecraft Version Checker            ║")
    print(f" ║                                                  ║")
    print(" ╠══════════════════════════════════════════════════╣")
    print(" ║ 1. Проверка обычных версий                       ║")
    print(" ║ 2. Проверка LabyMod версий                       ║")
    print(" ║ 3. Выход                                         ║")
    print(" ╚══════════════════════════════════════════════════╝")
    choice = input("Выберите программу (1-3): ").strip()
    return choice


class MinecraftHashChecker:
    def __init__(self):
        self.script_dir = Path(__file__).parent if "__file__" in globals() else Path.cwd()
        self.reference_hashes = MINECRAFT_HASHES.copy()

    def find_minecraft_installations(self):
        """Поиск установок Minecraft"""
        possible_paths = [
            os.path.join(os.environ.get('APPDATA', ''), '.minecraft'),
            os.path.join(os.environ.get('APPDATA', ''), '.tlauncher', 'legacy', 'Minecraft', 'game'),
            os.path.join(os.environ.get('APPDATA', ''), '.tlauncher'),
            os.path.join(os.environ.get('APPDATA', ''), 'MultiMC', 'instances'),
            os.path.join(os.environ.get('APPDATA', ''), 'ATLauncher'),
            os.path.join(os.environ.get('APPDATA', ''), '.hmcl'),
            os.path.join(os.environ.get('APPDATA', ''), '.technic'),
            os.path.join(os.environ.get('APPDATA', ''), 'CurseForge', 'Games', 'Minecraft'),
        ]

        found_paths = []
        for path in possible_paths:
            if os.path.exists(path):
                found_paths.append(path)
                print(f"✅ Найден: {path}")

        return found_paths

    def calculate_file_hash(self, filepath):
        """Вычисление SHA256 хеша файла"""
        hash_func = hashlib.sha256()
        try:
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hash_func.update(chunk)
            return hash_func.hexdigest().upper()
        except Exception as e:
            print(f"    ⚠️ Ошибка чтения файла {filepath}: {e}")
            return None

    def check_installation(self, minecraft_path):
        """Поиск JAR файлов в установке Minecraft"""
        jar_files = []

        # Возможные пути к папке versions
        possible_version_paths = [
            os.path.join(minecraft_path, "versions"),
            os.path.join(minecraft_path, "minecraft", "versions"),
            os.path.join(minecraft_path, ".minecraft", "versions"),
            os.path.join(minecraft_path, "game", "versions"),
        ]

        versions_path = None
        for possible_path in possible_version_paths:
            if os.path.exists(possible_path):
                versions_path = possible_path
                break

        # Если не нашли — ищем рекурсивно
        if not versions_path:
            for root, dirs, files in os.walk(minecraft_path):
                if "versions" in dirs:
                    versions_path = os.path.join(root, "versions")
                    break

        # Если всё ещё не нашли — ищем все JAR в папке
        if not versions_path:
            for root, dirs, files in os.walk(minecraft_path):
                for file in files:
                    if file.endswith('.jar'):
                        jar_files.append(os.path.join(root, file))
            return jar_files

        # Ищем JAR в папках версий
        if os.path.exists(versions_path):
            try:
                version_folders = [d for d in os.listdir(versions_path)
                                   if os.path.isdir(os.path.join(versions_path, d))]

                for folder in version_folders:
                    folder_path = os.path.join(versions_path, folder)
                    for file in os.listdir(folder_path):
                        if file.endswith('.jar'):
                            jar_files.append(os.path.join(folder_path, file))
            except Exception as e:
                print(f"  ⚠️ Ошибка чтения папки версий: {e}")

        return jar_files

    def run_check(self):
        """Основная функция проверки хешей"""
        print("=== Проверка хешей Minecraft ===")
        print("Ищу установки Minecraft...")

        # Поиск установок
        found_paths = self.find_minecraft_installations()

        # Если не нашли — запрашиваем путь
        if not found_paths:
            print("❌ Minecraft не найден в стандартных местах.")
            manual_path = input("Укажите путь к папке Minecraft: ").strip()

            if manual_path and os.path.exists(manual_path):
                found_paths.append(manual_path)
            else:
                print("❌ Указанный путь не существует.")
                input("Нажмите Enter для возврата...")
                return

        # Меню выбора установки
        print("\n📁 НАЙДЕННЫЕ УСТАНОВКИ:")
        for i, path in enumerate(found_paths, 1):
            print(f"  [{i}] {path}")
        print("  [A] Проверить все")
        print()

        choice = input("Выберите номер установки (или A для всех): ").strip().upper()

        selected_paths = []
        if choice == "A":
            selected_paths = found_paths
        else:
            try:
                index = int(choice) - 1
                if 0 <= index < len(found_paths):
                    selected_paths.append(found_paths[index])
                else:
                    print("❌ Неверный выбор.")
                    input("Нажмите Enter для возврата...")
                    return
            except ValueError:
                print("❌ Неверный выбор.")
                input("Нажмите Enter для возврата...")
                return

        # Основная проверка
        total_checked = 0
        total_matches = 0
        total_mismatches = 0
        total_unknown = 0
        total_cheats = 0

        for installation in selected_paths:
            jar_files = self.check_installation(installation)

            if not jar_files:
                print("  ⚠️ В этой установке нет файлов для проверки")
                continue

            print(f"\n🔍 Проверяю: {installation}")
            print(f"  📊 Найдено JAR файлов: {len(jar_files)}")

            for jar_path in jar_files:
                total_checked += 1
                jar_name = os.path.basename(jar_path)

                # Проверка по названию чита
                if is_cheat_filename(jar_name):
                    detected_cheat = get_detected_cheat(jar_name)
                    print(f"    ❌ ЧИТ: {jar_name} ({detected_cheat})")
                    total_cheats += 1
                    continue

                # Проверка по хешу
                if jar_name in self.reference_hashes:
                    expected_hash = self.reference_hashes[jar_name]
                    actual_hash = self.calculate_file_hash(jar_path)

                    if actual_hash:
                        if actual_hash == expected_hash:
                            print(f"    ✅ {jar_name}")
                            total_matches += 1
                        else:
                            print(f"    ❌ {jar_name} (хеш не совпадает)")
                            total_mismatches += 1
                else:
                    # Неизвестная версия
                    actual_hash = self.calculate_file_hash(jar_path)
                    if actual_hash:
                        print(f"    ⚠️ НЕИЗВЕСТНО: {jar_name}")
                        total_unknown += 1

        # Итоговый отчет
        print("\n" + "=" * 60)
        print("ИТОГОВЫЙ ОТЧЕТ")
        print("=" * 60)
        print(f"Проверено установок: {len(selected_paths)}")
        print(f"Проверено файлов: {total_checked}")
        print(f"✅ Чистых: {total_matches}")
        print(f"❌ Не совпадает хеш: {total_mismatches}")
        print(f"⚠️ Неизвестных версий: {total_unknown}")
        if total_cheats > 0:
            print(f"🚫 ОБНАРУЖЕНО ЧИТОВ: {total_cheats}")
        print("=" * 60)

        input("\nНажмите Enter для возврата в главное меню...")


def check_jar_file(jar_path):
    """Проверяет JAR файл LabyMod на подозрительные классы по времени компиляции"""
    try:
        with zipfile.ZipFile(jar_path, 'r') as jar:
            class_files = []

            for entry in jar.infolist():
                if entry.filename.endswith('.class'):
                    mod_time = datetime.datetime(*entry.date_time)
                    class_files.append((entry.filename, mod_time))

            if not class_files:
                return "❌ Нет классов для проверки"

            # Группируем по времени (до минуты)
            time_groups = defaultdict(list)
            for filename, file_time in class_files:
                time_key = file_time.replace(second=0, microsecond=0)
                time_groups[time_key].append(filename)

            if not time_groups:
                return "❌ Не удалось проанализировать время"

            # Находим основную группу (большинство классов)
            main_group_time = max(time_groups.items(), key=lambda x: len(x[1]))[0]

            # Ищем отклоняющиеся классы (разница > 1 минута)
            suspicious = []
            for filename, file_time in class_files:
                time_diff = abs((file_time - main_group_time).total_seconds())
                if time_diff > 60:
                    suspicious.append(filename)

            total = len(class_files)
            suspicious_count = len(suspicious)

            if suspicious_count == 0:
                return "✅ Чисто"
            else:
                result = f"⚠️ Подозрительно: {suspicious_count} из {total} классов\n"
                for i, class_name in enumerate(suspicious[:10], 1):
                    result += f"   {i}. {class_name}\n"
                if len(suspicious) > 10:
                    result += f"   ... и еще {len(suspicious) - 10}\n"
                return result.strip()

    except Exception as e:
        return f"❌ Ошибка при проверке: {e}"


def find_labymod_jars():
    """Ищет JAR файлы LabyMod"""
    appdata = os.getenv('APPDATA')
    if not appdata:
        return []

    versions_paths = [
        os.path.join(appdata, '.tlauncher', 'legacy', 'Minecraft', 'game', 'versions'),
        os.path.join(appdata, '.tlauncher', 'minecraft', 'versions'),
        os.path.join(appdata, '.minecraft', 'versions'),
    ]

    found_jars = []

    for versions_dir in versions_paths:
        if not os.path.exists(versions_dir):
            continue

        try:
            for item in os.listdir(versions_dir):
                item_path = os.path.join(versions_dir, item)

                if os.path.isdir(item_path):
                    for file in os.listdir(item_path):
                        if file.lower().endswith('.jar') and 'labymod' in file.lower():
                            jar_path = os.path.join(item_path, file)
                            found_jars.append(jar_path)
        except:
            continue

    return found_jars


def run_labymod_checker():
    """Проверка LabyMod клиентов (только полный режим)"""
    print("🔍 Проверка LabyMod клиентов")
    print("=" * 50)

    jars = find_labymod_jars()

    if not jars:
        print("❌ LabyMod не найден автоматически")
        custom_path = input("Введите путь к JAR файлу (или Enter для выхода): ").strip()
        if custom_path and os.path.exists(custom_path):
            jars = [custom_path]
        else:
            return

    print(f"Найдено LabyMod клиентов: {len(jars)}\n")

    all_clean = True
    suspicious_clients = []

    for jar_path in jars:
        jar_name = os.path.basename(jar_path)
        folder_name = os.path.basename(os.path.dirname(jar_path))

        print(f"📁 {folder_name}/{jar_name}")
        result = check_jar_file(jar_path)

        if "Подозрительно" in result or "⚠️" in result:
            all_clean = False
            suspicious_clients.append((jar_path, result))
            print(result)
        else:
            print(result)

        print("-" * 50)

    # Итоговый вывод
    print("\n" + "=" * 50)
    if all_clean:
        print("✅ Все клиенты чистые")
    else:
        print(f"⚠️ Найдено подозрительных клиентов: {len(suspicious_clients)}")
    print("=" * 50)

    input("\nНажмите Enter для возврата в главное меню...")


def main():
    """Главная функция"""
    while True:
        # Очистка экрана
        os.system('cls' if os.name == 'nt' else 'clear')

        choice = main_menu()

        if choice == '1':
            os.system('cls' if os.name == 'nt' else 'clear')
            checker = MinecraftHashChecker()
            checker.run_check()
        elif choice == '2':
            os.system('cls' if os.name == 'nt' else 'clear')
            run_labymod_checker()
        elif choice == '3':
            print("Выход из программы...")
            break
        else:
            print("Неверный выбор. Попробуйте снова.")
            time.sleep(1)


if __name__ == "__main__":
    main()
