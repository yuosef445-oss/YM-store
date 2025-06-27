# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from flask_cors import CORS
import requests # لاستخدام مكتبة requests لإجراء طلبات HTTP
import json # لمعالجة بيانات JSON

# تهيئة تطبيق Flask
app = Flask(__name__)
CORS(app)

# تحديد مسار قاعدة البيانات
DATABASE = 'database.db'

# بيانات المنتجات (لا تزال موجودة ولكن لن يستخدمها الشات بوت مباشرة الآن)
PRODUCTS_DATA = {
    "هواتف": [
        {"name": "Honor Magic5", "price": 700, "category": "هواتف"},
        {"name": "Samsung Galaxy S23 Ultra", "price": 1199, "category": "هواتف"},
        {"name": "iPhone 15 Pro Max", "price": 990, "category": "هواتف"}
    ],
    "حواسيب": [
        {"name": "لابتوب ديل إنسبايرون 14-7490", "price": 990, "category": "حواسيب"},
        {"name": "لابتوب ASUS ROG Zephyrus G15", "price": 1499, "category": "حواسيب"},
        {"name": "لابتوب HP 250 G8 Dark", "price": 1199, "category": "حواسيب"},
        {"name": "ماك بوك من آبل", "price": 1299, "category": "حواسيب"}
    ],
    "كروت شاشة": [
        {"name": "بطاقة الرسومات ASUS TUF Gaming GeForce RTX 4090", "price": 1599, "category": "كروت شاشة"},
        {"name": "بطاقة الرسومات NVIDIA Founders Edition RTX 4090", "price": 1699, "category": "كروت شاشة"}
    ],
    "لوحة المفاتيح": [
        {"name": "لوحة مفاتيح لوجيتك", "price": 49, "category": "لوحة المفاتيح"},
        {"name": "لوحة مفاتيح رايدر هايبرسبيد اللاسلكية", "price": 129, "category": "لوحة المفاتيح"},
        {"name": "لوحة مفاتيح هافيت ماجيك إيغل للألعاب", "price": 89, "category": "لوحة المفاتيح"}
    ],
    "فأرة": [
        {"name": "فأرة لوجيتك G502 للألعاب", "price": 79, "category": "فأرة"},
        {"name": "فأرة SteelSeries Rival 650 Black للألعاب", "price": 69, "category": "فأرة"},
        {"name": "فأرة MASTER اللاسلكية للألعاب", "price": 59, "category": "فأرة"}
    ],
    "سماعات": [
        {"name": "سماعات ستيل سيريس GX2017 المهنية للألعاب", "price": 159, "category": "سماعات"},
        {"name": "سماعات مارشال مايجور IV اللاسلكية", "price": 99, "category": "سماعات"},
        {"name": "سماعات AirDots Pro اللاسلكية", "price": 89, "category": "سماعات"}
    ],
    "ساعات ذكية": [
        {"name": "Apple Watch Series 8", "price": 400, "category": "ساعات ذكية"},
        {"name": "Samsung Galaxy Watch6 Classic", "price": 350, "category": "ساعات ذكية"},
        {"name": "Xiaomi Mi Watch Lite", "price": 60, "category": "ساعات ذكية"},
        {"name": "Huawei Watch Fit", "price": 100, "category": "ساعات ذكية"},
        {"name": "Amazfit GTS 4", "price": 130, "category": "ساعات ذكية"},
        {"name": "Fitbit Sense", "price": 250, "category": "ساعات ذكية"},
        {"name": "Garmin Venu Sq", "price": 300, "category": "ساعات ذكية"}
    ],
    "بطارية محمولة": [
        {"name": "Xiaomi Power Bank 10,000mAh", "price": 15, "category": "بطارية محمولة"},
        {"name": "Samsung 10,000mAh Fast Charge", "price": 20, "category": "بطارية محمولة"},
        {"name": "RAVPower 26800mAh", "price": 35, "category": "بطارية محمولة"},
        {"name": "Mophie Powerstation XXL", "price": 40, "category": "بطارية محمولة"},
        {"name": "Aukey Power Bank 20,000mAh", "price": 25, "category": "بطارية محمولة"}
    ],
    "فلاش ميموري": [
        {"name": "مفتاح USB 3.0 من وانسندا", "price": 29, "category": "فلاش ميموري"},
        {"name": "مفتاح USB من كوهيسيف", "price": 19, "category": "فلاش ميموري"},
        {"name": "مفتاح USB من كينغستون", "price": 25, "category": "فلاش ميموري"}
    ],
    "سبيكر": [
        {"name": "مكبر صوت JBL المحمول", "price": 69, "category": "سبيكر"},
        {"name": "مكبر صوت JBL Boombox 2", "price": 299, "category": "سبيكر"},
        {"name": "مكبر صوت boAt Signature Sound", "price": 149, "category": "سبيكر"}
    ],
    "قلم لمس": [
        {"name": "قلم UGREEN Pencil", "price": 39, "category": "قلم لمس"},
        {"name": "قلم آبل Pencil Midnight Green Edition", "price": 129, "category": "قلم لمس"}
    ],
    "Xbox": [
        {"name": "Xbox Series X", "price": 499, "category": "Xbox"},
        {"name": "Xbox Series S", "price": 299, "category": "Xbox"},
        {"name": "Xbox Wireless Controller", "price": 59, "category": "Xbox"},
        {"name": "Xbox Elite Controller Series 2", "price": 179, "category": "Xbox"},
        {"name": "Xbox Adaptive Controller", "price": 99, "category": "Xbox"},
        {"name": "Halo Infinite Edition Controller", "price": 69, "category": "Xbox"},
        {"name": "Starfield", "price": 59, "category": "Xbox"},
        {"name": "Halo Infinite", "price": 59, "category": "Xbox"},
        {"name": "Forza Horizon 5", "price": 59, "category": "Xbox"}
    ],
    "PlayStation": [
        {"name": "PlayStation 5 Standard Edition", "price": 500, "category": "PlayStation"},
        {"name": "PlayStation 5 Digital Edition", "price": 450, "category": "PlayStation"},
        {"name": "PS4 Pro", "price": 400, "category": "PlayStation"},
        {"name": "DualShock 4 – الأسود", "price": 60, "category": "PlayStation"},
        {"name": "DualSense – الأبيض", "price": 70, "category": "PlayStation"},
        {"name": "DualSense Edge", "price": 200, "category": "PlayStation"},
        {"name": "God of War Ragnarök", "price": 60, "category": "PlayStation"},
        {"name": "Spider-Man: Miles Morales", "price": 40, "category": "PlayStation"},
        {"name": "Demon’s Souls Remake", "price": 50, "category": "PlayStation"}
    ],
    "شاشات": [
        {"name": "Samsung QLED QN90B", "price": 1500, "category": "شاشات"},
        {"name": "Sony Bravia XR A80K OLED TV", "price": 2000, "category": "شاشات"},
        {"name": "LG NanoCell NANO85", "price": 900, "category": "شاشات"},
        {"name": "TCL 6-Series Roku TV", "price": 700, "category": "شاشات"},
        {"name": "Dell UltraSharp U2723QE 4K Monitor", "price": 600, "category": "شاشات"},
        {"name": "LG UltraGear 27GP950-B OLED Monitor", "price": 900, "category": "شاشات"},
        {"name": "Samsung Odyssey G7 Curved Gaming Monitor", "price": 750, "category": "شاشات"}
    ],
    "معالجات": [
        {"name": "Intel Core i5 – الجيل 13", "price": 200, "category": "معالجات"},
        {"name": "Intel Core i7 – الجيل 13", "price": 350, "category": "معالجات"},
        {"name": "Intel Core i9 – الجيل 13", "price": 600, "category": "معالجات"},
        {"name": "Intel Core Ultra 7", "price": 450, "category": "معالجات"},
        {"name": "AMD Ryzen 5 – الجيل 7000", "price": 220, "category": "معالجات"},
        {"name": "AMD Ryzen 7 – الجيل 7000", "price": 380, "category": "معالجات"}
    ]
}


