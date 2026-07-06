import { useEffect, useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/Card';
import { getTopRecommendations } from '@/utils/api';
import { TrendingUp, AlertTriangle, Info } from 'lucide-react';

const riskColors = {
  Low: 'bg-green-100 text-green-800',
  Medium: 'bg-yellow-100 text-yellow-800',
  High: 'bg-red-100 text-red-800',
};

const typeLabels = {
  consolidation: 'Vendor Consolidation',
  license_optimization: 'License Optimization',
  shadow_it: 'Shadow IT',
  price_benchmark: 'Price Benchmarking',
  contract_renewal: 'Contract Renewal',
};

export function RecommendationsPage() {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadRecommendations();
  }, []);

  const loadRecommendations = async () => {
    try {
      const response = await getTopRecommendations();
      setRecommendations(response.data);
    } catch (error) {
      console.error('Failed to load recommendations:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="p-8">Loading recommendations...</div>;
  }

  const totalSavings = recommendations.reduce((sum, rec) => sum + rec.savings, 0);

  return (
    <div className="p-8 space-y-8 bg-slate-50 min-h-screen">
      <div className="border-b border-slate-200 pb-6">
        <h1 className="text-3xl font-semibold text-slate-900 tracking-tight">Cost Optimization Recommendations</h1>
        <p className="text-slate-600 mt-2 font-light">Actionable insights to reduce enterprise spend</p>
      </div>

      <Card className="bg-gradient-to-br from-green-50 to-emerald-50 border-green-200 shadow-sm">
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-medium text-slate-700 uppercase tracking-wider">Total Potential Annual Savings</p>
              <p className="text-4xl font-semibold text-green-700 mt-3">
                ₹{(totalSavings / 10000000).toFixed(2)} Cr
              </p>
            </div>
            <TrendingUp className="text-green-600" size={40} strokeWidth={1.5} />
          </div>
        </CardContent>
      </Card>

      <div className="space-y-4">
        {recommendations.map((rec, index) => (
          <Card key={rec.id} className="border-slate-200 shadow-sm hover:shadow-md transition-shadow">
            <CardContent className="pt-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="text-lg font-bold text-slate-400">#{index + 1}</span>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${riskColors[rec.risk_level]}`}>
                      {rec.risk_level} Risk
                    </span>
                    <span className="px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      {typeLabels[rec.type]}
                    </span>
                  </div>

                  <h3 className="text-xl font-semibold text-slate-900 mb-2">{rec.vendor}</h3>
                  <p className="text-slate-600 mb-3">{rec.rationale}</p>

                  {rec.alternative && (
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-3">
                      <p className="text-sm font-medium text-blue-900 mb-1">
                        Recommended Alternative: {rec.alternative}
                      </p>
                      <p className="text-sm text-blue-700">{rec.feature_parity}</p>
                    </div>
                  )}

                  {rec.feature_parity && !rec.alternative && (
                    <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
                      <p className="text-sm text-slate-700">
                        <Info className="inline mr-1" size={14} />
                        {rec.feature_parity}
                      </p>
                    </div>
                  )}
                </div>

                <div className="ml-6 text-right">
                  <p className="text-sm text-slate-600">Projected Savings</p>
                  <p className="text-3xl font-bold text-green-600">
                    ₹{(rec.savings / 100000).toFixed(1)}L
                  </p>
                  <p className="text-xs text-slate-500 mt-1">per year</p>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {recommendations.length === 0 && (
        <Card>
          <CardContent className="pt-6 text-center text-slate-600">
            No recommendations available. Upload data to generate insights.
          </CardContent>
        </Card>
      )}
    </div>
  );
}
