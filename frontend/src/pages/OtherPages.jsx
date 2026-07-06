import { Card, CardContent } from '@/components/Card';

export function SubscriptionsPage() {
  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Subscription Optimization</h1>
        <p className="text-slate-600 mt-1">License tier optimization and seat management</p>
      </div>
      <Card>
        <CardContent className="pt-6">
          <p className="text-slate-600">
            This page will show detailed subscription analysis including over-provisioned seats,
            premium tier optimization opportunities, and license utilization metrics.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}

export function ReportsPage() {
  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Executive Reports</h1>
        <p className="text-slate-600 mt-1">CFO-ready cost optimization reports</p>
      </div>
      <Card>
        <CardContent className="pt-6">
          <p className="text-slate-600">
            Export comprehensive reports including spend analysis, optimization roadmap,
            and projected savings in PDF and Excel formats.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
