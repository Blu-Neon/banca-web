from db import get_connection
con=get_connection()
cur=con.cursor()
cur.execute("SELECT DISTINCT category FROM transactions ORDER BY category;")
rows=cur.fetchall()
print("Categorie presenti:")
for r in rows:
    print("-",r["category"])
con.close()
