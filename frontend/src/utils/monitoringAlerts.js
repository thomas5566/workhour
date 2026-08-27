export function getSpeedFusionDrop(previousValue, currentValue, totalValue) {
  const previous = Number(previousValue);
  const current = Number(currentValue);
  const total = Number(totalValue);

  if (!Number.isFinite(current)) return null;

  const droppedSinceRefresh = Number.isFinite(previous) && current < previous;
  const currentlyMissingConnections = Number.isFinite(total) && current < total;
  if (!droppedSinceRefresh && !currentlyMissingConnections) return null;

  // The configured total is also a reliable baseline after reload/navigation,
  // when no prior in-memory sample exists.
  const baselines = [previous, total].filter(
    (value) => Number.isFinite(value) && value > current,
  );
  return {
    previous: baselines.length ? Math.max(...baselines) : current,
    current,
  };
}

export function getCriticalProblemCount(problems = []) {
  // Zabbix severity 4 is High and 5 is Disaster.
  return problems.filter((problem) => Number(problem.severity) >= 4).length;
}

export function getResourceUtilizationClass(key, value) {
  const isUtilizationMetric = ["cpu", "memory", "storage_utilization"].includes(key)
    || String(key).startsWith("disk_usage:");
  if (!isUtilizationMetric) return "";

  const utilization = Number(value);
  if (!Number.isFinite(utilization)) return "";
  if (utilization >= 90) return "metric-critical";
  if (utilization >= 80) return "metric-warning";
  return "metric-healthy";
}
