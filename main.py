import gradio as gr
import json
import random
import os
import base64
import hashlib
import string
import time
import requests

# Имя БД изменено для локального запуска (создается в папке со скриптом)
db_file = 'cyber_users_v6.json'

if not os.path.exists(db_file):
    with open(db_file, 'w') as f:
        json.dump({}, f)

# === 🛡️ ЛОГИКА 1: РЕГИСТРАЦИЯ И УПРАВЛЕНИЕ СЕССИЯМИ ===
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    if not username or not password:
        return "❌ Ошибка: Введите данные."
    with open(db_file, 'r') as f:
        data = json.load(f)
    if username in data:
        return f"⚠️ Пользователь {username} уже есть!"

    data[username] = {
        "hash": hash_password(password),
        "status": "🔴 OFFLINE"
    }
    with open(db_file, 'w') as f:
        json.dump(data, f)
    return f"✅ {username} зарегистрирован! Теперь войдите в систему."

def login_user(username, password):
    if not username or not password:
        return "❌ Введите логин и пароль.", None, gr.update(visible=False), gr.update(visible=True)
    
    with open(db_file, 'r') as f:
        data = json.load(f)
        
    if username in data and data[username]["hash"] == hash_password(password):
        data[username]["status"] = "🟢 ONLINE"
        with open(db_file, 'w') as f:
            json.dump(data, f)
            
        return f"✅ Доступ разрешен. Добро пожаловать, {username}.", username, gr.update(visible=True), gr.update(visible=False)
    else:
        return "⛔ Неверный логин или пароль.", None, gr.update(visible=False), gr.update(visible=True)

def logout_user(username):
    if username:
        try:
            with open(db_file, 'r') as f:
                data = json.load(f)
            if username in data:
                data[username]["status"] = "🔴 OFFLINE"
                with open(db_file, 'w') as f:
                    json.dump(data, f)
        except Exception:
            pass 
            
    return "Ожидание входа...", None, gr.update(visible=False), gr.update(visible=True)

def view_database(admin_password):
    if admin_password == "admin777":
        with open(db_file, 'r') as f:
            data = json.load(f)
        table_data = [[user, info["hash"], info.get("status", "🔴 OFFLINE")] for user, info in data.items()]
        return "✅ Доступ открыт. Мониторинг активен.", table_data
    return "⛔ ДОСТУП ЗАПРЕЩЕН.", []

# === 🌐 ЛОГИКА 2: ИНСТРУМЕНТЫ И УТЕЧКИ ===
def check_password_leak(password):
    if not password: return "Введите пароль."
    sha1_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    prefix, suffix = sha1_hash[:5], sha1_hash[5:]
    try:
        response = requests.get(f"https://api.pwnedpasswords.com/range/{prefix}")
        if response.status_code != 200: return "❌ Ошибка API."
        for h, count in (line.split(':') for line in response.text.splitlines()):
            if h == suffix: return f"⚠️ ВНИМАНИЕ! Пароль слит {count} раз! Срочно смените его."
        return "✅ Отлично! Пароль не найден в известных базах утечек."
    except Exception as e:
        return f"❌ Ошибка соединения: {str(e)}"

def fake_nmap(ip_address):
    time.sleep(1.5) 
    if not ip_address: return "Введите IP!"
    ports = [21, 22, 23, 80, 443, 3306, 8080]
    open_ports = random.sample(ports, k=random.randint(1, 4))
    result = f"[*] Инициализация сканирования цели: {ip_address}...\n"
    result += f"[*] Отправка SYN пакетов...\n" + "-"*35 + "\n"
    for port in sorted(open_ports):
        service = {21:"FTP", 22:"SSH", 23:"TELNET", 80:"HTTP", 443:"HTTPS", 3306:"MYSQL", 8080:"HTTP-ALT"}.get(port, "UNKNOWN")
        result += f"[+] Порт {port}/tcp \t ОТКРЫТ \t ({service})\n"
    return result

def generate_strong_password(length, use_chars):
    chars = string.ascii_letters + string.digits
    if use_chars: chars += "!@#$%^&*()_+"
    return "".join(random.choice(chars) for _ in range(int(length)))

# === 🔐 ЛОГИКА 3: КРИПТОГРАФИЯ И КОДИРОВАНИЕ ===
def process_base64(text, mode):
    if not text: return "Введите текст!"
    try:
        if mode == "Кодировать (Encode)":
            return base64.b64encode(text.encode('utf-8')).decode('utf-8')
        else:
            return base64.b64decode(text.encode('utf-8')).decode('utf-8')
    except Exception:
        return "❌ Ошибка: Неверный формат Base64."

