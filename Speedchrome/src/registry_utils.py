import winreg
import logging
from typing import Optional, Any

class RegistryManager:
    @staticmethod
    def set_registry_value(browser_path: str, key_path: str, 
                          value_name: str, value: int) -> bool:
        """Establece un valor en el registro de Windows."""
        try:
            full_path = f"SOFTWARE\\{browser_path}\\{key_path}"
            with winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, full_path, 
                                  0, winreg.KEY_WRITE | winreg.KEY_WOW64_64KEY) as key:
                winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, value)
            return True
        except Exception as e:
            logging.error(f"Error al establecer registro {full_path}\\{value_name}: {e}")
            return False

    @staticmethod
    def get_registry_value(browser_path: str, key_path: str, 
                          value_name: str) -> Optional[Any]:
        """Obtiene un valor del registro de Windows."""
        try:
            full_path = f"SOFTWARE\\{browser_path}\\{key_path}"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, full_path, 
                              0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY) as key:
                value, _ = winreg.QueryValueEx(key, value_name)
                return value
        except Exception as e:
            logging.debug(f"No se pudo leer registro {full_path}\\{value_name}: {e}")
            return None 