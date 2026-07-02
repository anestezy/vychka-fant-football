
import os
import mysql.connector
from mysql.connector import pooling, Error
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'fantasy_football'),
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
}

class Database:
    _pool = None

    @classmethod
    def initialize_pool(cls, pool_size=5):
        try:
            cls._pool = pooling.MySQLConnectionPool(
                pool_name="fantasy_pool",
                pool_size=pool_size,
                **DB_CONFIG
            )
            print(f"✅ Connection pool создан (size={pool_size})")
        except Error as e:
            print(f"❌ Ошибка создания pool: {e}")
            raise

    @classmethod
    def get_connection(cls):
        if cls._pool is None:
            cls.initialize_pool()
        return cls._pool.get_connection()

    @classmethod
    def execute_query(cls, query, params=None, fetch=False):
        conn = None
        cursor = None
        try:
            conn = cls.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params or ())

            if fetch:
                result = cursor.fetchall()
            else:
                conn.commit()
                result = cursor.rowcount

            return result
        except Error as e:
            if conn:
                conn.rollback()
            print(f"❌ Ошибка SQL: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @classmethod
    def execute_many(cls, query, params_list):
        conn = None
        cursor = None
        try:
            conn = cls.get_connection()
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()
            return cursor.rowcount
        except Error as e:
            if conn:
                conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

Database.initialize_pool()