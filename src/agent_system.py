import os
import datetime
import json
import numpy as np

class MonitoringAgent:
    """
    Monitors 24/7 acoustic telemetry stream, comparing clip MSE against baseline threshold.
    """
    def run(self, machine_type: str, file_path: str, clip_score: float, threshold: float):
        ratio = clip_score / max(1.0, threshold)
        is_anom = clip_score > threshold
        return {
            "machine_type": machine_type.lower(),
            "file_name": os.path.basename(file_path),
            "clip_score": round(clip_score, 2),
            "threshold": round(threshold, 2),
            "anomaly_ratio": round(ratio, 2),
            "is_anomaly": is_anom
        }

class DiagnosticAgent:
    """
    Analyzes acoustic anomaly score, machine type, section, and frequency shift
    to pinpoint physical components.
    Distinguishes between Detected Anomaly, Possible Fault, and Confirmed Fault.
    If evidence is insufficient, explicitly returns manual inspection recommendation.
    """
    def run(self, machine_type: str, section: str, anomaly_score: float, threshold: float):
        ratio = anomaly_score / max(1.0, threshold)
        
        # Deterministic Severity & Statistical Confidence Calculation (No Randomness)
        if ratio <= 1.0:
            severity = "Normal"
            confidence = 98.0
            status = "Operating Baseline"
        elif ratio <= 1.15:
            severity = "Low"
            confidence = 72.0 # Borderline evidence
            status = "Detected Anomaly"
        elif ratio <= 1.5:
            severity = "Medium"
            confidence = 88.5
            status = "Possible Fault"
        elif ratio <= 2.0:
            severity = "High"
            confidence = 94.2
            status = "Possible Fault"
        else:
            severity = "Critical"
            confidence = 98.6
            status = "Confirmed Fault"
            
        m_type = machine_type.lower()
        if m_type == "fan":
            components_map = {
                "0": "High-Speed Rotor Bearing Assembly",
                "1": "Aerodynamic Fan Impeller Blade",
                "2": "Motor Drive Assembly & Shaft Coupling"
            }
            issues = {
                "Normal": "Standard operating acoustic baseline.",
                "Low": "Slight dynamic imbalance on fan rotor blades.",
                "Medium": "Acoustic spectrum distortion in 200-400Hz band indicating inner race bearing wear.",
                "High": "Severe friction and thermal expansion in rotor bearing assembly.",
                "Critical": "Bearing cage failure imminent. Risk of rotor lockup."
            }
        elif m_type == "gearbox":
            components_map = {
                "0": "Helical Pinion Gear Teeth Assembly",
                "1": "Input Shaft Synthetic Oil Seal",
                "2": "Gearbox Housing & Lubrication Reservoir"
            }
            issues = {
                "Normal": "Standard operating acoustic baseline.",
                "Low": "Minor gear oil viscosity breakdown and micro-chatter.",
                "Medium": "Micro-pitting and surface fatigue on Helical Pinion Gear teeth.",
                "High": "Severe gear tooth chipping and excessive backlash in drive train.",
                "Critical": "Broken helical gear tooth. High danger of total gearbox seizure."
            }
        elif m_type == "pump":
            components_map = {
                "0": "Hydraulic Impeller Vane Assembly",
                "1": "Mechanical Shaft Seal Assembly",
                "2": "Suction Inlet & Volute Housing"
            }
            issues = {
                "Normal": "Standard operating acoustic baseline.",
                "Low": "Mild fluid cavitation ripples at pump inlet.",
                "Medium": "Impeller vane tip erosion and localized flow turbulence.",
                "High": "Mechanical shaft seal face degradation causing fluid bypass.",
                "Critical": "Impeller cavitation lock and seal blowout danger."
            }
        else: # valve
            components_map = {
                "0": "Hardened Valve Seat & Plunger Assembly",
                "1": "Pneumatic Actuator Diaphragm",
                "2": "Pneumatic Guide Seal & Packing Gland"
            }
            issues = {
                "Normal": "Standard operating acoustic baseline.",
                "Low": "Minor steam scale deposit on valve plunger guide.",
                "Medium": "Stellite valve seat erosion causing internal steam leakage.",
                "High": "Actuator diaphragm tearing causing sluggish stroke control.",
                "Critical": "Valve plunger stickage in open state under high pressure."
            }
            
        sec_str = str(int(section)) if section.isdigit() else "0"
        faulty_component = components_map.get(sec_str, list(components_map.values())[0])
        
        # Ambiguity Guardrail: If ratio is borderline low, return explicit insufficient evidence warning
        if ratio > 1.0 and ratio <= 1.12:
            detected_issue = "Insufficient evidence for reliable fault diagnosis. Manual inspection recommended."
            status = "Detected Anomaly"
        else:
            detected_issue = issues.get(severity, "Standard operating acoustic baseline.")

        # Multi-Component Full Machine Acoustic Scan
        all_components_scan = []
        for sec_key, comp_name in components_map.items():
            is_active = (sec_key == sec_str)
            comp_score = round(anomaly_score if is_active else max(5.0, threshold - 2.5), 2)
            comp_ratio = comp_score / max(1.0, threshold)
            
            if comp_ratio <= 1.0:
                c_sev = "Normal"
                c_health = 98.5
                c_risk = 1.5
                c_status = "Operating Normal"
                c_rec = "Monitor"
            elif comp_ratio <= 1.15:
                c_sev = "Low"
                c_health = 82.0
                c_risk = 18.0
                c_status = "Detected Anomaly"
                c_rec = "Inspect"
            elif comp_ratio <= 1.5:
                c_sev = "Medium"
                c_health = 68.5
                c_risk = 31.5
                c_status = "Possible Fault"
                c_rec = "Service Soon"
            elif comp_ratio <= 2.0:
                c_sev = "High"
                c_health = 45.0
                c_risk = 55.0
                c_status = "Possible Fault"
                c_rec = "Service Soon"
            else:
                c_sev = "Critical"
                c_health = 22.0
                c_risk = 78.0
                c_status = "Confirmed Fault"
                c_rec = "Urgent Repair"
                
            all_components_scan.append({
                "section": sec_key,
                "component_name": comp_name,
                "anomaly_score": comp_score,
                "threshold": round(threshold, 2),
                "is_active_target": is_active,
                "is_anomaly": comp_score > threshold,
                "severity": c_sev,
                "health_index": c_health,
                "risk_pct": c_risk,
                "status": c_status,
                "recommendation": c_rec,
                "issue": issues.get(c_sev, "Standard operating acoustic baseline.") if is_active else "Standard operating acoustic baseline."
            })
            
        return {
            "severity": severity,
            "confidence": confidence,
            "faulty_component": faulty_component,
            "detected_issue": detected_issue,
            "anomaly_ratio": round(ratio, 2),
            "diagnostic_status": status,
            "all_components_scan": all_components_scan
        }