# دالة مساعدة للاتصال بقاعدة البيانات
def get_db_connection():
    """
    ينشئ اتصالاً بقاعدة بيانات SQLite ويعيد كائن الاتصال.
    يضمن أن الصفوف يمكن الوصول إليها ككائنات شبيهة بالقاموس.
    """
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# تهيئة قاعدة البيانات عند بدء التطبيق
def init_db():
    """
    يهيئ قاعدة البيانات بإنشاء جدول المستخدمين إذا لم يكن موجودًا.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()
    print("تم تهيئة قاعدة البيانات بنجاح.")

# إنشاء مخطط للواجهة البرمجية (API Blueprint) لتنظيم المسارات
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@app.route('/')
def home():
    """
    مسار الصفحة الرئيسية.
    """
    return "مرحبًا بكم في متجرنا! يرجى استخدام مسارات API للمصادقة."

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    مسار تسجيل دخول المستخدم.
    يتوقع 'email' و 'password' في بيانات النموذج.
    """
    try:
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            return jsonify({"message": "البريد الإلكتروني وكلمة المرور مطلوبان"}), 400

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            return jsonify({"message": "تم تسجيل الدخول بنجاح!", "user_id": user['id']}), 200
        else:
            return jsonify({"message": "البريد الإلكتروني أو كلمة المرور غير صحيحة"}), 401

    except Exception as e:
        app.logger.error(f"خطأ في تسجيل الدخول: {e}", exc_info=True)
        return jsonify({"message": "حدث خطأ في الخادم", "error": str(e)}), 500

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """
    مسار إنشاء حساب مستخدم جديد.
    يتوقع 'email' و 'password' و 'confirm-password' في بيانات النموذج.
    """
    try:
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm-password')

        if not email or not password or not confirm_password:
            return jsonify({"message": "جميع الحقول مطلوبة"}), 400

        if password != confirm_password:
            return jsonify({"message": "كلمات المرور غير متطابقة"}), 400

        if len(password) < 6:
            return jsonify({"message": "يجب أن تكون كلمة المرور 6 أحرف على الأقل"}), 400

        hashed_password = generate_password_hash(password)

        with get_db_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, hashed_password))
                conn.commit()
                return jsonify({"message": "تم إنشاء الحساب بنجاح!"}), 201
            except sqlite3.IntegrityError:
                return jsonify({"message": "البريد الإلكتروني مستخدم بالفعل"}), 409
            except Exception as db_e:
                app.logger.error(f"خطأ في قاعدة البيانات أثناء التسجيل: {db_e}", exc_info=True)
                return jsonify({"message": "حدث خطأ في قاعدة البيانات أثناء إنشاء الحساب"}), 500

    except Exception as e:
        app.logger.error(f"خطأ في التسجيل: {e}", exc_info=True)
        return jsonify({"message": "حدث خطأ في الخادم", "error": str(e)}), 500

