import sqlite3
import random
from datetime import date, timedelta

DB_FILE = 'construction_log.db'

def seed_data():
    print("🌱 Starte Datengenerierung (Deutsch + Finanzen)...")
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # 1. СОЗДАНИЕ ТАБЛИЦ (С НОВЫМИ КОЛОНКАМИ)
    c.execute('''CREATE TABLE IF NOT EXISTS projects
                 (id INTEGER PRIMARY KEY, name TEXT UNIQUE)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS workers
                 (id INTEGER PRIMARY KEY, name TEXT UNIQUE, position TEXT)''')
    
    # ВНИМАНИЕ: Здесь добавлены volume_m3 и total_cost
    c.execute('''CREATE TABLE IF NOT EXISTS scaffolds
                 (id INTEGER PRIMARY KEY, 
                  project_id INTEGER,
                  number TEXT, 
                  description TEXT,
                  volume_m3 REAL,
                  total_cost REAL,
                  FOREIGN KEY(project_id) REFERENCES projects(id),
                  UNIQUE(project_id, number))''')
                  
    c.execute('''CREATE TABLE IF NOT EXISTS work_logs
                 (id INTEGER PRIMARY KEY, 
                  user_name TEXT, 
                  project_name TEXT, 
                  scaffold_number TEXT, 
                  work_date DATE, 
                  hours REAL)''')

    # 2. СОТРУДНИКИ
    workers = [
        ("Thomas Müller", "Vorarbeiter"),
        ("Andreas Schmidt", "Gerüstbauer"),
        ("Michael Weber", "Bauleiter"),
        ("Sabine Fischer", "Sicherheitsbeauftragte"),
        ("Klaus Wagner", "Monteur"),
        ("Stefan Richter", "Hilfsarbeiter")
    ]
    print(f"👥 Füge {len(workers)} Mitarbeiter hinzu...")
    for name, pos in workers:
        try:
            c.execute("INSERT INTO workers (name, position) VALUES (?, ?)", (name, pos))
        except sqlite3.IntegrityError:
            pass 

    # 3. ПРОЕКТЫ
    projects = [
        "Wohnpark Berlin-Mitte", 
        "Einkaufszentrum West", 
        "Sanierung Rathaus",
        "Logistikzentrum Nord"
    ]
    print(f"🏗️ Füge {len(projects)} Projekte hinzu...")
    for proj in projects:
        try:
            c.execute("INSERT INTO projects (name) VALUES (?)", (proj,))
        except sqlite3.IntegrityError:
            pass

    conn.commit()

    # 4. ЛЕСА С ОБЪЕМАМИ И ЦЕНАМИ
    proj_map = {}
    for proj in projects:
        c.execute("SELECT id FROM projects WHERE name = ?", (proj,))
        result = c.fetchone()
        if result:
            proj_map[proj] = result[0]

    scaffolds_data = [
        ("Wohnpark Berlin-Mitte", "G-101", "Nordfassade"),
        ("Wohnpark Berlin-Mitte", "G-102", "Südfassade"),
        ("Wohnpark Berlin-Mitte", "T-01", "Treppenhausturm"),
        ("Einkaufszentrum West", "E-05", "Haupteingang"),
        ("Einkaufszentrum West", "E-06", "Ladezone"),
        ("Sanierung Rathaus", "R-20", "Uhrturm"),
        ("Sanierung Rathaus", "R-21", "Innenhof"),
        ("Logistikzentrum Nord", "L-50", "Halle 3 Innen")
    ]

    print(f"🪜 Installiere Gerüste mit Finanzdaten ({len(scaffolds_data)} Stück)...")
    for proj_name, num, desc in scaffolds_data:
        if proj_name in proj_map:
            p_id = proj_map[proj_name]
            
            # Генерируем случайные финансовые данные
            vol = round(random.uniform(50.0, 500.0), 0)  # Объем
            cost = round(vol * random.uniform(25.0, 60.0), 2) # Цена
            
            try:
                # Вставляем данные уже с объемом и ценой
                c.execute("INSERT INTO scaffolds (project_id, number, description, volume_m3, total_cost) VALUES (?, ?, ?, ?, ?)", 
                          (p_id, num, desc, vol, cost))
            except sqlite3.IntegrityError:
                pass

    # 5. ГЕНЕРАЦИЯ ОТЧЕТОВ
    print("📝 Generiere Arbeitsberichte...")
    scaffolds_in_projects = {}
    for p_name, s_num, _ in scaffolds_data:
        if p_name not in scaffolds_in_projects:
            scaffolds_in_projects[p_name] = []
        scaffolds_in_projects[p_name].append(s_num)
    
    today = date.today()
    log_count = 0
    
    for worker_name, _ in workers:
        days_worked = random.randint(5, 12)
        for i in range(days_worked):
            delta = random.randint(0, 14)
            work_date = today - timedelta(days=delta)
            proj = random.choice(projects)
            
            if proj in scaffolds_in_projects:
                scaf = random.choice(scaffolds_in_projects[proj])
                hours = random.choice([4.0, 5.0, 8.0, 8.5, 9.0, 10.0])
                
                c.execute('''INSERT INTO work_logs (user_name, project_name, scaffold_number, work_date, hours) 
                             VALUES (?, ?, ?, ?, ?)''', 
                          (worker_name, proj, scaf, work_date, hours))
                log_count += 1

    conn.commit()
    conn.close()
    print(f"✅ Fertig! {log_count} Datensätze erstellt.")

if __name__ == "__main__":
    seed_data()