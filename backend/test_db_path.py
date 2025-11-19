import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import DATABASE_URL, engine
import sqlite3

print("\n" + "="*60)
print("🔍 DATABASE CONNECTION ANALYSIS")
print("="*60)

print(f"\n1. DATABASE_URL from database.py:")
print(f"   {DATABASE_URL}")

print(f"\n2. SQLAlchemy engine URL:")
print(f"   {engine.url}")

print(f"\n3. Absolute path resolved:")
db_path = str(engine.url).replace('sqlite:///', '')
print(f"   {db_path}")

print(f"\n4. Does this file exist?")
print(f"   {os.path.exists(db_path)}")

if os.path.exists(db_path):
    print(f"\n5. Checking contents:")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM studies")
    count = cursor.fetchone()[0]
    print(f"   Studies in this database: {count}")
    conn.close()

print("\n6. All .db files in backend directory:")
for f in os.listdir('.'):
    if f.endswith('.db'):
        full_path = os.path.abspath(f)
        conn = sqlite3.connect(f)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM studies")
            count = cursor.fetchone()[0]
            print(f"   {f}: {count} studies (path: {full_path})")
        except:
            print(f"   {f}: no studies table")
        conn.close()

print("="*60 + "\n")
