import tkinter as tk
from tkinter import ttk, messagebox
import ctypes
import logging
import psutil
from datetime import datetime
from browser_manager import BrowserManager
from registry_utils import RegistryManager

class SpeedChromeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SpeedChrome Optimizer")
        self.root.geometry("600x700")
        
        # Crear menú
        self.create_menu()
        
        # Verificar configuración previa
        self.has_previous_config, self.previous_config = BrowserManager.check_previous_config()
        
        self.setup_ui()
        self.setup_logging()
        self.check_browsers()
        
        # Cargar configuración previa si existe
        if self.has_previous_config:
            self.load_previous_config()
            self.log_message("Configuración anterior cargada")

    def create_menu(self):
        """Crea la barra de menú"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menú Archivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Salir", command=self.root.quit)
        
        # Menú Ayuda
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=help_menu)
        help_menu.add_command(label="Acerca de", command=self.show_about)

    def setup_ui(self):
        # Frame principal
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título y descripción
        ttk.Label(
            self.main_frame,
            text="SpeedChrome Optimizer",
            font=("Helvetica", 14, "bold")
        ).pack(pady=5)
        
        ttk.Label(
            self.main_frame,
            text="Esta herramienta optimiza navegadores basados en Chromium.\n"
                 "Compatible con Google Chrome, Microsoft Edge y Brave.",
            wraplength=500,
            justify="center"
        ).pack(pady=5)

        # Indicador de configuración previa
        if self.has_previous_config:
            self.config_label = ttk.Label(
                self.main_frame,
                text="✓ Configuración anterior detectada",
                foreground='green'
            )
            self.config_label.pack(pady=5)

        # Frame de navegadores
        self.browsers_frame = ttk.LabelFrame(self.main_frame, text="Navegadores")
        self.browsers_frame.pack(fill=tk.X, pady=10)
        
        self.browser_vars = {}
        for browser, info in BrowserManager.BROWSER_PATHS.items():
            var = tk.BooleanVar(value=False)
            self.browser_vars[browser] = var
            ttk.Checkbutton(
                self.browsers_frame,
                text=info['friendly_name'],
                variable=var
            ).pack(anchor=tk.W, padx=5, pady=2)

        # Frame de opciones
        self.options_frame = ttk.LabelFrame(self.main_frame, text="Opciones de Optimización")
        self.options_frame.pack(fill=tk.X, pady=10)
        
        # Opciones de memoria
        self.memory_frame = ttk.LabelFrame(self.options_frame, text="Configuración de Memoria")
        self.memory_frame.pack(fill=tk.X, padx=5, pady=5)

        total_memory = psutil.virtual_memory().total // (1024 * 1024 * 1024)
        self.memory_var = tk.BooleanVar(value=True)
        self.memory_limit_var = tk.StringVar(value="4")
        
        ttk.Checkbutton(
            self.memory_frame,
            text="Limitar memoria",
            variable=self.memory_var,
            command=self.toggle_memory_options
        ).pack(anchor=tk.W, padx=5, pady=2)

        self.memory_options_frame = ttk.Frame(self.memory_frame)
        self.memory_options_frame.pack(fill=tk.X, padx=20, pady=2)

        ttk.Label(
            self.memory_options_frame,
            text="Límite de memoria (GB):"
        ).pack(side=tk.LEFT, padx=5)

        self.memory_spinbox = ttk.Spinbox(
            self.memory_options_frame,
            from_=1,
            to=total_memory,
            textvariable=self.memory_limit_var,
            width=5
        )
        self.memory_spinbox.pack(side=tk.LEFT, padx=5)

        ttk.Label(
            self.memory_options_frame,
            text=f"(Máximo disponible: {total_memory} GB)"
        ).pack(side=tk.LEFT, padx=5)

        # Otras opciones
        self.preload_var = tk.BooleanVar(value=True)
        self.hardware_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(
            self.options_frame,
            text="Deshabilitar precarga de páginas",
            variable=self.preload_var
        ).pack(anchor=tk.W, padx=5, pady=2)
        
        ttk.Checkbutton(
            self.options_frame,
            text="Deshabilitar aceleración de hardware",
            variable=self.hardware_var
        ).pack(anchor=tk.W, padx=5, pady=2)

        # Botones
        self.buttons_frame = ttk.Frame(self.main_frame)
        self.buttons_frame.pack(pady=10)

        if self.has_previous_config:
            ttk.Button(
                self.buttons_frame,
                text="Restablecer valores por defecto",
                command=self.reset_to_defaults
            ).pack(side=tk.LEFT, padx=5)

        self.apply_button = ttk.Button(
            self.buttons_frame,
            text="Aplicar Cambios",
            command=self.apply_changes
        )
        self.apply_button.pack(side=tk.LEFT, padx=5)
        
        # Área de log
        self.log_frame = ttk.LabelFrame(self.main_frame, text="Log")
        self.log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(self.log_frame, height=8, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    def check_browsers(self):
        installed_browsers = BrowserManager.detect_installed_browsers()
        for browser, installed in installed_browsers.items():
            if browser in self.browser_vars:
                for child in self.browsers_frame.winfo_children():
                    if browser in child.cget('text'):
                        child.configure(state='normal' if installed else 'disabled')
                        if not installed:
                            self.browser_vars[browser].set(False)

    def load_previous_config(self):
        """Carga la configuración anterior en la interfaz"""
        try:
            for browser, config in self.previous_config.items():
                if browser in self.browser_vars:
                    # Convertir timestamp a fecha legible
                    last_update = datetime.fromtimestamp(config['last_update'])
                    date_str = last_update.strftime("%d/%m/%Y %H:%M")
                    
                    # Verificar si el navegador está instalado
                    browser_installed = any(
                        child.cget('state') != 'disabled' 
                        for child in self.browsers_frame.winfo_children() 
                        if browser in child.cget('text')
                    )
                    
                    if browser_installed:
                        self.browser_vars[browser].set(True)
                        self.log_message(f"Configuración encontrada para {browser} (última modificación: {date_str})")
                        
                        # Cargar configuración de memoria
                        if 'memory_limit' in config:
                            memory_gb = config['memory_limit'] // 1024  # Convertir MB a GB
                            self.memory_var.set(True)
                            self.memory_limit_var.set(str(memory_gb))
                        
                        # Cargar otras configuraciones
                        if 'disable_preload' in config:
                            self.preload_var.set(bool(config['disable_preload']))
                        
                        if 'disable_hardware' in config:
                            self.hardware_var.set(bool(config['disable_hardware']))
            
            # Mostrar mensaje informativo
            messagebox.showinfo(
                "Configuración Anterior",
                "Se ha detectado una configuración anterior y se ha cargado.\n\n"
                "Puede realizar cambios o aplicar la misma configuración nuevamente."
            )
            
        except Exception as e:
            self.log_message(f"Error al cargar configuración anterior: {e}")

    def toggle_memory_options(self):
        state = 'normal' if self.memory_var.get() else 'disabled'
        self.memory_spinbox.configure(state=state)

    def reset_to_defaults(self):
        """Restablece todos los valores a su configuración por defecto"""
        if messagebox.askyesno(
            "Restablecer valores",
            "¿Está seguro de que desea restablecer todos los valores a su configuración por defecto?"
        ):
            # Desmarcar todos los navegadores
            for var in self.browser_vars.values():
                var.set(False)
            
            # Restablecer opciones de memoria
            self.memory_var.set(True)
            self.memory_limit_var.set("4")
            
            # Restablecer otras opciones
            self.preload_var.set(True)
            self.hardware_var.set(True)
            
            self.log_message("Valores restablecidos a configuración por defecto")

    def show_about(self):
        """Muestra la ventana de Acerca de"""
        about_window = tk.Toplevel(self.root)
        about_window.title("Acerca de SpeedChrome Optimizer")
        about_window.geometry("400x300")
        about_window.resizable(False, False)
        
        # Hacer la ventana modal
        about_window.transient(self.root)
        about_window.grab_set()
        
        # Frame principal
        frame = ttk.Frame(about_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(
            frame,
            text="SpeedChrome Optimizer",
            font=("Helvetica", 16, "bold")
        ).pack(pady=10)
        
        # Versión
        ttk.Label(
            frame,
            text="Versión 1.0",
            font=("Helvetica", 10)
        ).pack()
        
        # Descripción
        ttk.Label(
            frame,
            text="Optimizador de navegadores basados en Chromium",
            wraplength=350,
            justify="center"
        ).pack(pady=10)
        
        # Separador
        ttk.Separator(frame, orient='horizontal').pack(fill='x', pady=10)
        
        # Créditos
        ttk.Label(
            frame,
            text="Desarrollado por:",
            font=("Helvetica", 10, "bold")
        ).pack(pady=5)
        
        ttk.Label(
            frame,
            text="Martin Alejandro Oviedo\nClaude AI Assistant",
            justify="center"
        ).pack()
        
        # Separador
        ttk.Separator(frame, orient='horizontal').pack(fill='x', pady=10)
        
        # Copyright
        ttk.Label(
            frame,
            text="© 2024 SpeedChrome Optimizer\nTodos los derechos reservados",
            justify="center",
            font=("Helvetica", 8)
        ).pack(pady=10)
        
        # Botón cerrar
        ttk.Button(
            frame,
            text="Cerrar",
            command=about_window.destroy
        ).pack(pady=10)
        
        # Centrar la ventana
        about_window.update_idletasks()
        width = about_window.winfo_width()
        height = about_window.winfo_height()
        x = (about_window.winfo_screenwidth() // 2) - (width // 2)
        y = (about_window.winfo_screenheight() // 2) - (height // 2)
        about_window.geometry(f'{width}x{height}+{x}+{y}')

    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        logging.info(message)

    def apply_changes(self):
        if not self.is_admin():
            messagebox.showerror(
                "Error",
                "Este programa requiere privilegios de administrador."
            )
            return

        selected_browsers = [
            browser for browser, var in self.browser_vars.items() 
            if var.get() and any(
                child.cget('state') != 'disabled' 
                for child in self.browsers_frame.winfo_children() 
                if browser in child.cget('text')
            )
        ]

        if not selected_browsers:
            messagebox.showwarning(
                "Advertencia",
                "Por favor seleccione al menos un navegador."
            )
            return

        # Preguntar si quiere sobrescribir la configuración anterior
        if self.has_previous_config and any(browser in self.previous_config for browser in selected_browsers):
            if not messagebox.askyesno(
                "Configuración existente",
                "Ya existe una configuración anterior para algunos navegadores.\n"
                "¿Desea sobrescribir la configuración existente?"
            ):
                return

        self.log_message("Iniciando optimización...")
        
        for browser in selected_browsers:
            browser_path = BrowserManager.get_browser_path(browser)
            if not browser_path:
                self.log_message(f"⚠ No se pudo encontrar la ruta de registro para {browser}")
                continue
                
            self.log_message(f"Configurando {browser}...")

            if self.memory_var.get():
                memory_limit = int(self.memory_limit_var.get()) * 1024  # Convertir a MB
                success = RegistryManager.set_registry_value(
                    browser_path, "Process", "MaxMemPerProcess", memory_limit
                )
                self.log_message(f"✓ Límite de memoria configurado a {memory_limit}MB: {success}")

            if self.preload_var.get():
                success = RegistryManager.set_registry_value(
                    browser_path, "Prefetch", "EnablePrefetch", 0
                )
                self.log_message(f"✓ Precarga deshabilitada: {success}")

            if self.hardware_var.get():
                success = RegistryManager.set_registry_value(
                    browser_path, "HardwareAcceleration", 
                    "EnableHardwareAcceleration", 0
                )
                self.log_message(f"✓ Aceleración hardware deshabilitada: {success}")

            # Guardar la configuración actual
            config = {
                'memory_limit': int(self.memory_limit_var.get()) * 1024,
                'disable_preload': int(self.preload_var.get()),
                'disable_hardware': int(self.hardware_var.get()),
                'last_update': int(datetime.now().timestamp())
            }
            if BrowserManager.save_config(browser, config):
                self.log_message(f"✓ Configuración guardada para {browser}")
            else:
                self.log_message(f"⚠ No se pudo guardar la configuración para {browser}")

        if messagebox.askyesno(
            "Reiniciar navegadores",
            "¿Desea reiniciar los navegadores ahora?"
        ):
            results = BrowserManager.kill_browsers(selected_browsers)
            for browser, killed in results.items():
                self.log_message(
                    f"{'✓' if killed else '✗'} {browser} "
                    f"{'cerrado' if killed else 'no pudo ser cerrado'}"
                )

        self.log_message("¡Optimización completada!")

    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

def main():
    if not ctypes.windll.shell32.IsUserAnAdmin():
        messagebox.showerror(
            "Error",
            "Este programa requiere privilegios de administrador.\n"
            "Por favor, ejecútelo como administrador."
        )
        return

    root = tk.Tk()
    app = SpeedChromeGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 