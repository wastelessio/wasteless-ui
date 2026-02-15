# Wasteless

**Open-source cloud cost optimization. Detect idle EC2 instances. Remediate with one click.**

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-green.svg)](https://www.python.org/)

---

## What it does

Wasteless monitors your AWS EC2 instances, detects idle resources, and lets you stop or terminate them with confidence.

- **Detect** - Continuously monitors CPU, memory, network metrics
- **Analyze** - Confidence scoring identifies true waste vs. low-usage workloads
- **Remediate** - One-click stop/terminate with dry-run mode for safety

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL (via Docker)
- AWS credentials configured (`aws configure`)

### 1. Clone both repos

```bash
# Backend (required)
git clone https://github.com/wastelessio/wasteless.git
cd wasteless
docker-compose up -d  # Starts PostgreSQL
cd ..

# UI
git clone https://github.com/wastelessio/wasteless-ui.git
cd wasteless-ui
```

### 2. Install and run

```bash
# Install
./install.sh

# Start
./start.sh

# Open
open http://localhost:8888
```

**That's it.** You should see the dashboard.

## Screenshots

### Dashboard
Real-time KPIs and savings metrics.

### Recommendations
Approve or reject actions with confidence scores.

### Cloud Resources
Live inventory of all EC2 instances across regions.

## Features

| Feature | Description |
|---------|-------------|
| **Dashboard** | KPIs, savings metrics, recommendations overview |
| **Recommendations** | Confidence-scored actions, bulk approve/reject |
| **Dry-Run Mode** | Test actions safely before production |
| **Auto-Sync** | Background sync every 5 minutes with AWS |
| **Action History** | Complete audit trail of all remediations |
| **Cloud Inventory** | Live view of EC2 instances across regions |

## Configuration

Edit `.env`:

```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=wasteless
DB_USER=wasteless
DB_PASSWORD=your_password
```

## Project Structure

```
wasteless-ui/
├── main.py              # FastAPI application
├── templates/           # Jinja2 HTML templates
├── utils/               # Database, config, remediator
├── start.sh             # Start script
└── requirements.txt
```

## How it works

```
AWS CloudWatch → wasteless (backend) → PostgreSQL → wasteless-ui
                     │                      │
                     └── Detects waste ─────┘
                                            │
                          User approves ────┘
                                            │
                     └── Executes action ───┘
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Home dashboard |
| `/dashboard` | GET | Detailed metrics |
| `/recommendations` | GET | Pending recommendations |
| `/history` | GET | Action history |
| `/settings` | GET | Configuration |
| `/cloud-resources` | GET | EC2 inventory |
| `/api/actions` | POST | Execute approve/reject |

## Development

```bash
# Run with hot reload
uvicorn main:app --reload --port 8888

# Run tests
python run_tests.py
```

## License

Apache 2.0 - Free for commercial use.

## Links

- **Backend**: [wastelessio/wasteless](https://github.com/wastelessio/wasteless)
- **Issues**: [GitHub Issues](https://github.com/wastelessio/wasteless-ui/issues)
- **Email**: wasteless.io.entreprise@gmail.com
