import Dashboard from "@/components/dashboard";
import { loadHistoricalDashboardData } from "@/lib/historicalData";
import { fallbackDashboardData } from "@/lib/mockData";
import type { HistoricalDashboardData } from "@/lib/types";

export default async function Home() {
  let data: HistoricalDashboardData = fallbackDashboardData;

  try {
    data = await loadHistoricalDashboardData();
  } catch (error) {
    console.warn("[frontend] error loading historical data", error);
  }

  return <Dashboard data={data} />;
}
