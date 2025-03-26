import os
import psutil
import winreg
import logging
from typing import Dict, List, Tuple
from datetime import datetime

class BrowserManager:
    BROWSER_PATHS = {
        'Chrome': {
            'reg_paths': [
                r'SOFTWARE\Google\Chrome',
                r'SOFTWARE\Wow6432Node\Google\Chrome'
            ],
            'process': 'chrome.exe',
            'friendly_name': 'Google Chrome'
        },
        'Edge': {
            'reg_paths': [
                r'SOFTWARE\Microsoft\Edge'
            ],
            'process': 'msedge.exe',
            'friendly_name': 'Microsoft Edge (Chromium)'
        },
        'Brave': {
            'reg_paths': [
                r'SOFTWARE\BraveSoftware\Brave-Browser'
            ],
            'process': 'brave.exe',
            'friendly_name': 'Brave Browser'
        }
    }

    SPEEDCHROME_REG_PATH = r'SOFTWARE\SpeedChrome'
    
    @staticmethod
    def check_registry_paths(reg_paths: List[str]) -> bool:
        """Verifica la existencia del navegador en el registro."""
        for reg_path in reg_paths:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, 
                                  winreg.KEY_READ | winreg.KEY_WOW64_64KEY):
                    return True
            except WindowsError:
                continue
        return False

    @staticmethod
    def detect_installed_browsers() -> Dict[str, bool]:
        """Detecta los navegadores instalados usando el registro."""
        installed = {}
        
        for browser, info in BrowserManager.BROWSER_PATHS.items():
            # Verificar en el registro
            installed[browser] = BrowserManager.check_registry_paths(info['reg_paths'])
            logging.debug(f"{browser}: instalado={installed[browser]}")

        return installed

    @staticmethod
    def get_browser_path(browser: str) -> str:
        """Obtiene la ruta del registro correcta para un navegador."""
        if browser in BrowserManager.BROWSER_PATHS:
            # Intentar obtener la primera ruta de registro válida
            for reg_path in BrowserManager.BROWSER_PATHS[browser]['reg_paths']:
                if BrowserManager.check_registry_paths([reg_path]):
                    # Eliminar 'SOFTWARE\' del inicio de la ruta
                    return reg_path.replace('SOFTWARE\\', '', 1)
        return ""

    @staticmethod
    def check_previous_config() -> Tuple[bool, Dict[str, Dict]]:
        """Verifica si existe una configuración previa y la retorna"""
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, BrowserManager.SPEEDCHROME_REG_PATH, 0, 
                              winreg.KEY_READ | winreg.KEY_WOW64_64KEY) as key:
                # Leer la última configuración
                config = {}
                for browser in BrowserManager.BROWSER_PATHS:
                    try:
                        with winreg.OpenKey(key, browser, 0, winreg.KEY_READ) as browser_key:
                            config[browser] = {
                                'memory_limit': winreg.QueryValueEx(browser_key, 'memory_limit')[0],
                                'disable_preload': winreg.QueryValueEx(browser_key, 'disable_preload')[0],
                                'disable_hardware': winreg.QueryValueEx(browser_key, 'disable_hardware')[0],
                                'last_update': winreg.QueryValueEx(browser_key, 'last_update')[0]
                            }
                    except WindowsError:
                        continue
                return True, config
        except WindowsError:
            return False, {}

    @staticmethod
    def save_config(browser: str, config: Dict) -> bool:
        """Guarda la configuración aplicada"""
        try:
            # Crear clave principal si no existe
            key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, BrowserManager.SPEEDCHROME_REG_PATH, 0, 
                                   winreg.KEY_WRITE | winreg.KEY_WOW64_64KEY)
            
            # Crear subclave para el navegador
            browser_key = winreg.CreateKeyEx(key, browser, 0, winreg.KEY_WRITE)
            
            # Guardar configuración
            for name, value in config.items():
                winreg.SetValueEx(browser_key, name, 0, winreg.REG_DWORD, value)
            
            # Agregar timestamp
            timestamp = int(datetime.now().timestamp())
            winreg.SetValueEx(browser_key, 'last_update', 0, winreg.REG_DWORD, timestamp)
            
            return True
        except Exception as e:
            logging.error(f"Error al guardar configuración: {e}")
            return False

    @staticmethod
    def kill_browsers(selected_browsers: List[str]) -> Dict[str, bool]:
        """Cierra los navegadores seleccionados."""
        results = {}
        for browser in selected_browsers:
            if browser in BrowserManager.BROWSER_PATHS:
                process_name = BrowserManager.BROWSER_PATHS[browser]['process']
                try:
                    killed = False
                    for proc in psutil.process_iter(['name']):
                        if proc.info['name'].lower() == process_name.lower():
                            proc.kill()
                            killed = True
                    results[browser] = killed
                except Exception as e:
                    logging.error(f"Error al cerrar {browser}: {e}")
                    results[browser] = False
        return results 