import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/Card';
import { Button } from '@/components/Button';
import { queryCopilot, getCopilotHistory } from '@/utils/api';
import { Send, MessageSquare, Code } from 'lucide-react';

export function CopilotPage() {
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const res = await getCopilotHistory();
      setHistory(res.data);
    } catch (error) {
      console.error('Failed to load history:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    setLoading(true);
    try {
      const res = await queryCopilot(question);
      setResponse(res.data);
      loadHistory();
    } catch (error) {
      console.error('Query failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const exampleQueries = [
    'Top 5 vendors by annual spend',
    'Which categories have redundancy',
    'How much can we save by consolidation',
    'List renewals in next 90 days',
    'Total annual spend',
    'Spend by department',
  ];

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Finance Copilot</h1>
        <p className="text-slate-600 mt-1">Ask questions about your enterprise spend in natural language</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Ask a Question</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <textarea
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    placeholder="e.g., What are the top 5 vendors by spend?"
                    className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows={3}
                  />
                </div>
                <Button type="submit" disabled={loading} className="w-full">
                  <Send size={16} className="mr-2" />
                  {loading ? 'Processing...' : 'Ask Question'}
                </Button>
              </form>

              <div className="mt-4">
                <p className="text-sm font-medium text-slate-700 mb-2">Example queries:</p>
                <div className="flex flex-wrap gap-2">
                  {exampleQueries.map((query) => (
                    <button
                      key={query}
                      onClick={() => setQuestion(query)}
                      className="px-3 py-1 text-xs bg-slate-100 hover:bg-slate-200 rounded-full text-slate-700"
                    >
                      {query}
                    </button>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          {response && (
            <>
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Code size={20} />
                    Generated SQL
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <pre className="bg-slate-900 text-slate-100 p-4 rounded-lg overflow-x-auto text-sm">
                    {response.sql}
                  </pre>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Results</CardTitle>
                </CardHeader>
                <CardContent>
                  {response.result.success ? (
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead>
                          <tr className="border-b">
                            {response.result.columns.map((col) => (
                              <th key={col} className="text-left py-2 px-4 font-medium text-slate-700">
                                {col}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {response.result.data.map((row, idx) => (
                            <tr key={idx} className="border-b hover:bg-slate-50">
                              {response.result.columns.map((col) => (
                                <td key={col} className="py-2 px-4 text-slate-600">
                                  {typeof row[col] === 'number' 
                                    ? row[col].toLocaleString('en-IN')
                                    : row[col]}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <div className="text-red-600">Error: {response.result.error}</div>
                  )}
                </CardContent>
              </Card>
            </>
          )}
        </div>

        <div>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MessageSquare size={20} />
                Query History
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {history.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => setQuestion(item.question)}
                    className="w-full text-left p-3 bg-slate-50 hover:bg-slate-100 rounded-lg text-sm"
                  >
                    <p className="text-slate-900 font-medium">{item.question}</p>
                    <p className="text-xs text-slate-500 mt-1">
                      {new Date(item.created_at).toLocaleString()}
                    </p>
                  </button>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