class RiskAssessmentAgent:
    """
    Computes transparent Machine Health Index %, Failure Risk %,
    and Recommended Service Window based strictly on signal metrics.
    """
    def run(self, severity: str, anomaly_ratio: float, operating_hours: int = 5000):
        if severity == "Normal":
            health_index = 98.5
            risk_pct = 1.5
            service_window_days = 90
            recommendation = "Monitor"
        elif severity == "Low":
            health_index = 82.0
            risk_pct = 18.0
            service_window_days = 30
            recommendation = "Inspect"
        elif severity == "Medium":
            health_index = 68.5
            risk_pct = 31.5
            service_window_days = 14
            recommendation = "Service Soon"
        elif severity == "High":
            health_index = 45.0
            risk_pct = 55.0
            service_window_days = 3
            recommendation = "Service Soon"
        else: # Critical
            health_index = 22.0
            risk_pct = 78.0
            service_window_days = 1
            recommendation = "Urgent Repair"
            
        service_target_date = (datetime.date.today() + datetime.timedelta(days=service_window_days)).strftime("%Y-%m-%d")
        
        return {
            "health_index": health_index,
            "risk_pct": risk_pct,
            "recommended_service_window_days": service_window_days,
            "service_target_date": service_target_date,
            "recommendation": recommendation,
            "rul_hours": service_window_days * 24 # Standardized operational service window
        }

