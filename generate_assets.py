import os
import subprocess

# Убедимся, что Pillow установлен
try:
    from PIL import Image
except ImportError:
    subprocess.run(["pip", "install", "pillow"])
    from PIL import Image

def hex_to_rgba(hex_color):
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 6:
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4)) + (255,)
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4, 6))

# Шаблоны (маски) для 8x8 пикселей.
# 0 - прозрачный, 1 - контур, 2 - базовый цвет, 3 - блик, 4 - тень
INGOT = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 1, 1, 0, 0],
    [0, 0, 1, 3, 2, 1, 1, 0],
    [0, 1, 3, 2, 2, 4, 1, 0],
    [1, 3, 2, 2, 4, 4, 1, 0],
    [1, 1, 4, 4, 4, 1, 0, 0],
    [0, 1, 1, 1, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0]
]

GUARD = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 1, 0, 0, 0],
    [0, 1, 3, 2, 1, 0, 0, 0],
    [1, 3, 2, 4, 1, 0, 0, 0],
    [1, 2, 4, 4, 1, 0, 0, 0],
    [1, 1, 1, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0]
]

HANDLE = [
    [0, 0, 0, 1, 1, 0, 0, 0],
    [0, 0, 1, 3, 1, 0, 0, 0],
    [0, 1, 3, 2, 4, 1, 0, 0],
    [0, 1, 2, 2, 4, 1, 0, 0],
    [1, 2, 2, 4, 4, 1, 0, 0],
    [1, 4, 4, 1, 1, 0, 0, 0],
    [0, 1, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0]
]

