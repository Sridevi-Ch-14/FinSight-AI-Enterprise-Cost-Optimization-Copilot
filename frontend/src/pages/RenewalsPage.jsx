import { useEffect, useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/Card';
import { getUpcomingRenewals } from '@/utils/api';
import { Calendar, AlertCircle } from 'lucide-react';

export function RenewalsPage() {
  const [renewals, setRenewals] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const response = await getUpcomingRenewals();
      setRenewals(response.data);
    } catch (error) {
      console.error('Failed to load renewals:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="p-8">Loading contract renewals...</div>;
  }

  const getRiskColor = (risk) => {
    if (risk === 'High') return 'bg-red-100 text-red-800 border-red-200';
    if (risk === 'Medium') return 'bg-orange-100 text-orange-800 border-orange-200';
    return 'bg-yellow-100 text-yellow-800 border-yellow-200';
  };

  const getUrgencyColor = (days) => {
    if (days <= 30) return 'bg-red-100 text-red-800 border-red-200';
    if (days <= 60) return 'bg-orange-100 text-orange-800 border-orange-200';
    return 'bg-yellow-100 text-yellow-800 border-yellow-200';
  };

  return (
    <div className="p-8 space-y-8 bg-slate-50 min-h-screen">
      <div className="border-b border-slate-200 pb-6">
        <h1 className="text-3xl font-semibold text-slate-900 tracking-tight">Contract Renewal Watchlist</h1>
        <p className="text-slate-600 mt-2 font-light">Upcoming contract renewals requiring procurement review</p>
      </div>

      {renewals.length > 0 && (
        <Card className="bg-orange-50 border-orange-200">
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <AlertCircle className="text-orange-600" size={24} />
              <div>
                <p className="font-medium text-slate-900">
                  {renewals.length} contracts renewing in the next 90 days
                </p>
                <p className="text-sm text-slate-600">
                  Total value: ₹{(renewals.reduce((sum, r) => sum + r.annual_value, 0) / 10000000).toFixed(2)} Cr
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="space-y-4">
        {renewals.map((renewal) => (
          <Card key={renewal.vendor} className="hover:shadow-md transition-shadow">
            <CardContent className="pt-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-3">
                    <Calendar className="text-blue-600" size={24} />
                    <h3 className="text-xl font-semibold text-slate-900">{renewal.vendor}</h3>
                    <span className={`px-3 py-1 rounded-full text-sm font-medium border ${getUrgencyColor(renewal.days_until)}`}>
                      {renewal.days_until} days
                    </span>
                    {renewal.auto_renew && (
                      <span className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm font-medium">
                        Auto-Renew
                      </span>
                    )}
                  </div>

                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div>
                      <p className="text-sm text-slate-600">Renewal Date</p>
                      <p className="text-lg font-medium text-slate-900">
                        {new Date(renewal.renewal_date).toLocaleDateString('en-IN', {
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric'
                        })}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-slate-600">Annual Contract Value</p>
                      <p className="text-lg font-medium text-slate-900">
                        ₹{(renewal.annual_value / 100000).toFixed(2)}L
                      </p>
                    </div>
                  </div>

                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <p className="text-sm text-blue-900">
                      <strong>Action Required:</strong> Review this contract for renegotiation opportunities. 
                      Consider alternative vendors, volume discounts, or multi-year commitments for better pricing.
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {renewals.length === 0 && (
        <Card>
          <CardContent className="pt-6 text-center text-slate-600">
            No upcoming renewals in the next 90 days.
          </CardContent>
        </Card>
      )}
    </div>
  );
}
