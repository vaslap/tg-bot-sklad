import sqlite3

class Database:
    def __init__(self, db_name="data/warehouse.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()
    
    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                sku TEXT PRIMARY KEY,
                name TEXT,
                location TEXT,
                quantity INTEGER DEFAULT 0,
                reserved INTEGER DEFAULT 0
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS operations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sku TEXT,
                type TEXT,
                quantity INTEGER,
                user_id INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()
    
    def get_product(self, sku):
        self.cursor.execute("SELECT * FROM products WHERE sku = ?", (sku,))
        row = self.cursor.fetchone()
        if row:
            return {"sku": row[0], "name": row[1], "location": row[2], "quantity": row[3], "reserved": row[4]}
        return None
    
    def reserve_product(self, sku, qty, user_id):
        product = self.get_product(sku)
        if not product:
            return False
        available = product["quantity"] - product["reserved"]
        if qty > available:
            return False
        self.cursor.execute("UPDATE products SET reserved = reserved + ? WHERE sku = ?", (qty, sku))
        self.cursor.execute("INSERT INTO operations (sku, type, quantity, user_id) VALUES (?, 'reserve', ?, ?)", (sku, qty, user_id))
        self.conn.commit()
        return True
    
    def receipt_product(self, sku, name, qty, user_id):
        product = self.get_product(sku)
        if product:
            self.cursor.execute("UPDATE products SET quantity = quantity + ? WHERE sku = ?", (qty, sku))
        else:
            self.cursor.execute("INSERT INTO products (sku, name, quantity, reserved) VALUES (?, ?, ?, 0)", (sku, name, qty))
        self.cursor.execute("INSERT INTO operations (sku, type, quantity, user_id) VALUES (?, 'receipt', ?, ?)", (sku, qty, user_id))
        self.conn.commit()
    
    def ship_product(self, sku, qty, user_id):
        product = self.get_product(sku)
        if not product:
            return False
        available = product["quantity"] - product["reserved"]
        if qty > available:
            return False
        if qty <= product["reserved"]:
            self.cursor.execute("UPDATE products SET reserved = reserved - ? WHERE sku = ?", (qty, sku))
        else:
            qty_from_stock = qty - product["reserved"]
            self.cursor.execute("UPDATE products SET reserved = 0, quantity = quantity - ? WHERE sku = ?", (qty_from_stock, sku))
        self.cursor.execute("INSERT INTO operations (sku, type, quantity, user_id) VALUES (?, 'ship', ?, ?)", (sku, qty, user_id))
        self.conn.commit()
        return True