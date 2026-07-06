# FinSight AI – Enterprise Cost Optimization Copilot

A production-grade SaaS platform for enterprise cost optimization, vendor consolidation, and spend intelligence.

## 🎯 Overview

FinSight AI is NOT a personal finance tracker. It's a corporate-level spend intelligence platform designed for:

- **CFOs** - Executive spend visibility and savings opportunities
- **Finance Teams** - Vendor spend analysis and optimization
- **Procurement** - Vendor consolidation and contract management
- **FinOps Teams** - SaaS subscription optimization
- **IT Leadership** - Shadow IT detection and license management

## 🚀 Key Features

### 1. Vendor Spend Intelligence
- Multi-department spend analysis
- Vendor normalization and categorization
- Spend visualization by vendor, department, and category

### 2. Vendor Consolidation Radar
- Detect overlapping tools (e.g., Zoom + Teams + Meet)
- Identify redundancy across departments
- Calculate consolidation savings

### 3. SaaS Subscription Optimization
- License tier optimization
- Over-provisioned seat detection
- Subscription sprawl analysis

### 4. Shadow IT Detection
- Identify unauthorized vendor purchases
- Department-level procurement analysis
- Risk assessment

### 5. Contract Renewal Management
- 90-day renewal alerts
- Auto-renew tracking
- Renegotiation opportunities

### 6. Price Benchmarking
- Compare against market rates
- Identify overpaying scenarios
- Vendor pricing intelligence

### 7. Alternative Recommendations
- Feature-parity alternatives
- Zero quality loss suggestions
- Risk-assessed switching options

### 8. Finance Copilot (Text-to-SQL)
- Natural language queries
- "Top 5 vendors by spend?"
- "Which categories have redundancy?"
- SQL transparency

### 9. Executive Reporting
- CFO-ready dashboards
- Savings roadmap
- Export to PDF/Excel

## 🏗️ Architecture

```
FinSight AI/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # REST endpoints
│   │   ├── services/    # Business logic
│   │   ├── models/      # SQLAlchemy models
│   │   ├── utils/       # Vendor normalization, alternatives
│   │   └── config/      # Database configuration
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/            # React + Vite frontend
│   ├── src/
│   │   ├── components/  # Reusable UI components
│   │   ├── pages/       # Page components
│   │   ├── utils/       # API client
│   │   └── lib/         # Utilities
│   ├── package.json
│   └── Dockerfile
├── database/            # MySQL schema and samples
│   ├── schema.sql
│   ├── sample_spend.csv
│   ├── sample_subscriptions.csv
│   └── sample_contracts.csv
└── docker-compose.yml
```

## 🛠️ Tech Stack

**Backend:**
- FastAPI (Python)
- SQLAlchemy ORM
- MySQL
- Pandas for CSV processing

**Frontend:**
- React 18
- Vite
- Tailwind CSS
- Recharts for visualizations
- Axios for API calls

**Database:**
- MySQL 8.0

**Deployment:**
- Docker & Docker Compose

## 📦 Installation

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)
- Node.js 18+ (for local development)

### Quick Start with Docker

1. **Clone the repository**
```bash
cd "FinSight AI – Enterprise Cost Optimization Copilot"
```

2. **Start all services**
```bash
docker-compose up -d
```

3. **Access the application**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Local Development Setup

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Start MySQL (via Docker or local)
docker run -d -p 3306:3306 -e MYSQL_ROOT_PASSWORD=password -e MYSQL_DATABASE=finsight_db mysql:8.0

# Run migrations
python -c "from app.config.database import engine, Base; from app.models.models import *; Base.metadata.create_all(bind=engine)"

# Start backend
uvicorn app.main:app --reload
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## 📊 Usage Guide

### 1. Upload Data

Navigate to **Upload Data** page and upload:

- **Vendor Spend CSV**: Company-wide vendor transactions
- **SaaS Subscriptions CSV**: License and seat information
- **Contract Renewals CSV**: Renewal dates and values

Sample CSV files are provided in `database/` folder.

### 2. View Dashboard

The dashboard shows:
- Total annual spend
- Identified savings potential
- Redundant vendor count
- Upcoming renewals
- Spend charts by vendor, department, category

### 3. Vendor Consolidation

View overlapping tools in same categories:
- Multiple communication tools (Zoom, Teams, Slack)
- Multiple project management tools (Jira, Asana, Trello)
- Consolidation recommendations

### 4. Recommendations

Ranked list of cost-cutting opportunities:
- Projected savings
- Risk level
- Alternative vendors
- Feature parity explanation

### 5. Contract Renewals

Track upcoming renewals:
- 90-day visibility
- Auto-renew flags
- Renegotiation opportunities

### 6. Finance Copilot

Ask questions in natural language:
- "Top 5 vendors by annual spend"
- "Which categories have redundancy"
- "List renewals in next 90 days"
- "Spend by department"

View generated SQL and results.

## 🔌 API Endpoints

### Upload
- `POST /api/upload/spend` - Upload vendor spend CSV
- `POST /api/upload/subscriptions` - Upload subscriptions CSV
- `POST /api/upload/contracts` - Upload contracts CSV

### Analytics
- `GET /api/dashboard/summary` - Dashboard summary data
- `GET /api/vendors/redundancy` - Vendor consolidation opportunities
- `GET /api/recommendations/top` - Top cost optimization recommendations
- `GET /api/contracts/upcoming-renewals` - Upcoming contract renewals

### Copilot
- `POST /api/copilot/query` - Natural language query
- `GET /api/copilot/history` - Query history

### Reports
- `GET /api/reports/export` - Export executive report

## 🎨 UI Features

- **Enterprise-grade design** - Professional, not childish
- **Responsive layout** - Works on all screen sizes
- **Dark sidebar navigation** - Clean and modern
- **Interactive charts** - Recharts visualizations
- **Color-coded risk levels** - Visual risk assessment
- **Real-time updates** - Instant feedback on uploads

## 🔐 Security

- No personal bank statements required
- Company-safe data only
- SQL injection protection
- Input validation
- Secure file uploads

## 📈 Business Impact

Target savings: **Multi-crore annual cost reduction**

Example scenarios:
- Consolidate 3 communication tools → ₹1.2 Cr/year
- Optimize Adobe licenses → ₹60L/year
- Renegotiate Salesforce contract → ₹80L/year
- Replace Datadog with Grafana → ₹1.08 Cr/year

## 🧪 Testing

Use the provided sample data:
```bash
# Sample files in database/ folder
- sample_spend.csv
- sample_subscriptions.csv
- sample_contracts.csv
```

Upload these files to see the platform in action.

## 🚢 Deployment

### Production Build

**Backend:**
```bash
cd backend
docker build -t finsight-backend .
docker run -p 8000:8000 finsight-backend
```

**Frontend:**
```bash
cd frontend
npm run build
# Serve dist/ folder with nginx or similar
```

### Environment Variables

**Backend (.env):**
```
DATABASE_URL=mysql+pymysql://user:password@host:3306/finsight_db
```

## 📝 License

Enterprise Edition - All Rights Reserved

## 🤝 Support

For enterprise support and customization, contact your system administrator.

---

**FinSight AI** - Intelligent Cost Optimization for Modern Enterprises
