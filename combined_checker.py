import os
import sys
import hashlib
import json
import zipfile
import datetime
from datetime import datetime as dt
from pathlib import Path
import time
from collections import defaultdict

# Информация для сборки EXE
APP_NAME = "Minecraft Version Checker"
APP_VERSION = "1.1.0"
APP_AUTHOR = "holyworld"
APP_DESCRIPTION = "Проверка версий Minecraft клиентов"
APP_COPYRIGHT = f"© 2024 {APP_AUTHOR}. Все права защищены."

# Точка входа для pyinstaller
def is_frozen():
    """Проверка, скомпилирован ли скрипт в EXE"""
    return hasattr(sys, 'frozen')

def get_base_path():
    """Получение базового пути (рабочая директория для EXE)"""
    if is_frozen():
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def main_menu():
    """Главное меню для выбора программы"""
    print(" ╔══════════════════════════════════════════════════╗")
    print(" ║                 Check Version                    ║")
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

        # Встроенные хеши (SHA256)
        self.builtin_hashes = {
            "1.16.jar": "00740EF4475D4CD0A1D7064F89602F759C45FF9AFE29DA9B0EE0B9037EBB2A71",
            "1.16.1.jar": "B4831E7B63B10588FF06EA86322108D916C536446F3AEA3AE988B7FE3E1F66EF",
            "1.16.2.jar": "19960F4E3C60F2723F361844D2B4020B8BF2160BD91A1E1EFDE8CE5AEA4FF73D",
            "1.16.3.jar": "DA85197BABD989A7DE318774CF5D97BCEF95E89A70C9FA9A4C8180463E9589FA",
            "1.16.4.jar": "D6740464EE2BDF37D285C5D368D2E16497492427FB5783E2DB3482BBF0079ED0",
            "1.16.5.jar": "00B5EBBC33E95EA88C1AB80601599C9827E9AA861D93CCC2CFCBBFD996E86263",
            "1.17.jar": "14122287D4E4256C2D65EC8C0CCFA3B56448495FA3CCABC87D0F0EEB4FA1C30F",
            "1.17.1.jar": "A49B4A56C5BBE15C9ED9FE53EFA9A591F265A1F5BA7D6AA9739A58EA7A92B79D",
            "1.18.jar": "381E090EF22584526113BCCCF26AE38A310A22094D14C2D0DEC72B71FDF65AAA",
            "1.18.1.jar": "737C28A56C8980FCD8574465C61538EBDE8F511BDD035C69D0CBE27953F892AA",
            "1.18.2.jar": "1D09E3639644B6B2254499469D0765CC005A286D19F3FA595B0ED8FB07971EC7",
            "1.19.jar": "FFD4FB3037D4110085B4D3D2DC47B760695528EB14292C3E5F7C758983C6D764",
            "1.19.1.jar": "146D4018CFED50C5E77483940653091F186D2EEA9AD42FC40939F5C72D6B7F52",
            "1.19.2.jar": "E1AC65DE9B471B6916CC457FDCFF00C1BAFAC17027AA79100C4DF893B3D956DB",
            "1.19.3.jar": "B7228C23DBC8988129561AF3918DD469577DE842D2EB3C7DABE00316BF9A44D6",
            "1.19.4.jar": "0E79CF7F07C107E9A1FE22ED703E472372B44149E64114944F0811ABBD25F3EC",
            "1.20.jar": "5AC9EAD135746F5F27048F2E01D8D5BDC2DABC4D91422F73EF2435F4C3D24AFF",
            "1.20.1.jar": "56B71336D2B4FDFFD197F56595B0DA93E32A946F78F382A299B8F4B92758BB0F",
            "1.20.2.jar": "FA1A19BE56A506426308ABBC1CAD85F299A7FC6DAE4335559351BA0246713FDA",
            "1.20.3.jar": "BEF21938224902DD925E2D89DCFE1D2540656D4CF7A5ABD2B93E0402D135C655",
            "1.20.4.jar": "9221AB461A491BF9661CD8E773A5E662AAA43D600FA7970B8C12BBFB0431B838",
            "1.20.5.jar": "49D5949ADBB1021A7EB00C1B949F9E39934B10249CBF86D25004774D1B3FF510",
            "1.20.6.jar": "02DFD345AC1AD55692D5DBC8486AC7E4FEA72CD54AC494A79CD48963048E56B2",
            "1.21.jar": "4B56BC9B44DE7E88F9FBB52E716C18240DA34469FCBAFA5ED2E75B04D60617E8",
            "1.21.1.jar": "499F6897D1837516680F3114072D8106E11C9ADCD933FE5CF051B551089B0C99",
            "1.21.2.jar": "613091DA0F62426AE8DCF9AFB30EB639485F493B81CDA3A2B96B1FB8A6B9976C",
            "1.21.3.jar": "25190C556BC56D11070638CCAB3B3C6EFD76BB9684C92A2680A4DE01C3C7138B",
            "1.21.4.jar": "C17C450C6E72CC51297DAA57CE38F800AA01CF022B743DAA21A0512D326D894E",
            "1.21.5.jar": "522672AD20B460C02C2E39B6C5035EF6A849AF28EB11AB2AC7EB293D395A8C11",
            "1.21.6.jar": "9592DF8587D6D3EC0334C873AD432DC76006D6129AFDCE9A7EAC52638339A24A",
            "1.21.7.jar": "6D0AA64C6A0AEE3270253317F51E9E816F94CD3B16B44F5D605615C39FC62FB9",
            "1.21.8.jar": "EA74E9C5E92D01F95F3D39196DDB734E19A077A58B4C433C34109487D600276F",
            "Fabric 1.16.jar": "00740EF4475D4CD0A1D7064F89602F759C45FF9AFE29DA9B0EE0B9037EBB2A71",
            "Fabric 1.16.1.jar": "B4831E7B63B10588FF06EA86322108D916C536446F3AEA3AE988B7FE3E1F66EF",
            "Fabric 1.16.2.jar": "19960F4E3C60F2723F361844D2B4020B8BF2160BD91A1E1EFDE8CE5AEA4FF73D",
            "Fabric 1.16.3.jar": "DA85197BABD989A7DE318774CF5D97BCEF95E89A70C9FA9A4C8180463E9589FA",
            "Fabric 1.16.4.jar": "D6740464EE2BDF37D285C5D368D2E16497492427FB5783E2DB3482BBF0079ED0",
            "Fabric 1.16.5.jar": "00B5EBBC33E95EA88C1AB80601599C9827E9AA861D93CCC2CFCBBFD996E86263",
            "Fabric 1.17.jar": "14122287D4E4256C2D65EC8C0CCFA3B56448495FA3CCABC87D0F0EEB4FA1C30F",
            "Fabric 1.17.1.jar": "A49B4A56C5BBE15C9ED9FE53EFA9A591F265A1F5BA7D6AA9739A58EA7A92B79D",
            "Fabric 1.18.jar": "381E090EF22584526113BCCCF26AE38A310A22094D14C2D0DEC72B71FDF65AAA",
            "Fabric 1.18.1.jar": "737C28A56C8980FCD8574465C61538EBDE8F511BDD035C69D0CBE27953F892AA",
            "Fabric 1.18.2.jar": "1D09E3639644B6B2254499469D0765CC005A286D19F3FA595B0ED8FB07971EC7",
            "Fabric 1.19.jar": "FFD4FB3037D4110085B4D3D2DC47B760695528EB14292C3E5F7C758983C6D764",
            "Fabric 1.19.1.jar": "146D4018CFED50C5E77483940653091F186D2EEA9AD42FC40939F5C72D6B7F52",
            "Fabric 1.19.2.jar": "E1AC65DE9B471B6916CC457FDCFF00C1BAFAC17027AA79100C4DF893B3D956DB",
            "Fabric 1.19.3.jar": "B7228C23DBC8988129561AF3918DD469577DE842D2EB3C7DABE00316BF9A44D6",
            "Fabric 1.19.4.jar": "0E79CF7F07C107E9A1FE22ED703E472372B44149E64114944F0811ABBD25F3EC",
            "Fabric 1.20.jar": "5AC9EAD135746F5F27048F2E01D8D5BDC2DABC4D91422F73EF2435F4C3D24AFF",
            "Fabric 1.20.1.jar": "56B71336D2B4FDFFD197F56595B0DA93E32A946F78F382A299B8F4B92758BB0F",
            "Fabric 1.20.2.jar": "FA1A19BE56A506426308ABBC1CAD85F299A7FC6DAE4335559351BA0246713FDA",
            "Fabric 1.20.3.jar": "BEF21938224902DD925E2D89DCFE1D2540656D4CF7A5ABD2B93E0402D135C655",
            "Fabric 1.20.4.jar": "9221AB461A491BF9661CD8E773A5E662AAA43D600FA7970B8C12BBFB0431B838",
            "Fabric 1.20.5.jar": "49D5949ADBB1021A7EB00C1B949F9E39934B10249CBF86D25004774D1B3FF510",
            "Fabric 1.20.6.jar": "02DFD345AC1AD55692D5DBC8486AC7E4FEA72CD54AC494A79CD48963048E56B2",
            "Fabric 1.21.jar": "4B56BC9B44DE7E88F9FBB52E716C18240DA34469FCBAFA5ED2E75B04D60617E8",
            "Fabric 1.21.1.jar": "499F6897D1837516680F3114072D8106E11C9ADCD933FE5CF051B551089B0C99",
            "Fabric 1.21.2.jar": "613091DA0F62426AE8DCF9AFB30EB639485F493B81CDA3A2B96B1FB8A6B9976C",
            "Fabric 1.21.3.jar": "25190C556BC56D11070638CCAB3B3C6EFD76BB9684C92A2680A4DE01C3C7138B",
            "Fabric 1.21.4.jar": "C17C450C6E72CC51297DAA57CE38F800AA01CF022B743DAA21A0512D326D894E",
            "Fabric 1.21.5.jar": "522672AD20B460C02C2E39B6C5035EF6A849AF28EB11AB2AC7EB293D395A8C11",
            "Fabric 1.21.6.jar": "9592DF8587D6D3EC0334C873AD432DC76006D6129AFDCE9A7EAC52638339A24A",
            "Fabric 1.21.7.jar": "6D0AA64C6A0AEE3270253317F51E9E816F94CD3B16B44F5D605615C39FC62FB9",
            "Fabric 1.21.8.jar": "EA74E9C5E92D01F95F3D39196DDB734E19A077A58B4C433C34109487D600276F",
            "Forge 1.16.1.jar": "B4831E7B63B10588FF06EA86322108D916C536446F3AEA3AE988B7FE3E1F66EF",
            "Forge 1.16.2.jar": "19960F4E3C60F2723F361844D2B4020B8BF2160BD91A1E1EFDE8CE5AEA4FF73D",
            "Forge 1.16.3.jar": "DA85197BABD989A7DE318774CF5D97BCEF95E89A70C9FA9A4C8180463E9589FA",
            "Forge 1.16.4.jar": "D6740464EE2BDF37D285C5D368D2E16497492427FB5783E2DB3482BBF0079ED0",
            "Forge 1.16.5.jar": "00B5EBBC33E95EA88C1AB80601599C9827E9AA861D93CCC2CFCBBFD996E86263",
            "Forge 1.17.1.jar": "A49B4A56C5BBE15C9ED9FE53EFA9A591F265A1F5BA7D6AA9739A58EA7A92B79D",
            "Forge 1.18.jar": "381E090EF22584526113BCCCF26AE38A310A22094D14C2D0DEC72B71FDF65AAA",
            "Forge 1.18.1.jar": "737C28A56C8980FCD8574465C61538EBDE8F511BDD035C69D0CBE27953F892AA",
            "Forge 1.18.2.jar": "1D09E3639644B6B2254499469D0765CC005A286D19F3FA595B0ED8FB07971EC7",
            "Forge 1.19.jar": "FFD4FB3037D4110085B4D3D2DC47B760695528EB14292C3E5F7C758983C6D764",
            "Forge 1.19.1.jar": "146D4018CFED50C5E77483940653091F186D2EEA9AD42FC40939F5C72D6B7F52",
            "Forge 1.19.2.jar": "E1AC65DE9B471B6916CC457FDCFF00C1BAFAC17027AA79100C4DF893B3D956DB",
            "Forge 1.19.3.jar": "B7228C23DBC8988129561AF3918DD469577DE842D2EB3C7DABE00316BF9A44D6",
            "Forge 1.19.4.jar": "0E79CF7F07C107E9A1FE22ED703E472372B44149E64114944F0811ABBD25F3EC",
            "Forge 1.20.jar": "5AC9EAD135746F5F27048F2E01D8D5BDC2DABC4D91422F73EF2435F4C3D24AFF",
            "Forge 1.20.1.jar": "56B71336D2B4FDFFD197F56595B0DA93E32A946F78F382A299B8F4B92758BB0F",
            "Forge 1.20.2.jar": "FA1A19BE56A506426308ABBC1CAD85F299A7FC6DAE4335559351BA0246713FDA",
            "Forge 1.20.4.jar": "9221AB461A491BF9661CD8E773A5E662AAA43D600FA7970B8C12BBFB0431B838",
            "Forge 1.20.6.jar": "02DFD345AC1AD55692D5DBC8486AC7E4FEA72CD54AC494A79CD48963048E56B2",
            "Forge 1.21.jar": "4B56BC9B44DE7E88F9FBB52E716C18240DA34469FCBAFA5ED2E75B04D60617E8",
            "Forge 1.21.1.jar": "499F6897D1837516680F3114072D8106E11C9ADCD933FE5CF051B551089B0C99",
            "Forge 1.21.3.jar": "25190C556BC56D11070638CCAB3B3C6EFD76BB9684C92A2680A4DE01C3C7138B",
            "Forge 1.21.4.jar": "C17C450C6E72CC51297DAA57CE38F800AA01CF022B743DAA21A0512D326D894E",
            "Forge 1.21.5.jar": "522672AD20B460C02C2E39B6C5035EF6A849AF28EB11AB2AC7EB293D395A8C11",
            "Forge 1.21.6.jar": "9592DF8587D6D3EC0334C873AD432DC76006D6129AFDCE9A7EAC52638339A24A",
            "Forge 1.21.8.jar": "EA74E9C5E92D01F95F3D39196DDB734E19A077A58B4C433C34109487D600276F",
            "ForgeOptiFine 1.16.1.jar": "B4831E7B63B10588FF06EA86322108D916C536446F3AEA3AE988B7FE3E1F66EF",
            "ForgeOptiFine 1.16.2.jar": "19960F4E3C60F2723F361844D2B4020B8BF2160BD91A1E1EFDE8CE5AEA4FF73D",
            "ForgeOptiFine 1.16.3.jar": "DA85197BABD989A7DE318774CF5D97BCEF95E89A70C9FA9A4C8180463E9589FA",
            "ForgeOptiFine 1.16.4.jar": "D6740464EE2BDF37D285C5D368D2E16497492427FB5783E2DB3482BBF0079ED0",
            "ForgeOptiFine 1.16.5.jar": "00B5EBBC33E95EA88C1AB80601599C9827E9AA861D93CCC2CFCBBFD996E86263",
            "ForgeOptiFine 1.17.1.jar": "A49B4A56C5BBE15C9ED9FE53EFA9A591F265A1F5BA7D6AA9739A58EA7A92B79D",
            "ForgeOptiFine 1.18.jar": "381E090EF22584526113BCCCF26AE38A310A22094D14C2D0DEC72B71FDF65AAA",
            "ForgeOptiFine 1.18.1.jar": "737C28A56C8980FCD8574465C61538EBDE8F511BDD035C69D0CBE27953F892AA",
            "ForgeOptiFine 1.18.2.jar": "1D09E3639644B6B2254499469D0765CC005A286D19F3FA595B0ED8FB07971EC7",
            "ForgeOptiFine 1.19.jar": "FFD4FB3037D4110085B4D3D2DC47B760695528EB14292C3E5F7C758983C6D764",
            "ForgeOptiFine 1.19.1.jar": "146D4018CFED50C5E77483940653091F186D2EEA9AD42FC40939F5C72D6B7F52",
            "ForgeOptiFine 1.19.2.jar": "E1AC65DE9B471B6916CC457FDCFF00C1BAFAC17027AA79100C4DF893B3D956DB",
            "ForgeOptiFine 1.19.3.jar": "B7228C23DBC8988129561AF3918DD469577DE842D2EB3C7DABE00316BF9A44D6",
            "ForgeOptiFine 1.19.4.jar": "0E79CF7F07C107E9A1FE22ED703E472372B44149E64114944F0811ABBD25F3EC",
            "NeoForge 1.20.2.jar": "FA1A19BE56A506426308ABBC1CAD85F299A7FC6DAE4335559351BA0246713FDA",
            "NeoForge 1.20.4.jar": "9221AB461A491BF9661CD8E773A5E662AAA43D600FA7970B8C12BBFB0431B838",
            "NeoForge 1.20.6.jar": "02DFD345AC1AD55692D5DBC8486AC7E4FEA72CD54AC494A79CD48963048E56B2",
            "NeoForge 1.21.jar": "4B56BC9B44DE7E88F9FBB52E716C18240DA34469FCBAFA5ED2E75B04D60617E8",
            "NeoForge 1.21.1.jar": "499F6897D1837516680F3114072D8106E11C9ADCD933FE5CF051B551089B0C99",
            "NeoForge 1.21.3.jar": "25190C556BC56D11070638CCAB3B3C6EFD76BB9684C92A2680A4DE01C3C7138B",
            "NeoForge 1.21.4.jar": "C17C450C6E72CC51297DAA57CE38F800AA01CF022B743DAA21A0512D326D894E",
            "NeoForge 1.21.5.jar": "522672AD20B460C02C2E39B6C5035EF6A849AF28EB11AB2AC7EB293D395A8C11",
            "NeoForge 1.21.8.jar": "EA74E9C5E92D01F95F3D39196DDB734E19A077A58B4C433C34109487D600276F",
            "OptiFine 1.16.1.jar": "B4831E7B63B10588FF06EA86322108D916C536446F3AEA3AE988B7FE3E1F66EF",
            "OptiFine 1.16.2.jar": "19960F4E3C60F2723F361844D2B4020B8BF2160BD91A1E1EFDE8CE5AEA4FF73D",
            "OptiFine 1.16.3.jar": "DA85197BABD989A7DE318774CF5D97BCEF95E89A70C9FA9A4C8180463E9589FA",
            "OptiFine 1.16.4.jar": "D6740464EE2BDF37D285C5D368D2E16497492427FB5783E2DB3482BBF0079ED0",
            "OptiFine 1.16.5.jar": "00B5EBBC33E95EA88C1AB80601599C9827E9AA861D93CCC2CFCBBFD996E86263",
            "OptiFine 1.17.1.jar": "A49B4A56C5BBE15C9ED9FE53EFA9A591F265A1F5BA7D6AA9739A58EA7A92B79D",
            "OptiFine 1.18.jar": "381E090EF22584526113BCCCF26AE38A310A22094D14C2D0DEC72B71FDF65AAA",
            "OptiFine 1.18.1.jar": "737C28A56C8980FCD8574465C61538EBDE8F511BDD035C69D0CBE27953F892AA",
            "OptiFine 1.18.2.jar": "1D09E3639644B6B2254499469D0765CC005A286D19F3FA595B0ED8FB07971EC7",
            "OptiFine 1.19.jar": "FFD4FB3037D4110085B4D3D2DC47B760695528EB14292C3E5F7C758983C6D764",
            "OptiFine 1.19.1.jar": "146D4018CFED50C5E77483940653091F186D2EEA9AD42FC40939F5C72D6B7F52",
            "OptiFine 1.19.2.jar": "E1AC65DE9B471B6916CC457FDCFF00C1BAFAC17027AA79100C4DF893B3D956DB",
            "OptiFine 1.19.3.jar": "B7228C23DBC8988129561AF3918DD469577DE842D2EB3C7DABE00316BF9A44D6",
            "OptiFine 1.19.4.jar": "0E79CF7F07C107E9A1FE22ED703E472372B44149E64114944F0811ABBD25F3EC",
            "OptiFine 1.20.1.jar": "56B71336D2B4FDFFD197F56595B0DA93E32A946F78F382A299B8F4B92758BB0F",
            "OptiFine 1.20.4.jar": "9221AB461A491BF9661CD8E773A5E662AAA43D600FA7970B8C12BBFB0431B838",
            "OptiFine 1.21.1.jar": "499F6897D1837516680F3114072D8106E11C9ADCD933FE5CF051B551089B0C99",
            "OptiFine 1.21.3.jar": "25190C556BC56D11070638CCAB3B3C6EFD76BB9684C92A2680A4DE01C3C7138B",
            "OptiFine 1.21.4.jar": "C17C450C6E72CC51297DAA57CE38F800AA01CF022B743DAA21A0512D326D894E",
            "Quilt 1.16.jar": "00740EF4475D4CD0A1D7064F89602F759C45FF9AFE29DA9B0EE0B9037EBB2A71",
            "Quilt 1.16.1.jar": "B4831E7B63B10588FF06EA86322108D916C536446F3AEA3AE988B7FE3E1F66EF",
            "Quilt 1.16.2.jar": "19960F4E3C60F2723F361844D2B4020B8BF2160BD91A1E1EFDE8CE5AEA4FF73D",
            "Quilt 1.16.3.jar": "DA85197BABD989A7DE318774CF5D97BCEF95E89A70C9FA9A4C8180463E9589FA",
            "Quilt 1.16.4.jar": "D6740464EE2BDF37D285C5D368D2E16497492427FB5783E2DB3482BBF0079ED0",
            "Quilt 1.16.5.jar": "00B5EBBC33E95EA88C1AB80601599C9827E9AA861D93CCC2CFCBBFD996E86263",
            "Quilt 1.17.jar": "14122287D4E4256C2D65EC8C0CCFA3B56448495FA3CCABC87D0F0EEB4FA1C30F",
            "Quilt 1.17.1.jar": "A49B4A56C5BBE15C9ED9FE53EFA9A591F265A1F5BA7D6AA9739A58EA7A92B79D",
            "Quilt 1.18.jar": "381E090EF22584526113BCCCF26AE38A310A22094D14C2D0DEC72B71FDF65AAA",
            "Quilt 1.18.1.jar": "737C28A56C8980FCD8574465C61538EBDE8F511BDD035C69D0CBE27953F892AA",
            "Quilt 1.18.2.jar": "1D09E3639644B6B2254499469D0765CC005A286D19F3FA595B0ED8FB07971EC7",
            "Quilt 1.19.jar": "FFD4FB3037D4110085B4D3D2DC47B760695528EB14292C3E5F7C758983C6D764",
            "Quilt 1.19.1.jar": "146D4018CFED50C5E77483940653091F186D2EEA9AD42FC40939F5C72D6B7F52",
            "Quilt 1.19.2.jar": "E1AC65DE9B471B6916CC457FDCFF00C1BAFAC17027AA79100C4DF893B3D956DB",
            "Quilt 1.19.3.jar": "B7228C23DBC8988129561AF3918DD469577DE842D2EB3C7DABE00316BF9A44D6",
            "Quilt 1.19.4.jar": "0E79CF7F07C107E9A1FE22ED703E472372B44149E64114944F0811ABBD25F3EC",
            "Quilt 1.20.jar": "5AC9EAD135746F5F27048F2E01D8D5BDC2DABC4D91422F73EF2435F4C3D24AFF",
            "Quilt 1.20.1.jar": "56B71336D2B4FDFFD197F56595B0DA93E32A946F78F382A299B8F4B92758BB0F",
            "Quilt 1.20.2.jar": "FA1A19BE56A506426308ABBC1CAD85F299A7FC6DAE4335559351BA0246713FDA",
            "Quilt 1.20.3.jar": "BEF21938224902DD925E2D89DCFE1D2540656D4CF7A5ABD2B93E0402D135C655",
            "Quilt 1.20.4.jar": "9221AB461A491BF9661CD8E773A5E662AAA43D600FA7970B8C12BBFB0431B838",
            "Quilt 1.20.5.jar": "49D5949ADBB1021A7EB00C1B949F9E39934B10249CBF86D25004774D1B3FF510",
            "Quilt 1.20.6.jar": "02DFD345AC1AD55692D5DBC8486AC7E4FEA72CD54AC494A79CD48963048E56B2",
            "Quilt 1.21.jar": "4B56BC9B44DE7E88F9FBB52E716C18240DA34469FCBAFA5ED2E75B04D60617E8",
            "Quilt 1.21.1.jar": "499F6897D1837516680F3114072D8106E11C9ADCD933FE5CF051B551089B0C99",
            "Quilt 1.21.2.jar": "613091DA0F62426AE8DCF9AFB30EB639485F493B81CDA3A2B96B1FB8A6B9976C",
            "Quilt 1.21.3.jar": "25190C556BC56D11070638CCAB3B3C6EFD76BB9684C92A2680A4DE01C3C7138B",
            "Quilt 1.21.4.jar": "C17C450C6E72CC51297DAA57CE38F800AA01CF022B743DAA21A0512D326D894E",
            "Quilt 1.21.5.jar": "522672AD20B460C02C2E39B6C5035EF6A849AF28EB11AB2AC7EB293D395A8C11",
            "Quilt 1.21.6.jar": "9592DF8587D6D3EC0334C873AD432DC76006D6129AFDCE9A7EAC52638339A24A",
            "Quilt 1.21.7.jar": "6D0AA64C6A0AEE3270253317F51E9E816F94CD3B16B44F5D605615C39FC62FB9",
            "Quilt 1.21.8.jar": "EA74E9C5E92D01F95F3D39196DDB734E19A077A58B4C433C34109487D600276F"
        }

        self.reference_hashes = {}

    def print_colored(self, text, color_code="\033[0m"):
        """Цветной вывод в консоль"""
        colors = {
            "red": "\033[91m",
            "green": "\033[92m",
            "yellow": "\033[93m",
            "cyan": "\033[96m",
            "gray": "\033[90m",
            "reset": "\033[0m"
        }
        print(f"{colors.get(color_code, '')}{text}{colors['reset']}")

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
                self.print_colored(f"✅ Найден: {path}", "green")

        return found_paths

    def load_hashes(self):
        """Загрузка хешей из встроенных данных"""
        self.print_colored("📖 Загружаю эталонные хеши...", "cyan")
        self.reference_hashes = self.builtin_hashes.copy()
        self.print_colored(f"✅ Загружено эталонов: {len(self.reference_hashes)}", "green")

    def calculate_file_hash(self, filepath, hash_length=64):
        """Вычисление хеша файла"""
        hash_func = hashlib.sha256()  # Все хеши в списке - SHA256
        try:
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hash_func.update(chunk)
            return hash_func.hexdigest().upper()
        except Exception as e:
            self.print_colored(f"    ⚠️ Ошибка чтения файла {filepath}: {e}", "yellow")
            return None

    def check_installation(self, minecraft_path):
        """Проверка одной установки Minecraft"""
        self.print_colored(f"\n🔍 Проверяю: {minecraft_path}", "cyan")

        jar_files = []

        # Способ 1: Прямо в корне
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
                self.print_colored(f"  📁 Папка версий: {versions_path}", "gray")
                break

        # Способ 2: Ищем рекурсивно
        if not versions_path:
            self.print_colored("  🔎 Ищу папку versions рекурсивно...", "yellow")
            for root, dirs, files in os.walk(minecraft_path):
                if "versions" in dirs:
                    versions_path = os.path.join(root, "versions")
                    self.print_colored(f"  📁 Найдена папка версий: {versions_path}", "green")
                    break

        # Если не нашли - ищем jar файлы везде
        if not versions_path:
            self.print_colored("  ⚠️ Папка versions не найдена. Ищу jar файлы в любом месте...", "yellow")
            for root, dirs, files in os.walk(minecraft_path):
                for file in files:
                    if file.endswith('.jar'):
                        jar_files.append(os.path.join(root, file))

            if jar_files:
                self.print_colored(f"  ✅ Найдено jar файлов: {len(jar_files)}", "green")
            else:
                self.print_colored("  ❌ Не найдено ни одного jar файла", "red")
            return jar_files

        # Ищем jar файлы в папках версий
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
                self.print_colored(f"  ⚠️ Ошибка чтения папки версий: {e}", "yellow")

        return jar_files

    def run_check(self):
        """Основная функция проверки"""
        self.print_colored("=== Minecraft Hash Checker (Python) ===", "cyan")
        self.print_colored("Ищу установки Minecraft...", "gray")

        # Поиск установок
        found_paths = self.find_minecraft_installations()

        # Если не нашли - запрашиваем путь
        if not found_paths:
            self.print_colored("❌ Minecraft не найден в стандартных местах.", "red")
            manual_path = input("Укажите путь к папке Minecraft (например, C:\Games\Minecraft): ")

            if manual_path and os.path.exists(manual_path):
                found_paths.append(manual_path)
            else:
                self.print_colored("❌ Указанный путь не существует.", "red")
                input("Нажмите Enter для выхода...")
                return

        # Меню выбора
        self.print_colored("\n📁 НАЙДЕННЫЕ УСТАНОВКИ:", "cyan")
        for i, path in enumerate(found_paths, 1):
            self.print_colored(f"  [{i}] {path}", "gray")
        self.print_colored("  [A] Проверить все", "gray")
        print()

        choice = input("Выберите номер установки (или A для всех): ").strip().upper()

        selected_paths = []
        if choice == "A":
            selected_paths = found_paths
            self.print_colored("✅ Будут проверены все установки", "green")
        else:
            try:
                index = int(choice) - 1
                if 0 <= index < len(found_paths):
                    selected_paths.append(found_paths[index])
                    self.print_colored(f"✅ Выбрана установка: {selected_paths[0]}", "green")
                else:
                    self.print_colored("❌ Неверный выбор.", "red")
                    input("Нажмите Enter для выхода...")
                    return
            except ValueError:
                self.print_colored("❌ Неверный выбор.", "red")
                input("Нажмите Enter для выхода...")
                return

        # Загрузка хешей
        self.load_hashes()

        # Основная проверка
        total_checked = 0
        total_matches = 0
        total_mismatches = 0
        total_unknown = 0  # Добавляем счетчик неизвестных версий
        results = []

        for installation in selected_paths:
            jar_files = self.check_installation(installation)

            if not jar_files:
                self.print_colored("  ⚠️ В этой установке нет файлов для проверки", "yellow")
                continue

            self.print_colored(f"  📊 Найдено jar файлов: {len(jar_files)}", "gray")

            for jar_path in jar_files:
                total_checked += 1
                jar_name = os.path.basename(jar_path)

                if jar_name in self.reference_hashes:
                    expected_hash = self.reference_hashes[jar_name]
                    actual_hash = self.calculate_file_hash(jar_path)

                    if actual_hash:
                        if actual_hash == expected_hash:
                            self.print_colored(f"    ✅ {jar_name}", "green")
                            total_matches += 1
                            results.append({
                                "File": jar_name,
                                "Status": "OK",
                                "Hash": actual_hash
                            })
                        else:
                            self.print_colored(f"    ❌ {jar_name}", "red")
                            self.print_colored(f"      Ожидался: {expected_hash}", "yellow")
                            self.print_colored(f"      Фактически: {actual_hash}", "red")
                            total_mismatches += 1
                            results.append({
                                "File": jar_name,
                                "Status": "MISMATCH",
                                "Expected": expected_hash,
                                "Actual": actual_hash
                            })
                else:
                    # Добавляем статус "неизвестно" для версий, которых нет в списке
                    actual_hash = self.calculate_file_hash(jar_path)
                    if actual_hash:
                        self.print_colored(f"    ⚠️  (неизвестно) {jar_name}", "yellow")
                        self.print_colored(f"      Хеш: {actual_hash}", "gray")
                        total_unknown += 1
                        results.append({
                            "File": jar_name,
                            "Status": "UNKNOWN",
                            "Hash": actual_hash
                        })

        # Итоговый отчет
        self.print_colored("\n" + "=" * 60, "cyan")
        self.print_colored("ИТОГОВЫЙ ОТЧЕТ", "cyan")
        self.print_colored("=" * 60, "cyan")

        self.print_colored(f"Проверено установок: {len(selected_paths)}", "gray")
        self.print_colored(f"Проверено файлов: {total_checked}", "gray")
        self.print_colored(f"✅ Чистых: {total_matches}", "green")
        self.print_colored(f"❌ Необходимо проверить: {total_mismatches}", "red")
        self.print_colored(f"⚠️  Неизвестных версий: {total_unknown}", "yellow")  # Добавляем вывод неизвестных версий


        input("\nНажмите Enter для возврата в главное меню...")


