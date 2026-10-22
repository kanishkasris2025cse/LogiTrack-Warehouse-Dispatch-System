CREATE TABLE IF NOT EXISTS inventory_items (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku_code TEXT UNIQUE NOT NULL,
    item_name TEXT NOT NULL,
    current_stock INTEGER DEFAULT 0,
    reorder_level INTEGER DEFAULT 10,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dispatch_orders (
    dispatch_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_ref TEXT NOT NULL,
    sku_code TEXT NOT NULL,
    quantity_dispatched INTEGER NOT NULL,
    dispatch_status TEXT CHECK(dispatch_status IN ('PENDING', 'SHIPPED', 'CANCELLED')),
    dispatch_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(sku_code) REFERENCES inventory_items(sku_code)
);

CREATE TRIGGER IF NOT EXISTS update_inventory_after_dispatch
AFTER INSERT ON dispatch_orders
WHEN NEW.dispatch_status = 'SHIPPED'
BEGIN
    UPDATE inventory_items
    SET current_stock = current_stock - NEW.quantity_dispatched,
        last_updated = CURRENT_TIMESTAMP
    WHERE sku_code = NEW.sku_code;
END;