# تسجيل المخطط (Blueprint) مع التطبيق
app.register_blueprint(auth_bp)

# مسار جديد للشات بوت
@app.route('/api/chat', methods=['POST'])
def chat():
    """
    مسار الشات بوت.
    يتوقع 'message' في بيانات JSON.
    يستخدم Gemini API لتوليد الردود.
    """
    try:
        data = request.get_json()
        user_message = data.get('message', '')

        if not user_message:
            return jsonify({"response": "عذرًا، لم أستلم رسالة. كيف يمكنني مساعدتك؟"}), 200

        # بناء البيانات لإرسالها إلى Gemini API
        chat_history = []
        chat_history.append({"role": "user", "parts": [{"text": user_message}]})

        # إضافة سياق للمتجر إلى النموذج
        store_context = (
            "أنت مساعد شات بوت لمتجر إلكتروني يسمى 'متجر YM'. "
            "تبيع منتجات إلكترونية مثل الهواتف، الحواسيب، كروت الشاشة، لوحات المفاتيح، الفأرات، السماعات، الساعات الذكية، "
            "البطاريات المحمولة، فلاش ميموري، السبيكر، أقلام اللمس، أجهزة Xbox و PlayStation، الشاشات، والمعالجات. "
            "أسعار المنتجات تتراوح من 15 دولارًا إلى 2000 دولار. "
            "طرق الدفع تشمل البطاقات الائتمانية (فيزا، ماستركارد)، مدى، Apple Pay، والدفع عند الاستلام. "
            "الشحن يستغرق من 3 إلى 5 أيام عمل. "
            "ساعات العمل من السبت إلى الخميس، 9 صباحًا - 9 مساءً، والجمعة 2 ظهرًا - 10 مساءً. "
            "سياسة الإرجاع والاستبدال خلال 14 يومًا. "
            "كن ودودًا ومفيدًا ومختصرًا قدر الإمكان. إذا لم تكن متأكدًا، اطلب من المستخدم توضيحًا أو اقترح زيارة صفحة المنتجات. "
            "لا تختلق معلومات غير موجودة في السياق المقدم. إذا سئلت عن منتج غير موجود، قل أنك لا تملك معلومات عنه."
        )
        
        full_prompt = f"{store_context}\n\nسؤال المستخدم: {user_message}"
        
        payload = {
            "contents": [{"role": "user", "parts": [{"text": full_prompt}]}],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 200
            }
        }

        api_key = "AIzaSyDSkFLH_y1aIih4mFDVopAsK6rqMBbosLI" 
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

        headers = {
            'Content-Type': 'application/json'
        }

        app.logger.info(f"إرسال طلب إلى Gemini API. الحمولة: {payload}") # تسجيل الحمولة
        
        response_from_gemini = requests.post(api_url, headers=headers, data=json.dumps(payload))
        
        app.logger.info(f"حالة استجابة Gemini: {response_from_gemini.status_code}") # تسجيل حالة الاستجابة
        app.logger.info(f"نص استجابة Gemini: {response_from_gemini.text}") # تسجيل نص الاستجابة الكامل

        response_from_gemini.raise_for_status() # إطلاق استثناء لأخطاء HTTP (4xx أو 5xx)
        
        gemini_result = response_from_gemini.json()
        
        bot_response = "عذرًا، لم أتمكن من الحصول على رد من الشات بوت."
        if gemini_result and "candidates" in gemini_result and len(gemini_result["candidates"]) > 0:
            if "content" in gemini_result["candidates"][0] and "parts" in gemini_result["candidates"][0]["content"]:
                bot_response = gemini_result["candidates"][0]["content"]["parts"][0]["text"]
            else:
                app.logger.warning(f"رد Gemini غير متوقع: {gemini_result}")
                bot_response = "عذرًا، تلقيت ردًا غير متوقع من الذكاء الاصطناعي."
        else:
            app.logger.warning(f"رد Gemini فارغ أو غير صالح: {gemini_result}")
            bot_response = "عذرًا، لم يتمكن الذكاء الاصطناعي من توليد رد."

        return jsonify({"response": bot_response}), 200

    except requests.exceptions.RequestException as req_e:
        # هذا الاستثناء يلتقط أخطاء الاتصال بالشبكة أو أخطاء HTTP من API
        app.logger.error(f"خطأ في الاتصال بـ Gemini API: {req_e}", exc_info=True)
        return jsonify({"error": "حدث خطأ في الاتصال بخدمة الذكاء الاصطناعي. يرجى المحاولة لاحقًا."}), 500
    except Exception as e:
        # هذا الاستثناء يلتقط أي أخطاء أخرى غير متوقعة
        app.logger.error(f"خطأ عام في الشات بوت: {e}", exc_info=True)
        return jsonify({"error": "حدث خطأ داخلي في الخادم أثناء معالجة رسالة الشات بوت."}), 500


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
