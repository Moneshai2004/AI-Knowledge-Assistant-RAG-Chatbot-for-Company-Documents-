import AdminCard from "./AdminCard";

export default function SystemStats({
  stats,
  loading,
}: {
  stats: any;
  loading: boolean;
}) {
  if (loading) {
    return <p className="text-slate-400 text-sm">Loading stats...</p>;
  }

  if (!stats) {
    return <p className="text-red-400 text-sm">Failed to load stats.</p>;
  }

  const items = [
    { label: "Total Documents", value: stats.total_documents },
    { label: "Total Chunks", value: stats.total_chunks },
    { label: "Total Queries", value: stats.total_queries },
    {
      label: "Latest Index Date",
      value: stats.latest_index_date || "None",
    },
    { label: "Embedding Dim", value: stats.embed_dim || "Unknown" },
  ];

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
      {items.map((item) => (
        <AdminCard key={item.label}>
          <p className="text-xs text-slate-400">{item.label}</p>
          <p className="text-lg font-semibold mt-1">{item.value}</p>
        </AdminCard>
      ))}
    </div>
  );
}
