# 💰 Wasteless UI - Web Interface

<div align="center">

**The control center for autonomous cloud cost optimization**

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-green.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red.svg)](https://streamlit.io/)
[![Status](https://img.shields.io/badge/Status-MVP-yellow.svg)]()

*Stop monitoring waste. Start eliminating it.*

**This is the web UI.** For the backend engine, see [wasteless](https://github.com/wastelessio/wasteless).

[Features](#-features) • [Quick Start](#-quick-start) • [Screenshots](#-screenshots) • [Documentation](#-documentation)

</div>

---

## 🎯 What is Wasteless UI?

**Wasteless UI** is the web-based command center for the Wasteless cloud optimization platform. It transforms complex cost data into actionable insights and puts the power of autonomous remediation at your fingertips.

### The Problem We Solve

Cloud teams today face a dilemma:
- ❌ **Cost monitoring tools** show you the waste but don't fix it
- ❌ **Manual optimization** is time-consuming and error-prone
- ❌ **Command-line tools** require technical expertise
- ❌ **No visibility** into ROI or verified savings

### Our Solution

Wasteless UI provides:
- ✅ **One-click approvals** for cost optimizations
- ✅ **Real-time dashboards** for CFOs and DevOps
- ✅ **Complete audit trail** of all actions
- ✅ **Verified savings tracking** with before/after proof
- ✅ **Intelligent safeguards** to prevent accidents

---

## ✨ Features

### 🏠 Executive Dashboard
Real-time KPIs showing potential and realized savings, waste detection trends, and optimization success rates.

### 📋 Smart Recommendations
AI-powered recommendations sorted by impact, with confidence scores and one-click approval workflows.

### 📊 Visual Analytics
Interactive charts showing:
- Cost trends over time
- Waste distribution by service
- Savings forecasts
- Optimization success metrics

### 📜 Complete Audit Trail
Every action logged with:
- Timestamp and executor
- Before/after states
- Success/failure status
- Rollback capabilities

### 🛡️ Safeguard Configuration
Multi-layer protection system:
- Tag-based whitelisting
- Confidence thresholds
- Blast radius limits
- Dry-run testing

### ⚡ Instant Actions
- **Approve** - Execute optimization with one click
- **Reject** - Dismiss recommendation with reason
- **Dry-run** - Test action without real execution
- **Rollback** - Undo actions within 7 days

---

## 🚀 Quick Start

### ⚠️ Important: Backend Required

**This UI requires the wasteless backend to be running first.**

The UI connects to the PostgreSQL database managed by the backend engine.

### Prerequisites

Before starting, ensure you have:
- Python 3.11 or higher
- **[Wasteless backend](https://github.com/wastelessio/wasteless) installed and running** (PostgreSQL must be up)
- 5 minutes

### Step 1: Install Backend (if not done)

```bash
# If you haven't installed the backend yet:
git clone https://github.com/wastelessio/wasteless.git
cd wasteless

# Follow installation instructions in wasteless/README.md
# Ensure PostgreSQL is running: docker-compose up -d
```

### Step 2: Install UI

```bash
# 1. Clone this repository (in a different directory)
cd ..
git clone https://github.com/wastelessio/wasteless-ui.git
cd wasteless-ui

# 2. Set up Python environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure database connection
cp .env.template .env
# Edit .env - default values should work if backend is on localhost

# 5. Verify backend database is accessible
# The backend should be running: docker ps | grep wasteless-postgres

# 6. Launch the UI
./start.sh

# 7. Open your browser
open http://localhost:8888
```

**That's it!** You now have a beautiful interface on your cloud cost data.

### Typical Setup

Most users will have this structure:

```
~/projects/
├── wasteless/          # Backend engine (clone first)
│   ├── docker-compose.yml   # PostgreSQL + Metabase
│   ├── src/                 # Detection & execution code
│   └── venv/
└── wasteless-ui/       # Web UI (clone second)
    ├── app.py               # Streamlit app
    ├── pages/               # UI pages
    └── venv/
```

Both run simultaneously:
- Backend: PostgreSQL on port 5432, Metabase on port 3000
- UI: Streamlit on port 8888

---

## 📸 Screenshots

### Home Dashboard
*Real-time overview of potential savings and recent activity*

![Dashboard Preview](https://via.placeholder.com/1200x600/667eea/ffffff?text=Wasteless+Dashboard+Preview)

### Recommendations Manager
*Filter, sort, and approve optimizations with confidence*

![Recommendations Preview](https://via.placeholder.com/1200x600/764ba2/ffffff?text=Recommendations+Manager)

---

## 🏗️ Architecture

### Complete System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     wasteless Backend                        │
│  ┌────────────┐  ┌──────────┐  ┌──────────┐                 │
│  │ Collectors │→ │ Detectors│→ │Remediators│                │
│  └────────────┘  └──────────┘  └──────────┘                 │
│         │              │              │                       │
│         ↓              ↓              ↓                       │
│  ┌───────────────────────────────────────────┐               │
│  │      PostgreSQL Database                  │               │
│  │  • ec2_metrics                            │               │
│  │  • waste_detected                         │               │
│  │  • recommendations                        │               │
│  │  • actions_log                            │               │
│  │  • savings_realized                       │               │
│  └────────────┬──────────────────────────────┘               │
└───────────────┼──────────────────────────────────────────────┘
                │
                │ SQL Queries (Read/Write)
                │
                ↓
┌──────────────────────────────────────────────────────────────┐
│                  wasteless-ui (This Repo)                    │
│                                                              │
│  ┌──────────────┐  ┌──────────────────────┐                 │
│  │  Streamlit   │  │   Interactive Pages  │                 │
│  │  Web Server  │  │  • Dashboard         │                 │
│  │ (Port 8888)  │  │  • Recommendations   │                 │
│  │              │  │  • History           │                 │
│  │              │  │  • Settings          │                 │
│  └──────────────┘  └──────────────────────┘                 │
└──────────────────────────────────────────────────────────────┘
```

### Data Flow
1. **Backend** collects metrics from AWS → stores in PostgreSQL
2. **Backend** detects waste → creates recommendations in DB
3. **UI** queries PostgreSQL → displays data in web interface
4. **User** reviews and approves recommendations via UI
5. **Backend** executes actions → updates status in DB
6. **UI** shows updated results → complete audit trail

### Why Two Repositories?

| Aspect | Reasoning |
|--------|-----------|
| **Separation of Concerns** | Backend = data processing, UI = presentation |
| **Independent Deployment** | Can run backend without UI (CLI-only) |
| **Technology Stack** | Backend uses boto3/pandas, UI uses Streamlit |
| **Development** | Different teams can work independently |
| **Scalability** | Can add multiple UIs (web, mobile, CLI) |

---

## 📖 Documentation

### Configuration

The UI connects to your Wasteless PostgreSQL database. Configure credentials in `.env`:

```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=wasteless
DB_USER=wasteless
DB_PASSWORD=wasteless_dev_2025

# UI Configuration
STREAMLIT_SERVER_PORT=8888
STREAMLIT_SERVER_ADDRESS=localhost
```

### Pages Overview

| Page | Purpose | Key Features |
|------|---------|--------------|
| 🏠 **Home** | Quick overview | KPIs, recent activity, quick actions |
| 📊 **Dashboard** | Executive insights | Charts, trends, forecasts |
| 📋 **Recommendations** | Action center | Filter, approve, reject, dry-run |
| 📜 **History** | Audit trail | Complete log, rollback options |
| ⚙️ **Settings** | Configuration | Safeguards, whitelists, schedules |

### Running the Application

```bash
# Standard start (port 8888)
./start.sh

# Manual start with custom settings
streamlit run app.py --server.port 3000

# Background mode
nohup streamlit run app.py --server.port 8888 &

# Check if running
lsof -i :8888
```

### Stopping the Application

```bash
# Find the process
lsof -i :8888 | grep LISTEN

# Kill it
kill -9 <PID>

# Or use Ctrl+C in the terminal where it's running
```

---

## 🛠️ Development

### Project Structure

```
wasteless-ui/
├── app.py                      # Main entry point (Home page)
├── pages/                      # Multi-page Streamlit app
│   ├── 1_📊_Dashboard.py      # Executive dashboard
│   ├── 2_📋_Recommendations.py # Recommendation manager
│   ├── 3_📜_History.py        # Action history
│   └── 4_⚙️_Settings.py       # Configuration panel
├── start.sh                    # Quick start script
├── requirements.txt            # Python dependencies
├── .env.template               # Environment template
├── .env                        # Local config (gitignored)
├── .gitignore
└── README.md
```

### Adding Custom Pages

Streamlit automatically discovers pages in the `pages/` directory:

```python
# pages/5_📈_Custom_Analytics.py
import streamlit as st

st.set_page_config(page_title="Custom Analytics", page_icon="📈")
st.title("📈 Custom Analytics")

# Your custom code here
```

The page will appear in the sidebar navigation automatically.

### Database Queries

All pages use the shared database connection:

```python
from app import get_db_connection
import pandas as pd

conn = get_db_connection()
df = pd.read_sql("SELECT * FROM recommendations WHERE status='pending'", conn)
st.dataframe(df)
```

### Customizing Styles

Add custom CSS in any page:

```python
st.markdown("""
<style>
    .custom-metric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
    }
</style>
""", unsafe_allow_html=True)
```

---

## 🚢 Deployment

### Local Development
```bash
streamlit run app.py --server.port 8888
```

### Docker (Coming Soon)
```bash
docker build -t wasteless-ui .
docker run -p 8888:8888 wasteless-ui
```

### Streamlit Cloud (Free Hosting)
1. Push to GitHub
2. Connect to [Streamlit Cloud](https://streamlit.io/cloud)
3. Deploy in one click
4. Set environment variables in dashboard

### Production Considerations
- Use environment-specific `.env` files
- Enable HTTPS with reverse proxy (nginx)
- Set up monitoring and logging
- Configure backup database connections
- Implement rate limiting

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Ways to Contribute
- 🐛 Report bugs via [GitHub Issues](https://github.com/wastelessio/wasteless-ui/issues)
- 💡 Suggest features or improvements
- 📝 Improve documentation
- 🎨 Enhance UI/UX
- 🧪 Add tests
- 🌍 Translate to other languages

### Development Workflow
```bash
# 1. Fork the repository
# 2. Create a feature branch
git checkout -b feature/amazing-feature

# 3. Make your changes
# 4. Test thoroughly
streamlit run app.py

# 5. Commit with clear message
git commit -m "Add amazing feature: description"

# 6. Push to your fork
git push origin feature/amazing-feature

# 7. Open a Pull Request
```

### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable names
- Add docstrings to functions
- Keep pages under 300 lines
- Test with sample data

---

## 🔗 Related Projects

Part of the **Wasteless ecosystem**:

- **[wasteless](https://github.com/wastelessio/wasteless)** - Main detection & execution engine
- **[wasteless-terraform](https://github.com/wastelessio/wasteless-terraform)** - Infrastructure as code (planned)
- **[wasteless-cli](https://github.com/wastelessio/wasteless-cli)** - Command-line interface (planned)

---

## 📊 Roadmap

### ✅ Phase 1 - MVP (Current)
- [x] Home dashboard with KPIs
- [x] Recommendations list with filters
- [x] Action history viewer
- [x] Settings configuration panel
- [x] PostgreSQL integration

### 🔄 Phase 2 - Enhanced UX (Next 2 weeks)
- [ ] Advanced filtering (date ranges, tags)
- [ ] Batch operations (approve multiple)
- [ ] Detailed instance drill-down
- [ ] Export to CSV/PDF
- [ ] Dark mode theme

### 📅 Phase 3 - Execution (Month 2)
- [ ] Direct EC2Remediator integration
- [ ] Real-time action progress
- [ ] One-click rollback
- [ ] Slack/Email notifications
- [ ] Scheduled reports

### 📅 Phase 4 - Enterprise (Month 3+)
- [ ] User authentication (OAuth)
- [ ] Role-based access control
- [ ] Multi-account support
- [ ] Custom dashboards
- [ ] API access

---

## 🛡️ Security

### Data Protection
- ✅ Read-only database access by default
- ✅ No credentials stored in code
- ✅ Environment variables for secrets
- ✅ Local execution (no data sent externally)

### Best Practices
- Always use `.env` for sensitive data
- Never commit `.env` to version control
- Use VPN when accessing production databases
- Review all recommendations before approving
- Test with dry-run first

**Found a security issue?** Please email security@wasteless.io (don't open a public issue).

---

## 📄 License

**Apache License 2.0**

This project is free and open source forever. See [LICENSE](LICENSE) for details.

### Why Apache 2.0?
- ✅ Maximum adoption (permissive)
- ✅ Commercial use allowed
- ✅ Patent protection included
- ✅ Enterprise-friendly
- ✅ No copyleft restrictions

---

## 💬 Support & Community

### Get Help
- 📧 **Email**: wasteless.io.entreprise@gmail.com
- 💬 **Issues**: [GitHub Issues](https://github.com/wastelessio/wasteless-ui/issues)
- 📚 **Documentation**: [Main Repo Docs](https://github.com/wastelessio/wasteless)

### Stay Updated
- ⭐ Star this repo to show support
- 👀 Watch for updates
- 🐦 Follow us on Twitter (coming soon)
- 📰 Subscribe to our newsletter (coming soon)

---

## 🙏 Acknowledgments

Built with these amazing open source tools:
- [Streamlit](https://streamlit.io/) - The fastest way to build data apps
- [Plotly](https://plotly.com/) - Interactive visualizations
- [PostgreSQL](https://www.postgresql.org/) - The world's most advanced database
- [pandas](https://pandas.pydata.org/) - Data analysis powerhouse

---

## 📈 Status

**Current Version**: v0.1.0-alpha
**Status**: Active Development
**First Release**: January 2026
**Production Ready**: Q2 2026 (planned)

---

<div align="center">

### 🚀 Ready to optimize your cloud costs?

**[Get Started](#-quick-start)** • **[View Demo](http://localhost:8888)** • **[Read Docs](#-documentation)**

---

<sub>Built with ❤️ by the Wasteless team for CFOs and DevOps engineers who demand results.</sub>

**Stop monitoring waste. Start eliminating it.**

</div>
