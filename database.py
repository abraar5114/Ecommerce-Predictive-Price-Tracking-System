# =============================================
# ECOMMERCE PREDICTIVE PRICE TRACKING SYSTEM
# Database File
# =============================================

import sqlite3
from config import DATABASE_NAME

def create_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    return conn

def create_tables():
    conn = create_connection()
    cursor = conn.cursor()

    # Products Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            url TEXT NOT NULL,
            site TEXT NOT NULL,
            target_price REAL NOT NULL,
            email TEXT NOT NULL,
            current_price REAL,
            best_site TEXT
        )
    ''')

    # Price History Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            price REAL NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')

    conn.commit()
    conn.close()
    print("Database created successfully!")

def save_product(name, url, site, target_price, email, current_price):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO products (name, url, site, target_price, email, current_price)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, url, site, target_price, email, current_price))
    conn.commit()
    product_id = cursor.lastrowid
    conn.close()
    return product_id

def save_price_history(product_id, price):
    from datetime import datetime
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO price_history (product_id, price, date)
        VALUES (?, ?, ?)
    ''', (product_id, price, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def get_all_products():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    conn.close()
    return products

def get_price_history(product_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT price, date FROM price_history
        WHERE product_id = ?
        ORDER BY date ASC
    ''', (product_id,))
    history = cursor.fetchall()
    conn.close()
    return history

def update_current_price(product_id, price):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE products SET current_price = ?
        WHERE id = ?
    ''', (price, product_id))
    conn.commit()
    conn.close()

# Create tables when file runs
create_tables()