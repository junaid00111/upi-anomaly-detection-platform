import { queryOptions } from "@tanstack/react-query";

import { apiMonitoringDataService } from "./monitoring-api";

export const monitoringQueryOptions = queryOptions({
  queryKey: ["monitoring-snapshot", "postgres-api"],
  queryFn: () => apiMonitoringDataService.getSnapshot(),
  staleTime: 30_000,
});
