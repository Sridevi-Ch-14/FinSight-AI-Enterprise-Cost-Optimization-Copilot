import { useEffect, useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/Card';
import { getVendorRedundancy } from '@/utils/api';
import { GitMerge } from 'lucide-react';

export function ConsolidationPage() {
  const [redundancy, setRedundancy] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const response = await getVendorRedundancy();
      setRedundancy(response.data);
    } catch (error) {
      console.error('Failed to load redundancy data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="p-8">Loading consolidation opportunities...</div>;
  }

  return (
    <div className="p-8 space-y-8 bg-slate-50 min-h-screen">
      <div className="border-b border-slate-200 pb-6">
        <h1 className="text-3xl font-semibold text-slate-900 tracking-tight">Vendor Consolidation Opportunities</h1>
        <p className="text-slate-600 mt-2 font-light">Identify overlapping tools and reduce vendor sprawl</p>
      </div>

      <div className="space-y-4">
        {redundancy.map((item) => (
          <Card key={item.category} className="border-slate-200 shadow-sm hover:shadow-md transition-shadow">
            <CardContent className="pt-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-3">
                    <GitMerge className="text-orange-600" size={24} strokeWidth={1.5} />
                    <h3 className="text-xl font-semibold text-slate-900">{item.category}</h3>
                    <span className="px-3 py-1 bg-orange-100 text-orange-800 rounded-full text-sm font-medium">
                      {item.vendor_count} vendors
                    </span>
                    <span className="px-3 py-1 bg-slate-100 text-slate-700 rounded-full text-xs font-medium">
                      {item.transaction_count} transactions
                    </span>
                  </div>

                  <div className="mb-4">
                    <p className="text-sm text-slate-600 mb-2">Overlapping vendors detected:</p>
                    <div className="flex flex-wrap gap-2">
                      {item.vendors.map((vendor) => (
                        <span
                          key={vendor}
                          className="px-3 py-1 bg-slate-100 text-slate-700 rounded-lg text-sm font-medium"
                        >
                          {vendor}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <p className="text-sm text-blue-900">
                      <strong>Enterprise Recommendation:</strong> {item.vendor_count} overlapping vendors detected. 
                      Standardize on primary platform to reduce complexity, improve procurement leverage, and optimize spend.
                    </p>
                  </div>
                </div>

                <div className="ml-6 text-right">
                  <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">Combined Spend</p>
                  <p className="text-3xl font-semibold text-slate-900 mt-2">
                    ₹{(item.total_spend / 100000).toFixed(1)}L
                  </p>
                  <p className="text-xs text-slate-500 mt-1">per year</p>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {redundancy.length === 0 && (
        <Card className="border-slate-200">
          <CardContent className="pt-6 text-center text-slate-600">
            No vendor redundancy detected. Your vendor portfolio is optimized.
          </CardContent>
        </Card>
      )}
    </div>
  );
}
