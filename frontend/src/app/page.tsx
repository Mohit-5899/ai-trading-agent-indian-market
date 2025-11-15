import Dashboard from "@/components/dashboard";
import { fallbackPerformance } from "@/lib/mockData";
import type { MultiAssetPerformance } from "@/lib/types";

async function fetchMultiAssetPerformance(): Promise<MultiAssetPerformance> {
  const baseUrl =
    process.env.API_BASE_URL ??
    process.env.NEXT_PUBLIC_API_BASE_URL ??
    "http://localhost:8000";

  try {
    const response = await fetch(
      `${baseUrl}/api/portfolio/multi-asset-performance`,
      {
        method: "GET",
        cache: "no-store",
        next: { revalidate: 60 },
      },
    );

    if (!response.ok) {
      console.warn(
        `[frontend] falling back to mock data: ${response.status} ${response.statusText}`,
      );
      return fallbackPerformance;
    }

    const payload = (await response.json()) as MultiAssetPerformance;
    if (!payload?.timestamps?.length) {
      return fallbackPerformance;
    }
    return payload;
  } catch (error) {
    console.warn("[frontend] error fetching performance data", error);
    return fallbackPerformance;
  }
}

export default async function Home() {
  const data = await fetchMultiAssetPerformance();
  return <Dashboard data={data} />;
}
