#!/bin/bash

# Script: configurar_navegadores_motosierra.sh
# Autor: Martín y su IA cómplice en modo destructor
# Misión: Hackear navegadores y ejecutarlos con sonido de motosierra, por el bien de la humanidad.

# Verificar si el sistema es x64
ARCH=$(uname -m)
if [[ "$ARCH" != "x86_64" ]]; then
    echo "Este script solo es compatible con sistemas x64. Si no sos x64, lo lamento mucho."
    exit 1
fi

# Solicitar confirmación antes de comenzar el asalto quirúrgico
echo "Este script realizará los siguientes cambios:"
echo " - Establecer límite de memoria para JS en 32 GB."
echo " - Deshabilitar la aceleración de hardware."
echo " - Deshabilitar la precarga de páginas."
echo
read -p "¿Desea continuar? (S/N): " respuesta

respuesta=$(echo "$respuesta" | tr '[:lower:]' '[:upper:]')
if [[ "$respuesta" != "S" ]]; then
    echo "Cancelando operación... por ahora."
    exit 0
fi

# Navegadores objetivo
browsers=("google-chrome" "chromium" "brave-browser" "opera" "microsoft-edge")

# Flags que queremos meterle sí o sí
NEW_FLAGS="--disable-gpu --disable-prerender --js-flags=--max_old_space_size=32960"

# Ruta del sonido de motosierra (ejemplo estándar de sistemas Linux)
SONIDO_MOTOSIERRA="/usr/share/sounds/freedesktop/stereo/alarm-clock-elapsed.oga"

# Chequear si existe sonido
if [[ ! -f "$SONIDO_MOTOSIERRA" ]]; then
    echo "⚠️ Sonido de motosierra no encontrado. Se ejecutará la misión en silencio."
    USAR_SONIDO=false
else
    USAR_SONIDO=true
fi

# Función para modificar el .desktop
patch_desktop() {
    local browser="$1"
    echo "Procesando $browser..."

    # Intentamos buscar el archivo .desktop
    local desktop_file=""
    if [[ -f "/usr/share/applications/$browser.desktop" ]]; then
        desktop_file="/usr/share/applications/$browser.desktop"
    elif [[ -f "$HOME/.local/share/applications/$browser.desktop" ]]; then
        desktop_file="$HOME/.local/share/applications/$browser.desktop"
    else
        echo "Archivo .desktop no encontrado para $browser. Saltando..."
        return
    fi

    echo "Archivo .desktop encontrado: $desktop_file"

    # Backup si no existe todavía
    if [[ ! -f "${desktop_file}.bak" ]]; then
        sudo cp "$desktop_file" "${desktop_file}.bak"
        echo "Backup creado en ${desktop_file}.bak"
    fi

    # Modificar la línea Exec=
    sudo sed -i "/^Exec=/ s#\$# $NEW_FLAGS#" "$desktop_file"
    echo "Se aplicaron flags a $browser."
}

# Loop principal para modificar lanzadores
for browser in "${browsers[@]}"; do
    patch_desktop "$browser"
done

# Mensaje final de misión cumplida
echo
echo "¡Listo! Los navegadores fueron modificados con éxito."
echo "Es recomendable cerrar y volver a abrir los navegadores para que los cambios surtan efecto."
echo

# Función para matar procesos con sonido de motosierra
matar_proceso_con_motosierra() {
    local proceso="$1"

    if pgrep -f "$proceso" > /dev/null; then
        echo "🔴 Detectado proceso relacionado a '$proceso'. Procediendo a su ejecución..."
        pkill -9 -f "$proceso"

        if [[ "$USAR_SONIDO" == true ]]; then
            paplay "$SONIDO_MOTOSIERRA" 2>/dev/null || aplay "$SONIDO_MOTOSIERRA" 2>/dev/null
        fi

        echo "✅ $proceso ELIMINADO."
    else
        echo "⚪ No se encontró proceso '$proceso'. Nada que cortar."
    fi
}

# Preguntar si queremos cerrar los navegadores
read -p "¿Desea cerrar los navegadores ahora? (S/N): " cerrar

cerrar=$(echo "$cerrar" | tr '[:lower:]' '[:upper:]')
if [[ "$cerrar" == "S" ]]; then
    echo
    echo "🪓 Iniciando secuencia de motosierra sobre navegadores..."
    for proc in "chrome" "chromium" "brave" "opera" "microsoft-edge" "microsoft-edge-stable" "msedge"; do
        matar_proceso_con_motosierra "$proc"
    done
    echo
    echo "🪓 Todos los navegadores chromium-based han sido ejecutados. 🪓"
    echo "🎯 Misión cumplida. La consola queda limpia como el alma de un héroe."
else
    echo "Muy bien, reinicialos manualmente cuando quieras."
fi

echo
