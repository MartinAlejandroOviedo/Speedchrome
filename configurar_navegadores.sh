#!/bin/bash

# Verificar si el sistema es x64
ARCH=$(uname -m)
if [[ "$ARCH" != "x86_64" ]]; then
    echo "Este script solo es compatible con sistemas x64."
    exit 1
fi

# Solicitar confirmación
echo "Este script realizará los siguientes cambios:"
echo " - Establecer límite de memoria de Chromium"
echo " - Deshabilitar precarga de páginas"
echo " - Deshabilitar aceleración de hardware"
echo
read -p "¿Desea continuar? (S/N): " respuesta

respuesta=$(echo "$respuesta" | tr '[:lower:]' '[:upper:]')
if [[ "$respuesta" == "N" ]]; then
    echo "Cancelando..."
    exit 0
fi

# Función para detectar memoria
detectar_memoria() {
    total_memoria=$(free -m | awk '/^Mem:/ {print $2}')
    max_memoria=$((total_memoria / 2))
    
    read -p "Memoria a asignar (MB, máximo $max_memoria): " memoria_asignada
    memoria_asignada=${memoria_asignada:-$max_memoria}
    
    if [[ ! "$memoria_asignada" =~ ^[0-9]+$ ]] || (( memoria_asignada > max_memoria )); then
        echo "Usando valor máximo."
        memoria_asignada=$max_memoria
    fi

    export CHROME_MAX_MEMORY=$memoria_asignada
}

# Navegadores compatibles
browsers=("google-chrome" "chromium" "brave-browser" "opera" "microsoft-edge" "vivaldi" "yandex" "epic-browser" "colibri" "srware-iron" "comodo-dragon" "torch" "blisk" "coccoc" "slimjet")

# Función de configuración
configure_browser() {
    local browser=$1
    config_dir="$HOME/.config/$browser"
    
    [ ! -d "$config_dir" ] && return  # Saltar si no existe
    
    launch_flags_file="$config_dir/launch_flags.conf"
    touch "$launch_flags_file"
    
    grep -q "--disable-gpu" "$launch_flags_file" || echo "--disable-gpu" >> "$launch_flags_file"
    grep -q "--disable-preloading" "$launch_flags_file" || echo "--disable-preloading" >> "$launch_flags_file"
    
    echo "Configurado $browser con ${CHROME_MAX_MEMORY}MB"
}

# Proceso principal
detectar_memoria
for browser in "${browsers[@]}"; do
    configure_browser "$browser"
done

# Reinicio de navegadores
read -p "¿Reiniciar navegadores ahora? (S/N): " reiniciar
reiniciar=$(echo "$reiniciar" | tr '[:lower:]' '[:upper:]')

if [[ "$reiniciar" == "S" ]]; then
    echo "Cerrando navegadores..."
    
    # Lista actualizada de procesos coincidentes
    processes=(
        "chrome"                # Google Chrome
        "chromium"              # Chromium
        "brave"                 # Brave
        "opera"                 # Opera
        "msedge"                # Microsoft Edge
        "vivaldi"               # Vivaldi
        "yandex_browser"        # Yandex
        "epic"                  # Epic
        "colibri"               # Colibri
        "iron"                  # SRWare Iron
        "dragon"                # Comodo Dragon
        "torch"                 # Torch
        "blisk"                 # Blisk
        "coccoc"                # Cốc Cốc
        "slimjet"               # Slimjet
    )
    
    for proc in "${processes[@]}"; do
        if pkill -f "$proc"; then
            echo "✓ Cerrado: $proc"
        else
            echo "× No en ejecución: $proc"
        fi
    done
    
    echo "¡Reinicia manualmente los navegadores para aplicar cambios!"
fi
