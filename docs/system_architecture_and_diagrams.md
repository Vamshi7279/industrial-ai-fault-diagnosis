# System Architecture & Diagrams
## AI-Agent Based Intelligent Predictive Maintenance System Using Machine Sound Analysis

---

## 1. High-Level System Architecture Diagram

```mermaid
flowchart TD
    subgraph Client ["Frontend Layer (React 18 + Vite + Tailwind CSS)"]
        UI["Live Monitoring Dashboard"]
        Grid["Simultaneous Multi-Component Scan Grid"]
        ChatUI["RAG AI Maintenance Assistant"]
        AlertUI["Real-Time Alert & Kanban Center"]
    end

    subgraph API_Gateway ["API & Gateway Layer (FastAPI + Uvicorn)"]
        REST["REST API Endpoints (/api/v2/*)"]
        WS["WebSocket Telemetry Server (/ws/telemetry)"]
        CORS["CORS & Security Middleware"]
    end

    subgraph MultiAgent ["10-Agent Orchestrator Engine (Python)"]
        A1["1. Sensor Data Aggregator"]
        A2["2. Acoustic Feature Extractor (Librosa Log-Mel)"]
        A3["3. Deep Autoencoder Anomaly Evaluator"]
        A4["4. Fault Diagnostic & Root Cause Analyzer"]
        A5["5. Health Index & Risk Assessor"]
        A6["6. RAG Document & Manual Engine"]
        A7["7. Work Order & Ticket Generator"]
        A8["8. Spare Parts Inventory Specialist"]
        A9["9. Manufacturer RFP Specialist"]
        A10["10. Multi-Channel Notification Dispatcher"]
    end

    subgraph ML_Layer ["ML Model Layer (Keras / TensorFlow 2.x)"]
        M1["Fan Autoencoder Model (fan_model.keras)"]
        M2["Pump Autoencoder Model (pump_model.keras)"]
        M3["Slider Autoencoder Model (slider_model.keras)"]
        M4["Valve Autoencoder Model (valve_model.keras)"]
    end

    subgraph Storage ["Data Layer (SQLAlchemy ORM + SQLite / PostgreSQL)"]
        DB[("industrial_plant.db (22 ORM Tables)")]
    end

    subgraph External ["External Integration Services"]
        Telegram["Telegram Bot API (Interactive Notifications)"]
        WhatsApp["WhatsApp Gateway"]
        Email["SMTP Email Service"]
    end

    %% Connections
    UI <--> REST
    UI <--> WS
    ChatUI <--> REST
    REST --> MultiAgent
    WS --> MultiAgent

    A2 --> ML_Layer
    A3 <--> ML_Layer
    MultiAgent <--> DB
    A10 --> External
```

---

## 2. 10-Agent Orchestration Workflow Diagram

```mermaid
flowchart LR
    subgraph Phase1 ["Data Sensing & Extraction"]
        A1["Agent 1: Sensor Aggregator"] --> A2["Agent 2: Feature Extractor (Log-Mel Spectrogram)"]
    end

    subgraph Phase2 ["AI Anomaly & Diagnostics"]
        A2 --> A3["Agent 3: Deep Autoencoder Anomaly Evaluator"]
        A3 --> A4["Agent 4: Root Cause Diagnostic Analyzer"]
        A3 --> A5["Agent 5: Health Index & Risk Assessor"]
    end

    subgraph Phase3 ["Action & Ticket Generation"]
        A4 --> A7["Agent 7: Work Order Generator"]
        A4 --> A8["Agent 8: Inventory Specialist"]
        A4 --> A9["Agent 9: Manufacturer RFP Specialist"]
    end

    subgraph Phase4 ["Notification & Guidance"]
        A5 --> A10["Agent 10: Telegram Notification Dispatcher"]
        A4 --> A6["Agent 6: RAG Manual Assistant Engine"]
    end
```

---

## 3. Real-Time Acoustic Telemetry & Anomaly Processing Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    participant Sensor as Acoustic Sensor / Audio File
    participant WS as WebSocket Gateway
    participant Agent2 as Agent 2 (Feature Extractor)
    participant ML as Keras Autoencoder Model
    participant Agent3 as Agent 3 (Anomaly Evaluator)
    participant Agent4 as Agent 4 (Diagnostic Analyzer)
    participant DB as SQLite / PostgreSQL DB
    participant UI as React Frontend Dashboard

    Sensor->>WS: Emit Raw 16kHz Audio Stream (.wav)
    WS->>Agent2: Forward Audio Buffer
    Agent2->>Agent2: Compute 128-band Log-Mel Spectrogram
    Agent2->>ML: Pass Feature Vector Array
    ML-->>Agent3: Return Reconstructed Spectrogram Tensor
    Agent3->>Agent3: Compute MSE Reconstruction Error (Anomaly Score)
    
    alt Anomaly Score > Dynamic Threshold
        Agent3->>Agent4: Trigger Multi-Component Section Scan
        Agent4->>Agent4: Pinpoint Faulty Section (Section 00 / 01 / 02)
        Agent4->>DB: Log Anomaly Event & Component Health
        Agent3->>WS: Broadcast Alert Event + High Risk Metric
    else Score <= Threshold
        Agent3->>WS: Broadcast Normal Baseline Metrics
    end

    WS-->>UI: Real-Time Telemetry JSON Payload
    UI->>UI: Update Live Log-Mel Spectrogram & Component Scanning Grid