# Вторая программа (LabyMod Checker)
def check_jar_file(jar_path):
    """Проверяет JAR файл на подозрительные классы."""

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

            # Находим основную группу
            if not time_groups:
                return "❌ Не удалось проанализировать время"

            main_group_time = max(time_groups.items(), key=lambda x: len(x[1]))[0]
            main_group_count = len(time_groups[main_group_time])

            # Ищем отклоняющиеся классы (разница > 1 минута)
            suspicious = []
            for filename, file_time in class_files:
                time_diff = abs((file_time - main_group_time).total_seconds())
                if time_diff > 60:  # 1 минута
                    suspicious.append(filename)

            total = len(class_files)
            suspicious_count = len(suspicious)

            if suspicious_count == 0:
                return f"✅ Чисто)"
            else:
                result = f"⚠️  Подозрительно: {suspicious_count} из {total} классов имеют разное время компиляции\n"
                for i, class_name in enumerate(suspicious[:10], 1):  # Показываем первые 10
                    result += f"   {i}. {class_name}\n"
                if len(suspicious) > 10:
                    result += f"   ... и еще {len(suspicious) - 10} классов\n"
                return result

    except Exception as e:
        return f"❌ Ошибка при проверке: {e}"


def find_labymod_jars():
    """Ищет JAR файлы LabyMod."""

    appdata = os.getenv('APPDATA')
    if not appdata:
        return []

    # Основные пути
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
                    # Ищем JAR файлы в папке версии
                    for file in os.listdir(item_path):
                        if file.lower().endswith('.jar') and 'labymod' in file.lower():
                            jar_path = os.path.join(item_path, file)
                            found_jars.append(jar_path)
        except:
            continue

    return found_jars


