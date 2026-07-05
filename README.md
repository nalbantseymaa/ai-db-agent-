# Telecom Cognitive AI Agent with Groq and LibreDB Studio

This repository contains a professional, production-style cognitive AI agent designed for telecom database operations, churn analysis, and customer retention workflows. The system combines a modern language model workflow with a containerized PostgreSQL database and a browser-based database studio to deliver a full end-to-end business intelligence experience.

---

## 1. Project Overview

The agent is built to act like an intelligent business assistant for telecom operations. It can:
- interpret user requests in natural language,
- translate them into SQL queries,
- query a live PostgreSQL database,
- analyze churn-related signals,
- generate business recommendations in a professional report format.

This project is designed for demonstrations, academic presentations, and practical prototype development.

---

## 2. Core Concepts

### What is an AI Agent?
Unlike a simple chatbot, an AI agent can reason through a task, plan an execution path, invoke tools, and interact with external systems. In this project, the agent uses structured prompts, logic hooks, and tool-based execution to perform database-driven analysis.

### Why Tools Matter
Large language models cannot directly access live corporate data. Tools bridge that gap by allowing the agent to run Python functions, query databases, and produce meaningful analysis based on real records.

### Why Environment Variables Matter
API keys and credentials should never be hardcoded into source files. Keeping them in a local .env file improves both security and portability. This also prevents GitHub push protection from blocking the repository.

---

## 3. Architecture and Data Flow

Human request → AI reasoning layer → SQL generation → database query → churn analysis → business report

The main components are:
- the AI agent logic in Python,
- the PostgreSQL database engine,
- the LibreDB Studio interface for database visualization,
- the Groq-based language model integration.

---

## 4. Installation and Setup

### Step 1: Create a Python Environment
```bash
git clone <your-repository-url>
cd ai-db-agent
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### Step 2: Install Dependencies
```bash
pip install langchain langchain-core langchain-community langchain-groq psycopg2-binary python-dotenv
```

### Step 3: Create a Local Environment File
Create a file named .env in the project root and add your API key:

```env
GROQ_API_KEY=your_real_key_here
```

---

## 5. Docker Setup

This project uses Docker to run PostgreSQL and LibreDB Studio locally.

### Docker Compose File
The repository includes a docker-compose.yml file that starts:
- PostgreSQL as the main database service,
- LibreDB Studio as the web-based database interface.

```yaml
version: '3.8'

services:
  telekom-database:
    image: postgres:15
    container_name: telekom_postgres_core
    environment:
      POSTGRES_USER: telekom_admin
      POSTGRES_PASSWORD: safe_telekom_password123
      POSTGRES_DB: telekom_crm_db
    ports:
      - "5432:5432"
    volumes:
      - telekom_db_storage:/var/lib/postgresql/data

  libredb-studio:
    image: libredb/libredb-studio
    container_name: libredb_studio_ui
    ports:
      - "8080:3000"
    depends_on:
      - telekom-database

volumes:
  telekom_db_storage:
```

### Start the Containers
```bash
docker compose up -d
```

Open your browser at http://localhost:8080 to access LibreDB Studio.

![Docker Compose Startup](https://github.com/user-attachments/assets/e37bb7c6-f473-4705-b5cb-becb264b5bfe)

---

## 6. LibreDB Studio Configuration
![LibreDB Connection Setup](https://github.com/user-attachments/assets/6b62d35b-0152-4f3c-b649-58fc6fdc6264)


### Default Login Credentials
- Email: admin@libredb.org
- Password: LibreDB.2026

### Create a New Connection
Use the following settings:
- Connection Name: Telekom CRM Core
- Database Engine: PostgreSQL
- Host: localhost
- Port: 5432
- Username: telekom_admin
- Password: safe_telekom_password123
- Database: telekom_crm_db

---

## 7. Database Schema and Sample Data

Run the following SQL in LibreDB Studio to create the telecom schema and seed sample data:

```sql
-- =========================================================================
-- ADVANCED TELEKOM CRM DATABASE SCHEMA WITH INVENTORY EXTRA LAYER
-- AUTHOR: SEYMA NALBANT
-- =========================================================================

-- 1. CLEANUP: Drop existing tables if they exist

-- 2. CREATE CUSTOMERS TABLE
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    plan_type VARCHAR(50) NOT NULL, -- 'Postpaid' or 'Prepaid'
    monthly_fee DECIMAL(10,2) NOT NULL,
    contract_months_left INT NOT NULL,
    ai_welcome_story TEXT
);

-- 3. CREATE COMPLAINTS TABLE
CREATE TABLE complaints (
    ticket_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(customer_id) ON DELETE CASCADE,
    issue_type VARCHAR(255) NOT NULL,
    is_resolved BOOLEAN DEFAULT FALSE,
    created_at DATE NOT NULL
);

