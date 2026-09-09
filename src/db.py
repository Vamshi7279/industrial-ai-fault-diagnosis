import sqlite3
import os
import datetime

DB_PATH = "industrial_plant.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout=30000;")
    except Exception:
        pass
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Machines Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS machines (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        location TEXT NOT NULL,
        type TEXT NOT NULL,
        status TEXT NOT NULL,
        health_score REAL NOT NULL,
        install_date TEXT NOT NULL,
        last_service_date TEXT NOT NULL,
        operating_hours INTEGER NOT NULL
    );
    """)

    # 2. Components Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS components (
        id TEXT PRIMARY KEY,
        machine_id TEXT NOT NULL,
        name TEXT NOT NULL,
        health_score REAL NOT NULL,
        install_date TEXT NOT NULL,
        service_interval_hours INTEGER NOT NULL,
        recommended_part_no TEXT NOT NULL,
        FOREIGN KEY (machine_id) REFERENCES machines (id)
    );
    """)

    # 3. Spare Parts Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS spare_parts (
        part_number TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        compatible_machine TEXT NOT NULL,
        manufacturer TEXT NOT NULL,
        supplier TEXT NOT NULL,
        stock_qty INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        warranty_months INTEGER NOT NULL,
        lead_time_days INTEGER NOT NULL
    );
    """)

    # 4. Manufacturers Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS manufacturers (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        service_center TEXT NOT NULL,
        contact_email TEXT NOT NULL,
        contact_phone TEXT NOT NULL,
        specialty TEXT NOT NULL
    );
    """)

    # 5. Technicians Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS technicians (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        specialty TEXT NOT NULL,
        shift TEXT NOT NULL,
        status TEXT NOT NULL,
        phone TEXT NOT NULL
    );
    """)

    # 6. Maintenance Tickets Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS maintenance_tickets (
        id TEXT PRIMARY KEY,
        machine_id TEXT NOT NULL,
        component_id TEXT NOT NULL,
        severity TEXT NOT NULL,
        health_score REAL NOT NULL,
        anomaly_score REAL NOT NULL,
        issue_description TEXT NOT NULL,
        recommended_action TEXT NOT NULL,
        assigned_tech_id TEXT,
        status TEXT NOT NULL,
        created_at TEXT NOT NULL,
        scheduled_date TEXT NOT NULL,
        part_number_used TEXT,
        technician_feedback TEXT,
        post_repair_verified INTEGER DEFAULT 0,
        FOREIGN KEY (machine_id) REFERENCES machines (id)
    );
    """)

    # 7. Maintenance History Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS maintenance_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        machine_id TEXT NOT NULL,
        component_name TEXT NOT NULL,
        service_type TEXT NOT NULL,
        service_date TEXT NOT NULL,
        technician_name TEXT NOT NULL,
        notes TEXT NOT NULL,
        FOREIGN KEY (machine_id) REFERENCES machines (id)
    );
    """)

    conn.commit()

    # Seed data if database is empty
    cursor.execute("SELECT COUNT(*) FROM machines;")
    if cursor.fetchone()[0] == 0:
        seed_data(cursor)
        conn.commit()

    conn.close()

def seed_data(cursor):
    print("[DB] Seeding industrial plant database with initial asset records...")

    # Seed Machines
    machines = [
        ("FAN-01", "Primary Exhaust Cooling Fan", "Plant 2 - Assembly Line 4", "fan", "Operating", 94.5, "2024-03-15", "2026-05-10", 4120),
        ("GEARBOX-01", "Heavy Conveyor Drive Gearbox", "Plant 1 - Stamping Bay B", "gearbox", "Operating", 91.0, "2023-11-20", "2026-04-18", 6850),
        ("PUMP-01", "Coolant Circulation Hydraulic Pump", "Plant 3 - Machining Shop 1", "pump", "Operating", 96.2, "2024-06-01", "2026-06-22", 3490),
        ("VALVE-01", "High-Pressure Steam Control Valve", "Plant 2 - Boiler House", "valve", "Operating", 88.7, "2023-08-10", "2026-03-05", 8910)
    ]
    cursor.executemany("INSERT INTO machines VALUES (?,?,?,?,?,?,?,?,?);", machines)

    # Seed Components
    components = [
        ("COMP-FAN-01", "FAN-01", "High-Speed Rotor Bearing Assembly", 94.5, "2024-03-15", 2500, "SKF-6208-2RS"),
        ("COMP-FAN-02", "FAN-01", "Aerodynamic Fan Impeller Blade", 97.0, "2024-03-15", 5000, "FAN-BLD-880"),
        ("COMP-GBX-01", "GEARBOX-01", "Helical Pinion Gear Teeth Assembly", 91.0, "2023-11-20", 4000, "GBX-HEL-402"),
        ("COMP-GBX-02", "GEARBOX-01", "Input Shaft Synthetic Oil Seal", 89.5, "2023-11-20", 2000, "GBX-SEAL-90"),
        ("COMP-PMP-01", "PUMP-01", "Hydraulic Impeller Vane Assembly", 96.2, "2024-06-01", 3000, "PMP-IMP-310"),
        ("COMP-PMP-02", "PUMP-01", "Mechanical Shaft Seal Assembly", 92.8, "2024-06-01", 2000, "PMP-SEAL-44"),
        ("COMP-VLV-01", "VALVE-01", "Hardened Valve Seat & Plunger Assembly", 88.7, "2023-08-10", 3500, "VLV-SET-102"),
        ("COMP-VLV-02", "VALVE-01", "Pneumatic Actuator Diaphragm", 86.0, "2023-08-10", 1800, "VLV-ACT-55")
    ]
    cursor.executemany("INSERT INTO components VALUES (?,?,?,?,?,?,?);", components)

    # Seed Spare Parts
    spare_parts = [
        ("SKF-6208-2RS", "Deep Groove Ball Bearing 40x80x18mm", "fan", "SKF Industrial", "Industrial Automation Ltd", 12, 145.0, 12, 1),
        ("FAN-BLD-880", "Balanced Industrial Aluminum Fan Blade", "fan", "AirFlow Dynamics", "Global HVAC Supplies", 3, 420.0, 24, 3),
        ("GBX-HEL-402", "Helical Pinion Gear 24-Tooth Alloy", "gearbox", "Bosch Rexroth", "DriveSystems Direct", 2, 890.0, 18, 2),
        ("GBX-SEAL-90", "Viton High-Temp Shaft Seal 90mm", "gearbox", "Freudenberg Sealing", "Industrial Automation Ltd", 0, 48.0, 6, 4), # Out of stock intentionally to test supplier routing
        ("PMP-IMP-310", "Stainless Steel Pump Impeller 310mm", "pump", "Grundfos Industrial", "PumpTech Parts", 5, 580.0, 24, 2),
        ("PMP-SEAL-44", "Silicon Carbide Mechanical Seal 44mm", "pump", "EagleBurgmann", "PumpTech Parts", 8, 125.0, 12, 1),
        ("VLV-SET-102", "Stellite Coated Valve Seat 2-Inch", "valve", "Emerson Fisher", "ControlValve Solutions", 4, 310.0, 18, 2),
        ("VLV-ACT-55", "Heavy Duty Rubber Actuator Diaphragm", "valve", "Flowserve Corp", "ControlValve Solutions", 0, 75.0, 12, 5) # Out of stock
    ]
    cursor.executemany("INSERT INTO spare_parts VALUES (?,?,?,?,?,?,?,?,?);", spare_parts)

    # Seed Manufacturers
    manufacturers = [
        ("MFR-SKF", "SKF Industrial Motion & Bearings", "SKF Regional Technical Repair Center", "service@skf-industrial.com", "+1-800-555-0199", "Precision Bearings & Lubrication"),
        ("MFR-REX", "Bosch Rexroth Motion & Gearboxes", "Rexroth Drive & Gearbox Authorized Service Facility", "support@rexroth-drives.com", "+1-800-555-0244", "Heavy Industrial Drives & Helical Gearboxes"),
        ("MFR-GDF", "Grundfos Industrial Pumps", "Grundfos Authorized Hydro Service Network", "tech@grundfos-industrial.com", "+1-800-555-0311", "Industrial Centrifugal & Hydraulic Pumps"),
        ("MFR-EMR", "Emerson Fisher Valve Systems", "Emerson Flow Control Field Service Division", "service@emerson-fisher.com", "+1-800-555-0488", "High-Pressure Control Valves & Pneumatics")
    ]
    cursor.executemany("INSERT INTO manufacturers VALUES (?,?,?,?,?,?);", manufacturers)

    # Seed Technicians
    technicians = [
        ("TECH-101", "Rajesh Kumar", "Vibration & Acoustic Diagnostics Specialist", "Day Shift (08:00 - 16:00)", "Available", "+91-98765-43210"),
        ("TECH-102", "Sarah Jenkins", "Heavy Mechanical Drive & Gearbox Technician", "Day Shift (08:00 - 16:00)", "Available", "+1-555-014-9922"),
        ("TECH-103", "Vikram Patel", "Hydraulic Pumps & Fluid Dynamics Engineer", "Evening Shift (16:00 - 00:00)", "Available", "+91-98123-45678"),
        ("TECH-104", "Marcus Vance", "High-Pressure Valve & Pneumatic Systems Specialist", "Day Shift (08:00 - 16:00)", "Available", "+1-555-018-7733")
    ]
    cursor.executemany("INSERT INTO technicians VALUES (?,?,?,?,?,?);", technicians)

    # Seed Maintenance History
    history = [
        ("FAN-01", "High-Speed Rotor Bearing Assembly", "Service", "2026-05-10", "Rajesh Kumar", "Re-greased bearing housing with synthetic lithium grease. Vibration amplitude dropped by 18%."),
        ("GEARBOX-01", "Helical Pinion Gear Teeth Assembly", "Inspection", "2026-04-18", "Sarah Jenkins", "Borescope inspection revealed minor gear tooth surface smoothing. Oil sample clean."),
        ("PUMP-01", "Mechanical Shaft Seal Assembly", "Replacement", "2026-06-22", "Vikram Patel", "Replaced worn mechanical seal #PMP-SEAL-44. Hydrostatic test passed at 15 bar."),
        ("VALVE-01", "Hardened Valve Seat & Plunger Assembly", "Service", "2026-03-05", "Marcus Vance", "Cleaned steam scale buildup from plunger guide. Seat lapped and re-calibrated.")
    ]
    cursor.executemany("INSERT INTO maintenance_history (machine_id, component_name, service_type, service_date, technician_name, notes) VALUES (?,?,?,?,?,?);", history)

    # Seed Initial Demo Ticket
    tickets = [
        ("WO-2026-8801", "GEARBOX-01", "COMP-GBX-01", "High", 74.5, 942.50, "Micro-pitting detected on Helical Pinion Gear teeth.", "Inspect pinion gear teeth, replace oil seal, and schedule replacement.", "TECH-102", "In Progress", "2026-07-28 10:15:00", "2026-07-30", "GBX-HEL-402", "Inspected gear casing. Part is on standby.", 0)
    ]
    cursor.executemany("INSERT INTO maintenance_tickets VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);", tickets)

# Helper DB Access API

def get_all_machines():
    init_db()
    conn = get_connection()
    res = conn.execute("SELECT * FROM machines").fetchall()
    conn.close()
    return [dict(r) for r in res]

def get_machine(machine_id):
    init_db()
    conn = get_connection()
    res = conn.execute("SELECT * FROM machines WHERE id = ?", (machine_id,)).fetchone()
    conn.close()
    return dict(res) if res else None

def get_machine_by_type(machine_type):
    init_db()
    conn = get_connection()
    res = conn.execute("SELECT * FROM machines WHERE type = ?", (machine_type.lower(),)).fetchone()
    conn.close()
    return dict(res) if res else None

def get_components_for_machine(machine_id):
    init_db()
    conn = get_connection()
    res = conn.execute("SELECT * FROM components WHERE machine_id = ?", (machine_id,)).fetchall()
    conn.close()
    return [dict(r) for r in res]

def get_spare_part(part_number):
    init_db()
    conn = get_connection()
    res = conn.execute("SELECT * FROM spare_parts WHERE part_number = ?", (part_number,)).fetchone()
    conn.close()
    return dict(res) if res else None

def get_all_spare_parts():
    init_db()
    conn = get_connection()
    res = conn.execute("SELECT * FROM spare_parts").fetchall()
    conn.close()
    return [dict(r) for r in res]

def get_manufacturer_for_machine(machine_type):
    init_db()
    mapping = {
        "fan": "MFR-SKF",
        "gearbox": "MFR-REX",
        "pump": "MFR-GDF",
        "valve": "MFR-EMR"
    }
    mfr_id = mapping.get(machine_type.lower(), "MFR-SKF")
    conn = get_connection()
    res = conn.execute("SELECT * FROM manufacturers WHERE id = ?", (mfr_id,)).fetchone()
    conn.close()
    return dict(res) if res else None

def get_all_manufacturers():
    init_db()
    conn = get_connection()
    res = conn.execute("SELECT * FROM manufacturers").fetchall()
    conn.close()
    return [dict(r) for r in res]

def get_all_technicians():
    init_db()
    conn = get_connection()
    res = conn.execute("SELECT * FROM technicians").fetchall()
    conn.close()
    return [dict(r) for r in res]

def get_tickets():
    init_db()
    conn = get_connection()
    res = conn.execute("SELECT t.*, m.name as machine_name, tech.name as tech_name FROM maintenance_tickets t JOIN machines m ON t.machine_id = m.id LEFT JOIN technicians tech ON t.assigned_tech_id = tech.id ORDER BY t.created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in res]

def create_ticket(ticket_id, machine_id, component_id, severity, health_score, anomaly_score, issue_desc, rec_action, assigned_tech_id=None, scheduled_date=None, part_no=None):
    init_db()
    conn = get_connection()
    
    # Check if an active ticket already exists for this machine
    existing = conn.execute("SELECT id FROM maintenance_tickets WHERE machine_id = ? AND status IN ('Open', 'In Progress')", (machine_id,)).fetchone()
    if existing:
        conn.close()
        return existing["id"]

    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not scheduled_date:
        scheduled_date = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        
    conn.execute("""
    INSERT INTO maintenance_tickets (id, machine_id, component_id, severity, health_score, anomaly_score, issue_description, recommended_action, assigned_tech_id, status, created_at, scheduled_date, part_number_used, technician_feedback, post_repair_verified)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Open', ?, ?, ?, '', 0)
    """, (ticket_id, machine_id, component_id, severity, health_score, anomaly_score, issue_desc, rec_action, assigned_tech_id, now_str, scheduled_date, part_no))
    
    # Update machine status
    conn.execute("UPDATE machines SET status = ?, health_score = ? WHERE id = ?", (f"Warning ({severity})", health_score, machine_id))
    conn.commit()
    conn.close()
    return ticket_id

def update_ticket_status(ticket_id, status, feedback=None, verified=None):
    init_db()
    conn = get_connection()
    if feedback is not None and verified is not None:
        conn.execute("UPDATE maintenance_tickets SET status = ?, technician_feedback = ?, post_repair_verified = ? WHERE id = ?", (status, feedback, verified, ticket_id))
    elif feedback is not None:
        conn.execute("UPDATE maintenance_tickets SET status = ?, technician_feedback = ? WHERE id = ?", (status, feedback, ticket_id))
    else:
        conn.execute("UPDATE maintenance_tickets SET status = ? WHERE id = ?", (status, ticket_id))
        
    # If verified, restore machine health to 98%
    if verified == 1:
        ticket = conn.execute("SELECT machine_id FROM maintenance_tickets WHERE id = ?", (ticket_id,)).fetchone()
        if ticket:
            conn.execute("UPDATE machines SET status = 'Operating', health_score = 98.5, last_service_date = ? WHERE id = ?", (datetime.date.today().strftime("%Y-%m-%d"), ticket["machine_id"]))
            
    conn.commit()
    conn.close()

def get_maintenance_history(machine_id):
    init_db()
    conn = get_connection()
    res = conn.execute("SELECT * FROM maintenance_history WHERE machine_id = ? ORDER BY service_date DESC", (machine_id,)).fetchall()
    conn.close()
    return [dict(r) for r in res]

def add_maintenance_history(machine_id, component_name, service_type, technician_name, notes):
    init_db()
    conn = get_connection()
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    conn.execute("""
    INSERT INTO maintenance_history (machine_id, component_name, service_type, service_date, technician_name, notes)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (machine_id, component_name, service_type, today_str, technician_name, notes))
    conn.commit()
    conn.close()
