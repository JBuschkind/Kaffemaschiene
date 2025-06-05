# app.py
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///interaktionen.db'
db = SQLAlchemy(app)

class Interaktion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    element = db.Column(db.String(50))
    chip_id = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/')
def index():
    return render_template('index.html')

def lese_chip():
    """
    Simuliert das Lesen eines Chips.
    Gibt '1234' zurück als Testwert oder '0' wenn kein Chip erkannt wurde.
    """
    import random
    if random.random() < 0.9:
        return "1234"  # Test-Chip-ID
    else:
        return "0"     # kein Chip erkannt


@app.route('/interaktion', methods=['POST'])
def interaktion():
    data = request.json
    chip_id = lese_chip()

    if chip_id == "0":
        return jsonify({"status": "fehler", "grund": "Kein Chip erkannt"})

    neue_interaktion = Interaktion(
        element=data['element'],
        chip_id=chip_id
    )

    db.session.add(neue_interaktion)
    db.session.commit()
    return jsonify({"status": "ok", "chip_id": chip_id})

@app.route('/statistik')
def statistik_seite():
    return render_template('statistik.html')

@app.route('/api/statistik')
def statistik_api():
    from sqlalchemy.sql import func
    results = db.session.query(
        Interaktion.chip_id,
        Interaktion.element,
        func.count()
    ).group_by(Interaktion.chip_id, Interaktion.element).all()
    return jsonify([
        {"chip_id": r[0], "element": r[1], "anzahl": r[2]} for r in results
    ])


#@app.route('/statistik')
#def statistik():
#    from sqlalchemy.sql import func
#    results = db.session.query(
#        func.strftime('%Y-%m', Interaktion.timestamp).label('monat'),
#        Interaktion.element,
#        func.count()
#    ).group_by('monat', Interaktion.element).all()
#    return jsonify([{"monat": r[0], "element": r[1], "anzahl": r[2]} for r in results])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)

