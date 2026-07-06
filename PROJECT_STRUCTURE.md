# FinSight AI - Project Structure

## Complete File Tree

```
FinSight AI – Enterprise Cost Optimization Copilot/
│
├── README.md                          # Main documentation
├── QUICKSTART.md                      # Quick start guide
├── .gitignore                         # Git ignore rules
├── docker-compose.yml                 # Docker orchestration
│
├── backend/                           # FastAPI Backend
│   ├── Dockerfile                     # Backend container
│   ├── requirements.txt               # Python dependencies
│   ├── .env.example                   # Environment template
│   └── app/
│       ├── __init__.py
│       ├── main.py                    # FastAPI application entry
│       │
│       ├── api/                       # REST API endpoints
│       │   ├── __init__.py
│       │   └── routes.py              # All API routes
│       │
│       ├── services/                  # Business logic layer
│       │   ├── __init__.py
│       │   ├── upload_service.py      # CSV upload processing
│       │   ├── recommendation_engine.py # Cost optimization logic
│       │   └── text_to_sql.py         # Natural language to SQL
│       │
│       ├── models/                    # Database models
│       │   ├── __init__.py
│       │   └── models.py              # SQLAlchemy ORM models
│       │
│       ├── utils/                     # Utility functions
│       │   ├── __init__.py
│       │   ├── vendor_utils.py        # Vendor normalization
│       │   └── alternatives.py        # Alternative recommendations KB
│       │
│       └── config/                    # Configuration
│           ├── __init__.py
│           └── database.py            # Database connection
│
├── frontend/                          # React Frontend
│   ├── Dockerfile                     # Frontend container
│   ├── package.json                   # Node dependencies
│   ├── vite.config.js                 # Vite configuration
│   ├── tailwind.config.js             # Tailwind CSS config
│   ├── postcss.config.js              # PostCSS config
│   ├── index.html                     # HTML entry point
│   │
│   └── src/
│       ├── main.jsx                   # React entry point
│       ├── App.jsx                    # Main app component
│       ├── index.css                  # Global styles
│       │
│       ├── components/                # Reusable UI components
│       │   ├── Card.jsx               # Card component
│       │   ├── Button.jsx             # Button component
│       │   └── Sidebar.jsx            # Navigation sidebar
│       │
│       ├── pages/                     # Page components
│       │   ├── Dashboard.jsx          # Main dashboard
│       │   ├── UploadPage.jsx         # Data upload
│       │   ├── ConsolidationPage.jsx  # Vendor consolidation
│       │   ├── RecommendationsPage.jsx # Cost recommendations
│       │   ├── RenewalsPage.jsx       # Contract renewals
│       │   ├── CopilotPage.jsx        # Finance copilot
│       │   └── OtherPages.jsx         # Subscriptions & Reports
│       │
│       ├── utils/                     # Utilities
│       │   └── api.js                 # API client
│       │
│       └── lib/                       # Libraries
│           └── utils.js               # Helper functions
│
└── database/                          # Database files
    ├── schema.sql                     # MySQL schema
    ├── sample_spend.csv               # Sample vendor spend data
    ├── sample_subscriptions.csv       # Sample subscription data
    └── sample_contracts.csv           # Sample contract data
```

## Key Components

### Backend Architecture

**API Layer** (`api/routes.py`)
- Upload endpoints for CSV files
- Dashboard summary analytics
- Vendor redundancy detection
- Recommendations retrieval
- Contract renewal tracking
- Finance copilot queries

**Service Layer**
- `upload_service.py` - Processes CSV uploads, normalizes vendors
- `recommendation_engine.py` - Generates cost optimization recommendations
- `text_to_sql.py` - Converts natural language to SQL queries

**Data Layer** (`models/models.py`)
- Department, Vendor, SpendTransaction
- Subscription, Contract
- Recommendation, ChatQuery

**Utilities**
- `vendor_utils.py` - Vendor name normalization and categorization
- `alternatives.py` - Alternative vendor recommendations knowledge base

### Frontend Architecture

**Pages**
- Dashboard - Spend analytics and visualizations
- Upload - CSV file upload interface
- Consolidation - Vendor redundancy analysis
- Recommendations - Cost optimization opportunities
- Renewals - Contract renewal tracking
- Copilot - Natural language query interface

**Components**
- Card, Button - Reusable UI components
- Sidebar - Navigation menu

**API Client** (`utils/api.js`)
- Axios-based API communication
- All backend endpoint wrappers

### Database Schema

**Core Tables**
- `departments` - Company departments
- `vendors` - Vendor master with normalization
- `spend_transactions` - All vendor spend records
- `subscriptions` - SaaS subscription details
- `contracts` - Contract renewal information
- `recommendations` - Generated cost optimization recommendations
- `chat_queries` - Finance copilot query history

## Data Flow

1. **Upload** → CSV files uploaded via frontend
2. **Processing** → Backend normalizes vendors, categorizes spend
3. **Analysis** → Recommendation engine detects opportunities
4. **Visualization** → Frontend displays insights and charts
5. **Interaction** → Users query via Finance Copilot
6. **Export** → Generate executive reports

## Technology Stack

**Backend**
- FastAPI - Modern Python web framework
- SQLAlchemy - ORM for database operations
- Pandas - CSV processing
- PyMySQL - MySQL connector

**Frontend**
- React 18 - UI library
- Vite - Build tool
- Tailwind CSS - Styling
- Recharts - Data visualization
- Axios - HTTP client

**Database**
- MySQL 8.0 - Relational database

**DevOps**
- Docker - Containerization
- Docker Compose - Multi-container orchestration

## API Endpoints

### Upload
- `POST /api/upload/spend`
- `POST /api/upload/subscriptions`
- `POST /api/upload/contracts`

### Analytics
- `GET /api/dashboard/summary`
- `GET /api/vendors/redundancy`
- `GET /api/recommendations/top`
- `GET /api/contracts/upcoming-renewals`

### Copilot
- `POST /api/copilot/query`
- `GET /api/copilot/history`

### Reports
- `GET /api/reports/export`

## Environment Configuration

**Backend** (`.env`)
```
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/finsight_db
```

**Frontend** (Vite proxy)
- API proxied through Vite dev server
- Production: Configure CORS in FastAPI

## Deployment

**Development**
```bash
docker-compose up -d
```

**Production**
- Build Docker images
- Deploy to cloud (AWS, Azure, GCP)
- Configure environment variables
- Set up MySQL instance
- Enable HTTPS

## Customization Points

1. **Vendor Categories** - `backend/app/utils/vendor_utils.py`
2. **Alternative Recommendations** - `backend/app/utils/alternatives.py`
3. **Text-to-SQL Patterns** - `backend/app/services/text_to_sql.py`
4. **UI Theme** - `frontend/tailwind.config.js`
5. **Recommendation Logic** - `backend/app/services/recommendation_engine.py`

---

**FinSight AI** - Enterprise-Grade Cost Optimization Platform
