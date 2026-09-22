"""Kabadiwala Connect backend: first working slice (Flask + PostgreSQL).

Run:  python app.py
Test: open http://127.0.0.1:5000/health and http://127.0.0.1:5000/api/v1/categories
"""
import os

from dotenv import load_dotenv
from flask import Flask, jsonify
from sqlalchemy import create_engine, text

# Read settings (like the database password) from the .env file
load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

app = Flask(__name__)
app.json.ensure_ascii = False  # show Marathi and Hindi text normally, not as \u codes


@app.route("/health")
def health():
    """Checks that the web server AND the database are alive."""
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return jsonify(status="ok", database="connected")


@app.route("/api/v1/categories")
def categories():
    """Returns the material categories in English, Marathi and Hindi."""
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT category_id, name_en, name_mr, name_hi, hazard_level "
                "FROM material_categories ORDER BY category_id"
            )
        ).mappings().all()
    return jsonify([dict(row) for row in rows])


if __name__ == "__main__":
    app.run(debug=True)
