import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "rh_simples.db")

def conectar():
    return sqlite3.connect(DB_PATH)

def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()

    # FUNCIONARIOS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS funcionarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT
    )
    """)

    # EMPRESA / SETOR / ETC
    cursor.execute("CREATE TABLE IF NOT EXISTS empresas (id INTEGER PRIMARY KEY, nome TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS setores (id INTEGER PRIMARY KEY, nome TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS cargos (id INTEGER PRIMARY KEY, nome TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS obras (id INTEGER PRIMARY KEY, nome TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS cidades (id INTEGER PRIMARY KEY, nome TEXT)")

    # FECHAMENTO
    cursor.execute("""
CREATE TABLE IF NOT EXISTS fechamento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    funcionario TEXT,
    empresa TEXT,
    setor TEXT,
    cargo TEXT,
    obra TEXT,
    cidade TEXT,

    tipo TEXT,
    ano INTEGER,
    mes INTEGER,

    salario REAL,
    premio REAL,

    filhos INTEGER,
    desconto REAL,

    dias_normais INTEGER,
    dias_faltas INTEGER,
    dsr INTEGER,
    horas_falta TEXT,

    valor_dias_normais REAL,
    valor_premio REAL,
    salario_familia REAL,

    dias_faltas_valor REAL,
    dsr_faltas_valor REAL,
    horas_faltas_valor REAL,

    base_inss REAL,
    inss REAL,

    total_vencimentos REAL,
    total_descontos REAL,
    liquido REAL
);
    """)

    conn.commit()
    conn.close()