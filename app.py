from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app)

# تحديد مسار قاعدة البيانات
DATABASE = 'database.db'

# بيانات المنتجات
PRODUCTS_DATA = {
    "هواتف": [
        {"name": "Honor Magic5", "price": 700, "category": "هواتف"},
        # ... باقي المنتجات
    ],
    "ساعات ذكية": [
        {"name": "Apple Watch Series 9", "price": 400, "category": "ساعات ذكية"},
        # ... باقي المنتجات
    ]
}

# دالة للاتصال بقاعدة البيانات
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# تهيئة قاعدة البيانات
def init_db():
    with app.app_context():
        db = get_db_connection()
        db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        db.commit()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('', filename)

@app.route('/api/chat', methods=['POST'])
def chatbot():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip().lower()

        store_context = (
            "أنت مساعد شات بوت لمتجر إلكتروني يسمى 'متجر YM'. "
            "تبيع منتجات إلكترونية مثل الهواتف، الحواسيب، كروت الشاشة، لوحات المفاتيح، الفأرات، السماعات، الساعات الذكية، "
            "البطاريات المحمولة، فلاش ميموري، السبيكر، أقلام اللمس، أجهزة Xbox و PlayStation، الشاشات، والمعالجات. "
            "أسعار المنتجات تتراوح من 15 دولارًا إلى 2000 دولار. "
            "طرق الدفع تشمل البطاقات الائتمانية (فيزا، ماستركارد)، مدى، Apple Pay، والدفع عند الاستلام. "
            "الشحن يستغرق من 3 إلى 5 أيام عمل. "
            "ساعات العمل من السبت إلى الخميس، 9 صباحًا - 9 مساءً، والجمعة 2 ظهرًا - 10 مساءً. "
            "سياسة الإرجاع والاستبدال خلال 14 يومًا. "
            "كن ودودًا ومفيدًا ومختصرًا قدر الإمكان. "
            "إذا لم تكن متأكدًا، اطلب من المستخدم توضيحًا أو اقترح زيارة صفحة المنتجات."
        )

        full_prompt = f"{store_context}\nسؤال المستخدم: {user_message}"

        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        if not GEMINI_API_KEY:
            return jsonify({"error": "API key is missing"}), 500

        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro :generateContent"
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{"parts": [{"text": full_prompt}]}]
        }

        response = requests.post(f"{url}?key={GEMINI_API_KEY}", headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            bot_response = response.json().get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'عذرًا، لا يمكنني المساعدة حاليًا.')
        else:
            bot_response = "عذرًا، حدث خطأ في الاتصال بالشات بوت."

        return jsonify({"response": bot_response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run()