def process_caesar(text, shift, mode):
    if not text: return "Введите текст!"
    result = ""
    shift = int(shift) if mode == "Зашифровать" else -int(shift)
    for char in text:
        if char.isalpha():
            ascii_offset = 65 if char.isupper() else 97
            result += chr((ord(char) - ascii_offset + shift) % 26 + ascii_offset)
        else:
            result += char
    return result

# === 🕹️ ЛОГИКА 4: МИНИ-ИГРЫ ===
def generate_pin(): return "".join([str(random.randint(0, 9)) for _ in range(4)])
def play_pin_brute(guess, secret_code, attempts):
    if not guess or len(guess) != 4 or not guess.isdigit(): return "⚠️ Введите 4 цифры!", secret_code, attempts
    attempts += 1
    bulls = sum(1 for i in range(4) if guess[i] == secret_code[i])
    if bulls == 4: return f"🔓 ПИН ВЗЛОМАН за {attempts} попыток!", generate_pin(), 0
    return f"❌ Совпало цифр: {bulls} (Попытка {attempts})", secret_code, attempts

words_db = ["admin", "hacker", "cyber", "python", "linux", "root"]
def get_new_md5():
    word = random.choice(words_db)
    return word, hashlib.md5(word.encode()).hexdigest()

def play_hash_cracker(guess, actual_word, target_hash):
    guess_hash = hashlib.md5(guess.encode()).hexdigest()
    if guess_hash == target_hash:
        new_word, new_hash = get_new_md5()
        return f"🎯 УСПЕХ! Исходное слово: {actual_word}", new_word, new_hash
    return f"❌ Неверно. Ваш хэш: {guess_hash}", actual_word, target_hash


# === 🎨 ВИЗУАЛЬНЫЙ ИНТЕРФЕЙС (ТЕМНЫЙ RED TEAM СТИЛЬ) ===
red_cyber_theme = gr.themes.Soft(
    primary_hue="red",
    secondary_hue="rose",
    neutral_hue="slate",
    font=[gr.themes.GoogleFont("Fira Code"), "monospace"],
).set(
    body_background_fill="*neutral_950",
    body_text_color="*neutral_100",
    background_fill_primary="*neutral_900",
    background_fill_secondary="*neutral_800",
    border_color_primary="*primary_700",
    color_accent_soft="*primary_800",
    block_title_text_color="*primary_500",
)

