from db import get_connection
con=get_connection()
cur=con.cursor()
cur.execute("SELECT id, username FROM users ORDER BY id;")
rows=cur.fetchall()
print("User presenti:")
for r in rows:
    print(f"ID: {r["id"]} | username: {r["username"]}")
con.close()
