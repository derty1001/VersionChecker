import PyInstaller.__main__
import os

# Настройки сборки
APP_NAME = "MinecraftVersionChecker"
ICON_FILE = "icon.ico"  # Убедитесь, что у вас есть этот файл
MAIN_FILE = "combined_checker.py"

# Создание файла version_info.txt
version_info_content = r"""# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 1, 0, 0),
    prodvers=(1, 1, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          u'040904B0',
          [StringStruct(u'CompanyName', u'holyworld'),
           StringStruct(u'FileDescription', u'Minecraft Version Checker'),
           StringStruct(u'FileVersion', u'1.1.0.0'),
           StringStruct(u'InternalName', u'MinecraftVersionChecker'),
           StringStruct(u'LegalCopyright', u'Copyright 2024'),
           StringStruct(u'OriginalFilename', u'MinecraftVersionChecker.exe'),
           StringStruct(u'ProductName', u'Minecraft Version Checker'),
           StringStruct(u'ProductVersion', u'1.1.0.0')])
      ]
    ),
    VarFileInfo([VarStruct(u'Translation', [0x409, 0x4B0])])
  ]
)"""

# Сохранение version_info.txt
with open("version_info.txt", "w", encoding="utf-8") as f:
    f.write(version_info_content)

# Параметры PyInstaller
params = [
    MAIN_FILE,
    '--onefile',  # Один файл EXE
    '--console',  # Консольное приложение
    f'--name={APP_NAME}',
    '--clean',
    '--noconfirm',
    '--upx-exclude=vcruntime140.dll',
    '--add-data=version_info.txt;.',  # Для включения version_info
    '--version-file=version_info.txt',
]

# Добавляем иконку, если файл существует
if os.path.exists(ICON_FILE):
    params.append(f'--icon={ICON_FILE}')
else:
    print(f"⚠️ Предупреждение: Файл иконки '{ICON_FILE}' не найден")

# Дополнительные параметры для уменьшения ложных срабатываний антивируса
params.extend([
    '--hidden-import=os',
    '--hidden-import=sys',
    '--hidden-import=hashlib',
    '--hidden-import=json',
    '--hidden-import=zipfile',
    '--hidden-import=datetime',
    '--hidden-import=pathlib',
    '--hidden-import=time',
    '--hidden-import=collections',
    '--disable-windowed-traceback',
])

print("🚀 Начинаю сборку EXE файла...")
print(f"📦 Параметры сборки: {params}")

try:
    PyInstaller.__main__.run(params)
    print("✅ Сборка успешно завершена!")

    # Удаление временных файлов
    for file in ["version_info.txt"]:
        if os.path.exists(file):
            os.remove(file)
            print(f"🗑️ Удален временный файл: {file}")

except Exception as e:
    print(f"❌ Ошибка при сборке: {e}")
    input("Нажмите Enter для выхода...")