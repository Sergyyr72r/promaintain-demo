import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import date
import io
import time

DB_FILE = 'construction_log.db'

# --- CSS STYLES (Дополнительная страховка дизайна) ---
def local_css():
    st.markdown("""
    <style>
        /* Логотип */
        .logo-container { font-family: 'Arial', sans-serif; font-weight: bold; font-size: 40px; line-height: 1; }
        .logo-pro { color: #003366 !important; }
        .logo-maintain { color: #8DB600 !important; }
        .slogan { font-size: 12px; color: #003366 !important; margin-top: 5px; font-weight: bold; }
        .phone-header { text-align: right; color: #003366 !important; font-size: 20px; font-weight: bold; padding-top: 10px; }
        
        /* КНОПКИ: Принудительно белый текст на синем фоне */
        div.stButton > button { 
            background-color: #003366 !important; 
            color: #FFFFFF !important; 
            border: none;
            border-radius: 4px;
            font-weight: bold;
        }
        div.stButton > button:hover { 
            background-color: #8DB600 !important; 
            color: #FFFFFF !important; 
        }
        div.stButton > button p {
            color: #FFFFFF !important; 
        }

        /* Футер */
        .footer { 
            position: fixed; left: 0; bottom: 0; width: 100%; 
            background-color: #f1f1f1; 
            color: #555555; 
            text-align: center; font-size: 12px; padding: 10px; 
            border-top: 1px solid #ddd; z-index: 100; 
        }
        .block-container { padding-bottom: 50px; }
    </style>
    """, unsafe_allow_html=True)

# --- DB INIT ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS projects (id INTEGER PRIMARY KEY, name TEXT UNIQUE)''')
    c.execute('''CREATE TABLE IF NOT EXISTS workers (id INTEGER PRIMARY KEY, name TEXT UNIQUE, position TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS scaffolds (id INTEGER PRIMARY KEY, project_id INTEGER, number TEXT, description TEXT, volume_m3 REAL, total_cost REAL, FOREIGN KEY(project_id) REFERENCES projects(id), UNIQUE(project_id, number))''')
    c.execute('''CREATE TABLE IF NOT EXISTS work_logs (id INTEGER PRIMARY KEY, user_name TEXT, project_name TEXT, scaffold_number TEXT, work_date DATE, hours REAL)''')
    conn.commit()
    conn.close()

init_db()

# --- STATE ---
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'user_role' not in st.session_state: st.session_state['user_role'] = None 
if 'current_user_name' not in st.session_state: st.session_state['current_user_name'] = None
if 'admin_warning_shown' not in st.session_state: st.session_state['admin_warning_shown'] = False

def get_data(query, params=()):
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def run_query(query, params=()):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute(query, params)
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False

def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Report')
    return output.getvalue()

def logout():
    st.session_state['logged_in'] = False
    st.session_state['user_role'] = None; st.rerun()

