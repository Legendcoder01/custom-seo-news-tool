import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
import logging
from datetime import datetime, timedelta

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fallback in-memory SQLite for local testing if MySQL isn't configured
import sqlite3

class DocumentDB:
    def __init__(self):
        # Hostinger Database configuration
        self.db_host = os.getenv("DB_HOST")
        self.db_user = os.getenv("DB_USER")
        self.db_password = os.getenv("DB_PASSWORD")
        self.db_name = os.getenv("DB_NAME")
        
        self.use_mysql = bool(self.db_host and self.db_user and self.db_name)
        
        if self.use_mysql:
            logger.info(f"Connecting to Hostinger MySQL database at {self.db_host}.")
            try:
                self.conn = mysql.connector.connect(
                    host=self.db_host,
                    user=self.db_user,
                    password=self.db_password,
                    database=self.db_name
                )
            except Error as e:
                logger.error(f"Error connecting to MySQL: {e}")
                self.conn = None
                self.use_mysql = False
        else:
            logger.info("No DB credentials found. Falling back to local SQLite for testing.")
            self.conn = sqlite3.connect("local_sightings.db", check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            
        self._init_db()

    def _init_db(self):
        """Creates the necessary tables if they don't exist."""
        if not self.conn: return
        
        cursor = self.conn.cursor()
        
        if self.use_mysql:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS keyword_sightings (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    keyword VARCHAR(255) NOT NULL,
                    url TEXT NOT NULL,
                    source_domain VARCHAR(255) NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        else:
            # SQLite Syntax
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS keyword_sightings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    keyword TEXT NOT NULL,
                    url TEXT NOT NULL,
                    source_domain TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
        self.conn.commit()
        cursor.close()

    def log_sighting(self, keyword, url, source_domain):
        """Logs a single occurrence of a keyword from a specific source."""
        if not self.conn: return
        
        cursor = self.conn.cursor()
        query = '''
            INSERT INTO keyword_sightings (keyword, url, source_domain)
            VALUES (%s, %s, %s)
        ''' if self.use_mysql else '''
            INSERT INTO keyword_sightings (keyword, url, source_domain)
            VALUES (?, ?, ?)
        '''
        
        try:
            cursor.execute(query, (keyword, url, source_domain))
            self.conn.commit()
        except Error as e:
            logger.error(f"Error inserting sighting: {e}")
        finally:
            cursor.close()

    def check_high_priority_alert(self, keyword, hours=1, min_sources=5):
        """
        Checks if a keyword has been seen on `min_sources` distinct domains
        within the last `hours`.
        """
        if not self.conn: return False, 0
        
        # We need a dictionary cursor for MySQL logic, SQLite returns Rows natively via connection setting
        cursor = self.conn.cursor(dictionary=True) if self.use_mysql else self.conn.cursor()
        
        if self.use_mysql:
            # MySQL Interval Syntax
            query = '''
                SELECT COUNT(DISTINCT source_domain) as unique_sources 
                FROM keyword_sightings
                WHERE keyword = %s AND timestamp >= NOW() - INTERVAL %s HOUR
            '''
            cursor.execute(query, (keyword, hours))
            result = cursor.fetchone()
            unique_sources = result['unique_sources'] if result else 0
        else:
            # SQLite
            cutoff = (datetime.utcnow() - timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M:%S")
            query = '''
                SELECT COUNT(DISTINCT source_domain) as unique_sources 
                FROM keyword_sightings
                WHERE keyword = ? AND timestamp >= ?
            '''
            cursor.execute(query, (keyword, cutoff))
            result = cursor.fetchone()
            unique_sources = result['unique_sources'] if result else 0
            
        cursor.close()
        return unique_sources >= min_sources, unique_sources

# Singleton instance
db = DocumentDB()

if __name__ == "__main__":
    # Test
    db.log_sighting("Sora 2", "http://example.com/1", "example.com")
    db.log_sighting("Sora 2", "http://test.com/1", "test.com")
    is_alert, sources = db.check_high_priority_alert("Sora 2", min_sources=2)
    print(f"Alert triggering: {is_alert} (Sources: {sources})")
