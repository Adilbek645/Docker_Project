from flask import Flask, render_template, request, redirect, url_for
import os
import sqlite3

DB_FOLDER = "data"
DB_PATH = "data/Forgery.db"


def get_connection():
    os.makedirs(DB_FOLDER, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def create_tables():
    connection = get_connection()
    cursor = connection.cursor()

    # users / игрок
    cursor.execute("""  
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        gold INTEGER DEFAULT 0,
        forge_level INTEGER DEFAULT 1,
        guild_reputation INTEGER DEFAULT 0,
        auction_access BOOLEAN DEFAULT 0
    )
    """)

    # inventory (инвентарь расходников)
    cursor.execute("""  
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        material_type TEXT NOT NULL,
        quantity INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    """)

    # swords (инвентарь мечей)
    cursor.execute("""  
    CREATE TABLE IF NOT EXISTS swords (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        creator_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        blade_material TEXT NOT NULL,
        guard_material TEXT NOT NULL,
        handle_material TEXT NOT NULL,
        final_damage INTEGER NOT NULL,
        final_price INTEGER NOT NULL,
        status TEXT DEFAULT 'В наличии',
        FOREIGN KEY (creator_id) REFERENCES users (id) ON DELETE CASCADE
    )
    """)

    # shop
    cursor.execute("""  
    CREATE TABLE IF NOT EXISTS shop_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        material_name TEXT NOT NULL,
        material_category TEXT NOT NULL,
        price INTEGER NOT NULL,
        required_forge_level INTEGER DEFAULT 1
    )
    """)

    connection.commit()
    connection.close()

def create_materials_table():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""  
    CREATE TABLE IF NOT EXISTS materials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        rarity TEXT NOT NULL,     
        image_url TEXT NOT NULL
    )
    """)

    all_materials = [
        # лезвия
        ('Бронза', 'Лезвие', 'Обычный', 'images/materials/blade_bronze.png'),
        ('Железо', 'Лезвие', 'Обычный', 'images/materials/blade_iron.png'),
        ('Углеродистая сталь', 'Лезвие', 'Обычный', 'images/materials/blade_carbon_steel.png'),
        ('Дамасская сталь', 'Лезвие', 'Обычный', 'images/materials/blade_damascus.png'),
        ('Обсидиан', 'Лезвие', 'Обычный', 'images/materials/blade_obsidian.png'),
        ('Порошковая сталь', 'Лезвие', 'Обычный', 'images/materials/blade_powder_steel.png'),
        ('Мифрил', 'Лезвие', 'Обычный', 'images/materials/blade_mithril.png'),
        ('Метеоритное железо', 'Лезвие', 'Обычный', 'images/materials/blade_meteorite.png'),
        
        # лезвия крутые
        ('Титановый сплав', 'Лезвие', 'Редкий', 'images/materials/blade_titanium.png'),
        ('Пещерное железо', 'Лезвие', 'Редкий', 'images/materials/blade_cave_iron.png'),
        ('Звёздная ртуть', 'Лезвие', 'Эпический', 'images/materials/blade_star_mercury.png'),
        ('Теневой обсидиан', 'Лезвие', 'Эпический', 'images/materials/blade_shadow_obsidian.png'),
        ('Пустотная сталь', 'Лезвие', 'Легендарный', 'images/materials/blade_void_steel.png'),
        ('Осколок Солнечного Горна', 'Лезвие', 'Легендарный', 'images/materials/blade_sun_forge.png'),
        ('Мокумэ-Ганэ', 'Лезвие', 'Легендарный', 'images/materials/blade_mokume_gane.png'),
        # гарды
        ('Бронза', 'Гарда', 'Обычный', 'images/materials/guard_bronze.png'),
        ('Латунь', 'Гарда', 'Обычный', 'images/materials/guard_brass.png'),
        ('Углеродистая сталь', 'Гарда', 'Обычный', 'images/materials/guard_carbon_steel.png'),
        # гарды крутые
        ('Оружейная бронза', 'Гарда', 'Редкий', 'images/materials/guard_weapon_bronze.png'),
        ('Кость Титана', 'Гарда', 'Эпический', 'images/materials/guard_titan_bone.png'),
        ('Хроно-Лёд', 'Гарда', 'Легендарный', 'images/materials/guard_chrono_ice.png'),
        # рукоятки
        ('Дуб', 'Рукоять', 'Обычный', 'images/materials/handle_oak.png'),
        ('Орех', 'Рукоять', 'Обычный', 'images/materials/handle_walnut.png'),
        ('Клен', 'Рукоять', 'Обычный', 'images/materials/handle_maple.png'),
        ('Слоновая кость', 'Рукоять', 'Обычный', 'images/materials/handle_ivory.png'),
        ('Кожа ската', 'Рукоять', 'Обычный', 'images/materials/handle_stingray.png'),
        # крутые рукоятки
        ('Красное дерево', 'Рукоять', 'Редкий', 'images/materials/handle_mahogany.png'),
        ('Рог оленя', 'Рукоять', 'Редкий', 'images/materials/handle_deer_horn.png'),
        ('Черное дерево', 'Рукоять', 'Эпический', 'images/materials/handle_ebony.png'),
        ('Кожа Драконида', 'Рукоять', 'Эпический', 'images/materials/handle_dragonkin.png'),
        ('Шелк Иллюзий', 'Рукоять', 'Легендарный', 'images/materials/handle_illusion_silk.png'),
        ('Бивень Мамонта', 'Рукоять', 'Легендарный', 'images/materials/handle_mammoth.png'),
    ]

    cursor.execute("DELETE FROM materials")
    cursor.executemany("""
        INSERT INTO materials (name, category, rarity, image_url) 
        VALUES (?, ?, ?, ?)
    """, all_materials)

    connection.commit()
    connection.close()

def fill_shop():
    shop_items = [
        ('Бронза', 'Лезвие', 50, 1),
        ('Железо', 'Лезвие', 100, 1),
        ('Углеродистая сталь', 'Лезвие', 250, 2),
        ('Дуб', 'Рукоять', 20, 1),
        ('Кожа ската', 'Рукоять', 150, 1)
    ]
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM shop_items")
    cursor.executemany("""
        INSERT INTO shop_items (material_name, material_category, price, required_forge_level) 
        VALUES (?, ?, ?, ?)
    """, shop_items)
    
    connection.commit()
    connection.close()



app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def forgery():
    return render_template("forgery.html")

@app.route("/auction", methods=["GET", "POST"])
def auction():
    return render_template("auction.html")

@app.route("/shop", methods=["GET", "POST"])
def shop():
    user_id = 1
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT gold, forge_level FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    cursor.execute("""
        SELECT s.id, s.material_name, s.material_category ,s.price, s.required_forge_level, m.rarity, m.image_url
        FROM shop_items s
        JOIN materials m ON s.material_name = m.name AND s.material_category = m.category
    """)
    shop_items_db = cursor.fetchall()
    connection.close()

    items = []
    for item in shop_items_db:
        items.append({
            "id": item["id"],
            "name": item["material_name"],
            "price": item["price"],
            "required_forge_level": item["required_forge_level"],
            "rarity": item["rarity"],
            "image": f"/static/{item['image_url']}",
            "category": item["material_category"]
        })

    return render_template("shop.html", items=items, user=user)

@app.route("/guild", methods=["GET", "POST"])
def guild():
    return render_template("guild.html")

@app.route("/upgrades", methods=["GET", "POST"])
def upgrades():
    return render_template("upgrades.html")

@app.route("/inventory", methods=["GET", "POST"])
def inventory():
    # тут тоже поменяю
    user_id = 1
    connection = get_connection()
    cursor = connection.cursor()
    inventory_items = []

    cursor.execute("""
        SELECT m.name, m.category, m.rarity, m.image_url, i.quantity 
        FROM inventory i
        JOIN materials m ON i.material_type = m.name
        WHERE i.user_id = ?
    """, (user_id,))
    items = cursor.fetchall()
    connection.close()

    for item in items:
        inventory_items.append({
            "name": item["name"],
            "category": item["category"],
            "rarity": item["rarity"],
            "image": f"/static/{item['image_url']}", 
            "quantity": item["quantity"]
        })

    return render_template("inventory.html", items=inventory_items)

if __name__ == '__main__':
    # проверка работы, я это потом удалю 👍
    create_tables()
    create_materials_table()
    fill_shop()
    
    conn = get_connection()
    conn.cursor().execute("INSERT OR IGNORE INTO users (id, gold) VALUES (1, 1000)")

    conn.cursor().execute("DELETE FROM inventory WHERE user_id = 1")
    conn.cursor().execute("INSERT INTO inventory (user_id, material_type, quantity) VALUES (1, 'Железо', 15)")
    conn.cursor().execute("INSERT INTO inventory (user_id, material_type, quantity) VALUES (1, 'Пустотная сталь', 2)")
    
    conn.commit()
    conn.close()
    
    app.run(host="0.0.0.0", port=5000)