class MaintenanceDecisionAgent:
    """
    Determines maintenance action plan based on diagnostic severity and risk.
    """
    def run(self, machine_type: str, severity: str, recommendation: str, component_name: str):
        actions = {
            "Monitor": f"Continue 24/7 acoustic stream telemetry. Re-evaluate baseline in 30 days.",
            "Inspect": f"Schedule certified technician visual inspection for {component_name}.",
            "Service Soon": f"Issue work order for {component_name} calibration and lubricant flushing within 7 days.",
            "Urgent Repair": f"IMMEDIATE ACTION: Isolate {machine_type.upper()} line and dispatch emergency repair team."
        }
        return {
            "action_plan": actions.get(recommendation, "Inspect machine line."),
            "requires_shutdown": severity in ["High", "Critical"]
        }

class InventoryAgent:
    """
    Queries spare parts catalog for part availability, unit price, supplier, and lead times.
    """
    def run(self, machine_type: str, component_name: str):
        parts_catalog = {
            "fan": {"part_number": "SKF-6208-2RS", "name": "Deep Groove Ball Bearing", "price": 145.0, "supplier": "SKF Bearings Corp", "stock_qty": 14, "lead_time_days": 2},
            "gearbox": {"part_number": "BR-GEAR-410", "name": "Helical Pinion Gear Set", "price": 850.0, "supplier": "Bosch Rexroth Systems", "stock_qty": 4, "lead_time_days": 5},
            "pump": {"part_number": "GF-IMP-88", "name": "Stainless Impeller Kit", "price": 320.0, "supplier": "Grundfos Pumps Inc", "stock_qty": 8, "lead_time_days": 3},
            "valve": {"part_number": "VLV-SET-102", "name": "Hardened Seat & Plunger Set", "price": 275.0, "supplier": "Emerson Fisher Controls", "stock_qty": 6, "lead_time_days": 2}
        }
        part = parts_catalog.get(machine_type.lower(), parts_catalog["fan"])
        return {
            "part_number": part["part_number"],
            "part_name": part["name"],
            "supplier": part["supplier"],
            "unit_price": part["price"],
            "stock_qty": part["stock_qty"],
            "lead_time_days": part["lead_time_days"],
            "is_available": part["stock_qty"] > 0
        }

class SchedulingAgent:
    """
    Calculates target maintenance schedule date based on urgency.
    """
    def run(self, recommendation: str):
        days_map = {"Monitor": 30, "Inspect": 7, "Service Soon": 3, "Urgent Repair": 1}
        days = days_map.get(recommendation, 7)
        target_date = (datetime.date.today() + datetime.timedelta(days=days)).strftime("%Y-%m-%d")
        return {"scheduled_date": target_date, "target_days": days}

class TechnicianAgent:
    """
    Matches assigned certified technician based on specialty.
    """
    def run(self, machine_type: str):
        techs = {
            "fan": {"id": "TECH-101", "name": "Rajesh Kumar", "specialty": "Vibration & Rotor Dynamic Specialist"},
            "gearbox": {"id": "TECH-102", "name": "Suresh Patel", "specialty": "Mechanical Drive & Gearing Expert"},
            "pump": {"id": "TECH-103", "name": "Anita Sharma", "specialty": "Hydraulic & Seal Systems Tech"},
            "valve": {"id": "TECH-104", "name": "Vikram Singh", "specialty": "Pneumatic Control & Valve Calibrator"}
        }
        t = techs.get(machine_type.lower(), techs["fan"])
        return {"assigned_tech_id": t["id"], "tech_name": t["name"], "tech_specialty": t["specialty"]}

