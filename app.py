from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import os
import sqlite3
import random
import PIL
from PIL import Image

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
        gold INTEGER DEFAULT 2000,
        forge_level INTEGER DEFAULT 1,
        guild_reputation INTEGER DEFAULT 0,
        auction_access BOOLEAN DEFAULT 0,
        username TEXT UNIQUE,
        password TEXT
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
    CREATE TABLE materials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        rarity TEXT NOT NULL,     
        image_url TEXT NOT NULL,
        base_price INTEGER NOT NULL DEFAULT 50,
        required_forge_level INTEGER NOT NULL DEFAULT 1
    )
    """)
    connection.cursor().execute("INSERT OR IGNORE INTO users (id, gold) VALUES (1, 10000)")

    all_materials = [
        # лезвия
        ('Бронза', 'Лезвие', 'Обычный', 'images/materials/blade_bronze.png', 50, 1),
        ('Железо', 'Лезвие', 'Обычный', 'images/materials/blade_iron.png', 100, 1),
        ('Углеродистая сталь', 'Лезвие', 'Обычный', 'images/materials/blade_carbon_steel.png', 200, 1),
        ('Дамасская сталь', 'Лезвие', 'Обычный', 'images/materials/blade_damascus.png', 250, 2),
        ('Обсидиан', 'Лезвие', 'Обычный', 'images/materials/blade_obsidian.png', 300, 2),
        ('Порошковая сталь', 'Лезвие', 'Обычный', 'images/materials/blade_powder_steel.png', 350, 3),
        ('Мифрил', 'Лезвие', 'Обычный', 'images/materials/blade_mithril.png', 400, 3),
        ('Метеоритное железо', 'Лезвие', 'Обычный', 'images/materials/blade_meteorite.png', 450, 3),
        
        # лезвия крутые
        ('Титановый сплав', 'Лезвие', 'Редкий', 'images/materials/blade_titanium.png', 600, 3),
        ('Пещерное железо', 'Лезвие', 'Редкий', 'images/materials/blade_cave_iron.png', 700, 3),
        ('Звёздная ртуть', 'Лезвие', 'Эпический', 'images/materials/blade_star_mercury.png', 1500, 4),
        ('Теневой обсидиан', 'Лезвие', 'Эпический', 'images/materials/blade_shadow_obsidian.png', 1800, 4),
        ('Пустотная сталь', 'Лезвие', 'Легендарный', 'images/materials/blade_void_steel.png', 5000, 5),
        ('Осколок Солнечного Горна', 'Лезвие', 'Легендарный', 'images/materials/blade_sun_forge.png', 6500, 5),
        ('Мокумэ-Ганэ', 'Лезвие', 'Легендарный', 'images/materials/blade_mokume_gane.png', 8000, 5),
        
        # гарды
        ('Бронза', 'Гарда', 'Обычный', 'images/materials/guard_bronze.png', 30, 1),
        ('Латунь', 'Гарда', 'Обычный', 'images/materials/guard_brass.png', 60, 2),
        ('Углеродистая сталь', 'Гарда', 'Обычный', 'images/materials/guard_carbon_steel.png', 120, 3),
        
        # гарды крутые
        ('Оружейная бронза', 'Гарда', 'Редкий', 'images/materials/guard_weapon_bronze.png', 300, 3),
        ('Кость Титана', 'Гарда', 'Эпический', 'images/materials/guard_titan_bone.png', 1000, 4),
        ('Хроно-Лёд', 'Гарда', 'Легендарный', 'images/materials/guard_chrono_ice.png', 4000, 5),
        
        # рукоятки
        ('Дуб', 'Рукоять', 'Обычный', 'images/materials/handle_oak.png', 20, 1),
        ('Орех', 'Рукоять', 'Обычный', 'images/materials/handle_walnut.png', 40, 1),
        ('Клен', 'Рукоять', 'Обычный', 'images/materials/handle_maple.png', 60, 1),
        ('Слоновая кость', 'Рукоять', 'Обычный', 'images/materials/handle_ivory.png', 100, 2),
        ('Кожа ската', 'Рукоять', 'Обычный', 'images/materials/handle_stingray.png', 150, 2),
        
        # крутые рукоятки
        ('Красное дерево', 'Рукоять', 'Редкий', 'images/materials/handle_mahogany.png', 400, 3),
        ('Рог оленя', 'Рукоять', 'Редкий', 'images/materials/handle_deer_horn.png', 500, 3),
        ('Черное дерево', 'Рукоять', 'Эпический', 'images/materials/handle_ebony.png', 1200, 4),
        ('Кожа Драконида', 'Рукоять', 'Эпический', 'images/materials/handle_dragonkin.png', 1600, 4),
        ('Шелк Иллюзий', 'Рукоять', 'Легендарный', 'images/materials/handle_illusion_silk.png', 3500, 5),
        ('Бивень Мамонта', 'Рукоять', 'Легендарный', 'images/materials/handle_mammoth.png', 4500, 5),
    ]

    for item in all_materials:
        cursor.execute("INSERT INTO materials (name, category, rarity, image_url, base_price, required_forge_level) VALUES (?, ?, ?, ?, ?, ?)", item)

    connection.commit()
    connection.close()

def fill_shop():
    shop_items = [
        # Лезвия
        ('Бронза', 'Лезвие', 50, 1),
        ('Железо', 'Лезвие', 100, 1),
        ('Углеродистая сталь', 'Лезвие', 200, 2),
        ('Дамасская сталь', 'Лезвие', 250, 3),
        ('Обсидиан', 'Лезвие', 300, 2),
        ('Порошковая сталь', 'Лезвие', 350, 3),
        ('Мифрил', 'Лезвие', 400, 3),
        ('Метеоритное железо', 'Лезвие', 450, 3),
        
        # Гарды
        ('Бронза', 'Гарда', 30, 1),
        ('Латунь', 'Гарда', 60, 2),
        ('Углеродистая сталь', 'Гарда', 120, 3),
        
        # Рукоятки
        ('Дуб', 'Рукоять', 20, 1),
        ('Клен', 'Рукоять', 60, 1),
        ('Орех', 'Рукоять', 40, 2),
        ('Слоновая кость', 'Рукоять', 100, 3),
        ('Кожа ската', 'Рукоять', 150, 3)
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
app.secret_key = "Forge_Secret_Key"

@app.route("/login" , methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        connection.close()
        if user and password == user["password"]:
            session["user_id"] = user["id"]
            return redirect(url_for("forgery"))
        else:
            return render_template("login.html", error="Неверное имя пользователя или пароль")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        existing_user = cursor.fetchone()
        if existing_user:
            connection.close()
            return render_template("register.html", error="Имя пользователя уже занято")
        password_hash = password
        cursor.execute("INSERT INTO users (username, password, gold) VALUES (?, ?, ?)", (username, password_hash, 1000))
        connection.commit()
        user_id = cursor.lastrowid
        connection.close()
        session["user_id"] = user_id
        return redirect(url_for("forgery"))
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("login"))

@app.route("/", methods=["GET", "POST"])
def forgery():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user_id = session["user_id"]
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute("""
        SELECT m.name, m.category, m.rarity, m.image_url, i.quantity, m.base_price, m.required_forge_level
        FROM inventory i 
        JOIN materials m ON i.material_name = m.name AND i.material_category = m.category 
        WHERE i.user_id = ? AND i.quantity > 0
    """, (user_id,))
    inventory = cursor.fetchall()
    cursor.execute("SELECT gold, forge_level FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    connection.close()
    return render_template("forgery.html", inventory=inventory, user=user)

@app.route("/forge_sword", methods=["POST"])
def forge_sword():
    data = request.get_json()
    blade = data.get("blade")
    guard = data.get("guard")
    handle = data.get("handle")
    sword_name = data.get("sword_name", "Новый Меч")
    quality = int(data.get("game_score") or 0)


    if quality > 90 and quality <= 100:
        multiplier = 1.5
    elif quality > 80 and quality <= 90:
        multiplier = 1.3
    elif quality >= 50:
        multiplier = 1.0
    elif quality >= 15:
        multiplier = 0.5
    else:
        return jsonify({"success": False, "error": "Вы провалили мини-игру! Попробуйте снова."})

    if not blade or not guard or not handle:
        return jsonify({"success": False, "error": "Нужны все 3 компонента!"})
        
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Пожалуйста, войдите в систему"})
    user_id = session["user_id"]
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        for material_name, material_category in [(blade, 'Лезвие'), (guard, 'Гарда'), (handle, 'Рукоять')]:
            cursor.execute("SELECT quantity FROM inventory WHERE user_id = ? AND material_name = ? AND material_category = ?", (user_id, material_name, material_category))
            item = cursor.fetchone()
            if not item or item["quantity"] < 1:
                return jsonify({"success": False, "error": f"Не хватает материала: {material_name}"})
                
        cursor.execute("SELECT forge_level FROM users WHERE id = ?", (user_id,))
        forge_level = cursor.fetchone()["forge_level"]

        materials_data = {}
        total_price = 0
        for material_name in [blade, guard, handle]:
            cursor.execute("SELECT image_url, base_price, required_forge_level FROM materials WHERE name = ?", (material_name,))
            mat_info = cursor.fetchone()
            if mat_info:
                if forge_level < mat_info["required_forge_level"]:
                    return jsonify({"success": False, "error": f"Ваш уровень кузницы слишком мал для '{material_name}' (Требуется {mat_info['required_forge_level']} ур.)"})
                materials_data[material_name] = mat_info["image_url"]
                total_price += mat_info["base_price"] * multiplier
            else:
                materials_data[material_name] = "images/materials/blade_iron.png"
                total_price += 50
        
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
        return jsonify({"success": True, "sword_id": sword_id, "price": final_price})
        
    except Exception as e:
        connection.rollback()
        return jsonify({"success": False, "error": str(e)})
    finally:
        connection.close()

@app.route("/shop", methods=["GET", "POST"])
def shop():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user_id = session["user_id"]
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
    if "user_id" not in session:
        return redirect(url_for("login"))
    user_id = session["user_id"]
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
    user_id = session.get("user_id")

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
    user_id = session.get("user_id")
    
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute("SELECT gold, guild_reputation FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
        expedition_settings = {
            1: {"req_rep": 100, "cost": 100, "chances": {"Обычный": 100}},
            2: {"req_rep": 300, "cost": 300, "chances": {"Обычный": 70, "Редкий": 30}},
            3: {"req_rep": 500, "cost": 600, "chances": {"Обычный": 40, "Редкий": 50, "Эпический": 10}},
            4: {"req_rep": 800, "cost": 1200, "chances": {"Обычный": 20, "Редкий": 30, "Эпический": 45, "Легендарный": 5}},
            5: {"req_rep": 1000, "cost": 2500, "chances": {"Обычный": 10, "Редкий": 20, "Эпический": 55, "Легендарный": 15}}
        }
        
        if tier not in expedition_settings:
            return jsonify({"success": False, "error": "Неверный уровень экспедиции"})
            
        settings = expedition_settings[tier]
        
        if user["guild_reputation"] < settings["req_rep"]:
            return jsonify({"success": False, "error": f"Требуется {settings['req_rep']} репутации"})
            
        if user["gold"] < settings["cost"]:
            return jsonify({"success": False, "error": "Недостаточно золота"})
            
        cursor.execute("UPDATE users SET gold = gold - ? WHERE id = ?", (settings["cost"], user_id))
        
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
    if "user_id" not in session:
        return redirect(url_for("login"))
    user_id = session["user_id"]
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
    if "user_id" not in session:
        return redirect(url_for("login"))
    user_id = session["user_id"]
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT forge_level, gold FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    connection.close()
    return render_template("upgrades.html", user=user)

@app.route("/upgrade_buy", methods=["POST"])
def upgrade_buy():
    data = request.get_json()
    try:
        new_level = int(data.get("new_forge_level", 0))
        cost = int(data.get("cost", 0))
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "Неверные данные от клиента!"})
    
    if "user_id" not in session:
        return redirect(url_for("login"))
    user_id = session["user_id"]
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT forge_level, gold FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
        if new_level <= user["forge_level"]:
            return jsonify({"success": False, "error": "Уровень кузницы уже выше или равен этому уровню."})
        if new_level > user["forge_level"] + 1:
            return jsonify({"success": False, "error": "Нельзя перепрыгивать уровни! Улучшайте по порядку."})
        if user["gold"] < cost:
            return jsonify({"success": False, "error": "Недостаточно золота."})
            
        cursor.execute("UPDATE users SET forge_level = ?, gold = gold - ? WHERE id = ?", (new_level, cost, user_id))
        
        connection.commit()
        return jsonify({"success": True, "new_forge_level": new_level, "new_gold": user["gold"] - cost})
    except Exception as e:
        connection.rollback()
        return jsonify({"success": False, "error": str(e)})
    finally:
        connection.close()

@app.route("/inventory", methods=["GET", "POST"])
def inventory():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user_id = session["user_id"]
    connection = get_connection()
    cursor = connection.cursor()
    inventory_items = []

    cursor.execute("""
        SELECT m.name, m.category, m.rarity, m.image_url, i.quantity, m.required_forge_level
        FROM inventory i
        JOIN materials m ON i.material_name = m.name AND i.material_category = m.category
        WHERE i.user_id = ?
    """, (user_id,))
    items = cursor.fetchall()
    cursor.execute("SELECT gold, forge_level FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    connection.close()

    for item in items:
        inventory_items.append({
            "name": item["name"],
            "category": item["category"],
            "rarity": item["rarity"],
            "image": f"/static/{item['image_url']}", 
            "quantity": item["quantity"],
            "required_forge_level": item["required_forge_level"]
        })

    return render_template("inventory.html", items=inventory_items, user=user)

@app.route("/shop_buy", methods=["POST"])
def shop_buy():
    data = request.get_json()
    material_name = data.get("material_name")
    category = data.get("material_category")
    quantity = data.get("quantity", 1)

    if "user_id" not in session:
        return redirect(url_for("login"))
    user_id = session["user_id"]
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
    
    if "user_id" not in session:
        return redirect(url_for("login"))
    user_id = session["user_id"]
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT final_price FROM swords WHERE id = ? AND creator_id = ? AND status = 'В наличии'", (sword_id, user_id))
        sword = cursor.fetchone()
        if not sword:
            return jsonify({"success": False, "error": "Меч не найден."})

        multiplier = random.uniform(0.5, 2.2)
        sold_price = int(sword["final_price"] * multiplier)

        cursor.execute("UPDATE users SET gold = gold + ? WHERE id = ?", (sold_price, user_id))

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
    create_tables()
    create_materials_table()
    fill_shop()
    
    conn = get_connection()
    conn.cursor().execute("INSERT OR IGNORE INTO users (id, gold) VALUES (1, 10000)")

    conn.commit()
    conn.close()
    
    app.run(host="0.0.0.0", port=5005)