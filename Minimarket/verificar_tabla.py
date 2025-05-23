import sqlite3

# Conexión a la base de datos
con = sqlite3.connect('database.db')
cur = con.cursor()

# Listar todas las tablas en la base de datos
cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cur.fetchall()

# Mostrar las tablas
print("Tablas en la base de datos:", tables)

con.close()
