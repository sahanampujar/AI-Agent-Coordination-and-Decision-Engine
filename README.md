# ✦ Enterprise Workflow Platform with Decision Automation

> **AI-powered multi-agent workflow orchestration for enterprise business automation, decision intelligence, human authorization, auditability, and business reporting.**

---

## 📌 Project Overview

The **Enterprise Workflow Platform with Decision Automation** is a Multi-Agent AI platform designed to automate and coordinate enterprise business workflows.

The platform accepts a business request, builds an executable workflow, coordinates specialized AI agents, selects intelligent tools when required, performs business analysis, makes a structured decision, and generates a final business response.

The system also supports **Human-in-the-Loop authorization**, persistent workflow tracking, audit logging, dashboards, and multi-format report generation.

### Core Workflow

```text
Business Request
       │
       ▼
Planner Agent
       │
       ▼
Intelligent Tool / Research
       │
       ▼
Analysis Agent
       │
       ▼
Decision Engine
       │
       ├───────────────┐
       │               │
       ▼               ▼
   APPROVE          REVIEW
       │               │
       │         Human Authorization
       │          ┌────┴────┐
       │          ▼         ▼
       │       APPROVE    REJECT
       │          │         │
       └──────────┼─────────┘
                  ▼
           Response Agent
                  │
                  ▼
         Business Reports
       PDF / DOCX / XLSX / JSON

🚀 Key Features
🤖 Multi-Agent AI Workflow

The platform coordinates multiple specialized agents:

🧠 Planner Agent
🔍 Research Agent
📊 Analysis Agent
⚖️ Decision Engine
📄 Response Agent
🤝 Agent Coordinator

Each agent performs a specific stage of the workflow and passes its results to the next stage.

🛠 Intelligent Tool Integration

The platform contains an intelligent tool-selection layer.

Available Tools
🧮 Calculator Tool
🔍 Search Tool
🌦 Weather Tool
📄 File Tool
⚙️ Intelligent Tool Selector

The system selects the appropriate tool according to the business request.

Example

Input:

22+1

Workflow:

Planner
   ↓
Calculator Tool
   ↓
Analysis
   ↓
Decision
   ↓
Response

Result:

23

The Calculator Tool uses an AST-based evaluator rather than Python's eval(), preventing arbitrary code execution.

🧠 Memory Management

The platform supports multiple memory mechanisms for agent collaboration and continuity.

💬 Conversation Memory

Stores the current conversation context between the user and the system.

🤝 Shared Memory

Allows agents to exchange intermediate workflow information such as:

Plan
Tool Output
Research
Analysis
Decision
Final Response
💾 Long-Term Memory

Stores conversation history for persistence across sessions.

The project includes context-aware agent communication and memory management functionality.

⚖️ Decision Intelligence

The Decision Engine evaluates the business analysis and produces one of four structured decisions:

APPROVE
REJECT
REVIEW
RECOMMEND

The decision output includes:

Decision
Decision Reason
Key Factors
Risks
Recommended Action
Confidence Level

The system parses the structured decision and routes the workflow accordingly.

🧑‍⚖️ Human-in-the-Loop Authorization

When the Decision Engine returns:

REVIEW

the workflow is paused instead of automatically continuing.

The workflow status becomes:

PENDING_REVIEW

A reviewer can then approve or reject the request.

Approval Flow
Decision = REVIEW
       ↓
PENDING_REVIEW
       ↓
Human Authorization
       ↓
APPROVE
       ↓
Workflow Resumes
       ↓
Response
       ↓
COMPLETED
Rejection Flow
Decision = REVIEW
       ↓
PENDING_REVIEW
       ↓
Human Authorization
       ↓
REJECT
       ↓
REJECTED

Human approval and rejection are available through the Streamlit Approvals page and REST API.

🗄️ Persistent Workflow Database

The platform uses SQLite by default and supports a configurable database URL.

The persistence layer tracks entities including:

Workflows
Workflow Runs
Workflow Steps
Decisions
Approvals
Audit Logs
Reports
Users

The database configuration is controlled through DATABASE_URL.

📊 Dashboard

The platform provides an enterprise workflow dashboard for monitoring system activity.

Dashboard Metrics
Total Workflows
Successful Runs
Failed Runs
Pending Reviews
Average Execution Time
Approval Rate
Rejection Rate
Review Rate
Step Failure Counts
Recent Workflow History

The dashboard is available through:
ui/pages/1_Dashboard.py

👤 Human Approvals Dashboard

Pending human decisions are available through:

ui/pages/2_Approvals.py

The approval interface provides:

Workflow status
Business request
Analysis
Decision reasoning
Reviewer name
Review comment
Approve action
Reject action

The approval state is persisted in the database so that pending workflows can be reviewed independently of the session that created them.

📜 Audit & Traceability

The platform records workflow activity for traceability and compliance-oriented monitoring.

Audit records can include:

Timestamp
Step
Status
Decision
User
Error

This allows a workflow run to be traced from execution through decision making and human authorization.

The main application includes an Audit Log tab, and audit records are also available through the REST API.

📑 Multi-Format Reporting

The system generates reports for individual workflow runs in:

📄 PDF
📝 DOCX
📊 XLSX
🗂 JSON

Reports are generated and stored per run to prevent different workflow executions from overwriting one another.

The reporting layer is coordinated through:

reports/report_manager.py

and generated reports are stored under:

reports_output/{run_id}.{extension}

The system also registers reports in the database.

🌐 REST API

The project includes a FastAPI service for programmatic workflow management.

Available Endpoints
GET  /api/health

POST /api/workflows
GET  /api/workflows
GET  /api/workflows/{id}

POST /api/workflows/{id}/execute
POST /api/workflows/execute

GET  /api/runs
GET  /api/runs/{id}

GET  /api/decisions/{id}

GET  /api/approvals/pending
POST /api/runs/{run_id}/decision

POST /api/runs/{run_id}/reports
GET  /api/runs/{run_id}/reports/{type}/download

GET  /api/audit-logs
GET  /api/dashboard/metrics

The API can optionally use bearer-token authentication through API_AUTH_TOKEN.

🔒 Reliability & Security

The platform includes several reliability and security mechanisms.

Workflow Reliability
Per-step execution timeout
Configurable retry handling
Failure propagation
Honest workflow status reporting
Workflow validation
Human-review pause and resume

The workflow is not marked COMPLETED unless all required steps successfully complete.

Calculator Security

The Calculator Tool avoids Python eval() and uses an AST-based evaluator with a restricted set of arithmetic operations.

API Security

Optional bearer-token authentication is available using:

API_AUTH_TOKEN=your_secure_token
Secret Management

Sensitive values such as API keys should be stored in .env and never committed to Git.

🤖 Supported AI Providers

The platform supports both cloud and local LLM execution.

Gemini

Configure:

LLM_PROVIDER=gemini
GEMINI_API_KEY=YOUR_API_KEY
GEMINI_MODEL=gemini-2.5-flash-lite
Ollama

Configure:

LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.2:latest

This allows the project to use a cloud-based Gemini model or a local Ollama model depending on the environment.

🏗️ System Architecture
                           ┌─────────────────────┐
                           │      Streamlit      │
                           │    Web Interface    │
                           └──────────┬──────────┘
                                      │
                                      ▼
                           ┌─────────────────────┐
                           │  Agent Coordinator  │
                           └──────────┬──────────┘
                                      │
              ┌───────────────────────┼───────────────────────┐
              │                       │                       │
              ▼                       ▼                       ▼
       Planner Agent          Intelligent Tools       Research Agent
                                      │
                                      ▼
                               Analysis Agent
                                      │
                                      ▼
                               Decision Engine
                                      │
                         ┌────────────┼────────────┐
                         │            │            │
                         ▼            ▼            ▼
                      APPROVE      REVIEW        REJECT
                                      │
                                      ▼
                            Human Authorization
                                      │
                                      ▼
                              Response Agent
                                      │
                                      ▼
                            Business Reports
                        PDF / DOCX / XLSX / JSON
                                      │
                                      ▼
                           SQLite + Audit Logs
🔄 Example Enterprise Workflow
Employee Leave Approval
Business Request
Automate employee leave approval workflow
Workflow
Planner
   ↓
Research
   ↓
Analysis
   ↓
Decision
   ↓
Response
High-Risk Request
Approve a high-risk employee leave request where human authorization is mandatory.
Result
Planner
   ↓
Research
   ↓
Analysis
   ↓
Decision = REVIEW
   ↓
Human Authorization
   ↓
Approve / Reject
🧮 Example Tool Workflow

Input:

22+1

The system detects that a calculator is required:

Planner
   ↓
Calculator
   ↓
Analysis
   ↓
Decision
   ↓
Response

Output:

Result: 23
🛠️ Technology Stack
Technology	Purpose
Python	Core application
LangChain	LLM and agent orchestration
Gemini API	Cloud LLM provider
Ollama	Local LLM provider
Streamlit	User interface
FastAPI	REST API
SQLite	Persistent storage
ReportLab	PDF generation
python-docx	DOCX generation
openpyxl	XLSX generation
Git	Version control
GitHub	Source-code repository
📂 Project Structure
AI-Agent-Coordination-and-Decision-Engine/
│
├── agents/
│   ├── planner_agent.py
│   ├── research_agent.py
│   ├── analysis_agent.py
│   └── response_agent.py
│
├── api/
│   └── main.py
│
├── core/
│   └── exceptions.py
│
├── database/
│   ├── models.py
│   └── repository.py
│
├── memory/
│   ├── conversation_memory.py
│   ├── shared_memory.py
│   ├── long_term_memory.py
│   └── history.json
│
├── prompts/
│
├── reports/
│   ├── pdf_generator.py
│   ├── docx_generator.py
│   ├── xlsx_generator.py
│   ├── json_generator.py
│   └── report_manager.py
│
├── tools/
│   ├── calculator.py
│   ├── search_tool.py
│   ├── weather_tool.py
│   ├── file_tool.py
│   └── tool_selector.py
│
├── workflows/
│   ├── coordinator.py
│   ├── workflow_builder.py
│   └── workflow_executor.py
│
├── ui/
│   ├── streamlit_app.py
│   └── pages/
│       ├── 1_Dashboard.py
│       └── 2_Approvals.py
│
├── tests/
│
├── config.py
├── requirements.txt
├── LICENSE
└── README.md
⚙️ Installation
1. Clone the Repository
git clone https://github.com/sahanampujar/AI-Agent-Coordination-and-Decision-Engine.git
cd AI-Agent-Coordination-and-Decision-Engine
2. Create Virtual Environment
Windows
python -m venv venv

Activate it:

.\venv\Scripts\Activate.ps1
3. Install Dependencies
python -m pip install -r requirements.txt
🔐 Environment Configuration

Create a .env file in the project root.

Gemini Configuration
LLM_PROVIDER=gemini
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
GEMINI_MODEL=gemini-2.5-flash-lite
Ollama Configuration
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.2:latest
Workflow Configuration
STEP_TIMEOUT_SECONDS=180
STEP_MAX_RETRIES=1
Database
DATABASE_URL=sqlite:///./enterprise_workflow.db
Optional API Security
API_AUTH_TOKEN=
Reports
REPORTS_OUTPUT_DIR=reports_output

Never commit your .env file or expose API keys publicly.

▶️ Running the Application
Streamlit Application
python -m streamlit run ui/streamlit_app.py

Open:

http://localhost:8501
🌐 Running the REST API
uvicorn api.main:app --reload --port 8000

Open the API documentation:

http://localhost:8000/docs
🧪 Testing

The project contains automated tests covering:

Agent execution
Agent failure handling
Tool selection
Calculator functionality
Calculator security
Workflow validation
Workflow execution
Retry handling
Timeout handling
Database persistence
Decision parsing
Human approval
Human rejection
API endpoints
Report generation
Audit logging
Dashboard metrics

Run the complete test suite:

python -m pytest tests/ -v
Current Test Status
47 passed

The tests are designed to mock LLM interactions, so the automated suite does not require real network calls.

🖥️ Streamlit Modules

The main Streamlit application provides:

🧠 Planner
🛠 Tool
🔍 Research
📊 Analysis
⚖️ Decision
🔄 Workflow
⚙️ Execution
🧠 Memory
🤝 Shared Memory
📄 Final Report
📜 Audit Log

The project also includes dedicated pages for:

📊 Dashboard
👤 Human Approvals
📈 Workflow Execution Metrics

Each workflow execution records metrics including:

Total Steps
Completed Steps
Failed Steps
Success Rate
Total Execution Time

Individual step logs record:

Step
Type
Status
Duration
Error
🏆 Enterprise Capabilities

The final platform combines:

✓ Multi-Agent AI
✓ Intelligent Tool Selection
✓ Workflow Automation
✓ Decision Intelligence
✓ Human-in-the-Loop
✓ Persistent Memory
✓ SQLite Persistence
✓ REST API
✓ Dashboard Monitoring
✓ Audit Logging
✓ Multi-format Reporting
✓ Retry & Timeout Handling
✓ Secure Calculator Execution
✓ Optional API Authentication
🐞 Important Reliability Improvements

The project includes fixes for false workflow completion and silent execution failures.

One important routing issue occurred because "research" contains "search" as a substring, which could incorrectly route a Research step to the Search Tool.

The workflow executor was updated to use exact step-type matching and safer word-boundary matching so that Research steps are routed correctly.

Agents also propagate execution errors instead of returning placeholder strings, allowing the workflow engine to report failures honestly.

📊 Project Milestones
✅ Milestone 1 — Multi-Agent Workflow
LangChain Setup
Ollama Integration
Planner Agent
Research Agent
Analysis Agent
Response Agent
Agent Coordinator
Streamlit UI
PDF Report Generation
GitHub Integration
✅ Milestone 2 — Tool Integration
Calculator Tool
Search Tool
Weather Tool
File Tool
Intelligent Tool Selector
Tool Invocation Workflow
Action Execution Validation
✅ Milestone 3 — Agent Coordination & Memory
Conversation Memory
Shared Memory
Long-Term Memory
Context-Aware Agents
Agent Communication
Memory Dashboard
Collaborative Workflow Validation
✅ Enterprise Platform Extensions
Reliable Workflow Execution
Retry and Timeout Handling
Persistent SQLite Database
Decision Engine
Human-in-the-Loop Approval
Human Rejection Flow
REST API
Dashboard
Approvals Page
Audit Log
PDF / DOCX / XLSX / JSON Reports
Security Improvements
Automated Test Suite
👩‍💻 Developed By

Sahana M Pujar

Information Science Engineering
Basaveshwar Engineering College, Bagalkote

📄 License

This project is distributed under the MIT License.

See the LICENSE file for the complete license terms.

🔗 Repository

GitHub:

https://github.com/sahanampujar/AI-Agent-Coordination-and-Decision-Engine