def render_header():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("""<div class="logo-container"><span class="logo-pro">pro</span><span class="logo-maintain">maintain</span><sup>®</sup></div><div class="slogan">Nah am Kunden. Nah am Projekt.</div>""", unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="phone-header">📞 08458 320800</div>', unsafe_allow_html=True)
    st.markdown("---")

st.set_page_config(page_title="promaintain Portal", page_icon="🏗️", layout="wide")
local_css()

# ================= LOGIN =================
if not st.session_state['logged_in']:
    render_header()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("System-Login")
        workers_df = get_data("SELECT name FROM workers ORDER BY name")
        workers_list = workers_df['name'].tolist()
        
        selected_worker = st.selectbox("Mitarbeiter auswählen", workers_list if workers_list else [""])
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Als Mitarbeiter anmelden", use_container_width=True):
            if workers_list:
                st.session_state['logged_in'] = True
                st.session_state['user_role'] = 'worker'
                st.session_state['current_user_name'] = selected_worker
                st.rerun()

        st.markdown("---")
        if not st.session_state['admin_warning_shown']:
            if st.button("Administrator-Login", use_container_width=True):
                st.session_state['admin_warning_shown'] = True
                st.rerun()
        else:
            st.warning("⚠️ Zugriff nur für Projektmanager!")
            c1, c2 = st.columns(2)
            if c1.button("OK", type="primary"):
                st.session_state['logged_in'] = True; st.session_state['user_role'] = 'admin'; st.rerun()
            if c2.button("Cancel"): st.session_state['admin_warning_shown'] = False; st.rerun()

# ================= APP =================
else:
    if st.session_state['user_role'] == 'admin': st.sidebar.markdown("### 👤 Administrator")
    else: st.sidebar.markdown(f"### 👷 {st.session_state['current_user_name']}")
    if st.sidebar.button("Abmelden"): logout()
    render_header()

    # --- WORKER ---
    if st.session_state['user_role'] == 'worker':
        st.title(f"Willkommen, {st.session_state['current_user_name']}")
        tab_work, tab_design = st.tabs(["🕒 Arbeitszeit erfassen", "🏗️ Daten nach Planung"])

        with tab_work:
            st.subheader("📝 Stunden buchen")
            projects_df = get_data("SELECT id, name FROM projects")
            if not projects_df.empty:
                p_map = dict(zip(projects_df['name'], projects_df['id']))
                sel_proj = st.selectbox("Projekt wählen", projects_df['name'], key="w_proj")
                scaf_df = get_data("SELECT number, description FROM scaffolds WHERE project_id = ?", (p_map[sel_proj],))
                
                if not scaf_df.empty:
                    scaf_df['disp'] = scaf_df.apply(lambda x: f"{x['number']} ({x['description']})" if x['description'] else x['number'], axis=1)
                    with st.form("wf"):
                        s_scaf = st.selectbox("Gerüstnummer", scaf_df['disp'])
                        w_date = st.date_input("Datum", date.today())
                        hours = st.number_input("Stunden", min_value=0.5, step=0.5)
                        if st.form_submit_button("Zeit buchen"):
                            run_query("INSERT INTO work_logs (user_name, project_name, scaffold_number, work_date, hours) VALUES (?, ?, ?, ?, ?)", 
                                      (st.session_state['current_user_name'], sel_proj, s_scaf.split(" (")[0], w_date, hours))
                            st.success("Gespeichert!"); time.sleep(1); st.rerun()
                else: st.info("Keine Gerüste für dieses Projekt.")
            else: st.warning("Keine Projekte.")

        with tab_design:
            st.subheader("🏗️ Daten nach abgeschlossener Planung erfassen")
            projects_df = get_data("SELECT id, name FROM projects")
            if not projects_df.empty:
                p_map = dict(zip(projects_df['name'], projects_df['id']))
                design_proj = st.selectbox("Ziel-Projekt", projects_df['name'], key="d_proj")
                scaf_df_design = get_data("SELECT id, number, description, volume_m3, total_cost FROM scaffolds WHERE project_id = ?", (p_map[design_proj],))
                
                if not scaf_df_design.empty:
                    scaf_df_design['disp'] = scaf_df_design.apply(lambda x: f"{x['number']} ({x['description']})", axis=1)
                    selected_scaf_display = st.selectbox("Gerüst auswählen", scaf_df_design['disp'], key="d_scaf_sel")
                    sel_num = selected_scaf_display.split(" (")[0]
                    current_row = scaf_df_design[scaf_df_design['number'] == sel_num].iloc[0]
                    
                    curr_vol = float(current_row['volume_m3']) if current_row['volume_m3'] else 0.0
                    curr_cost = float(current_row['total_cost']) if current_row['total_cost'] else 0.0
                    
                    st.info(f"Bearbeite Gerüst: **{sel_num}**")
                    with st.form("design_update_form"):
                        c3, c4 = st.columns(2)
                        new_vol = c3.number_input("Volumen (m³)", min_value=0.0, step=1.0, value=curr_vol)
                        new_cost = c4.number_input("Kalkulierte Kosten (€)", min_value=0.0, step=100.0, value=curr_cost)
                        if new_vol > 0: st.caption(f"📊 Durchschnittspreis: **{new_cost/new_vol:.2f} € / m³**")
                        if st.form_submit_button("Planungsdaten speichern"):
                             success = run_query("UPDATE scaffolds SET volume_m3=?, total_cost=? WHERE project_id=? AND number=?", (new_vol, new_cost, p_map[design_proj], sel_num))
                             if success: st.success("Aktualisiert!"); time.sleep(1.5); st.rerun()
                             else: st.error("Fehler beim Speichern.")
                else: st.warning("In diesem Projekt gibt es noch keine Gerüste.")
            else: st.warning("Keine Projekte.")

    # --- ADMIN ---
    elif st.session_state['user_role'] == 'admin':
        st.title("⚙️ Administrationsbereich")
        tab0, tab1, tab2, tab3 = st.tabs(["📋 Gesamtübersicht & Edit", "📈 KPI & Analytik", "👥 Mitarbeiter", "🏗️ Projekte/Gerüste"])

        # TAB 0: MASTER TABLE & EDIT
        with tab0:
            st.subheader("📋 Gesamtübersicht (Master-Tabelle)")
            
            # --- ФИЛЬТРЫ ---
            query_raw = "SELECT * FROM work_logs" 
            raw_logs = get_data(query_raw)
            all_projects = get_data("SELECT name FROM projects")['name'].tolist()
            
            col_f1, col_f2, col_f3 = st.columns(3)
            search_project = col_f1.multiselect("Filtern nach Projekt:", all_projects)
            all_workers = sorted(list(set(raw_logs['user_name'].unique()))) if not raw_logs.empty else []
            search_worker = col_f2.multiselect("Filtern nach Verantwortlichen:", all_workers)
            
            if search_project:
                scaffolds_in_proj = get_data(f"SELECT s.number FROM scaffolds s JOIN projects p ON s.project_id = p.id WHERE p.name IN ({','.join(['?']*len(search_project))})", tuple(search_project))
                available_scaffolds = sorted(scaffolds_in_proj['number'].tolist())
            else:
                available_scaffolds = get_data("SELECT number FROM scaffolds")['number'].tolist()
            
            search_scaffold = col_f3.multiselect("Filtern nach Gerüst (Nr.):", available_scaffolds)

            # --- MASTER TABLE QUERY ---
            query_master = '''
                SELECT 
                    p.name as Projekt,
                    s.number as Gerüst,
                    s.description as Beschreibung,
                    s.volume_m3 as Volumen,
                    s.total_cost as Kosten,
                    w.user_name as Arbeiter,
                    w.hours as Stunden
                FROM scaffolds s
                JOIN projects p ON s.project_id = p.id
                LEFT JOIN work_logs w ON s.number = w.scaffold_number AND p.name = w.project_name
            '''
            master_raw = get_data(query_master)
            
            if not master_raw.empty:
                if search_project: master_raw = master_raw[master_raw['Projekt'].isin(search_project)]
                if search_worker: master_raw = master_raw[master_raw['Arbeiter'].isin(search_worker)]
                if search_scaffold: master_raw = master_raw[master_raw['Gerüst'].isin(search_scaffold)]

                agg_df = master_raw.groupby(['Projekt', 'Gerüst', 'Beschreibung', 'Volumen', 'Kosten']).agg({
                    'Stunden': 'sum',
                    'Arbeiter': lambda x: ", ".join(sorted(list(set([str(i) for i in x if i is not None]))))
                }).reset_index()
                agg_df.rename(columns={'Arbeiter': 'Verantwortlich'}, inplace=True)
                
                st.dataframe(agg_df, use_container_width=True, 
                             column_config={"Volumen": st.column_config.NumberColumn(format="%.0f m³"), "Kosten": st.column_config.NumberColumn(format="%.2f €"), "Stunden": st.column_config.NumberColumn(format="%.1f h")})
                
                if not agg_df.empty:
                    st.download_button(label="📥 Tabelle als Excel exportieren", data=to_excel(agg_df), file_name=f"Gesamtuebersicht_{date.today()}.xlsx")

            st.divider()
            
            # --- БЛОК 1: РЕДАКТИРОВАНИЕ МАСТЕР-ДАННЫХ (ОБЪЕМ / СТОИМОСТЬ) ---
            st.subheader("✏️ Master-Daten bearbeiten (Volumen & Kosten)")
            
            # Используем фильтр проекта сверху, если он выбран, иначе просим выбрать
            if search_project and len(search_project) == 1:
                target_proj = search_project[0]
            else:
                target_proj = st.selectbox("Wählen Sie ein Projekt zur Bearbeitung:", all_projects, key="master_edit_proj")
            
            # Загружаем леса этого проекта
            scafs_for_edit = get_data('''
                SELECT s.number, s.description, s.volume_m3, s.total_cost, s.project_id 
                FROM scaffolds s 
                JOIN projects p ON s.project_id = p.id 
                WHERE p.name = ?
            ''', (target_proj,))
            
            if not scafs_for_edit.empty:
                scafs_for_edit['disp'] = scafs_for_edit.apply(lambda x: f"{x['number']} ({x['description']})", axis=1)
                
                # Выбор лесов
                sel_scaf_to_edit = st.selectbox("Gerüst wählen:", scafs_for_edit['disp'], key="master_edit_scaf")
                
                # Получаем текущие значения
                scaf_num_real = sel_scaf_to_edit.split(" (")[0]
                scaf_row = scafs_for_edit[scafs_for_edit['number'] == scaf_num_real].iloc[0]
                
                with st.form("edit_master_values"):
                    c_m1, c_m2, c_m3 = st.columns([1, 1, 1])
                    st.caption(f"Bearbeite: {target_proj} -> {scaf_num_real}")
                    
                    val_vol = float(scaf_row['volume_m3']) if pd.notna(scaf_row['volume_m3']) else 0.0
                    val_cost = float(scaf_row['total_cost']) if pd.notna(scaf_row['total_cost']) else 0.0
                    
                    new_vol_m = c_m1.number_input("Volumen (m³)", value=val_vol)
                    new_cost_m = c_m2.number_input("Kosten (€)", value=val_cost)
                    
                    if st.form_submit_button("💾 Speichern"):
                        pid_safe = int(scaf_row['project_id'])
                        run_query("UPDATE scaffolds SET volume_m3=?, total_cost=? WHERE project_id=? AND number=?", 
                                  (new_vol_m, new_cost_m, pid_safe, scaf_num_real))
                        st.success("Master-Daten aktualisiert!")
                        time.sleep(1)
                        st.rerun()
            else:
                st.warning("Keine Gerüste in diesem Projekt.")

            st.divider()

            # --- БЛОК 2: РЕДАКТИРОВАНИЕ ЧАСОВ (ДЕТАЛЬНО) ---
            st.subheader("🛠 Arbeitszeit-Einträge korrigieren")
            
            # Показываем детальную таблицу с фильтрами, которые выбраны сверху
            query_details = "SELECT * FROM work_logs WHERE 1=1"
            params_details = []
            
            if search_project:
                query_details += f" AND project_name IN ({','.join(['?']*len(search_project))})"
                params_details.extend(search_project)
            if search_worker:
                query_details += f" AND user_name IN ({','.join(['?']*len(search_worker))})"
                params_details.extend(search_worker)
            if search_scaffold:
                query_details += f" AND scaffold_number IN ({','.join(['?']*len(search_scaffold))})"
                params_details.extend(search_scaffold)
            
            query_details += " ORDER BY id DESC"
            df_details = get_data(query_details, tuple(params_details))
            
            st.dataframe(df_details, use_container_width=True)
            
            with st.expander("Eintrag bearbeiten / löschen (Nach ID)", expanded=False):
                edit_id_log = st.number_input("ID eingeben:", min_value=0, step=1)
                
                if edit_id_log > 0:
                    log_match = get_data("SELECT * FROM work_logs WHERE id=?", (edit_id_log,))
                    if not log_match.empty:
                        l_row = log_match.iloc[0]
                        st.markdown(f"**Bearbeite Eintrag ID: {edit_id_log}**")
                        
                        with st.form("edit_log_full_main"):
                            # Сотрудник
                            all_w = get_data("SELECT name FROM workers")['name'].tolist()
                            curr_u_idx = all_w.index(l_row['user_name']) if l_row['user_name'] in all_w else 0
                            new_user = st.selectbox("Mitarbeiter", all_w, index=curr_u_idx)
                            
                            # Проект
                            curr_p_idx = all_projects.index(l_row['project_name']) if l_row['project_name'] in all_projects else 0
                            new_proj = st.selectbox("Projekt", all_projects, index=curr_p_idx)
                            
                            # Леса (текущего проекта)
                            scafs_for_p = get_data(f"SELECT s.number FROM scaffolds s JOIN projects p ON s.project_id = p.id WHERE p.name = ?", (new_proj,))
                            scaf_list = scafs_for_p['number'].tolist() if not scafs_for_p.empty else [l_row['scaffold_number']]
                            try: curr_s_idx = scaf_list.index(l_row['scaffold_number'])
                            except: 
                                scaf_list.append(l_row['scaffold_number'])
                                curr_s_idx = len(scaf_list) - 1
                            new_scaf = st.selectbox("Gerüst", scaf_list, index=curr_s_idx)
                            
                            c_d1, c_d2 = st.columns(2)
                            try: cur_date = pd.to_datetime(l_row['work_date']).date()
                            except: cur_date = date.today()
                            new_date = c_d1.date_input("Datum", cur_date)
                            new_hours = c_d2.number_input("Stunden", value=float(l_row['hours']), step=0.5)
                            
                            if st.form_submit_button("✅ Speichern"):
                                run_query("UPDATE work_logs SET user_name=?, project_name=?, scaffold_number=?, work_date=?, hours=? WHERE id=?", 
                                          (new_user, new_proj, new_scaf, new_date, new_hours, edit_id_log))
                                st.success("Korrigiert!")
                                time.sleep(1)
                                st.rerun()
                        
                        if st.button("🗑️ Löschen", key="del_btn_main"):
                            run_query("DELETE FROM work_logs WHERE id=?", (edit_id_log,))
                            st.warning("Gelöscht!")
                            time.sleep(1)
                            st.rerun()
                    else:
                        st.warning("ID nicht gefunden.")

        # TAB 1: KPI
        with tab1:
            st.subheader("Projekt-Controlling")
            
            if not all_projects:
                st.warning("Keine Projekte vorhanden.")
            else:
                col_kpi_1, col_kpi_2 = st.columns([1, 2])
                selected_project = col_kpi_1.selectbox("1. Projekt auswählen", all_projects)
                date_range_type = col_kpi_2.radio("2. Zeitraum wählen", ["Gesamtzeitraum (Alle Daten)", "Datum auswählen"], horizontal=True)
                start_date, end_date = None, None
                if date_range_type == "Datum auswählen":
                    d1, d2 = col_kpi_2.columns(2)
                    start_date = d1.date_input("Von", date(2024, 1, 1))
                    end_date = d2.date_input("Bis", date.today())

                st.divider()

                scaffolds_data = get_data('SELECT s.volume_m3, s.total_cost FROM scaffolds s JOIN projects p ON s.project_id = p.id WHERE p.name = ?', (selected_project,))
                scaffolds_data = scaffolds_data.fillna(0)
                total_vol = scaffolds_data['volume_m3'].sum()
                total_cost = scaffolds_data['total_cost'].sum()
                avg_price = total_cost / total_vol if total_vol > 0 else 0

                st.markdown(f"**Projektkennzahlen: {selected_project}** (Daten aus Planung)")
                k1, k2, k3 = st.columns(3)
                k1.metric("Gesamtvolumen (Planung)", f"{total_vol:,.0f} m³")
                k2.metric("Gesamtkosten (Planung)", f"{total_cost:,.0f} €")
                k3.metric("Ø Preis / m³", f"{avg_price:.2f} €")
                st.markdown("---")

                query_proj_logs = "SELECT user_name, hours FROM work_logs WHERE project_name = ?"
                params_proj = [selected_project]
                query_all_logs = "SELECT project_name, hours FROM work_logs WHERE 1=1"
                params_all = []
                
                if date_range_type == "Datum auswählen":
                    date_filter = " AND work_date BETWEEN ? AND ?"
                    query_proj_logs += date_filter
                    params_proj.extend([start_date, end_date])
                    query_all_logs += date_filter
                    params_all.extend([start_date, end_date])
                
                df_proj_logs = get_data(query_proj_logs, tuple(params_proj))
                df_all_logs = get_data(query_all_logs, tuple(params_all))
                
                c_chart1, c_chart2 = st.columns(2)
                with c_chart1:
                    st.markdown(f"**Arbeitsstunden: {selected_project}**")
                    if not df_proj_logs.empty:
                        chart_data = df_proj_logs.groupby('user_name')['hours'].sum().reset_index()
                        st.plotly_chart(px.bar(chart_data, x='user_name', y='hours', labels={'hours': 'Stunden', 'user_name': 'Mitarbeiter'}), use_container_width=True)
                    else: st.info("Keine Arbeitsstunden für diesen Zeitraum.")
                
                with c_chart2:
                    st.markdown("**Vergleich aller Projekte (Gesamtstunden)**")
                    if not df_all_logs.empty:
                        pie_data = df_all_logs.groupby('project_name')['hours'].sum().reset_index()
                        st.plotly_chart(px.pie(pie_data, values='hours', names='project_name', hole=0.4), use_container_width=True)
                    else: st.info("Keine Daten im System.")

        # TAB 2: Workers
        with tab2:
            st.subheader("Personal")
            with st.form("aw"):
                n, p = st.text_input("Name"), st.text_input("Position")
                if st.form_submit_button("Hinzufügen"):
                    if n: run_query("INSERT INTO workers (name, position) VALUES (?, ?)", (n, p)); st.rerun()
            st.dataframe(get_data("SELECT * FROM workers"), hide_index=True, use_container_width=True)

        # TAB 3: Projects & Scaffolds
        with tab3:
            st.subheader("Stammdaten")
            c_p, c_s = st.columns(2)
            with c_p:
                st.markdown("### Projekte")
                with st.form("np"):
                    np = st.text_input("Name")
                    if st.form_submit_button("Erstellen"):
                        if np: run_query("INSERT INTO projects (name) VALUES (?)", (np,)); st.rerun()
                st.dataframe(get_data("SELECT * FROM projects"), hide_index=True)

            with c_s:
                st.markdown("### Gerüste (Übersicht)")
                pl = get_data("SELECT id, name FROM projects")
                if not pl.empty:
                    pm = dict(zip(pl['name'], pl['id']))
                    cp = st.selectbox("Projekt:", pl['name'], key="admin_scaf_view")
                    with st.expander("Gerüst manuell hinzufügen (Admin)"):
                        with st.form("ns_admin"):
                            nn = st.text_input("Nummer")
                            nd = st.text_input("Beschreibung")
                            vol = st.number_input("Vol.", min_value=0.0)
                            cost = st.number_input("Kosten", min_value=0.0)
                            if st.form_submit_button("Speichern"):
                                run_query("INSERT INTO scaffolds (project_id, number, description, volume_m3, total_cost) VALUES (?, ?, ?, ?, ?)", (pm[cp], nn, nd, vol, cost))
                                st.rerun()
                    sdf = get_data("SELECT number, description, volume_m3, total_cost FROM scaffolds WHERE project_id=?", (pm[cp],))
                    if not sdf.empty:
                        sdf = sdf.fillna(0)
                        sdf['€ / m³'] = sdf.apply(lambda x: round(x['total_cost'] / x['volume_m3'], 2) if x['volume_m3'] > 0 else 0, axis=1)
                        st.dataframe(sdf, hide_index=True, use_container_width=True)

st.markdown("""<div class="footer"><p>Sergey Romanov, 2025 | Developed for promaintain®</p></div>""", unsafe_allow_html=True)