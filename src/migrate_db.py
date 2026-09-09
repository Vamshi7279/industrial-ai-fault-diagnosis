import datetime
from sqlalchemy.orm import Session
from src.database import engine, SessionLocal, init_db
from src.models_orm import (
    Base, Role, User, Machine, MachineComponent, SparePart, Supplier,
    Manufacturer, Technician, MaintenanceTicket, MaintenanceHistory,
    AuditLog
)
from src.security import hash_password

import sqlite3

def patch_sqlite_columns():
    conn = sqlite3.connect("industrial_plant.db")
    cursor = conn.cursor()
    
    # Check manufacturers created_at
    cursor.execute("PRAGMA table_info(manufacturers);")
    cols = [r[1] for r in cursor.fetchall()]
    if "created_at" not in cols:
        cursor.execute("ALTER TABLE manufacturers ADD COLUMN created_at DATETIME;")
        
    # Check machines risk_level, manufacturer_id, created_at, updated_at
    cursor.execute("PRAGMA table_info(machines);")
    m_cols = [r[1] for r in cursor.fetchall()]
    if "risk_level" not in m_cols:
        cursor.execute("ALTER TABLE machines ADD COLUMN risk_level TEXT DEFAULT 'Low';")
    if "manufacturer_id" not in m_cols:
        cursor.execute("ALTER TABLE machines ADD COLUMN manufacturer_id TEXT;")
    if "created_at" not in m_cols:
        cursor.execute("ALTER TABLE machines ADD COLUMN created_at DATETIME;")
    if "updated_at" not in m_cols:
        cursor.execute("ALTER TABLE machines ADD COLUMN updated_at DATETIME;")
        
    # Check maintenance_tickets human_approved, updated_at
    cursor.execute("PRAGMA table_info(maintenance_tickets);")
    t_cols = [r[1] for r in cursor.fetchall()]
    if "human_approved" not in t_cols:
        cursor.execute("ALTER TABLE maintenance_tickets ADD COLUMN human_approved INTEGER DEFAULT 0;")
    if "updated_at" not in t_cols:
        cursor.execute("ALTER TABLE maintenance_tickets ADD COLUMN updated_at DATETIME;")
        
    # Check technicians user_id
    cursor.execute("PRAGMA table_info(technicians);")
    tech_cols = [r[1] for r in cursor.fetchall()]
    if "user_id" not in tech_cols:
        cursor.execute("ALTER TABLE technicians ADD COLUMN user_id TEXT;")
        
    # Check spare_parts component_name, min_stock_qty
    cursor.execute("PRAGMA table_info(spare_parts);")
    sp_cols = [r[1] for r in cursor.fetchall()]
    if "component_name" not in sp_cols:
        cursor.execute("ALTER TABLE spare_parts ADD COLUMN component_name TEXT;")
    if "min_stock_qty" not in sp_cols:
        cursor.execute("ALTER TABLE spare_parts ADD COLUMN min_stock_qty INTEGER DEFAULT 2;")

    # Check maintenance_history ticket_id, post_repair_verified
    cursor.execute("PRAGMA table_info(maintenance_history);")
    mh_cols = [r[1] for r in cursor.fetchall()]
    if "ticket_id" not in mh_cols:
        cursor.execute("ALTER TABLE maintenance_history ADD COLUMN ticket_id TEXT;")
    if "post_repair_verified" not in mh_cols:
        cursor.execute("ALTER TABLE maintenance_history ADD COLUMN post_repair_verified INTEGER DEFAULT 0;")

    conn.commit()
    conn.close()

