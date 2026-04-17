from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
from datetime import datetime
from twilio.rest import Client

app = Flask(__name__)
app.secret_key = "secret123"

DATABASE = "db.db"

# ---------- TWILIO SETUP ----------
TWILIO_SID = "your_sid"
TWILIO_AUTH = "your_auth_token"
TWILIO_PHONE = "+1234567890"

client = Client(TWILIO_SID, TWILIO_AUTH)

# ---------- DATABASE INIT ----------
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # USERS TABLE
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # SOS LOGS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sos_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gate_number TEXT,
            location TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

init_db()

# ---------- HOME ----------
@app.route("/")
def home():
    return render_template("index.html", active="home")

@app.route('/features')
def features():
    return render_template("features.html", active="features")

@app.route('/tips')
def tips():
    return render_template("safety.html", active="tips")

@app.route('/contact')
def contact():
    return render_template("contact.html", active="contact")

# ---------- ADMIN DASHBOARD ----------
@app.route('/admin')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('login'))

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # USERS
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    # SOS LOGS
    cursor.execute("SELECT * FROM sos_logs ORDER BY created_at DESC")
    sos_logs = cursor.fetchall()

    # 📊 CHART DATA (SOS PER DAY)
    cursor.execute("""
        SELECT DATE(created_at), COUNT(*) 
        FROM sos_logs 
        GROUP BY DATE(created_at)
    """)
    data = cursor.fetchall()

    dates = [row[0] for row in data]
    counts = [row[1] for row in data]

    # 📍 MAP DATA
    sos_data = []
    for row in sos_logs:
        if "maps?q=" in row[2]:
            coords = row[2].split("q=")[1]
            lat, lon = coords.split(",")
            sos_data.append({"lat": float(lat), "lon": float(lon)})

    conn.close()

    return render_template(
        "admin.html",
        users=users,
        sos_logs=sos_logs,
        dates=dates,
        counts=counts,
        sos_data=sos_data
    )

# ---------- REGISTER ----------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email, password)
            )
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except:
            return "Email already exists ❌"

    return render_template('register.html')

# ---------- LOGIN ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # ADMIN LOGIN
        if email == "admin@gmail.com" and password == "admin123":
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))

        # USER LOGIN
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user'] = user[1]
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid Email or Password ❌")

    return render_template('login.html')

# ---------- DASHBOARD ----------
@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template('dashboard.html', name=session['user'])
    return redirect(url_for('login'))

# ---------- DELETE USER ----------
@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    if not session.get('admin'):
        return redirect(url_for('login'))

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('admin_dashboard'))

# ---------- DELETE SOS ----------
@app.route('/delete_sos/<int:sos_id>')
def delete_sos(sos_id):
    if not session.get('admin'):
        return redirect(url_for('login'))

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sos_logs WHERE id=?", (sos_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('admin_dashboard'))

# ---------- SOS ALERT ----------
@app.route('/send_sos', methods=['POST'])
def send_sos():
    gate = request.form['gate_number']
    lat = request.form.get('latitude')
    lon = request.form.get('longitude')

    location_link = f"https://www.google.com/maps?q={lat},{lon}"

    # SAVE
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO sos_logs (gate_number, location) VALUES (?, ?)",
        (gate, location_link)
    )
    conn.commit()
    conn.close()

    # SEND SMS
    try:
        client.messages.create(
            body=f"🚨 SOS ALERT\nGate: {gate}\nLocation: {location_link}",
            from_=TWILIO_PHONE,
            to="+91XXXXXXXXXX"
        )
    except:
        print("SMS Failed")

    return redirect(url_for('dashboard'))

# ---------- REAL-TIME COUNT API ----------
@app.route('/get_sos_count')
def get_sos_count():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM sos_logs")
    count = cursor.fetchone()[0]
    conn.close()

    return jsonify({"count": count})

# ---------- LOGOUT ----------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)