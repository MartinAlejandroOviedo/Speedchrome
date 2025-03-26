from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    # Tamaños de icono requeridos por Windows
    sizes = [(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)]
    
    # Colores
    background_color = (52, 152, 219)  # Azul Chrome
    chrome_colors = [
        (234, 67, 53),    # Rojo
        (251, 188, 5),    # Amarillo
        (52, 168, 83),    # Verde
        (66, 133, 244)    # Azul
    ]

    images = []
    
    for size in sizes:
        # Crear imagen base
        image = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Calcular dimensiones
        width, height = size
        center = (width//2, height//2)
        radius = min(width, height) // 2
        inner_radius = int(radius * 0.6)
        
        # Dibujar círculo exterior
        draw.ellipse([
            center[0] - radius,
            center[1] - radius,
            center[0] + radius,
            center[1] + radius
        ], fill=background_color)
        
        # Dibujar círculo interior
        draw.ellipse([
            center[0] - inner_radius,
            center[1] - inner_radius,
            center[0] + inner_radius,
            center[1] + inner_radius
        ], fill='white')
        
        # Dibujar flecha de velocidad
        if size[0] >= 32:  # Solo para tamaños mayores
            arrow_points = [
                (center[0] - radius//2, center[1]),
                (center[0] + radius//2, center[1] - radius//3),
                (center[0] + radius//2, center[1] + radius//3),
            ]
            draw.polygon(arrow_points, fill=(52, 152, 219))
        
        images.append(image)
    
    # Guardar como .ico
    images[0].save('icon.ico', format='ICO', sizes=sizes, append_images=images[1:])
    print("Icono creado exitosamente como 'icon.ico'")

if __name__ == "__main__":
    create_icon() 