```

---

## 4. End-to-End Fault Detection to Telegram Notification Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    participant Engine as Agent Orchestrator Engine
    participant Agent5 as Agent 5 (Risk Assessor)
    participant Agent7 as Agent 7 (Work Order Generator)
    participant Agent10 as Agent 10 (Notification Dispatcher)
    participant Telegram as Telegram Bot API
    participant User as Plant Manager / Field Tech

    Engine->>Agent5: Evaluate Machine Acoustic Risk Score
    Agent5->>Agent5: Calculate Health Index % & Fault Severity (Critical/High)
    Agent5->>Agent7: Auto-Generate Maintenance Ticket (Work Order)
    Agent5->>Agent10: Trigger Urgent Notification Workflow
    Agent10->>Agent10: Format Markdown Payload & Inline Buttons
    Agent10->>Telegram: HTTP POST /sendMessage (Bot Token + Chat ID)
    Telegram-->>User: Push Telegram Alert with Interactive Action Buttons
    User->>Telegram: Click [ 🔍 Live Telemetry ] or [ 🛠️ Maintenance Kanban ]
    Telegram->>User: Redirect to Deployed Web Application Dashboard
```

---

## 5. Database Entity-Relationship (ER) Diagram

```mermaid
erDiagram
    MACHINES ||--o{ FAULT_DIAGNOSES : diagnoses
    MACHINES ||--o{ ALERTS : triggers
    MACHINES ||--o{ WORK_ORDERS : requires
    MACHINES ||--o{ ACOUSTIC_CLIPS : generates

    WORK_ORDERS ||--o{ WORK_ORDER_PARTS : uses
    SPARE_PARTS ||--o{ WORK_ORDER_PARTS : supplies
    TECHNICIANS ||--o{ WORK_ORDERS : assigned_to

    USERS ||--o{ AUDIT_LOGS : performs
    ROLES ||--o{ USERS : granted_to

    MANUFACTURERS ||--o{ SERVICE_REQUESTS : receives
    MACHINES ||--o{ SERVICE_REQUESTS : targets

    MACHINES {
        string id PK
        string name
        string machine_type
        string location
        string status
        float baseline_threshold
    }

    FAULT_DIAGNOSES {
        int id PK
        string machine_id FK
        float anomaly_score
        float threshold
        string faulty_component
        string detected_issue
        string severity
        datetime timestamp
    }

    ALERTS {
        string id PK
        string machine_id FK
        string severity
        string title
        string message
        string status
        datetime created_at
    }

    WORK_ORDERS {
        string id PK
        string machine_id FK
        string technician_id FK
        string title
        string priority
        string status
        datetime scheduled_date
    }

    SPARE_PARTS {
        string id PK
        string part_name
        int quantity_in_stock
        int minimum_threshold
        float unit_cost
    }

    AUDIT_LOGS {
        int id PK
        string user_id FK
        string action
        string details
        datetime timestamp
    }
```

---

## 6. Machine Health & Alert Lifecycle State Diagram

```mermaid
stateDiagram-v2
    [*] --> BaselineNormal: Machine Audio Sampling Started

    state BaselineNormal {
        [*] --> StreamingAudio
        StreamingAudio --> MelSpectrogramExtracted
        MelSpectrogramExtracted --> LowReconstructionError: Anomaly Score <= Threshold
    }

    BaselineNormal --> AnomalyDetected: Anomaly Score > Dynamic Threshold

    state AnomalyDetected {
        [*] --> MultiComponentScan
        MultiComponentScan --> IdentifyFaultySection
        IdentifyFaultySection --> TriggerAlertDispatcher
    }

    AnomalyDetected --> ActiveAlertState: Severity = Warning / Critical

    state ActiveAlertState {
        [*] --> TelegramNotificationSent
        TelegramNotificationSent --> WorkOrderCreated
        WorkOrderCreated --> TechAssigned
        TechAssigned --> RepairInExecution
    }

    ActiveAlertState --> PostRepairVerification: Tech Submits Completion Feedback

    state PostRepairVerification {
        [*] --> AcousticRecheck
        AcousticRecheck --> VerifiedNormal: Anomaly Score Back Below Threshold
    }

    VerifiedNormal --> BaselineNormal: Alert Resolved & Closed
```

---

## 7. RAG AI Maintenance Assistant Query Flowchart

```mermaid
flowchart TD
    Start(["User submits query in AI Assistant Tab"]) --> Embed["Tokenize Query & Extract Keywords"]
    Embed --> SearchManuals["Search Technical Manuals & Maintenance Docs"]
    SearchManuals --> VectorDB["Query Database & Knowledge Base"]
    VectorDB --> Context["Retrieve Relevant Manual Excerpts & Past Repairs"]
    Context --> LLM["Synthesize Answer with Diagnostic Context"]
    LLM --> FormattedResponse["Format Markdown Answer + Technical Steps"]
    FormattedResponse --> RenderUI["Display Interactive Response in UI"]
```
