export default function QueryLogTable({
  logs,
  loading,
}: {
  logs: any[];
  loading: boolean;
}) {
  if (loading) {
    return <p className="text-slate-400 text-sm">Loading logs...</p>;
  }

  if (!logs || logs.length === 0) {
    return <p className="text-slate-400 text-sm">No logs found.</p>;
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-slate-800 bg-slate-900">
      <table className="w-full text-left text-sm">
        <thead className="bg-slate-800 text-slate-300">
          <tr>
            <th className="p-3">Query</th>
            <th className="p-3">Chunk IDs</th>
            <th className="p-3">Response Time (ms)</th>
            <th className="p-3">Timestamp</th>
          </tr>
        </thead>

        <tbody>
          {logs.map((log) => (
            <tr
              key={log.id}
              className="border-t border-slate-800 hover:bg-slate-800/50"
            >
              <td className="p-3 max-w-xs truncate">{log.query_text}</td>

              <td className="p-3 text-xs">
                {log.returned_chunk_ids?.length
                  ? log.returned_chunk_ids.join(", ")
                  : "-"}
              </td>

              <td className="p-3">
                {log.response_time_ms ? log.response_time_ms : "-"}
              </td>

              <td className="p-3 text-xs text-slate-400">
                {new Date(log.timestamp).toLocaleString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
