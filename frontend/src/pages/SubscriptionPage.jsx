import { useState, useEffect } from 'react';
import { getTopRecommendations } from '../utils/api';

export default function SubscriptionPage() {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const response = await getTopRecommendations();
      const subRecs = response.data.filter(r => r.type === 'subscription_optimization');
      setRecommendations(subRecs);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (risk) => {
    const colors = {
      'High': 'bg-green-100 text-green-800',
      'Medium': 'bg-yellow-100 text-yellow-800',
      'Low': 'bg-orange-100 text-orange-800'
    };
    return colors[risk] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading subscription data...</div>
      </div>
    );
  }

  const totalSavings = recommendations.reduce((sum, rec) => sum + rec.savings, 0);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">Subscription Optimization</h1>
        <p className="mt-1 text-sm text-gray-600">
          License tier optimization and seat management
        </p>
      </div>

      {recommendations.length === 0 ? (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
          <div className="text-gray-400 mb-3">
            <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-1">No Subscription Data</h3>
          <p className="text-gray-600 mb-4">
            Upload SaaS subscription data to see license optimization opportunities
          </p>
          <a
            href="/upload"
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            Upload Subscriptions
          </a>
        </div>
      ) : (
        <>
          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg shadow-sm border border-blue-100 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-blue-900">Total Potential Savings</p>
                <p className="text-3xl font-semibold text-blue-600 mt-1">
                  ₹{(totalSavings / 100000).toFixed(2)}L
                </p>
                <p className="text-xs text-blue-700 mt-1">
                  From {recommendations.length} optimization opportunities
                </p>
              </div>
              <div className="bg-blue-100 rounded-full p-3">
                <svg className="h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-medium text-gray-900">Optimization Opportunities</h2>
            </div>
            <div className="divide-y divide-gray-200">
              {recommendations.map((rec, index) => (
                <div key={index} className="p-6 hover:bg-gray-50 transition-colors">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-base font-medium text-gray-900">{rec.vendor}</h3>
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getRiskColor(rec.risk_level)}`}>
                          {rec.risk_level} Confidence
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mb-3">{rec.rationale}</p>
                      <div className="flex items-center gap-4 text-xs text-gray-500">
                        <span className="flex items-center gap-1">
                          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                          </svg>
                          {rec.feature_parity}
                        </span>
                      </div>
                    </div>
                    <div className="ml-6 text-right">
                      <div className="text-sm font-medium text-gray-500">Potential Savings</div>
                      <div className="text-2xl font-semibold text-green-600">
                        ₹{(rec.savings / 100000).toFixed(2)}L
                      </div>
                      <div className="text-xs text-gray-500 mt-1">per year</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
