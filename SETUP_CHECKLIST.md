# FinSight AI - Setup Checklist & Verification

## ✅ Pre-Installation Checklist

### System Requirements
- [ ] Docker Desktop installed and running
- [ ] Docker Compose available (v2.0+)
- [ ] 4GB RAM available
- [ ] 2GB disk space available
- [ ] Ports 3306, 8000, 5173 available

### Optional (for local development)
- [ ] Python 3.11+ installed
- [ ] Node.js 18+ installed
- [ ] MySQL 8.0 (if not using Docker)

## 🚀 Installation Steps

### Step 1: Verify Docker
```bash
docker --version
# Expected: Docker version 20.10.0 or higher

docker-compose --version
# Expected: Docker Compose version 2.0.0 or higher
```

### Step 2: Navigate to Project
```bash
cd "FinSight AI – Enterprise Cost Optimization Copilot"
```

### Step 3: Start Services
```bash
docker-compose up -d
```

### Step 4: Verify Services
```bash
# Check all containers are running
docker-compose ps

# Expected output:
# finsight_mysql     running   0.0.0.0:3306->3306/tcp
# finsight_backend   running   0.0.0.0:8000->8000/tcp
# finsight_frontend  running   0.0.0.0:5173->5173/tcp
```

### Step 5: Check Logs
```bash
# Backend logs
docker-compose logs backend

# Should see: "Application startup complete"

# Frontend logs
docker-compose logs frontend

# Should see: "Local: http://localhost:5173/"
```

### Step 6: Test Endpoints
```bash
# Test backend health
curl http://localhost:8000/health
# Expected: {"status":"healthy"}

# Test API docs
# Open: http://localhost:8000/docs
# Should see Swagger UI
```

### Step 7: Access Frontend
```bash
# Open browser to: http://localhost:5173
# Should see FinSight AI dashboard
```

## 🧪 Functional Testing

### Test 1: Upload Vendor Spend Data
- [ ] Navigate to Upload page
- [ ] Click "Choose CSV File" under Vendor Spend Data
- [ ] Select `database/sample_spend.csv`
- [ ] Verify success message: "Successfully uploaded X records"

### Test 2: Upload Subscriptions
- [ ] Click "Choose CSV File" under SaaS Subscriptions
- [ ] Select `database/sample_subscriptions.csv`
- [ ] Verify success message

### Test 3: Upload Contracts
- [ ] Click "Choose CSV File" under Contract Renewals
- [ ] Select `database/sample_contracts.csv`
- [ ] Verify success message

### Test 4: View Dashboard
- [ ] Navigate to Dashboard
- [ ] Verify 4 summary cards show data:
  - Total Annual Spend: ~₹0.5 Cr
  - Identified Savings: >₹0 Cr
  - Redundant Vendors: >0
  - Upcoming Renewals: >0
- [ ] Verify charts are populated:
  - Top Vendors by Spend (bar chart)
  - Spend by Category (pie chart)
  - Spend by Department (horizontal bar chart)

### Test 5: Vendor Consolidation
- [ ] Navigate to Vendor Consolidation
- [ ] Verify redundancy cards appear
- [ ] Check for categories like:
  - Communication (Zoom, Slack, Teams)
  - Project Management (Jira, Asana, Trello)
  - Monitoring (Datadog, New Relic, Grafana)

### Test 6: Recommendations
- [ ] Navigate to Recommendations
- [ ] Verify total savings amount displayed
- [ ] Check recommendation cards show:
  - Vendor name
  - Recommendation type
  - Projected savings
  - Risk level
  - Rationale
  - Alternative suggestions (if applicable)

### Test 7: Contract Renewals
- [ ] Navigate to Contract Renewals
- [ ] Verify upcoming renewals listed
- [ ] Check urgency color coding:
  - Red: <30 days
  - Orange: 30-60 days
  - Yellow: 60-90 days
- [ ] Verify auto-renew flags shown

### Test 8: Finance Copilot
- [ ] Navigate to Finance Copilot
- [ ] Type: "Top 5 vendors by annual spend"
- [ ] Click "Ask Question"
- [ ] Verify:
  - Generated SQL displayed
  - Results table populated
  - Query saved in history

### Test 9: Try More Copilot Queries
- [ ] "Which categories have redundancy"
- [ ] "List renewals in next 90 days"
- [ ] "Spend by department"
- [ ] "Total annual spend"

