import sqlite3
import streamlit as st

def conectar():
    return sqlite3.connect("rh_simples.db")

conn = conectar()
cursor = conn.cursor()


try:
    cursor.execute("ALTER TABLE fechamento ADD COLUMN obra TEXT;")
except:
    pass

try:
    cursor.execute("ALTER TABLE fechamento ADD COLUMN cidade TEXT;")
except:
    pass

conn.commit()
conn.close()



