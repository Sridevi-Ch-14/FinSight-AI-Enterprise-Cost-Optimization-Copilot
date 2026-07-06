import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Sidebar } from './components/Sidebar';
import { Dashboard } from './pages/Dashboard';
import { UploadPage } from './pages/UploadPage';
import { ConsolidationPage } from './pages/ConsolidationPage';
import SubscriptionPage from './pages/SubscriptionPage';
import { ReportsPage } from './pages/OtherPages';
import { RenewalsPage } from './pages/RenewalsPage';
import { RecommendationsPage } from './pages/RecommendationsPage';
import { CopilotPage } from './pages/CopilotPage';

function App() {
  return (
    <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <div className="flex min-h-screen bg-slate-50">
        <Sidebar />
        <main className="flex-1 ml-64">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/consolidation" element={<ConsolidationPage />} />
            <Route path="/subscriptions" element={<SubscriptionPage />} />
            <Route path="/renewals" element={<RenewalsPage />} />
            <Route path="/recommendations" element={<RecommendationsPage />} />
            <Route path="/copilot" element={<CopilotPage />} />
            <Route path="/reports" element={<ReportsPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