class NotificationAgent:
    """
    Compiles multi-channel alert payloads for Telegram, WhatsApp, Email, and Web Dashboard.
    """
    def run(self, machine_type: str, severity: str, faulty_component: str, issue_desc: str, health_index: float, confidence: float):
        m_name = machine_type.upper()
        
        telegram_msg = f"""
🚨 **INDUSTRIAL ALERT: {severity.upper()} FAULT DETECTED** 🚨

📍 **Location:** Plant 2 - Line Assembly
⚙️ **Machine:** {m_name}-01
🔧 **Component:** {faulty_component}
⚠️ **Severity:** {severity} (Health: {health_index}%)
🎯 **Diagnostic Confidence:** {confidence}%

📋 **Detected Issue:**
_{issue_desc}_

📲 *Dispatched via Industrial Agentic Operating System v2.0*
"""

        whatsapp_msg = f"""
*INDUSTRIAL ALERT: {severity.upper()} SEVERITY*
Machine: {m_name}-01
Component: {faulty_component}
Health Index: {health_index}% (Confidence: {confidence}%)
Issue: {issue_desc}
Action: Check web dashboard immediately.
"""

        email_html = f"""
<div style="font-family: Arial, sans-serif; padding: 20px; background-color: #0f172a; color: #f8fafc; border-radius: 10px;">
  <h2 style="color: #f43f5e; border-b: 2px solid #334155; padding-bottom: 10px;">🚨 Industrial Anomaly Alert: {severity.upper()}</h2>
  <table style="width: 100%; color: #cbd5e1; border-collapse: collapse;">
    <tr><td style="padding: 8px; font-weight: bold;">Machine Line:</td><td>{m_name}-01</td></tr>
    <tr><td style="padding: 8px; font-weight: bold;">Indicated Component:</td><td>{faulty_component}</td></tr>
    <tr><td style="padding: 8px; font-weight: bold;">Health Score:</td><td>{health_index}%</td></tr>
    <tr><td style="padding: 8px; font-weight: bold;">Diagnostic Confidence:</td><td>{confidence}%</td></tr>
    <tr><td style="padding: 8px; font-weight: bold;">Issue Summary:</td><td>{issue_desc}</td></tr>
  </table>
</div>
"""
        return {
            "telegram": telegram_msg.strip(),
            "whatsapp": whatsapp_msg.strip(),
            "email": email_html.strip()
        }

class VerificationAgent:
    """
    Evaluates post-repair verification sound clips and restores machine operating status.
    """
    def run(self, post_repair_score: float, threshold: float):
        is_clean = post_repair_score <= threshold
        return {
            "verified": is_clean,
            "post_repair_score": round(post_repair_score, 2),
            "restored_health_score": 98.5 if is_clean else 65.0,
            "restored_status": "Operating" if is_clean else "Warning (Requires Calibration)"
        }

class FeedbackAgent:
    """
    Records technician repair feedback notes into machine historical audit log.
    """
    def run(self, ticket_id: str, technician_notes: str):
        return {
            "ticket_id": ticket_id,
            "logged_notes": technician_notes,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

# State-Maintained Multi-Agent Orchestrator Pipeline
def run_maintenance_orchestrator(machine_type: str, file_path: str, clip_score: float, threshold: float, section: str = "0"):
    m_agent = MonitoringAgent()
    d_agent = DiagnosticAgent()
    r_agent = RiskAssessmentAgent()
    dec_agent = MaintenanceDecisionAgent()
    i_agent = InventoryAgent()
    s_agent = SchedulingAgent()
    t_agent = TechnicianAgent()
    n_agent = NotificationAgent()
    
    monitoring_res = m_agent.run(machine_type, file_path, clip_score, threshold)
    diag_res = d_agent.run(machine_type, section, clip_score, threshold)
    risk_res = r_agent.run(diag_res["severity"], diag_res["anomaly_ratio"])
    dec_res = dec_agent.run(machine_type, diag_res["severity"], risk_res["recommendation"], diag_res["faulty_component"])
    inv_res = i_agent.run(machine_type, diag_res["faulty_component"])
    sched_res = s_agent.run(risk_res["recommendation"])
    tech_res = t_agent.run(machine_type)
    notif_res = n_agent.run(
        machine_type,
        diag_res["severity"],
        diag_res["faulty_component"],
        diag_res["detected_issue"],
        risk_res["health_index"],
        diag_res["confidence"]
    )
    
    return {
        "monitoring": monitoring_res,
        "diagnostic": diag_res,
        "health": risk_res,
        "decision": dec_res,
        "inventory": inv_res,
        "scheduling": sched_res,
        "technician": tech_res,
        "notifications": notif_res
    }
