from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import sqlite3
import random
import PIL
from PIL import Image
import os

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
        material_name TEXT NOT NULL,
        material_category TEXT NOT NULL,
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
    cursor.execute("DROP TABLE IF EXISTS materials")
    cursor.execute("""  
    CREATE TABLE IF NOT EXISTS materials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        rarity TEXT NOT NULL,     
        image_url TEXT NOT NULL,
        base_price INTEGER NOT NULL DEFAULT 50
    )
    """)

    all_materials = [
        # лезвия
        ('Бронза', 'Лезвие', 'Обычный', 'images/materials/blade_bronze.png', 50),
        ('Железо', 'Лезвие', 'Обычный', 'images/materials/blade_iron.png', 100),
        ('Углеродистая сталь', 'Лезвие', 'Обычный', 'images/materials/blade_carbon_steel.png', 200),
        ('Дамасская сталь', 'Лезвие', 'Обычный', 'images/materials/blade_damascus.png', 250),
        ('Обсидиан', 'Лезвие', 'Обычный', 'images/materials/blade_obsidian.png', 300),
        ('Порошковая сталь', 'Лезвие', 'Обычный', 'images/materials/blade_powder_steel.png', 350),
        ('Мифрил', 'Лезвие', 'Обычный', 'images/materials/blade_mithril.png', 400),
        ('Метеоритное железо', 'Лезвие', 'Обычный', 'images/materials/blade_meteorite.png', 450),
        
        # лезвия крутые
        ('Титановый сплав', 'Лезвие', 'Редкий', 'images/materials/blade_titanium.png', 600),
        ('Пещерное железо', 'Лезвие', 'Редкий', 'images/materials/blade_cave_iron.png', 700),
        ('Звёздная ртуть', 'Лезвие', 'Эпический', 'images/materials/blade_star_mercury.png', 1500),
        ('Теневой обсидиан', 'Лезвие', 'Эпический', 'images/materials/blade_shadow_obsidian.png', 1800),
        ('Пустотная сталь', 'Лезвие', 'Легендарный', 'images/materials/blade_void_steel.png', 5000),
        ('Осколок Солнечного Горна', 'Лезвие', 'Легендарный', 'images/materials/blade_sun_forge.png', 6500),
        ('Мокумэ-Ганэ', 'Лезвие', 'Легендарный', 'images/materials/blade_mokume_gane.png', 8000),
        
        # гарды
        ('Бронза', 'Гарда', 'Обычный', 'images/materials/guard_bronze.png', 30),
        ('Латунь', 'Гарда', 'Обычный', 'images/materials/guard_brass.png', 60),
        ('Углеродистая сталь', 'Гарда', 'Обычный', 'images/materials/guard_carbon_steel.png', 120),
        
        # гарды крутые
        ('Оружейная бронза', 'Гарда', 'Редкий', 'images/materials/guard_weapon_bronze.png', 300),
        ('Кость Титана', 'Гарда', 'Эпический', 'images/materials/guard_titan_bone.png', 1000),
        ('Хроно-Лёд', 'Гарда', 'Легендарный', 'images/materials/guard_chrono_ice.png', 4000),
        
        # рукоятки
        ('Дуб', 'Рукоять', 'Обычный', 'images/materials/handle_oak.png', 20),
        ('Орех', 'Рукоять', 'Обычный', 'images/materials/handle_walnut.png', 40),
        ('Клен', 'Рукоять', 'Обычный', 'images/materials/handle_maple.png', 60),
        ('Слоновая кость', 'Рукоять', 'Обычный', 'images/materials/handle_ivory.png', 100),
        ('Кожа ската', 'Рукоять', 'Обычный', 'images/materials/handle_stingray.png', 150),
        
        # крутые рукоятки
        ('Красное дерево', 'Рукоять', 'Редкий', 'images/materials/handle_mahogany.png', 400),
        ('Рог оленя', 'Рукоять', 'Редкий', 'images/materials/handle_deer_horn.png', 500),
        ('Черное дерево', 'Рукоять', 'Эпический', 'images/materials/handle_ebony.png', 1200),
        ('Кожа Драконида', 'Рукоять', 'Эпический', 'images/materials/handle_dragonkin.png', 1600),
        ('Шелк Иллюзий', 'Рукоять', 'Легендарный', 'images/materials/handle_illusion_silk.png', 3500),
        ('Бивень Мамонта', 'Рукоять', 'Легендарный', 'images/materials/handle_mammoth.png', 4500),
    ]

    cursor.execute("DELETE FROM materials")
    for item in all_materials:
        cursor.execute("INSERT OR IGNORE INTO materials (name, category, rarity, image_url, base_price) VALUES (?, ?, ?, ?, ?)", item)

    connection.commit()
    connection.close()