materials = {
    # Blades (Лезвия)
    'blade_bronze.png': {'mask': INGOT, 'outline': '#2E1906', 'base': '#CD7F32', 'high': '#E29C5B', 'shadow': '#8C5622'},
    'blade_iron.png': {'mask': INGOT, 'outline': '#1A1A1A', 'base': '#A0A0A0', 'high': '#D0D0D0', 'shadow': '#606060'},
    'blade_carbon_steel.png': {'mask': INGOT, 'outline': '#000000', 'base': '#505050', 'high': '#787878', 'shadow': '#282828'},
    'blade_damascus.png': {'mask': INGOT, 'outline': '#0F1215', 'base': '#3B444B', 'high': '#7A8B99', 'shadow': '#212629'},
    'blade_obsidian.png': {'mask': INGOT, 'outline': '#000000', 'base': '#1D1A25', 'high': '#5D4C7A', 'shadow': '#0D0C12'},
    'blade_powder_steel.png': {'mask': INGOT, 'outline': '#3A4045', 'base': '#B0B8C0', 'high': '#E0E5E9', 'shadow': '#757D85'},
    'blade_mithril.png': {'mask': INGOT, 'outline': '#153C55', 'base': '#88D8F8', 'high': '#D4F1FB', 'shadow': '#4A9FCE'},
    'blade_meteorite.png': {'mask': INGOT, 'outline': '#1B1410', 'base': '#64544A', 'high': '#9E8575', 'shadow': '#3D312A'},
    'blade_titanium.png': {'mask': INGOT, 'outline': '#2B3135', 'base': '#96A0A8', 'high': '#CCD2D6', 'shadow': '#626B72'},
    'blade_cave_iron.png': {'mask': INGOT, 'outline': '#0B110B', 'base': '#384A38', 'high': '#5E7A5E', 'shadow': '#1F2A1F'},
    'blade_star_mercury.png': {'mask': INGOT, 'outline': '#180E24', 'base': '#8A58D4', 'high': '#D6BFF2', 'shadow': '#512A8F'},
    'blade_shadow_obsidian.png': {'mask': INGOT, 'outline': '#000000', 'base': '#150529', 'high': '#43137A', 'shadow': '#080112'},
    'blade_void_steel.png': {'mask': INGOT, 'outline': '#110022', 'base': '#330066', 'high': '#FF00FF', 'shadow': '#000000'},
    'blade_sun_forge.png': {'mask': INGOT, 'outline': '#4A1100', 'base': '#FFAA00', 'high': '#FFFF66', 'shadow': '#CC4400'},
    'blade_mokume_gane.png': {'mask': INGOT, 'outline': '#331A10', 'base': '#A86C45', 'high': '#D4A37A', 'shadow': '#663C25'},

    # Guards (Гарды)
    'guard_bronze.png': {'mask': GUARD, 'outline': '#2E1906', 'base': '#CD7F32', 'high': '#E29C5B', 'shadow': '#8C5622'},
    'guard_brass.png': {'mask': GUARD, 'outline': '#383010', 'base': '#C8B038', 'high': '#E8D468', 'shadow': '#887420'},
    'guard_carbon_steel.png': {'mask': GUARD, 'outline': '#000000', 'base': '#505050', 'high': '#787878', 'shadow': '#282828'},
    'guard_weapon_bronze.png': {'mask': GUARD, 'outline': '#201610', 'base': '#8A6040', 'high': '#B48A68', 'shadow': '#553620'},
    'guard_titan_bone.png': {'mask': GUARD, 'outline': '#2A2925', 'base': '#D6D4C8', 'high': '#F2F1EC', 'shadow': '#99968A'},
    'guard_chrono_ice.png': {'mask': GUARD, 'outline': '#0A1A2A', 'base': '#4AAEE8', 'high': '#B4E6F8', 'shadow': '#2272A8'},

    # Handles (Рукоятки)
    'handle_oak.png': {'mask': HANDLE, 'outline': '#2E1D0F', 'base': '#784D2B', 'high': '#A87445', 'shadow': '#4A2E19'},
    'handle_walnut.png': {'mask': HANDLE, 'outline': '#1B1109', 'base': '#4A3018', 'high': '#704B2A', 'shadow': '#291A0C'},
    'handle_maple.png': {'mask': HANDLE, 'outline': '#3A2818', 'base': '#C4986C', 'high': '#E4C29E', 'shadow': '#8F6641'},
    'handle_ivory.png': {'mask': HANDLE, 'outline': '#36342F', 'base': '#EAE5D4', 'high': '#F8F6F0', 'shadow': '#B5B09E'},
    'handle_stingray.png': {'mask': HANDLE, 'outline': '#11151A', 'base': '#384B5F', 'high': '#647D94', 'shadow': '#202C38'},
    'handle_mahogany.png': {'mask': HANDLE, 'outline': '#2B0A0A', 'base': '#6B1F1F', 'high': '#9C3A3A', 'shadow': '#451010'},
    'handle_deer_horn.png': {'mask': HANDLE, 'outline': '#2A251E', 'base': '#9E8E78', 'high': '#C8BBAA', 'shadow': '#635646'},
    'handle_ebony.png': {'mask': HANDLE, 'outline': '#0B0A09', 'base': '#2C2825', 'high': '#554E4A', 'shadow': '#161311'},
    'handle_dragonkin.png': {'mask': HANDLE, 'outline': '#22080F', 'base': '#7A1C33', 'high': '#B83252', 'shadow': '#450D1A'},
    'handle_illusion_silk.png': {'mask': HANDLE, 'outline': '#1E0D2A', 'base': '#884DCE', 'high': '#DA9CF8', 'shadow': '#512A84'},
    'handle_mammoth.png': {'mask': HANDLE, 'outline': '#25211B', 'base': '#A89E8C', 'high': '#DCD3C4', 'shadow': '#696052'},
}

def create_image(filename, props):
    img = Image.new('RGBA', (8, 8), (0,0,0,0))
    pixels = img.load()
    mask = props['mask']
    colors = {
        0: (0,0,0,0),
        1: hex_to_rgba(props['outline']),
        2: hex_to_rgba(props['base']),
        3: hex_to_rgba(props['high']),
        4: hex_to_rgba(props['shadow'])
    }
    for y in range(8):
        for x in range(8):
            pixels[x, y] = colors[mask[y][x]]
    
    out_path = os.path.join("d:/Docker_Project/static/images/materials", filename)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path)

for filename, props in materials.items():
    create_image(filename, props)

print(f"Generated {len(materials)} 8x8 assets successfully!")
