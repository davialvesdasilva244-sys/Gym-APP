import sqlite3
from datetime import datetime

# ==========================================================
# 1. CONFIGURAÇÃO DO BANCO DE DADOS (SQLite em memória)
# ==========================================================

conn = sqlite3.connect(":memory:")
cur = conn.cursor()

# Criar tabelas
cur.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);
""")

cur.execute("""
CREATE TABLE gyms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    address TEXT NOT NULL
);
""")

cur.execute("""
CREATE TABLE checkins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    gym_id INTEGER NOT NULL,
    timestamp TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(gym_id) REFERENCES gyms(id)
);
""")


# ==========================================================
# 2. INSERIR USANDO SQL NORMAL
# ==========================================================

cur.execute("""
INSERT INTO gyms (name, address)
VALUES
("Iron Gym", "Rua Principal 123"),
("Power House", "Avenida Fitness 45"),
("MegaFit Center", "Rodovia 999");
""")

conn.commit()


# ==========================================================
# 3. FUNÇÕES — USANDO COMANDOS SQL REAIS
# ==========================================================

def register_user():
    print("\n===== REGISTRO DE USUÁRIO =====")
    name = input("Nome: ")
    email = input("E-mail: ")
    pw = input("Senha: ")

    try:
        cur.execute("""
            INSERT INTO users (name, email, password)
            VALUES (?, ?, ?)
        """, (name, email, pw))

        conn.commit()
        print("✔ Registro realizado com sucesso!")

    except sqlite3.IntegrityError:
        print("✖ Erro: E-mail já existe.")


def login_user():
    print("\n===== LOGIN =====")
    email = input("E-mail: ")
    pw = input("Senha: ")

    cur.execute("""
        SELECT id, name
        FROM users
        WHERE email = ? AND password = ?
    """, (email, pw))

    user = cur.fetchone()

    if user:
        print(f"\n✔ Bem-vindo(a), {user[1]}!")
        return user[0]
    else:
        print("✖ E-mail ou senha incorretos.")
        return None


def show_gyms():
    print("\n===== ACADEMIAS DISPONÍVEIS =====")
    cur.execute("SELECT id, name, address FROM gyms ORDER BY id ASC")
    rows = cur.fetchall()

    for r in rows:
        print(f"{r[0]} - {r[1]} ({r[2]})")


def check_in(user_id):
    show_gyms()

    try:
        gym_id = int(input("\nDigite o ID da academia para check-in: "))
    except:
        print("✖ Entrada inválida.")
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # -------------------------------------------
    # ✔ USANDO SQL "INSERT INTO SELECT"
    # -------------------------------------------
    cur.execute("""
        INSERT INTO checkins (user_id, gym_id, timestamp)
        SELECT ?, ?, ?
    """, (user_id, gym_id, timestamp))

    conn.commit()
    print("✔ Check-in concluído!")


def show_history(user_id):
    print("\n===== HISTÓRICO DE CHECK-INS =====")

    cur.execute("""
        SELECT c.timestamp, g.name
        FROM checkins c
        JOIN gyms g ON c.gym_id = g.id
        WHERE c.user_id = ?
        ORDER BY c.timestamp DESC
    """, (user_id,))

    rows = cur.fetchall()

    if not rows:
        print("Nenhum check-in ainda.")
    else:
        for t, gym in rows:
            print(f"{t} - {gym}")


def delete_user(user_id):
    print("\nExcluindo sua conta...")

    cur.execute("DELETE FROM checkins WHERE user_id = ?", (user_id,))
    cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()

    print("✔ Conta excluída com sucesso!")


# ==========================================================
# 4. MENU DO USUÁRIO LOGADO
# ==========================================================

def logged_menu(user_id):
    while True:
        print("""
===== MENU PRINCIPAL =====
1 - Fazer Check-in
2 - Mostrar Academias
3 - Histórico de Check-ins
4 - Excluir Minha Conta
0 - Sair
        """)

        choice = input("Escolha: ")

        if choice == "1":
            check_in(user_id)
        elif choice == "2":
            show_gyms()
        elif choice == "3":
            show_history(user_id)
        elif choice == "4":
            delete_user(user_id)
            break
        elif choice == "0":
            print("Deslogado.")
            break
        else:
            print("✖ Opção inválida.")


# ==========================================================
# 5. MENU PRINCIPAL
# ==========================================================

def main_menu():
    while True:
        print("""
===== SISTEMA DE GERENCIAMENTO DE ACADEMIA =====
1 - Entrar
2 - Cadastrar
0 - Sair
        """)

        choice = input("Escolha: ")

        if choice == "1":
            user_id = login_user()
            if user_id:
                logged_menu(user_id)

        elif choice == "2":
            register_user()

        elif choice == "0":
            print("Saindo...")
            break

        else:
            print("✖ Opção inválida.")


# ==========================================================
# 6. INICIAR PROGRAMA
# ==========================================================

main_menu()
