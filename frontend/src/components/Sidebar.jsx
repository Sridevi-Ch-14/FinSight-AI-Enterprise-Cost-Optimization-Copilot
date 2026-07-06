import { Link, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Upload, 
  GitMerge, 
  CreditCard, 
  FileText, 
  Lightbulb, 
  MessageSquare,
  BarChart3 
} from 'lucide-react';
import { cn } from '@/lib/utils';

const navItems = [
  { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/upload', icon: Upload, label: 'Upload Data' },
  { path: '/consolidation', icon: GitMerge, label: 'Vendor Consolidation' },
  { path: '/subscriptions', icon: CreditCard, label: 'Subscription Optimization' },
  { path: '/renewals', icon: FileText, label: 'Contract Renewals' },
  { path: '/recommendations', icon: Lightbulb, label: 'Recommendations' },
  { path: '/copilot', icon: MessageSquare, label: 'Finance Copilot' },
  { path: '/reports', icon: BarChart3, label: 'Reports' },
];

export function Sidebar() {
  const location = useLocation();

  return (
    <div className="w-64 bg-slate-900 text-white h-screen fixed left-0 top-0 flex flex-col border-r border-slate-800">
      <div className="p-6 border-b border-slate-800">
        <h1 className="text-xl font-semibold tracking-tight">FinSight AI</h1>
        <p className="text-xs text-slate-400 mt-1 font-light">Enterprise Cost Optimization</p>
      </div>
      
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;
          
          return (
            <Link
              key={item.path}
              to={item.path}
              className={cn(
                'flex items-center gap-3 px-4 py-2.5 rounded-md transition-all text-sm font-medium',
                isActive 
                  ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/20' 
                  : 'text-slate-300 hover:bg-slate-800 hover:text-white'
              )}
            >
              <Icon size={18} strokeWidth={1.5} />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>
      
      <div className="p-4 border-t border-slate-800 text-xs text-slate-500 font-light">
        Version 1.0.0
      </div>
    </div>
  );
}