def fill_shop():
    shop_items = [
        ('Бронза', 'Лезвие', 50, 1),
        ('Железо', 'Лезвие', 100, 1),
        ('Углеродистая сталь', 'Лезвие', 250, 2),
        ('Дуб', 'Рукоять', 20, 1),
        ('Кожа ската', 'Рукоять', 150, 1),
        ('Бронза', 'Гарда', 30, 1),
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
    user_id = 1
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute("""
        SELECT m.name, m.category, m.rarity, m.image_url, i.quantity 
        FROM inventory i
        JOIN materials m ON i.material_name = m.name AND i.material_category = m.category
        WHERE i.user_id = ? AND i.quantity > 0
    """, (user_id,))
    inventory = cursor.fetchall()
    
    connection.close()
    return render_template("forgery.html", inventory=inventory)

@app.route("/forge_sword", methods=["POST"])
def forge_sword():
    data = request.get_json()
    blade = data.get("blade")
    guard = data.get("guard")
    handle = data.get("handle")
    sword_name = data.get("sword_name", "Новый Меч")
    
    if not blade or not guard or not handle:
        return jsonify({"success": False, "error": "Нужны все 3 компонента!"})
        
    user_id = 1
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        for material_name, material_category in [(blade, 'Лезвие'), (guard, 'Гарда'), (handle, 'Рукоять')]:
            cursor.execute("SELECT quantity FROM inventory WHERE user_id = ? AND material_name = ? AND material_category = ?", (user_id, material_name, material_category))
            item = cursor.fetchone()
            if not item or item["quantity"] < 1:
                return jsonify({"success": False, "error": f"Не хватает материала: {material_name}"})
                
        materials_data = {}
        total_price = 0
        for material_name in [blade, guard, handle]:
            cursor.execute("SELECT image_url, base_price FROM materials WHERE name = ?", (material_name,))
            mat_info = cursor.fetchone()
            if mat_info:
                materials_data[material_name] = mat_info["image_url"]
                total_price += mat_info["base_price"]
            else:
                materials_data[material_name] = "images/materials/blade_iron.png"
                total_price += 50
            
        cursor.execute("SELECT forge_level FROM users WHERE id = ?", (user_id,))
        forge_level = cursor.fetchone()["forge_level"]
        
        level_multiplier = 1.0 + ((forge_level - 1) * 0.15)
        final_price = int(total_price * level_multiplier)
        final_damage = int((total_price / 10) * level_multiplier)
        
        for material_name, material_category in [(blade, 'Лезвие'), (guard, 'Гарда'), (handle, 'Рукоять')]:
            cursor.execute("UPDATE inventory SET quantity = quantity - 1 WHERE user_id = ? AND material_name = ? AND material_category = ?", (user_id, material_name, material_category))
            
        cursor.execute("""
            INSERT INTO swords (creator_id, name, blade_material, guard_material, handle_material, final_damage, final_price, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'В наличии')
        """, (user_id, sword_name, blade, guard, handle, final_damage, final_price))
        sword_id = cursor.lastrowid
        
        connection.commit()
        
        
        
        blade_img = Image.open(f"static/{materials_data[blade]}").convert("RGBA")
        guard_img = Image.open(f"static/{materials_data[guard]}").convert("RGBA")
        handle_img = Image.open(f"static/{materials_data[handle]}").convert("RGBA")
        
        sword_img = Image.new("RGBA", (8, 24), (0,0,0,0))
        sword_img.paste(blade_img, (0, 0), blade_img)
        sword_img.paste(guard_img, (0, 8), guard_img)
        sword_img.paste(handle_img, (0, 16), handle_img)
        
        os.makedirs("static/images/swords", exist_ok=True)
        sword_img.save(f"static/images/swords/{sword_id}.png")
        
        return jsonify({"success": True, "sword_id": sword_id, "price": final_price})
        
    except Exception as e:
        connection.rollback()
        return jsonify({"success": False, "error": str(e)})
    finally:
        connection.close()



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
    user_id = 1
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT gold, guild_reputation FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    cursor.execute("SELECT * FROM swords WHERE creator_id = ? AND status = 'В наличии'", (user_id,))
    swords = cursor.fetchall()

    connection.close()
    return render_template("guild.html", user=user, swords=swords)

@app.route("/guild_submit", methods=["POST"])
def guild_submit():
    data = request.get_json()
    sword_id = data.get("sword_id")
    user_id = 1
    
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute("SELECT final_price FROM swords WHERE id = ? AND creator_id = ? AND status = 'В наличии'", (sword_id, user_id))
        sword = cursor.fetchone()
        if not sword:
            return jsonify({"success": False, "error": "Меч не найден"})
            
        final_price = sword["final_price"]
        gold_reward = int(final_price * 0.8)
        rep_reward = int(final_price * 0.1)
        
        cursor.execute("UPDATE users SET gold = gold + ?, guild_reputation = guild_reputation + ? WHERE id = ?", (gold_reward, rep_reward, user_id))
        cursor.execute("DELETE FROM swords WHERE id = ?", (sword_id,))
        
        cursor.execute("SELECT guild_reputation FROM users WHERE id = ?", (user_id,))
        new_rep = cursor.fetchone()["guild_reputation"]
        
        connection.commit()
        return jsonify({"success": True, "reputation": new_rep})
    except Exception as e:
        connection.rollback()
        return jsonify({"success": False, "error": str(e)})
    finally:
        connection.close()

@app.route("/guild_expedition", methods=["POST"])
def guild_expedition():
    data = request.get_json()
    tier = data.get("tier", 1)
    user_id = 1
    
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute("SELECT gold, guild_reputation FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
        expedition_settings = {
            1: {"req_rep": 10, "cost": 100, "chances": {"Обычный": 100}},
            2: {"req_rep": 30, "cost": 300, "chances": {"Обычный": 70, "Редкий": 30}},
            3: {"req_rep": 50, "cost": 600, "chances": {"Обычный": 40, "Редкий": 50, "Эпический": 10}},
            4: {"req_rep": 80, "cost": 1200, "chances": {"Обычный": 20, "Редкий": 40, "Эпический": 35, "Легендарный": 5}},
            5: {"req_rep": 100, "cost": 2500, "chances": {"Обычный": 5, "Редкий": 30, "Эпический": 50, "Легендарный": 15}}
        }
        
        if tier not in expedition_settings:
            return jsonify({"success": False, "error": "Неверный уровень экспедиции"})
            
        settings = expedition_settings[tier]
        
        if user["guild_reputation"] < settings["req_rep"]:
            return jsonify({"success": False, "error": f"Требуется {settings['req_rep']} репутации"})
            
        if user["gold"] < settings["cost"]:
            return jsonify({"success": False, "error": "Недостаточно золота"})
            
        cursor.execute("UPDATE users SET gold = gold - ? WHERE id = ?", (settings["cost"], user_id))
        
        import random
        roll = random.uniform(0, 100)
        current = 0
        chosen_rarity = "Обычный"
        for rarity, chance in settings["chances"].items():
            current += chance
            if roll <= current:
                chosen_rarity = rarity
                break
                
        cursor.execute("SELECT name, category FROM materials WHERE rarity = ?", (chosen_rarity,))
        possible_materials = cursor.fetchall()
        if not possible_materials:
            return jsonify({"success": False, "error": "Ошибка базы данных: нет материалов"})
            
        found_material = random.choice(possible_materials)
        mat_name = found_material["name"]
        mat_cat = found_material["category"]
        
        cursor.execute("SELECT quantity FROM inventory WHERE user_id = ? AND material_name = ? AND material_category = ?", (user_id, mat_name, mat_cat))
        inv_item = cursor.fetchone()
        if inv_item:
            cursor.execute("UPDATE inventory SET quantity = quantity + 1 WHERE user_id = ? AND material_name = ? AND material_category = ?", (user_id, mat_name, mat_cat))
        else:
            cursor.execute("INSERT INTO inventory (user_id, material_name, material_category, quantity) VALUES (?, ?, ?, 1)", (user_id, mat_name, mat_cat))
            
        connection.commit()
        return jsonify({"success": True, "material_name": mat_name, "rarity": chosen_rarity, "new_gold": user["gold"] - settings["cost"]})
    except Exception as e:
        connection.rollback()
        return jsonify({"success": False, "error": str(e)})
    finally:
        connection.close()

@app.route("/auction", methods=["GET"])
def auction():
    user_id = 1
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT gold FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    
    cursor.execute("SELECT * FROM swords WHERE creator_id = ? AND status = 'В наличии'", (user_id,))
    swords = cursor.fetchall()

    connection.close()
    return render_template("auction.html", user=user, swords=swords)


@app.route("/upgrades", methods=["GET", "POST"])
def upgrades():
    user_id = 1
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT forge_level, gold FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    connection.close()
    return render_template("upgrades.html", user=user)

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
        JOIN materials m ON i.material_name = m.name AND i.material_category = m.category
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



@app.route("/shop_buy", methods=["POST"])
def shop_buy():
    data = request.get_json()
    material_name = data.get("material_name")
    category = data.get("material_category")
    quantity = data.get("quantity", 1)

    user_id = 1
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT price, required_forge_level FROM shop_items WHERE material_name = ? AND material_category = ?", (material_name, category))
        item = cursor.fetchone()
        if not item:
            return jsonify({"success": False, "error": "Товар не найден."})
        price = item["price"] * quantity
        required_level = item["required_forge_level"]


        cursor.execute("SELECT gold, forge_level FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        if user["forge_level"] < required_level:
            return jsonify({"success": False, "error": f"Требуется {required_level} уровень кузницы."})
        if user["gold"] < price:
            return jsonify({"success": False, "error": "Недостаточно золота."})
        cursor.execute("UPDATE users SET gold = gold - ? WHERE id = ?", (price, user_id))

        cursor.execute("SELECT id FROM inventory WHERE user_id = ? AND material_name = ? AND material_category = ?", (user_id, material_name, category))
        inv_item = cursor.fetchone()
        if inv_item:
            cursor.execute("UPDATE inventory SET quantity = quantity + ? WHERE id = ?", (quantity, inv_item["id"]))
        else:
            cursor.execute("INSERT INTO inventory (user_id, material_name, material_category, quantity) VALUES (?, ?, ?, ?)", (user_id, material_name, category, quantity))

        connection.commit()
        return jsonify({"success": True, "gold_left": user["gold"] - price})
    except Exception as e:
        connection.rollback()
        return jsonify({"success": False, "error": str(e)})
    finally:
        connection.close()

@app.route("/auction_sell", methods=["POST"])
def auction_sell():

    data = request.get_json()
    sword_id = data.get("sword_id")
    
    user_id = 1
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT final_price FROM swords WHERE id = ? AND creator_id = ? AND status = 'В наличии'", (sword_id, user_id))
        sword = cursor.fetchone()
        if not sword:
            return jsonify({"success": False, "error": "Меч не найден."})
        
        # Случайная цена от 0.7 до 1.3
        multiplier = random.uniform(0.7, 1.3)
        sold_price = int(sword["final_price"] * multiplier)
        
        # Обновляем золото
        cursor.execute("UPDATE users SET gold = gold + ? WHERE id = ?", (sold_price, user_id))
        
        # Удаляем проданный меч
        cursor.execute("DELETE FROM swords WHERE id = ?", (sword_id,))
        
        cursor.execute("SELECT gold FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
        connection.commit()
        return jsonify({"success": True, "sold_price": sold_price, "new_gold": user["gold"]})
    except Exception as e:
        connection.rollback()
        return jsonify({"success": False, "error": str(e)})
    finally:
        connection.close()

if __name__ == '__main__':
    # проверка работы, я это потом удалю 👍
    create_tables()
    create_materials_table()
    fill_shop()
    
    conn = get_connection()
    conn.cursor().execute("INSERT OR IGNORE INTO users (id, gold) VALUES (1, 1000)")

    conn.commit()
    conn.close()
    
    app.run(host="0.0.0.0", port=5000)