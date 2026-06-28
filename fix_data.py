import sqlite3

conn = sqlite3.connect("ecommerce_predictive_price_tracking_system.db")
cursor = conn.cursor()

# Fix Product 1 (Samsung S25 Ultra) — remove prices below 85000
cursor.execute("DELETE FROM price_history WHERE product_id = 1 AND price < 85000")
print(f"Samsung S25 Ultra: deleted {cursor.rowcount} bad records")

# Fix Product 5 — remove prices below 1000 (clearly wrong)
cursor.execute("DELETE FROM price_history WHERE product_id = 5 AND price < 1000")
print(f"Product 5: deleted {cursor.rowcount} bad records")

# Fix Product 7 — prices 180 to 466 — check if correct
cursor.execute("SELECT price, date FROM price_history WHERE product_id = 7 ORDER BY date")
rows = cursor.fetchall()
print(f"\nProduct 7 price history:")
for r in rows:
    print(f"  ₹{r[0]} — {r[1]}")

conn.commit()
conn.close()
print("\nDone! Bad data cleaned.")