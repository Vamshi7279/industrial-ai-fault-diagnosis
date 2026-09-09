import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey, Enum, JSON
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(String(50), primary_key=True) # admin, floor_manager, maintenance_manager, technician
    name = Column(String(100), nullable=False)
    permissions = Column(Text, nullable=False) # JSON array string of permissions
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(50), primary_key=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role_id = Column(String(50), ForeignKey("roles.id"), nullable=False)
    full_name = Column(String(150), nullable=False)
    phone = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class Manufacturer(Base):
    __tablename__ = "manufacturers"
    
    id = Column(String(50), primary_key=True)
    name = Column(String(150), nullable=False)
    service_center = Column(String(200), nullable=False)
    contact_email = Column(String(255), nullable=False)
    contact_phone = Column(String(50), nullable=False)
    specialty = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Supplier(Base):
    __tablename__ = "suppliers"
    
    id = Column(String(50), primary_key=True)
    name = Column(String(150), nullable=False)
    contact_person = Column(String(150), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=False)
    address = Column(Text, nullable=True)
    rating = Column(Float, default=4.8)

class Machine(Base):
    __tablename__ = "machines"
    
    id = Column(String(50), primary_key=True) # e.g. FAN-01, GEARBOX-01, PUMP-01, VALVE-01
    name = Column(String(150), nullable=False)
    location = Column(String(200), nullable=False)
    type = Column(String(50), nullable=False, index=True) # fan, gearbox, pump, valve
    status = Column(String(50), nullable=False, default="Operating")
    health_score = Column(Float, nullable=False, default=98.5)
    risk_level = Column(String(20), nullable=False, default="Low") # Low, Medium, High, Critical
    install_date = Column(String(20), nullable=False)
    last_service_date = Column(String(20), nullable=False)
    operating_hours = Column(Integer, nullable=False, default=0)
    manufacturer_id = Column(String(50), ForeignKey("manufacturers.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class MachineComponent(Base):
    __tablename__ = "machine_components"
    
    id = Column(String(50), primary_key=True)
    machine_id = Column(String(50), ForeignKey("machines.id"), nullable=False, index=True)
    name = Column(String(150), nullable=False)
    health_score = Column(Float, nullable=False, default=95.0)
    install_date = Column(String(20), nullable=False)
    service_interval_hours = Column(Integer, nullable=False, default=1500)
    recommended_part_no = Column(String(100), nullable=False)

class MachineHealth(Base):
    __tablename__ = "machine_health"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    machine_id = Column(String(50), ForeignKey("machines.id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    health_score = Column(Float, nullable=False)
    risk_score = Column(Float, nullable=False)
    rul_hours = Column(Integer, nullable=False) # Estimated remaining hours before maintenance recommended
    failure_risk = Column(String(50), nullable=False)
    action_recommendation = Column(String(100), nullable=False)

class AudioRecord(Base):
    __tablename__ = "audio_records"
    
    id = Column(String(100), primary_key=True)
    machine_id = Column(String(50), ForeignKey("machines.id"), nullable=False, index=True)
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    duration_sec = Column(Float, default=10.0)
    sample_rate = Column(Integer, default=16000)
    recorded_at = Column(DateTime, default=datetime.datetime.utcnow)

class AnomalyEvent(Base):
    __tablename__ = "anomaly_events"
    
    id = Column(String(100), primary_key=True)
    machine_id = Column(String(50), ForeignKey("machines.id"), nullable=False, index=True)
    audio_record_id = Column(String(100), ForeignKey("audio_records.id"), nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    model_used = Column(String(100), nullable=False)
    reconstruction_error = Column(Float, nullable=False)
    threshold = Column(Float, nullable=False)
    anomaly_score = Column(Float, nullable=False)
    is_anomaly = Column(Boolean, nullable=False, default=False)

class FaultDiagnosis(Base):
    __tablename__ = "fault_diagnoses"
    
    id = Column(String(100), primary_key=True)
    anomaly_event_id = Column(String(100), ForeignKey("anomaly_events.id"), nullable=False)
    machine_id = Column(String(50), ForeignKey("machines.id"), nullable=False)
    component_id = Column(String(100), nullable=True)
    severity = Column(String(20), nullable=False) # Normal, Low, Medium, High, Critical
    confidence = Column(Float, nullable=False)
    detected_issue = Column(Text, nullable=False)
    evidence_summary = Column(Text, nullable=True)
    status = Column(String(50), default="Detected Anomaly") # Detected Anomaly, Possible Fault, Confirmed Fault

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(String(100), primary_key=True)
    fault_diagnosis_id = Column(String(100), ForeignKey("fault_diagnoses.id"), nullable=True)
    machine_id = Column(String(50), ForeignKey("machines.id"), nullable=False, index=True)
    severity = Column(String(20), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(String(50), default="Active") # Active, Acknowledged, Resolved
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    acknowledged_at = Column(DateTime, nullable=True)
    acknowledged_by = Column(String(50), ForeignKey("users.id"), nullable=True)

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(String(100), primary_key=True)
    alert_id = Column(String(100), ForeignKey("alerts.id"), nullable=True)
    channel = Column(String(50), nullable=False) # telegram, whatsapp, email, web_dashboard
    recipient = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(String(50), default="Pending") # Pending, Sent, Delivered, Failed
    error_message = Column(Text, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    retry_count = Column(Integer, default=0)

class MaintenanceTicket(Base):
    __tablename__ = "maintenance_tickets"
    
    id = Column(String(50), primary_key=True) # e.g. WO-2026-9833
    machine_id = Column(String(50), ForeignKey("machines.id"), nullable=False, index=True)
    component_id = Column(String(150), nullable=False)
    severity = Column(String(20), nullable=False)
    health_score = Column(Float, nullable=False)
    anomaly_score = Column(Float, nullable=False)
    issue_description = Column(Text, nullable=False)
    recommended_action = Column(String(100), nullable=False)
    assigned_tech_id = Column(String(50), nullable=True)
    # Lifecycle: OPEN -> DIAGNOSING -> SCHEDULED -> PART_REQUIRED -> PART_ORDERED -> TECHNICIAN_ASSIGNED -> UNDER_REPAIR -> COMPLETED -> VERIFICATION -> CLOSED
    status = Column(String(50), nullable=False, default="OPEN", index=True)
    created_at = Column(String(50), nullable=False)
    scheduled_date = Column(String(50), nullable=False)
    part_number_used = Column(String(100), nullable=True)
    technician_feedback = Column(Text, default="")
    post_repair_verified = Column(Integer, default=0)
    human_approved = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class MaintenanceHistory(Base):
    __tablename__ = "maintenance_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(String(50), nullable=True)
    machine_id = Column(String(50), ForeignKey("machines.id"), nullable=False, index=True)
    component_name = Column(String(150), nullable=False)
    service_date = Column(String(50), nullable=False)
    service_type = Column(String(100), nullable=False)
    technician_name = Column(String(150), nullable=False)
    notes = Column(Text, nullable=True)
    post_repair_verified = Column(Integer, default=1)

class Technician(Base):
    __tablename__ = "technicians"
    
    id = Column(String(50), primary_key=True) # TECH-101
    user_id = Column(String(50), ForeignKey("users.id"), nullable=True)
    name = Column(String(150), nullable=False)
    specialty = Column(String(150), nullable=False)
    shift = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False, default="Available")
    phone = Column(String(50), nullable=False)

class TechnicianSkill(Base):
    __tablename__ = "technician_skills"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    technician_id = Column(String(50), ForeignKey("technicians.id"), nullable=False)
    skill_name = Column(String(100), nullable=False)
    certification_level = Column(String(50), default="Level 2 Certified")

class SparePart(Base):
    __tablename__ = "spare_parts"
    
    part_number = Column(String(100), primary_key=True)
    name = Column(String(150), nullable=False)
    compatible_machine = Column(String(50), nullable=False)
    component_name = Column(String(150), nullable=True)
    manufacturer = Column(String(150), nullable=False)
    supplier = Column(String(150), nullable=False)
    stock_qty = Column(Integer, nullable=False, default=10)
    min_stock_qty = Column(Integer, nullable=False, default=2)
    unit_price = Column(Float, nullable=False, default=150.0)
    warranty_months = Column(Integer, nullable=False, default=12)
    lead_time_days = Column(Integer, nullable=False, default=2)

class Inventory(Base):
    __tablename__ = "inventory"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    part_number = Column(String(100), ForeignKey("spare_parts.part_number"), nullable=False)
    warehouse_location = Column(String(100), default="Warehouse Bin 4A")
    bin_number = Column(String(50), default="B-4A")
    quantity_on_hand = Column(Integer, nullable=False, default=10)
    last_counted = Column(DateTime, default=datetime.datetime.utcnow)

class ServiceRequest(Base):
    __tablename__ = "service_requests"
    
    id = Column(String(50), primary_key=True) # RFP-1001
    ticket_id = Column(String(50), nullable=True)
    machine_id = Column(String(50), ForeignKey("machines.id"), nullable=False)
    manufacturer_id = Column(String(50), ForeignKey("manufacturers.id"), nullable=True)
    severity = Column(String(20), nullable=False)
    rfp_text = Column(Text, nullable=False)
    status = Column(String(50), default="REQUESTED") # REQUESTED -> SENT -> ACKNOWLEDGED -> IN_PROGRESS -> RESOLVED -> CLOSED
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    approved_by = Column(String(50), ForeignKey("users.id"), nullable=True)
    sent_at = Column(DateTime, nullable=True)

class ServiceHistory(Base):
    __tablename__ = "service_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    machine_id = Column(String(50), ForeignKey("machines.id"), nullable=False)
    manufacturer_id = Column(String(50), ForeignKey("manufacturers.id"), nullable=False)
    event_date = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    cost = Column(Float, default=0.0)

class AIConversation(Base):
    __tablename__ = "ai_conversations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), nullable=True)
    machine_id = Column(String(50), nullable=True)
    prompt = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    sources_json = Column(Text, nullable=True) # JSON array of RAG evidence sources
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), nullable=True)
    action = Column(String(100), nullable=False) # e.g. TICKET_STATUS_UPDATE, RFP_APPROVED, TECH_ASSIGNED
    entity_type = Column(String(100), nullable=False) # e.g. MaintenanceTicket, ServiceRequest
    entity_id = Column(String(100), nullable=False)
    previous_state = Column(Text, nullable=True)
    new_state = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
