export default function AdminCard({ children }: { children: React.ReactNode }) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900 p-4 shadow-lg">
      {children}
    </div>
  );
}