with gr.Blocks(theme=red_cyber_theme) as demo:
    current_user = gr.State(None)
    
    gr.Markdown("# 🩸 RED TEAM TERMINAL // CYBERSEC_V5")
    auth_status = gr.Markdown("> 👤 СТАТУС СЕССИИ: НЕ АВТОРИЗОВАН", elem_classes="text-center")

    with gr.Tab("📝 Auth_Sys"):
        with gr.Row():
            with gr.Column(variant="panel"):
                gr.Markdown("### 🔐 Secure Login")
                login_user_in = gr.Textbox(label="USER_ID")
                login_pass_in = gr.Textbox(label="PASSWORD", type="password")
                login_btn = gr.Button("INITIALIZE SESSION", variant="primary")
                logout_btn = gr.Button("TERMINATE SESSION")
                login_out = gr.Textbox(label="SYSTEM LOG")

            with gr.Column():
                gr.Markdown("### 🆕 New Identity")
                reg_user_in = gr.Textbox(label="NEW USER_ID")
                reg_pass_in = gr.Textbox(label="NEW PASSWORD", type="password")
                reg_btn = gr.Button("REGISTER")
                reg_out = gr.Textbox(label="REGISTRATION LOG")
                reg_btn.click(register_user, [reg_user_in, reg_pass_in], reg_out)

        with gr.Row():
            with gr.Column():
                gr.Markdown("### 🗄️ Master Database (Root Only)")
                admin_pass = gr.Textbox(label="ROOT PASSWORD (admin777)", type="password")
                db_btn = gr.Button("DUMP HASHES", variant="primary")
                db_table = gr.Dataframe(headers=["USER", "SHA-256 HASH", "STATUS"])
                db_btn.click(view_database, inputs=admin_pass, outputs=[gr.Textbox(visible=False), db_table])

    # Заглушка для неавторизованных
    lock_msg = gr.Markdown("## ⚠️ [ACCESS DENIED] АВТОРИЗУЙТЕСЬ ДЛЯ ДОСТУПА К ИНСТРУМЕНТАМ.")

    # Скрытый контент
    with gr.Column(visible=False) as main_content:
        
        with gr.Tab("🛠️ Cyber_Tools"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### 📡 Сканер портов (Nmap Sim)")
                    ip_in = gr.Textbox(label="Target IP (e.g. 192.168.0.1)")
                    scan_btn = gr.Button("RUN NMAP", variant="primary")
                    scan_out = gr.Textbox(label="CONSOLE OUTPUT", lines=6)
                    scan_btn.click(fake_nmap, ip_in, scan_out)

                with gr.Column():
                    gr.Markdown("### 🕵️ OSINT: Утечки паролей")
                    leak_pass_in = gr.Textbox(label="Пароль для проверки (k-Anonymity)", type="password")
                    leak_btn = gr.Button("QUERY HAVEIBEENPWNED")
                    leak_out = gr.Textbox(label="REPORT")
                    leak_btn.click(check_password_leak, leak_pass_in, leak_out)

        with gr.Tab("🔏 Cryptography"):
            with gr.Row():
                with gr.Column(variant="panel"):
                    gr.Markdown("### 📜 Шифр Цезаря (Сдвиг)")
                    caesar_text = gr.Textbox(label="Текст", lines=2)
                    caesar_shift = gr.Slider(minimum=1, maximum=25, value=3, step=1, label="Сдвиг (Shift)")
                    caesar_mode = gr.Radio(["Зашифровать", "Расшифровать"], value="Зашифровать", label="Режим")
                    caesar_btn = gr.Button("EXECUTE")
                    caesar_out = gr.Textbox(label="Результат", lines=2)
                    caesar_btn.click(process_caesar, [caesar_text, caesar_shift, caesar_mode], caesar_out)

                with gr.Column(variant="panel"):
                    gr.Markdown("### 📦 Base64 Encoder")
                    b64_text = gr.Textbox(label="Данные", lines=2)
                    b64_mode = gr.Radio(["Кодировать (Encode)", "Декодировать (Decode)"], value="Кодировать (Encode)", label="Действие")
                    b64_btn = gr.Button("PROCESS BASE64")
                    b64_out = gr.Textbox(label="Вывод Base64", lines=2)
                    b64_btn.click(process_base64, [b64_text, b64_mode], b64_out)

        with gr.Tab("🕹️ Hacking_Simulators"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### 🎯 Брутфорс ПИН-кода")
                    secret_pin = gr.State(generate_pin())
                    attempts = gr.State(0)
                    pin_in = gr.Textbox(label="Введите 4 цифры")
                    pin_btn = gr.Button("BRUTEFORCE")
                    pin_out = gr.Textbox(label="Лог")
                    pin_btn.click(play_pin_brute, [pin_in, secret_pin, attempts], [pin_out, secret_pin, attempts])

                with gr.Column():
                    gr.Markdown("### 💥 MD5 Hash Cracker")
                    init_word, init_hash = get_new_md5()
                    actual_word = gr.State(init_word)
                    target_hash = gr.State(init_hash)
                    hash_display = gr.Textbox(label="Target MD5", value=init_hash, interactive=False)
                    word_guess = gr.Textbox(label="Dictionary Guess")
                    hash_btn = gr.Button("CHECK COLLISION")
                    hash_out = gr.Textbox(label="STATUS")
                    hash_btn.click(play_hash_cracker, [word_guess, actual_word, target_hash], [hash_out, actual_word, target_hash]).then(
                        lambda h: h, target_hash, hash_display
                    )

    # Логика входа
    login_btn.click(
        login_user, 
        inputs=[login_user_in, login_pass_in], 
        outputs=[login_out, current_user, main_content, lock_msg]
    ).then(
        lambda user: f"> 👤 СТАТУС СЕССИИ: ACTIVE (USER: {user})" if user else "> 👤 СТАТУС СЕССИИ: НЕ АВТОРИЗОВАН", 
        inputs=current_user, 
        outputs=auth_status
    )
    
    # Логика выхода
    logout_btn.click(
        logout_user,
        inputs=current_user,
        outputs=[login_out, current_user, main_content, lock_msg]
    ).then(
        lambda: "> 👤 СТАТУС СЕССИИ: НЕ АВТОРИЗОВАН", 
        inputs=None, 
        outputs=auth_status
    )

# Запуск приложения локально (откроется в браузере)
demo.launch()