-- 4. CREATE BASE STATIONS TABLE
CREATE TABLE base_stations (
    station_id SERIAL PRIMARY KEY,
    region_name VARCHAR(100) NOT NULL,
    hardware_model VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    last_failure_date DATE
);

-- 5. CREATE USAGE DETAILS TABLE
CREATE TABLE usage_details (
    usage_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(customer_id) ON DELETE CASCADE,
    station_id INT REFERENCES base_stations(station_id) ON DELETE SET NULL,
    data_used_gb DECIMAL(10,2) NOT NULL,
    drop_call_count INT DEFAULT 0,
    log_date DATE NOT NULL
);

-- 6. NEW TABLE: CUSTOMER INVENTORIES (MODEMS, ROUTERS, PHONES)
CREATE TABLE inventories (
    inventory_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(customer_id) ON DELETE CASCADE,
    device_name VARCHAR(100) NOT NULL, -- e.g., 'Fiber Modem V5', '5G Home Router'
    brand VARCHAR(50) NOT NULL,        -- e.g., 'Huawei', 'ZTE', 'Apple'
    serial_number VARCHAR(100) UNIQUE NOT NULL,
    assigned_date DATE NOT NULL
);

-- =========================================================================
-- MOCK DATA INSERTION
-- =========================================================================

INSERT INTO customers (full_name, plan_type, monthly_fee, contract_months_left, ai_welcome_story) VALUES
('Ahmet Yilmaz', 'Postpaid', 450.00, 1, 'Once upon a time, Ahmet connected from Istanbul...'),
('Ayse Kaya', 'Prepaid', 150.00, 12, 'In the heart of Ankara, Ayse unlocked boundless mobile interactions...'),
('Mehmet Ozturk', 'Postpaid', 600.00, 0, NULL),
('Fatma Demir', 'Postpaid', 300.00, 6, NULL),
('Mustafa Sahin', 'Postpaid', 750.00, 0, NULL),
('Zeynep Celik', 'Prepaid', 200.00, 8, NULL);

INSERT INTO base_stations (region_name, hardware_model, status, last_failure_date) VALUES
('Kadikoy Center', 'Ericsson 5G', 'Overloaded', '2026-06-01'),
('Cankaya District', 'Huawei 4G', 'Under Maintenance', '2026-07-03'),
('Konak Bay', 'Nokia 5G', 'Active', NULL),
('Muratpasa Coast', 'Ericsson 4G', 'Active', NULL);

INSERT INTO complaints (customer_id, issue_type, is_resolved, created_at) VALUES
(1, 'Frequent connection drops and slow fiber speed in Kadikoy', false, '2026-06-15'),
(3, 'Unexpected high billing statement on mobile invoice', false, '2026-06-20'),
(2, 'Balance check USSD short code *123# not working', true, '2026-06-10'),
(5, 'Extreme network latency during data usage hours', false, '2026-07-02');

INSERT INTO usage_details (customer_id, station_id, data_used_gb, drop_call_count, log_date) VALUES
(1, 1, 45.50, 8, '2026-07-03'),
(3, 2, 12.00, 1, '2026-07-03'),
(4, 3, 85.00, 0, '2026-07-03'),
(5, 1, 95.00, 14, '2026-07-03'),
(6, 4, 10.00, 0, '2026-07-03');

INSERT INTO inventories (customer_id, device_name, brand, serial_number, assigned_date) VALUES
(1, 'Premium Fiber Modem V5', 'Huawei', 'HW123456789X', '2025-01-10'),
(3, 'Standard VDSL Router', 'TP-Link', 'TP987654321Y', '2023-05-20'),
(4, '5G Home Gateway', 'ZTE', 'ZTE55667788Z', '2026-02-15'),
(5, 'iPhone 15 Pro 256GB', 'Apple', 'APPL99887766M', '2025-09-25');
```

![Database Query Result](https://github.com/user-attachments/assets/484c5d00-739a-4de5-afa3-e8619ac55945)

---

## 8. AI Model and Technology Stack

This project uses:
- Python for the agent logic,
- Groq for the language model integration,
- LibreDB Studio for database interaction,
- PostgreSQL for structured telecom data,
- Docker for containerized deployment.

---

## 9. Demo and Verification Steps

### Start the Application
```bash
.venv\Scripts\Activate.ps1
python agent.py
```

### Example Test Requests
Try the following prompts:
- Identify customers with critical churn risk based on contract months left and dropped calls.
- Find premium customers with high monthly fees and zero contract months remaining.
- Locate failing base stations and related unresolved complaints.

### Guardrail Test
You can also test the safety filter with a non-business request:
```text
Hello agent, can you write a chocolate cake recipe for me?
```

The agent should respond with a restricted-access message and not proceed to the database workflow.

### Session Exit
```text
exit
```

---

## 10. Useful References

- Python: https://www.python.org/
- LibreDB Studio: https://libredb.org/
- Groq: https://groq.com/
- xAI: https://x.ai/
