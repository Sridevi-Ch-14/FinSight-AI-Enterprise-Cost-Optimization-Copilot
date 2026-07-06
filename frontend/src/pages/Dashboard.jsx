import { useEffect, useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/Card';
import { getDashboardSummary } from '@/utils/api';
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp, DollarSign, AlertTriangle, Calendar } from 'lucide-react';

const COLORS = ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#06b6d4', '#6366f1'];

export function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const response = await getDashboardSummary();
      setData(response.data);
    } catch (error) {
      console.error('Failed to load dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="p-8">Loading dashboard...</div>;
  }

  if (!data) {
    return <div className="p-8">No data available. Please upload spend data first.</div>;
  }

  const { summary, spend_by_vendor, spend_by_department, spend_by_category } = data;
  const hasSpendData = summary.total_annual_spend > 0;

  return (
    <div className="p-8 space-y-8 bg-slate-50 min-h-screen">
      <div className="border-b border-slate-200 pb-6">
        <h1 className="text-3xl font-semibold text-slate-900 tracking-tight">Cost Optimization Dashboard</h1>
        <p className="text-slate-600 mt-2 font-light">Enterprise-wide spend intelligence and savings opportunities</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="border-slate-200 shadow-sm hover:shadow-md transition-shadow">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">Total Annual Spend</p>
                <p className="text-3xl font-semibold text-slate-900 mt-3">
                  ₹{(summary.total_annual_spend / 10000000).toFixed(2)} Cr
                </p>
              </div>
              <div className="h-12 w-12 bg-blue-50 rounded-lg flex items-center justify-center">
                <DollarSign className="text-blue-600" size={22} strokeWidth={1.5} />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-slate-200 shadow-sm hover:shadow-md transition-shadow">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">Identified Savings</p>
                <p className="text-3xl font-semibold text-green-600 mt-3">
                  ₹{(summary.identified_savings / 10000000).toFixed(2)} Cr
                </p>
              </div>
              <div className="h-12 w-12 bg-green-50 rounded-lg flex items-center justify-center">
                <TrendingUp className="text-green-600" size={22} strokeWidth={1.5} />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-slate-200 shadow-sm hover:shadow-md transition-shadow">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">Redundant Vendors</p>
                <p className="text-3xl font-semibold text-orange-600 mt-3">
                  {summary.redundant_vendors}
                </p>
              </div>
              <div className="h-12 w-12 bg-orange-50 rounded-lg flex items-center justify-center">
                <AlertTriangle className="text-orange-600" size={22} strokeWidth={1.5} />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-slate-200 shadow-sm hover:shadow-md transition-shadow">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">Upcoming Renewals</p>
                <p className="text-3xl font-semibold text-purple-600 mt-3">
                  {summary.upcoming_renewals}
                </p>
              </div>
              <div className="h-12 w-12 bg-purple-50 rounded-lg flex items-center justify-center">
                <Calendar className="text-purple-600" size={22} strokeWidth={1.5} />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {!hasSpendData && (
          <Card className="lg:col-span-2 border-orange-200 bg-orange-50 shadow-sm">
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 bg-orange-100 rounded-lg flex items-center justify-center">
                  <AlertTriangle className="text-orange-600" size={20} />
                </div>
                <div>
                  <p className="font-medium text-orange-900">Vendor Spend Data Required</p>
                  <p className="text-sm text-orange-700 mt-1">
                    Upload vendor spend transactions to activate full dashboard analytics and savings calculations.
                    <a href="/upload" className="underline font-medium ml-1">Upload now</a>
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {summary.identified_savings > 0 && hasSpendData && (
          <Card className="lg:col-span-2 border-blue-200 bg-blue-50 shadow-sm">
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 bg-blue-100 rounded-lg flex items-center justify-center">
                  <TrendingUp className="text-blue-600" size={20} />
                </div>
                <div>
                  <p className="font-medium text-blue-900">Cost Optimization Opportunities Available</p>
                  <p className="text-sm text-blue-700 mt-1">
                    ₹{(summary.identified_savings / 10000000).toFixed(2)} Cr in potential savings identified. 
                    <a href="/recommendations" className="underline font-medium ml-1">View all recommendations</a>
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        <Card className="border-slate-200 shadow-sm">
          <CardHeader>
            <CardTitle className="text-lg font-semibold text-slate-900">Top Vendors by Spend</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={spend_by_vendor}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                <YAxis />
                <Tooltip formatter={(value) => `₹${(value / 100000).toFixed(2)}L`} />
                <Bar dataKey="value" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card className="border-slate-200 shadow-sm">
          <CardHeader>
            <CardTitle className="text-lg font-semibold text-slate-900">Spend by Category</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={spend_by_category}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {spend_by_category.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => `₹${(value / 100000).toFixed(2)}L`} />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card className="lg:col-span-2 border-slate-200 shadow-sm">
          <CardHeader>
            <CardTitle className="text-lg font-semibold text-slate-900">Spend by Department</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={spend_by_department} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="name" type="category" width={150} />
                <Tooltip formatter={(value) => `₹${(value / 100000).toFixed(2)}L`} />
                <Bar dataKey="value" fill="#8b5cf6" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
