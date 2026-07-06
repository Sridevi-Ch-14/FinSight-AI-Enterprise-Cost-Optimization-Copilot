# FinSight AI - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Option 1: Docker (Recommended)

1. **Ensure Docker is running**
   ```bash
   docker --version
   docker compose version
   ```

2. **Start the application**
   ```bash
   docker compose up -d
   ```

3. **Wait for services to be ready** (30-60 seconds)
   ```bash
   docker compose logs -f
   ```

4. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

5. **Upload sample data**
   - Go to http://localhost:5173/upload
   - Upload files from `database/` folder:
     - `sample_spend.csv`
     - `sample_subscriptions.csv`
     - `sample_contracts.csv`

6. **Explore the platform**
   - Dashboard: View spend analytics
   - Recommendations: See cost optimization opportunities
   - Finance Copilot: Ask natural language questions

### Option 2: Local Development

#### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start MySQL (Docker)
docker run -d --name finsight-mysql -p 3306:3306 -e MYSQL_ROOT_PASSWORD=password -e MYSQL_DATABASE=finsight_db mysql:8.0

# Wait 10 seconds for MySQL to start

# Create .env file
echo DATABASE_URL=mysql+pymysql://root:password@localhost:3306/finsight_db > .env

# Initialize database
python -c "from app.config.database import engine, Base; from app.models.models import *; Base.metadata.create_all(bind=engine)"

# Start backend
uvicorn app.main:app --reload
```

Backend will run on http://localhost:8000

#### Frontend Setup

```bash
# Open new terminal
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will run on http://localhost:5173

## 📊 Test the Platform

### 1. Upload Sample Data

Navigate to Upload page and upload the three CSV files from `database/` folder.

### 2. View Dashboard

Check the dashboard to see:
- Total spend: ~₹50L
- Identified savings: ~₹15-20L
- Redundant vendors: 3-4 categories
- Charts and visualizations

### 3. Check Recommendations

View cost optimization recommendations:
- Vendor consolidation opportunities
- License optimization suggestions
- Contract renewal alerts

### 4. Try Finance Copilot

Ask questions like:
- "Top 5 vendors by annual spend"
- "Which categories have redundancy"
- "List renewals in next 90 days"
- "Spend by department"

## 🛠️ Troubleshooting

### MySQL Connection Error

If backend can't connect to MySQL:

```bash
# Check MySQL is running
docker ps | grep mysql

# Check MySQL logs
docker logs finsight-mysql

# Restart MySQL
docker restart finsight-mysql
```

### Port Already in Use

If ports 3306, 8000, or 5173 are in use:

```bash
# Find process using port (Windows)
netstat -ano | findstr :8000

# Kill process (Windows)
taskkill /PID <PID> /F

# Or change ports in docker-compose.yml
```

### Frontend Build Errors

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Backend Import Errors

```bash
cd backend
pip install --upgrade -r requirements.txt
```

## 📝 Next Steps

1. **Customize vendor categories** - Edit `backend/app/utils/vendor_utils.py`
2. **Add more alternatives** - Edit `backend/app/utils/alternatives.py`
3. **Extend Text-to-SQL** - Add patterns in `backend/app/services/text_to_sql.py`
4. **Customize UI** - Modify components in `frontend/src/components/`

## 🎯 Key Features to Explore

✅ Vendor spend analytics
✅ Redundancy detection
✅ Alternative recommendations
✅ Contract renewal tracking
✅ Natural language queries
✅ Executive dashboards

## 📞 Need Help?

Check the main README.md for detailed documentation.

---

**Happy Cost Optimizing! 💰**
