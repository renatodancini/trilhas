import sqlite3

conn = sqlite3.connect('login_status.db')
c = conn.cursor()
try:
    c.execute('ALTER TABLE gestao_trilhas ADD COLUMN "Impresso por" TEXT')
    print("Coluna 'Impresso por' criada com sucesso!")
except Exception as e:
    print("Erro ao criar coluna 'Impresso por':", e)
try:
    c.execute('ALTER TABLE gestao_trilhas ADD COLUMN "Modificado em" TEXT')
    print("Coluna 'Modificado em' criada com sucesso!")
except Exception as e:
    print("Erro ao criar coluna 'Modificado em':", e)
conn.commit()
conn.close() 