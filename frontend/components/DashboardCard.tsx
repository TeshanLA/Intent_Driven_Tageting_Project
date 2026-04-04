export function DashboardCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="metric-card">
      <p>{label}</p>
      <strong>{value}</strong>
    </div>
  );
}
