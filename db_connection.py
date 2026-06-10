import os
import sys
import sqlite3


def get_app_dir():
    if getattr(sys, 'frozen', False):
        app_dir = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), 'Lost_and_Found_Desk_App')
    else:
        app_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(app_dir, exist_ok=True)
    return app_dir


def get_resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


def get_db_path():
    return os.path.join(get_app_dir(), 'lost_and_found.db')

def get_db_connection():
    conn = sqlite3.connect(get_db_path())
    # Ensure tables exist
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            full_name TEXT,
            email TEXT,
            phone TEXT,
            user_type TEXT DEFAULT 'user'
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lost_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            category TEXT,
            date_lost TEXT,
            location_lost TEXT,
            description TEXT,
            contact_info TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS found_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            category TEXT,
            date_found TEXT,
            location_found TEXT,
            description TEXT,
            contact_info TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS claimed_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            category TEXT,
            date_claimed TEXT,
            contact_info TEXT,
            description TEXT
        )
    ''')
    conn.commit()
    return conn