### Test 10: Navigation
- [ ] Test all sidebar links work
- [ ] Verify active page highlighted
- [ ] Check responsive design (resize browser)

## 🔍 Verification Checklist

### Backend Verification
- [ ] API responds at http://localhost:8000
- [ ] Swagger docs accessible at http://localhost:8000/docs
- [ ] Health check returns healthy status
- [ ] All endpoints listed in docs
- [ ] File uploads work
- [ ] Database queries execute

### Frontend Verification
- [ ] App loads at http://localhost:5173
- [ ] No console errors
- [ ] All pages accessible
- [ ] Charts render correctly
- [ ] Forms submit successfully
- [ ] API calls complete
- [ ] Loading states work
- [ ] Error handling works

### Database Verification
```bash
# Connect to MySQL
docker exec -it finsight_mysql mysql -uroot -ppassword finsight_db

# Run queries
SHOW TABLES;
# Expected: 7 tables

SELECT COUNT(*) FROM vendors;
# Expected: >0 after upload

SELECT COUNT(*) FROM spend_transactions;
# Expected: >0 after upload

SELECT COUNT(*) FROM recommendations;
# Expected: >0 after upload

exit
```

### Data Verification
- [ ] Vendors normalized correctly
- [ ] Categories assigned
- [ ] Departments created
- [ ] Transactions recorded
- [ ] Subscriptions stored
- [ ] Contracts tracked
- [ ] Recommendations generated

## 🐛 Troubleshooting

### Issue: Containers won't start
```bash
# Check Docker is running
docker info

# Check port conflicts
netstat -ano | findstr :3306
netstat -ano | findstr :8000
netstat -ano | findstr :5173

# Restart Docker Desktop
```

### Issue: Backend can't connect to MySQL
```bash
# Wait for MySQL to be ready (30 seconds)
docker-compose logs mysql | grep "ready for connections"

# Restart backend
docker-compose restart backend
```

### Issue: Frontend shows API errors
```bash
# Check backend is running
curl http://localhost:8000/health

# Check CORS configuration
# Verify frontend URL in backend CORS settings
```

### Issue: No data in dashboard
```bash
# Verify uploads completed
docker-compose logs backend | grep "records_added"

# Check database
docker exec -it finsight_mysql mysql -uroot -ppassword finsight_db -e "SELECT COUNT(*) FROM spend_transactions;"
```

### Issue: Recommendations not generating
```bash
# Trigger recommendation generation
curl -X POST http://localhost:8000/api/upload/spend -F "file=@database/sample_spend.csv"

# Check logs
docker-compose logs backend | grep "recommendation"
```

## 🎯 Success Criteria

Your installation is successful if:

✅ All 3 containers running
✅ Backend health check passes
✅ Frontend loads without errors
✅ Sample data uploads successfully
✅ Dashboard shows charts and data
✅ Recommendations generated
✅ Finance Copilot responds to queries
✅ All navigation links work

## 📊 Expected Results (with sample data)

After uploading all sample files:

- **Total Spend**: ~₹50 Lakhs
- **Vendors**: 15-20 unique vendors
- **Departments**: 5-6 departments
- **Transactions**: 20+ records
- **Subscriptions**: 12 subscriptions
- **Contracts**: 6 contracts
- **Recommendations**: 10-15 recommendations
- **Redundant Categories**: 3-4 categories
- **Upcoming Renewals**: 6 contracts

## 🔄 Reset and Restart

### Clean restart
```bash
# Stop all services
docker-compose down

# Remove volumes (clears database)
docker-compose down -v

# Start fresh
docker-compose up -d
```

### Rebuild containers
```bash
# Rebuild and restart
docker-compose up -d --build
```

## 📞 Support

If you encounter issues:

1. Check logs: `docker-compose logs`
2. Verify ports: `docker-compose ps`
3. Check database: Connect to MySQL
4. Review error messages in browser console
5. Ensure sample CSV files are in `database/` folder

## 🎓 Next Steps

After successful setup:

1. Explore all features
2. Try custom CSV uploads
3. Customize vendor categories
4. Add more alternative recommendations
5. Extend Text-to-SQL patterns
6. Customize UI theme

---

**Setup Complete! 🎉**

You now have a fully functional enterprise cost optimization platform.

Start by uploading the sample data and exploring the dashboard!
