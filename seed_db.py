import sqlite3
import random
from datetime import date, timedelta

DB_FILE = 'construction_log.db'

def seed_data():
    print("🌱 Starte Datengenerierung (Mit Projektnummern)...")
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # 1. СОЗДАНИЕ ТАБЛИЦ
    
    c.execute('''CREATE TABLE IF NOT EXISTS projects
                 (id INTEGER PRIMARY KEY, name TEXT UNIQUE)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS workers
                 (id INTEGER PRIMARY KEY, name TEXT UNIQUE, position TEXT)''')
    
    # Таблица лесов
    c.execute('''CREATE TABLE IF NOT EXISTS scaffolds
                 (id INTEGER PRIMARY KEY, 
                  project_id INTEGER,
                  number TEXT, 
                  description TEXT,
                  acc TEXT,
                  volume_m3 REAL,
                  area_m2 REAL,
                  weight_to REAL,
                  material_cost REAL,
                  FOREIGN KEY(project_id) REFERENCES projects(id),
                  UNIQUE(project_id, number))''')
                  
    # Таблица часов
    c.execute('''CREATE TABLE IF NOT EXISTS work_logs
                 (id INTEGER PRIMARY KEY, 
                  user_name TEXT, 
                  project_name TEXT, 
                  scaffold_number TEXT, 
                  work_date DATE, 
                  hours REAL,
                  comment TEXT,
                  version TEXT)''')

    # 2. СОТРУДНИКИ
    workers = [
        ("Andreas Schmidt", "Gerüstbauer"),
        ("Thomas Müller", "Vorarbeiter"),
        ("Michael Weber", "Bauleiter"),
        ("Klaus Wagner", "Planer")
    ]
    for name, pos in workers:
        try: c.execute("INSERT INTO workers (name, position) VALUES (?, ?)", (name, pos))
        except: pass 

    # 3. ПРОЕКТЫ (С НУМЕРАЦИЕЙ "00-000 Name")
    projects = [
        "02-016 Wohnpark Berlin-Mitte", 
        "05-104 Einkaufszentrum West", 
        "03-099 Logistikzentrum Nord"
    ]
    for proj in projects:
        try: c.execute("INSERT INTO projects (name) VALUES (?)", (proj,))
        except: pass

    conn.commit()

    # 4. ЛЕСА
    proj_map = {}
    for proj in projects:
        c.execute("SELECT id FROM projects WHERE name = ?", (proj,))
        proj_map[proj] = c.fetchone()[0]

    # Данные привязаны к новым именам проектов
    scaffolds_data = [
        # Проект (Новое имя), Номер, Описание, ACC, m3, m2, to, Materialwert
        ("02-016 Wohnpark Berlin-Mitte", "G-101", "Nordfassade", "ja", 120, 60, 3.5, 7500),
        ("02-016 Wohnpark Berlin-Mitte", "G-102", "Südfassade", "nein", 250, 120, 6.2, 14000),
        ("05-104 Einkaufszentrum West", "E-05", "Haupteingang", "ja", 80, 40, 2.1, 4200),
        ("03-099 Logistikzentrum Nord", "L-50", "Halle Innen", "", 500, 200, 12.5, 28000)
    ]

    print(f"🪜 Installiere Gerüste...")
    for row in scaffolds_data:
        p_name, num, desc, acc, vol, area, weight, cost = row
        if p_name in proj_map:
            p_id = proj_map[p_name]
            try:
                c.execute('''INSERT INTO scaffolds 
                             (project_id, number, description, acc, volume_m3, area_m2, weight_to, material_cost) 
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
                          (p_id, num, desc, acc, vol, area, weight, cost))
            except sqlite3.IntegrityError: pass

    # 5. ОТЧЕТЫ (ЧАСЫ)
    print("📝 Generiere Stunden-Buchungen...")
    
    scaffolds_in_projects = {}
    for row in scaffolds_data:
        p_name, s_num = row[0], row[1]
        if p_name not in scaffolds_in_projects: scaffolds_in_projects[p_name] = []
        scaffolds_in_projects[p_name].append(s_num)
    
    today = date.today()
    
    for worker_name, _ in workers:
        for i in range(5): 
            delta = random.randint(0, 10)
            work_date = today - timedelta(days=delta)
            proj = random.choice(projects) # Выбирает проект из нового списка
            
            if proj in scaffolds_in_projects:
                scaf = random.choice(scaffolds_in_projects[proj])
                hours = random.choice([2.0, 4.0, 5.5, 8.0])
                comment = random.choice(["", "Korrektur Statik", "Entwurf", "Detailplanung"])
                version = random.choice(["v1", "v2", ""])
                
                c.execute('''INSERT INTO work_logs 
                             (user_name, project_name, scaffold_number, work_date, hours, comment, version) 
                             VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                          (worker_name, proj, scaf, work_date, hours, comment, version))

    conn.commit()
    conn.close()
    print("✅ Fertig! Datenbank ist bereit.")

if __name__ == "__main__":
    seed_data()