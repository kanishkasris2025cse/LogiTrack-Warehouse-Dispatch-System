import sqlite3

class WarehouseSystem:
    def __init__(self, db_name="warehouse_logistics.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.init_db()

    def init_db(self):
        with open("schema.sql", "r") as f:
            self.cursor.executescript(f.read())
        self.conn.commit()

    def add_or_update_stock(self, sku, name, qty):
        self.cursor.execute("""
            INSERT INTO inventory_items (sku_code, item_name, current_stock)
            VALUES (?, ?, ?)
            ON CONFLICT(sku_code) DO UPDATE SET
            current_stock = current_stock + excluded.current_stock,
            last_updated = CURRENT_TIMESTAMP;
        """, (sku, name, qty))
        self.conn.commit()

    def process_dispatch(self, order_ref, sku, qty):
        self.cursor.execute("SELECT current_stock FROM inventory_items WHERE sku_code = ?", (sku,))
        record = self.cursor.fetchone()
        if not record or record[0] < qty:
            print(f"[REJECTED] Insufficient stock for Order {order_ref} (SKU: {sku})")
            return False

        self.cursor.execute("""
            INSERT INTO dispatch_orders (order_ref, sku_code, quantity_dispatched, dispatch_status)
            VALUES (?, ?, ?, 'SHIPPED');
        """, (order_ref, sku, qty))
        self.conn.commit()
        print(f"[SUCCESS] Dispatched {qty} units for Order {order_ref}.")
        return True

    def generate_audit_report(self):
        self.cursor.execute("SELECT sku_code, item_name, current_stock, reorder_level FROM inventory_items")
        items = self.cursor.fetchall()
        print("\n--- KYOWA WAREHOUSE INVENTORY AUDIT ---")
        for item in items:
            alert = " [!] REORDER REQUIRED" if item[2] <= item[3] else " [OK]"
            print(f"SKU: {item[0]} | Name: {item[1]} | In Stock: {item[2]}{alert}")

if __name__ == "__main__":
    system = WarehouseSystem()
    system.add_or_update_stock("KW-BOX-01", "Heavy Packaging Crates", 150)
    system.add_or_update_stock("KW-PLT-09", "Transport Pallets", 40)
    system.process_dispatch("ORD-9821", "KW-BOX-01", 30)
    system.generate_audit_report()