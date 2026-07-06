import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/Card';
import { Button } from '@/components/Button';
import { uploadSpendData, uploadSubscriptions, uploadContracts, getDataStats, clearData } from '@/utils/api';
import { Upload, CheckCircle, AlertCircle, Trash2, BarChart3 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export function UploadPage() {
  const [uploadStatus, setUploadStatus] = useState({});
  const [dataStats, setDataStats] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    loadDataStats();
  }, []);

  const loadDataStats = async () => {
    try {
      const response = await getDataStats();
      setDataStats(response.data);
    } catch (error) {
      console.error('Failed to load data stats:', error);
    }
  };

  const handleFileUpload = async (type, file) => {
    if (!file) return;

    setUploadStatus({ ...uploadStatus, [type]: { loading: true } });

    try {
      let response;
      if (type === 'spend') {
        response = await uploadSpendData(file);
      } else if (type === 'subscriptions') {
        response = await uploadSubscriptions(file);
      } else if (type === 'contracts') {
        response = await uploadContracts(file);
      }

      console.log('Upload response:', JSON.stringify(response.data, null, 2));
      const recordsAdded = response.data?.records_added || response.data?.success ? 'some' : '0';
      
      setUploadStatus({
        ...uploadStatus,
        [type]: {
          success: true,
          message: `Successfully uploaded ${recordsAdded} records`,
        },
      });
      
      loadDataStats();
    } catch (error) {
      console.error('Upload error:', error);
      setUploadStatus({
        ...uploadStatus,
        [type]: {
          error: true,
          message: error.response?.data?.error || 'Upload failed',
        },
      });
    }
  };

  const handleDelete = async (type) => {
    if (!window.confirm(`Are you sure you want to delete all ${type} data? This cannot be undone.`)) {
      return;
    }

    try {
      await clearData(type);
      setUploadStatus({ ...uploadStatus, [type]: { deleted: true } });
      loadDataStats();
    } catch (error) {
      console.error('Delete failed:', error);
      alert('Failed to delete data');
    }
  };

  const UploadCard = ({ title, description, type, expectedColumns, recordCount }) => (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">{title}</CardTitle>
        <p className="text-sm text-slate-600 mt-2">{description}</p>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="border-2 border-dashed border-slate-300 rounded-lg p-6 text-center">
            <Upload className="mx-auto text-slate-400 mb-2" size={32} />
            <input
              type="file"
              accept=".csv"
              onChange={(e) => handleFileUpload(type, e.target.files[0])}
              id={`upload-${type}`}
              style={{ display: 'none' }}
            />
            <label htmlFor={`upload-${type}`}>
              <span className="inline-flex items-center justify-center rounded-md font-medium transition-colors border border-slate-300 bg-white hover:bg-slate-100 h-10 px-4 py-2 cursor-pointer text-sm">
                Choose CSV File
              </span>
            </label>
          </div>

          {uploadStatus[type]?.loading && (
            <div className="text-sm text-blue-600">Uploading...</div>
          )}

          {uploadStatus[type]?.success && (
            <div className="flex items-center gap-2 text-sm text-green-600">
              <CheckCircle size={16} />
              {uploadStatus[type].message}
            </div>
          )}

          {uploadStatus[type]?.deleted && (
            <div className="flex items-center gap-2 text-sm text-orange-600">
              <AlertCircle size={16} />
              Data deleted successfully
            </div>
          )}

          {uploadStatus[type]?.error && (
            <div className="flex items-center gap-2 text-sm text-red-600">
              <AlertCircle size={16} />
              {uploadStatus[type].message}
            </div>
          )}

          {recordCount > 0 && (
            <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
              <div className="flex items-center gap-2 text-sm text-slate-700">
                <CheckCircle size={16} className="text-green-600" />
                <span>{recordCount} records uploaded</span>
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => navigate('/')}
                >
                  <BarChart3 size={14} className="mr-1" />
                  View Analysis
                </Button>
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={() => handleDelete(type)}
                >
                  <Trash2 size={14} className="mr-1" />
                  Delete
                </Button>
              </div>
            </div>
          )}

          <div className="text-xs text-slate-500">
            <p className="font-medium mb-1">Expected columns:</p>
            <p>{expectedColumns}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Upload Enterprise Data</h1>
        <p className="text-slate-600 mt-1">Import company spend, subscriptions, and contract data</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <UploadCard
          title="Vendor Spend Data"
          description="Upload company-wide vendor spend transactions"
          type="spend"
          expectedColumns="Date, Department, Vendor, Category, Amount, Payment Type"
          recordCount={dataStats?.spend_transactions || 0}
        />

        <UploadCard
          title="SaaS Subscriptions"
          description="Upload SaaS subscription and license information"
          type="subscriptions"
          expectedColumns="Vendor, Plan Tier, Seat Count, Monthly Cost, Department Owner"
          recordCount={dataStats?.subscriptions || 0}
        />

        <UploadCard
          title="Contract Renewals"
          description="Upload contract renewal dates and values"
          type="contracts"
          expectedColumns="Vendor, Renewal Date, Annual Contract Value, Auto-Renew Flag"
          recordCount={dataStats?.contracts || 0}
        />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Sample Data Templates</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-slate-600 mb-4">
            Download sample CSV templates to understand the expected format:
          </p>
          <div className="flex gap-4">
            <Button variant="outline" size="sm">Download Spend Template</Button>
            <Button variant="outline" size="sm">Download Subscription Template</Button>
            <Button variant="outline" size="sm">Download Contract Template</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
