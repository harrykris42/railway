import mysql.connector
from mysql.connector import errorcode
import os
from dotenv import load_dotenv

load_dotenv()

# DB config
db_user = os.getenv("MYSQL_USER")
db_pass = os.getenv("MYSQL_PASSWORD")
db_host = os.getenv("MYSQL_HOST")
db_name = os.getenv("MYSQL_DB")

# Create DB
def create_database():
    try:
        conn = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_pass
        )
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        print(f"✅ Database '{db_name}' ensured.")
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        print("❌ Error creating database:", err)
        exit(1)

create_database()

# Now import app
from app import create_app, db
from app.models import User, Train, Booking  # important

app = create_app()

with app.app_context():
    try:
        db.create_all()
        print("✅ Tables created.")
    except Exception as e:
        print("❌ Error creating tables:", e)