def run_labymod_checker():
    """Основная функция проверки LabyMod"""
    print("🔍 Проверка LabyMod клиентов")
    print("=" * 50)

    jars = find_labymod_jars()

    if not jars:
        print("❌ LabyMod не найден")

        # Пользовательский ввод
        custom_path = input("Введите путь к JAR файлу (или нажмите Enter для выхода): ").strip()
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
        print(f"⚠️  Найдено подозрительных клиентов: {len(suspicious_clients)}")
        for jar_path, result in suspicious_clients:
            jar_name = os.path.basename(jar_path)
            print(f"\n📌 {jar_name}:")
            # Выводим только строки с подозрительными классами
            for line in result.split('\n'):
                if line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.')):
                    print(f"   {line}")
    print("=" * 50)

    input("\nНажмите Enter для возврата в главное меню...")


# Компактная версия для быстрой проверки
def quick_check():
    """Только итоговый результат."""

    jars = find_labymod_jars()

    if not jars:
        print("LabyMod не найден")
        return

    print(f"Проверено клиентов: {len(jars)}")

    suspicious_count = 0
    results = []

    for jar_path in jars:
        jar_name = os.path.basename(jar_path)

        try:
            with zipfile.ZipFile(jar_path, 'r') as jar:
                class_times = []
                for entry in jar.infolist():
                    if entry.filename.endswith('.class'):
                        mod_time = datetime.datetime(*entry.date_time)
                        class_times.append(mod_time)

                if class_times:
                    # Проверяем, все ли времена одинаковы (до минуты)
                    first_time = class_times[0].replace(second=0, microsecond=0)
                    suspicious = []

                    for i, (entry) in enumerate(jar.infolist()):
                        if entry.filename.endswith('.class'):
                            file_time = datetime.datetime(*entry.date_time)
                            if abs((file_time.replace(second=0, microsecond=0) - first_time).total_seconds()) > 60:
                                suspicious.append(entry.filename)

                    if suspicious:
                        suspicious_count += 1
                        results.append(f"{jar_name}: {len(suspicious)} подозрительных классов")
                        # Выводим первые 3 подозрительных класса
                        for i, class_name in enumerate(suspicious[:3], 1):
                            results.append(f"   {class_name}")
                        if len(suspicious) > 3:
                            results.append(f"   ... и еще {len(suspicious) - 3}")
        except:
            results.append(f"{jar_name}: ошибка при проверке")

    # Итоговый вывод
    print("\n" + "=" * 50)
    if suspicious_count == 0:
        print("✅ Все клиенты чистые")
    else:
        print(f"⚠️  Подозрительных клиентов: {suspicious_count}")
        for result in results:
            print(result)
    print("=" * 50)

    input("\nНажмите Enter для возврата в главное меню...")


# Главная функция
def main():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        choice = main_menu()

        if choice == '1':
            os.system('cls' if os.name == 'nt' else 'clear')
            checker = MinecraftHashChecker()
            checker.run_check()
        elif choice == '2':
            os.system('cls' if os.name == 'nt' else 'clear')
            print("Выберите режим проверки LabyMod:")
            print("1. Полная проверка")
            print("2. Быстрая проверка")
            mode = input("Выберите режим (1-2): ").strip()

            if mode == '1':
                run_labymod_checker()
            elif mode == '2':
                quick_check()
        elif choice == '3':
            print("Выход из программы...")
            break
        else:
            print("Неверный выбор. Попробуйте снова.")
            time.sleep(1)


if __name__ == "__main__":
    main()