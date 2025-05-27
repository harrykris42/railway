#!/bin/bash
echo "📦 Setting up Railway Booking System..."

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
echo "✅ .env file created. Please edit it with your MySQL credentials."
read -p "✏️  Press Enter after editing the .env file..."

# Extract credentials from .env
MYSQL_USER=$(grep MYSQL_USER .env | cut -d '=' -f2)
MYSQL_PASSWORD=$(grep MYSQL_PASSWORD .env | cut -d '=' -f2)
MYSQL_HOST=$(grep MYSQL_HOST .env | cut -d '=' -f2)

# Run schema.sql using mysql CLI
echo "🛠️  Creating tables using MySQL CLI..."
mysql -h "$MYSQL_HOST" -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" < schema.sql

if [ $? -ne 0 ]; then
  echo "❌ Failed to execute schema.sql. Please check credentials and MySQL status."
  exit 1
fi

echo "✅ Database and tables created."
python run.py
