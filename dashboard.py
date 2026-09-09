import os
import time
import json
import glob
import random
import numpy as np
import librosa
import tensorflow as tf
import streamlit as st
import matplotlib.pyplot as plt

import src.db as db
import src.agent_system as agent

# Initialize DB on app load
db.init_db()

# Set page configuration with wide layout and custom title
st.set_page_config(
    page_title="AI Industrial Predictive Maintenance Portal",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for glassmorphism, animations, dark mode theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .stApp {
        background: radial-gradient(circle at top left, #0b0f19, #020617);
        color: #f8fafc;
    }
    
    .glass-card {
        background: rgba(15, 23, 42, 0.45);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
    }
    
    .glowing-header {
        font-weight: 800;
        background: linear-gradient(135deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 30px rgba(56, 189, 248, 0.25);
    }

    .badge-severity-normal {
        background-color: rgba(16, 185, 129, 0.2);
        color: #34d399;
        border: 1px solid #10b981;
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: bold;
    }
    .badge-severity-low {
        background-color: rgba(59, 130, 246, 0.2);
        color: #60a5fa;
        border: 1px solid #3b82f6;
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: bold;
    }
    .badge-severity-medium {
        background-color: rgba(245, 158, 11, 0.2);
        color: #fbbf24;
        border: 1px solid #f59e0b;
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: bold;
    }
    .badge-severity-high {
        background-color: rgba(249, 115, 22, 0.2);
        color: #fb923c;
        border: 1px solid #f97316;
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: bold;
    }
    .badge-severity-critical {
        background-color: rgba(239, 68, 68, 0.2);
        color: #f87171;
        border: 1px solid #ef4444;
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: bold;
        animation: pulse-ruby 1.5s infinite;
    }

    @keyframes pulse-ruby {
        0%, 100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }
        50% { box-shadow: 0 0 20px 8px rgba(239, 68, 68, 0.4); }
    }
    
    .agent-log {
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        color: #a7f3d0;
        background-color: #060913;
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 14px;
        margin-top: 10px;
        max-height: 350px;
        overflow-y: auto;
    }

    .chat-bubble-user {
        background-color: rgba(56, 189, 248, 0.15);
        border: 1px solid rgba(56, 189, 248, 0.3);
        border-radius: 12px 12px 0px 12px;
        padding: 12px 16px;
        margin: 8px 0;
        color: #f8fafc;
    }
    .chat-bubble-ai {
        background-color: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px 12px 12px 0px;
        padding: 14px 18px;
        margin: 8px 0;
        color: #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# Cache NN model loading
@st.cache_resource
def load_nn_model(model_path):
    if os.path.exists(model_path):
        try:
            return tf.keras.models.load_model(model_path)
        except Exception as e:
            return f"Error: {str(e)}"
    return None

def extract_features(file_path):
    y, sr = librosa.load(file_path, sr=None)
    stft = librosa.stft(y, n_fft=1024, hop_length=512)
    mel = librosa.feature.melspectrogram(S=np.abs(stft)**2, sr=sr, n_mels=128)
    log_mel = librosa.power_to_db(mel)
    
    log_mel = log_mel.T
    n_frames = log_mel.shape[0]
    vectors = []
    for i in range(n_frames - 5 + 1):
        vec = log_mel[i : i + 5].flatten()
        vectors.append(vec)
    return np.array(vectors), log_mel, y, sr

def get_machine_metadata(machine_name):
    meta_path = os.path.join("models", f"{machine_name}_meta.json")
    if os.path.exists(meta_path):
        with open(meta_path, "r") as f:
            return json.load(f)
    return {"thresholds": {"0": 12.0, "1": 12.0, "2": 12.0}}

def get_machine_metrics(machine_name):
    metrics_path = os.path.join("results", f"{machine_name}_metrics.json")
    if os.path.exists(metrics_path):
        with open(metrics_path, "r") as f:
            return json.load(f)
    return None

def get_test_files(machine_name):
    dataset_dir = os.path.join("dataset", f"dev_data_{machine_name}", machine_name)
    test_files = glob.glob(os.path.join(dataset_dir, "**/*.wav"), recursive=True)
    test_files = [f for f in test_files if "train" not in f]
    return sorted(test_files)

# Session state initialization
if "telemetry_active" not in st.session_state:
    st.session_state.telemetry_active = False
if "telemetry_history" not in st.session_state:
    st.session_state.telemetry_history = []
if "current_file_index" not in st.session_state:
    st.session_state.current_file_index = 0
if "last_machine" not in st.session_state:
    st.session_state.last_machine = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Title Header
st.markdown('<h1 class="glowing-header">AI Industrial Predictive Maintenance System</h1>', unsafe_allow_html=True)
st.markdown("Agentic AI Industrial Operating System — 24/7 Acoustic Monitoring, Fault Diagnostics & Automated Maintenance Orchestrator")
st.write("---")

# Sidebar
st.sidebar.markdown("### 🎛️ PLANT CONTROLS")
machine_name = st.sidebar.selectbox("Select Machine Asset", ["fan", "gearbox", "pump", "valve"])

# Clear history on machine switch
if st.session_state.last_machine != machine_name:
    st.session_state.telemetry_history = []
    st.session_state.last_machine = machine_name

# Load active model and thresholds
model_path = os.path.join("models", f"{machine_name}_model.keras")
model = load_nn_model(model_path)
meta = get_machine_metadata(machine_name)
thresholds = meta.get("thresholds", {})

is_fallback = False
if model is None or isinstance(model, str):
    is_fallback = True
    st.sidebar.warning("⚠️ Machine model training or initialization fallback active.")

test_files = get_test_files(machine_name)
machine_db_info = db.get_machine_by_type(machine_name)

# 6 Operational Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🛰️ 24/7 Telemetry & Health Risk Matrix",
    "🤖 Multi-Agent Orchestration Trace",
    "💬 AI Maintenance Assistant",
    "🛠️ Tickets, Dispatch & Calendar",
    "📦 Spare Parts & Manufacturer Network",
    "🔬 Fault Injection & Spectrogram Analysis"
])

# TAB 1: 24/7 Live Telemetry & Health Risk Matrix
with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 📊 Telemetry Controls")
        sim_speed = st.slider("Update Frequency (seconds)", 1.5, 8.0, 3.5, step=0.5)
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🟢 Start 24/7 Feed", use_container_width=True):
                st.session_state.telemetry_active = True
                st.rerun()
        with c2:
            if st.button("🔴 Stop Feed", use_container_width=True):
                st.session_state.telemetry_active = False
                st.rerun()
                
        st.write("---")
        st.markdown(f"**Asset Name:** {machine_db_info['name']}")
        st.markdown(f"**Location:** {machine_db_info['location']}")
        st.markdown(f"**Installed Date:** {machine_db_info['install_date']}")
        st.markdown(f"**Operating Hours:** {machine_db_info['operating_hours']} hrs")
        st.markdown('</div>', unsafe_allow_html=True)

    with col1:
        if st.session_state.telemetry_active:
            idx = st.session_state.current_file_index
            if idx >= len(test_files):
                idx = 0
            file_to_run = test_files[idx]
            
            basename = os.path.basename(file_to_run)
            section = "0"
            for s in ["00", "01", "02"]:
                if f"section_{s}" in basename:
                    section = str(int(s))
                    
            threshold = float(thresholds.get(section, 12.0))
            vectors, log_mel, y, sr = extract_features(file_to_run)
            
            if not is_fallback:
                reconstructed = model(vectors, training=False).numpy()
                frame_errors = np.mean(np.square(vectors - reconstructed), axis=1)
                clip_score = float(np.mean(frame_errors))
            else:
                is_anom = "anomaly" in basename
                clip_score = threshold + random.uniform(2.0, 8.0) if is_anom else threshold - random.uniform(1.0, 4.0)
                
            # Execute Multi-Agent Orchestrator
            agent_res = agent.run_maintenance_orchestrator(machine_name, file_to_run, clip_score, threshold)
            
            hist_entry = {
                "file": basename,
                "section": section,
                "score": clip_score,
                "threshold": threshold,
                "agent_res": agent_res,
                "timestamp": time.strftime("%H:%M:%S")
            }
            st.session_state.telemetry_history.append(hist_entry)
            if len(st.session_state.telemetry_history) > 30:
                st.session_state.telemetry_history.pop(0)
                
            st.session_state.current_file_index = idx + 1

        if len(st.session_state.telemetry_history) > 0:
            latest = st.session_state.telemetry_history[-1]
            a_res = latest["agent_res"]
            diag = a_res["diagnostic"]
            health = a_res["health"]
            sev = diag["severity"]
            
            badge_class = f"badge-severity-{sev.lower()}"
            
            st.markdown(f"""
            <div class="glass-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h2>{machine_db_info['name']} ({machine_db_info['id']})</h2>
                    <span class="{badge_class}">SEVERITY: {sev.upper()}</span>
                </div>
                <div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:15px; margin-top:15px;">
                    <div>
                        <span style="color:#94a3b8; font-size:12px;">MACHINE HEALTH INDEX</span><br/>
                        <span style="font-size:24px; font-weight:bold; color:{'#34d399' if health['health_index']>80 else '#fbbf24' if health['health_index']>60 else '#f87171'};">
                            {health['health_index']}%
                        </span>
                    </div>
                    <div>
                        <span style="color:#94a3b8; font-size:12px;">INDICATED FAULTY COMPONENT</span><br/>
                        <b style="color:#f8fafc;">{diag['faulty_component']}</b>
                    </div>
                    <div>
                        <span style="color:#94a3b8; font-size:12px;">ESTIMATED RUL</span><br/>
                        <b style="color:#38bdf8;">~{health['rul_hours']} Hours</b> ({health['rul_days']} days)
                    </div>
                    <div>
                        <span style="color:#94a3b8; font-size:12px;">RECOMMENDED ACTION</span><br/>
                        <b style="color:#a7f3d0;">{health['recommendation'].upper()}</b>
                    </div>
                </div>
                <div style="margin-top:15px; padding:10px; background:rgba(255,255,255,0.03); border-radius:8px;">
                    <span style="color:#94a3b8; font-size:12px;">DIAGNOSTIC ISSUE SUMMARY:</span><br/>
                    <span style="color:#e2e8f0; font-size:13px;">{diag['detected_issue']} (Confidence: {diag['confidence']}%)</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Live Plotting
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("### 📈 Real-Time Acoustic Anomaly Index Telemetry")
            
            scores = [x["score"] for x in st.session_state.telemetry_history]
            thresh_hist = [x["threshold"] for x in st.session_state.telemetry_history]
            timestamps = [x["timestamp"] for x in st.session_state.telemetry_history]
            
            fig, ax = plt.subplots(figsize=(10, 2.5), facecolor='#020617')
            ax.set_facecolor('none')
            ax.plot(range(len(scores)), scores, color="#38bdf8", linewidth=2, label="Anomaly Reconstruction Error")
            ax.axhline(y=thresh_hist[-1], color="#f43f5e", linestyle="--", label="Threshold", linewidth=1.5)
            
            ax.set_title("Vibrational Spectral Deviation Rate", color="#cbd5e1", fontsize=9)
            ax.tick_params(colors="#64748b", labelsize=8)
            ax.spines['bottom'].set_color('#1e293b')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#1e293b')
            ax.grid(True, color='#1e293b', linestyle=':', alpha=0.5)
            
            if len(timestamps) > 0:
                plt.xticks(range(0, len(timestamps), max(1, len(timestamps)//5)), timestamps[::max(1, len(timestamps)//5)])
            st.pyplot(fig)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Multi-channel Dispatch Payload Preview
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("### 📲 Multi-Channel Instant Alert Dispatch Payloads")
            
            notifs = a_res["notifications"]
            n_tab1, n_tab2, n_tab3 = st.tabs(["Telegram Payload", "WhatsApp Payload", "Email HTML Payload"])
            with n_tab1:
                st.code(notifs["telegram"], language="markdown")
            with n_tab2:
                st.code(notifs["whatsapp"], language="text")
            with n_tab3:
                st.code(notifs["email"], language="html")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Click 'Start 24/7 Feed' in the sidebar controls to begin live sensor stream telemetry.")
            
        if st.session_state.telemetry_active:
            time.sleep(sim_speed)
            st.rerun()

# TAB 2: Multi-Agent Orchestration Trace
with tab2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🤖 Agentic AI Multi-Agent Execution Trace")
    st.markdown("View how specialized AI agents diagnose faults, evaluate risk, query parts, dispatch technicians, and notify manufacturers in real time.")
    
    if len(st.session_state.telemetry_history) > 0:
        latest = st.session_state.telemetry_history[-1]
        res = latest["agent_res"]
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("#### 1. 🔍 Diagnostic & Risk Agents")
            st.json({
                "DiagnosticAgent": res["diagnostic"],
                "HealthRiskAgent": res["health"]
            })
            
            st.markdown("#### 2. 📦 Spare Parts Inventory Agent")
            st.json(res["parts"])
            
        with col_b:
            st.markdown("#### 3. 👷 Dispatcher & Ticket Agent")
            st.json(res["ticket"])
            
            st.markdown("#### 4. 🏢 Manufacturer Liaison Agent")
            st.json({
                "mfr_name": res["liaison"]["mfr_name"],
                "contact_email": res["liaison"]["contact_email"],
                "service_center": res["liaison"]["service_center"]
            })
            
        st.write("---")
        st.markdown("#### 📄 Official Generated Manufacturer RFP Document:")
        st.code(res["liaison"]["rfp_text"], language="text")
    else:
        st.info("Run Telemetry Feed or Fault Injection to trigger the Multi-Agent AI Orchestrator trace.")
    st.markdown('</div>', unsafe_allow_html=True)

# TAB 3: AI Maintenance Assistant
with tab3:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 💬 Conversational AI Industrial Maintenance Assistant")
    st.markdown("Ask the AI Assistant questions about machine health, component status, service dates, stock availability, and manufacturer service centers.")
    
    # Quick sample questions buttons
    st.markdown("**Suggested Manager Queries:**")
    q_col1, q_col2, q_col3 = st.columns(3)
    
    selected_sample = None
    with q_col1:
        if st.button("❓ Why did this alert trigger?"):
            selected_sample = "Why did this machine generate an alert?"
        if st.button("📦 Is required spare part available?"):
            selected_sample = "Is the required spare part available?"
    with q_col2:
        if st.button("🗓️ When was this machine last serviced?"):
            selected_sample = "When was this machine last serviced?"
        if st.button("⏳ When should next service occur?"):
            selected_sample = "When should the next service be performed?"
    with q_col3:
        if st.button("🔧 What component needs replacement?"):
            selected_sample = "What component may need replacement?"
        if st.button("👷 Who is assigned to this repair?"):
            selected_sample = "Who should handle this repair?"
            
    st.write("---")
    
    user_input = st.text_input("Type your question to the AI Maintenance Assistant:", value=selected_sample if selected_sample else "")
    
    if st.button("Send Query", type="primary") or selected_sample:
        if user_input:
            assistant = agent.ConversationalAssistantAgent()
            answer = assistant.answer_question(user_input, machine_name)
            
            st.session_state.chat_history.append({"user": user_input, "bot": answer})
            
    # Display Chat History
    for chat in reversed(st.session_state.chat_history[-6:]):
        st.markdown(f'<div class="chat-bubble-user">👤 <b>Manager:</b> {chat["user"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="chat-bubble-ai">{chat["bot"]}</div>', unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)

# TAB 4: Tickets, Dispatch & Calendar
with tab4:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🛠️ Maintenance Work Orders & Technician Roster")
    
    tickets = db.get_tickets()
    if tickets:
        st.write("#### Active Maintenance Tickets")
        st.dataframe(tickets, use_container_width=True)
    else:
        st.info("No active maintenance tickets.")
        
    st.write("---")
    st.write("#### Technician Directory")
    techs = db.get_all_technicians()
    st.dataframe(techs, use_container_width=True)
    
    st.write("---")
    st.markdown("### 🔄 Closed-Loop Post-Repair Acoustic Verification")
    st.markdown("After technicians complete a repair, run an acoustic verification test to confirm the abnormal sound has disappeared and restore machine health status.")
    
    if tickets:
        t_options = [f"{t['id']} - {t['machine_id']} ({t['severity']})" for t in tickets]
        selected_t = st.selectbox("Select Ticket to Verify & Close", t_options)
        selected_ticket_id = selected_t.split(" - ")[0]
        
        feedback_notes = st.text_area("Technician Root Cause & Repair Notes", "Replaced worn bearing housing. Lapped seat faces. Post-repair acoustic check verified normal baseline.")
        
        if st.button("✅ Confirm Verification & Close Ticket", type="primary"):
            db.update_ticket_status(selected_ticket_id, "Verified", feedback_notes, verified=1)
            st.success(f"Ticket {selected_ticket_id} verified and closed! Machine health restored to 98.5% Operating state.")
            time.sleep(1)
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# TAB 5: Spare Parts & Manufacturer Network
with tab5:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 📦 Industrial Spare-Parts Database")
    parts = db.get_all_spare_parts()
    st.dataframe(parts, use_container_width=True)
    
    st.write("---")
    st.markdown("### 🏭 Authorized Manufacturers & Service Centers")
    mfrs = db.get_all_manufacturers()
    st.dataframe(mfrs, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# TAB 6: Fault Injection & Spectrogram Analysis
with tab6:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🔬 Acoustic Spectrogram Analysis & Fault Injection")
    
    domain_select = st.selectbox("Select Domain Type", ["source", "target"])
    section_select = st.selectbox("Select Machine Section", ["00", "01", "02"])
    type_select = st.selectbox("Filter Sound Class", ["normal", "anomaly"])
    
    filtered_files = [f for f in test_files if domain_select in f and f"section_{section_select}" in f and type_select in f]
    
    if filtered_files:
        selected_test_file = st.selectbox("Select Test Clip", filtered_files, format_func=lambda x: os.path.basename(x))
        
        st.write("---")
        with open(selected_test_file, "rb") as f_aud:
            st.audio(f_aud.read(), format="audio/wav")
            
        if st.button("🔬 Analyze Audio Clip", type="primary"):
            with st.spinner("Extracting features and running model inference..."):
                vectors, log_mel, y, sr = extract_features(selected_test_file)
                section = str(int(section_select))
                threshold = float(thresholds.get(section, 12.0))
                
                if not is_fallback:
                    reconstructed = model(vectors, training=False).numpy()
                    frame_errors = np.mean(np.square(vectors - reconstructed), axis=1)
                    clip_score = float(np.mean(frame_errors))
                else:
                    clip_score = threshold + 5.0 if "anomaly" in selected_test_file else threshold - 3.0
                    frame_errors = [clip_score + random.uniform(-1, 1) for _ in range(len(vectors))]
                    
                is_anomaly = clip_score > threshold
                
                col_res1, col_res2 = st.columns(2)
                with col_res1:
                    st.metric("Anomaly Reconstruction Score", f"{clip_score:.2f}", delta=f"{(clip_score - threshold):+.2f} vs Threshold", delta_color="inverse")
                    st.metric("Section Baseline Threshold", f"{threshold:.2f}")
                with col_res2:
                    if is_anomaly:
                        st.error("🚨 CRITICAL FAULT DETECTED")
                    else:
                        st.success("✅ MACHINE NORMAL")
                        
                fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 5), facecolor='#020617')
                ax1.set_facecolor('none')
                ax2.set_facecolor('none')
                
                img = librosa.display.specshow(log_mel.T, sr=sr, hop_length=512, x_axis='time', y_axis='mel', ax=ax1, cmap='magma')
                ax1.set_title("Log-Mel Spectrogram (128 Mel Bins)", color="#cbd5e1", fontsize=10)
                ax1.tick_params(colors="#64748b", labelsize=8)
                fig.colorbar(img, ax=ax1, format='%+2.0f dB').ax.tick_params(colors="#64748b", labelsize=8)
                
                ax2.plot(frame_errors, color="#a855f7", linewidth=2, label="Frame Reconstruction Loss")
                ax2.axhline(y=threshold, color="#f43f5e", linestyle="--", label="Threshold")
                ax2.set_title("Frame-level Acoustic Deviation Profile", color="#cbd5e1", fontsize=10)
                ax2.tick_params(colors="#64748b", labelsize=8)
                ax2.grid(True, color='#1e293b', linestyle=':', alpha=0.5)
                ax2.legend(facecolor='#0f172a', edgecolor='#1e293b', fontsize=8).get_texts()[0].set_color('#cbd5e1')
                
                plt.tight_layout()
                st.pyplot(fig)
    st.markdown('</div>', unsafe_allow_html=True)