def seed_database():
    patch_sqlite_columns()
    init_db()
    db: Session = SessionLocal()
    
    try:
        # 1. Seed Roles
        if db.query(Role).count() == 0:
            roles_data = [
                Role(id="admin", name="System Administrator", permissions='["all"]'),
                Role(id="floor_manager", name="Plant Floor Manager", permissions='["view_dashboard", "view_telemetry", "view_alerts", "chat_ai", "view_reports"]'),
                Role(id="maintenance_manager", name="Maintenance Operations Manager", permissions='["view_dashboard", "manage_tickets", "assign_techs", "generate_rfp", "parts_inventory", "chat_ai"]'),
                Role(id="technician", name="Certified Maintenance Specialist", permissions='["view_tickets", "update_tickets", "verify_repairs", "view_parts"]')
            ]
            db.add_all(roles_data)
            db.commit()
            print("[Migrate] Roles seeded successfully.")
            
        # 2. Seed Default Users
        if db.query(User).count() == 0:
            users_data = [
                User(id="USR-101", username="admin", email="admin@plant.com", hashed_password=hash_password("admin123"), role_id="admin", full_name="Plant System Administrator"),
                User(id="USR-102", username="floor_manager", email="manager@plant.com", hashed_password=hash_password("manager123"), role_id="floor_manager", full_name="Vikram Sharma"),
                User(id="USR-103", username="maint_mgr", email="maint@plant.com", hashed_password=hash_password("maint123"), role_id="maintenance_manager", full_name="Priya Nair"),
                User(id="USR-104", username="technician", email="tech@plant.com", hashed_password=hash_password("tech123"), role_id="technician", full_name="Rajesh Kumar")
            ]
            db.add_all(users_data)
            db.commit()
            print("[Migrate] Users seeded successfully.")

        # 3. Seed Manufacturers
        if db.query(Manufacturer).count() == 0:
            mfrs = [
                Manufacturer(id="MFR-SKF", name="SKF Group Industrial Systems", service_center="SKF North America Service Center", contact_email="support@skf-industrial.com", contact_phone="+1-800-555-7531", specialty="High-Speed Bearing Units & Precision Rotors"),
                Manufacturer(id="MFR-REXROTH", name="Bosch Rexroth Drive Systems", service_center="Bosch Rexroth Global Service Hub", contact_email="service@boschrexroth.com", contact_phone="+1-800-555-9821", specialty="Industrial Gearboxes & Transmission Systems"),
                Manufacturer(id="MFR-GRUNDFOS", name="Grundfos Industrial Pumps", service_center="Grundfos Technical Support Center", contact_email="repairs@grundfos-pumps.com", contact_phone="+1-800-555-3412", specialty="Fluid Circulation & Cavitation Impellers"),
                Manufacturer(id="MFR-FISHER", name="Emerson Fisher Process Controls", service_center="Emerson Valve Calibration Facility", contact_email="support@emersonfisher.com", contact_phone="+1-800-555-6600", specialty="High-Pressure Steam Control Valves")
            ]
            db.add_all(mfrs)
            db.commit()
            print("[Migrate] Manufacturers seeded successfully.")

        # 4. Seed Suppliers
        if db.query(Supplier).count() == 0:
            suppliers = [
                Supplier(id="SUP-01", name="SKF Bearings Corp", contact_person="John Davis", email="sales@skf.com", phone="+1-800-555-1111", address="100 Bearing Way, PA", rating=4.9),
                Supplier(id="SUP-02", name="Bosch Rexroth Systems", contact_person="Hans Mueller", email="parts@boschrexroth.com", phone="+1-800-555-2222", address="500 Gear Drive, IL", rating=4.8),
                Supplier(id="SUP-03", name="Grundfos Pumps Inc", contact_person="Sarah Jenkins", email="spares@grundfos.com", phone="+1-800-555-3333", address="200 Pump Plaza, TX", rating=4.7),
                Supplier(id="SUP-04", name="Emerson Fisher Controls", contact_person="David Miller", email="valves@emerson.com", phone="+1-800-555-4444", address="300 Valve St, IA", rating=4.9)
            ]
            db.add_all(suppliers)
            db.commit()
            print("[Migrate] Suppliers seeded successfully.")

        # 5. Seed Machines
        if db.query(Machine).count() == 0:
            machines = [
                Machine(id="FAN-01", name="Primary Exhaust Cooling Fan", location="Plant 1 - Line Assembly 4", type="fan", status="Operating", health_score=95.6, risk_level="Low", install_date="2022-03-15", last_service_date="2026-01-10", operating_hours=14250, manufacturer_id="MFR-SKF"),
                Machine(id="GEARBOX-01", name="Conveyor Drive Gearbox Assembly", location="Plant 1 - Heavy Conveyor 2", type="gearbox", status="Operating", health_score=92.1, risk_level="Low", install_date="2021-06-20", last_service_date="2025-11-05", operating_hours=18900, manufacturer_id="MFR-REXROTH"),
                Machine(id="PUMP-01", name="Hydraulic Fluid Circulation Pump", location="Plant 3 - Hydraulic Bay 1", type="pump", status="Operating", health_score=97.4, risk_level="Low", install_date="2023-01-12", last_service_date="2026-02-18", operating_hours=11400, manufacturer_id="MFR-GRUNDFOS"),
                Machine(id="VALVE-01", name="High-Pressure Steam Control Valve", location="Plant 2 - Boiler House", type="valve", status="Operating", health_score=98.7, risk_level="Low", install_date="2023-08-10", last_service_date="2026-03-05", operating_hours=8910, manufacturer_id="MFR-FISHER")
            ]
            db.add_all(machines)
            db.commit()
            print("[Migrate] Machines seeded successfully.")

        # 6. Seed Machine Components
        if db.query(MachineComponent).count() == 0:
            components = [
                MachineComponent(id="CMP-FAN-01", machine_id="FAN-01", name="High-Speed Rotor Bearing Assembly", health_score=95.6, install_date="2022-03-15", service_interval_hours=1500, recommended_part_no="SKF-6208-2RS"),
                MachineComponent(id="CMP-FAN-02", machine_id="FAN-01", name="Aerodynamic Fan Impeller Blade", health_score=96.0, install_date="2022-03-15", service_interval_hours=3000, recommended_part_no="SKF-BLD-99"),
                MachineComponent(id="CMP-GBX-01", machine_id="GEARBOX-01", name="Helical Pinion Gear Teeth Assembly", health_score=92.1, install_date="2021-06-20", service_interval_hours=2000, recommended_part_no="BR-GEAR-410"),
                MachineComponent(id="CMP-PMP-01", machine_id="PUMP-01", name="Hydraulic Impeller Vane Assembly", health_score=97.4, install_date="2023-01-12", service_interval_hours=1800, recommended_part_no="GF-IMP-88"),
                MachineComponent(id="CMP-VLV-01", machine_id="VALVE-01", name="Hardened Valve Seat & Plunger Assembly", health_score=98.7, install_date="2023-08-10", service_interval_hours=2500, recommended_part_no="VLV-SET-102")
            ]
            db.add_all(components)
            db.commit()
            print("[Migrate] Components seeded successfully.")

        # 7. Seed Technicians
        if db.query(Technician).count() == 0:
            techs = [
                Technician(id="TECH-101", user_id="USR-104", name="Rajesh Kumar", specialty="Vibration & Rotor Dynamic Specialist", shift="Morning (06:00 - 14:00)", status="Available", phone="+91 98765 43210"),
                Technician(id="TECH-102", name="Suresh Patel", specialty="Mechanical Drive & Gearing Expert", shift="Evening (14:00 - 22:00)", status="Available", phone="+91 98765 43211"),
                Technician(id="TECH-103", name="Anita Sharma", specialty="Hydraulic & Seal Systems Tech", shift="Morning (06:00 - 14:00)", status="Available", phone="+91 98765 43212"),
                Technician(id="TECH-104", name="Vikram Singh", specialty="Pneumatic Control & Valve Calibrator", shift="Night (22:00 - 06:00)", status="Available", phone="+91 98765 43213")
            ]
            db.add_all(techs)
            db.commit()
            print("[Migrate] Technicians seeded successfully.")

        # 8. Seed Spare Parts
        if db.query(SparePart).count() == 0:
            parts = [
                SparePart(part_number="SKF-6208-2RS", name="Deep Groove Ball Bearing", compatible_machine="fan", component_name="Rotor Bearing Assembly", manufacturer="SKF Group", supplier="SKF Bearings Corp", stock_qty=14, min_stock_qty=4, unit_price=145.00, warranty_months=24, lead_time_days=2),
                SparePart(part_number="BR-GEAR-410", name="Helical Pinion Gear Set", compatible_machine="gearbox", component_name="Pinion Gear Assembly", manufacturer="Bosch Rexroth", supplier="Bosch Rexroth Systems", stock_qty=4, min_stock_qty=2, unit_price=850.00, warranty_months=36, lead_time_days=5),
                SparePart(part_number="GF-IMP-88", name="Stainless Steel Impeller Kit", compatible_machine="pump", component_name="Impeller Vane Assembly", manufacturer="Grundfos", supplier="Grundfos Pumps Inc", stock_qty=8, min_stock_qty=2, unit_price=320.00, warranty_months=18, lead_time_days=3),
                SparePart(part_number="VLV-SET-102", name="Hardened Seat & Plunger Set", compatible_machine="valve", component_name="Valve Seat & Plunger Assembly", manufacturer="Emerson Fisher", supplier="Emerson Fisher Controls", stock_qty=6, min_stock_qty=2, unit_price=275.00, warranty_months=12, lead_time_days=2)
            ]
            db.add_all(parts)
            db.commit()
            print("[Migrate] Spare Parts seeded successfully.")

        # 9. Seed Initial Maintenance Tickets
        if db.query(MaintenanceTicket).count() == 0:
            tickets = [
                MaintenanceTicket(
                    id="WO-2026-9833",
                    machine_id="VALVE-01",
                    component_id="Hardened Valve Seat & Plunger Assembly",
                    severity="Normal",
                    health_score=98.7,
                    anomaly_score=0.76,
                    issue_description="Standard operating acoustic baseline.",
                    recommended_action="Monitor",
                    assigned_tech_id="TECH-101",
                    status="OPEN",
                    created_at=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    scheduled_date=(datetime.date.today() + datetime.timedelta(days=7)).strftime("%Y-%m-%d"),
                    part_number_used="VLV-SET-102",
                    human_approved=False
                )
            ]
            db.add_all(tickets)
            db.commit()
            print("[Migrate] Maintenance Tickets seeded successfully.")

        # 10. Audit Log Initial Entry
        if db.query(AuditLog).count() == 0:
            log = AuditLog(
                user_id="USR-101",
                action="SYSTEM_INIT",
                entity_type="System",
                entity_id="SYS-001",
                new_state="Database successfully migrated and initialized to ORM schema.",
                timestamp=datetime.datetime.utcnow()
            )
            db.add(log)
            db.commit()
            print("[Migrate] System init audit log recorded.")

    except Exception as e:
        db.rollback()
        print(f"[Migrate Error] Seed transaction failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
