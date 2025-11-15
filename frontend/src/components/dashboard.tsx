"use client";

import { useEffect, useMemo, useState } from "react";
import {
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { format } from "date-fns";
import type { ChartPoint, MultiAssetPerformance } from "@/lib/types";

type ChartMode = "value" | "percentage";
type TimeRange = "all" | "72h";

const SERIES_PALETTE = [
  "#7c3aed",
  "#6366f1",
  "#f97316",
  "#0f172a",
  "#0891b2",
  "#22c55e",
  "#f973ab",
  "#eab308",
];

const TICKERS = [
  { symbol: "BTC", price: 105896.5, change: 1.2 },
  { symbol: "ETH", price: 3547.25, change: -0.8 },
  { symbol: "SOL", price: 166.78, change: 3.4 },
  { symbol: "BNB", price: 984.29, change: 0.5 },
  { symbol: "DOGE", price: 0.1795, change: -2.1 },
  { symbol: "XRP", price: 2.54, change: 4.2 },
];

const SEASON_ONE_CONCLUDED = new Date("2025-11-03T22:00:00Z");
const SEASON_ONE_POINT_FIVE = new Date("2025-11-21T22:00:00Z");

type DashboardProps = {
  data: MultiAssetPerformance;
};

type Countdown = {
  days: number;
  hours: number;
  minutes: number;
  seconds: number;
};

function formatCurrency(value: number) {
  return Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: value >= 1000 ? 0 : 2,
  }).format(value);
}

function formatPercent(value: number) {
  return `${value >= 0 ? "+" : ""}${value.toFixed(2)}%`;
}

function buildPoints(dataset: MultiAssetPerformance | null): ChartPoint[] {
  if (!dataset?.timestamps?.length) return [];

  const assetKeys = Object.keys(dataset.assets ?? {});
  return dataset.timestamps.map((timestamp, index) => {
    const point: ChartPoint = {
      timestamp,
      total_value: dataset.total_value?.[index] ?? 0,
    };

    for (const key of assetKeys) {
      const series = dataset.assets?.[key] ?? [];
      const safeIndex =
        index < series.length ? index : Math.max(series.length - 1, 0);
      point[key] = series[safeIndex] ?? 0;
    }

    return point;
  });
}

function getCountdown(target: Date, now: Date): Countdown {
  const diffMs = Math.max(target.getTime() - now.getTime(), 0);
  const totalSeconds = Math.floor(diffMs / 1000);
  const days = Math.floor(totalSeconds / (24 * 3600));
  const hours = Math.floor((totalSeconds % (24 * 3600)) / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;

  return { days, hours, minutes, seconds };
}

export function Dashboard({ data }: DashboardProps) {
  const [chartMode, setChartMode] = useState<ChartMode>("value");
  const [timeRange, setTimeRange] = useState<TimeRange>("all");
  const [now, setNow] = useState(() => new Date());

  useEffect(() => {
    const interval = window.setInterval(() => setNow(new Date()), 1000);
    return () => window.clearInterval(interval);
  }, []);

  const rawPoints = useMemo(() => buildPoints(data), [data]);

  const filteredPoints = useMemo(() => {
    if (timeRange === "all" || rawPoints.length === 0) {
      return rawPoints;
    }

    const cutoff = now.getTime() - 72 * 3600 * 1000;
    return rawPoints.filter(
      (point) => new Date(point.timestamp).getTime() >= cutoff,
    );
  }, [rawPoints, timeRange, now]);

  const seriesKeys = useMemo(() => {
    if (filteredPoints.length === 0) return [];
    return Object.keys(filteredPoints[0]).filter((key) => key !== "timestamp");
  }, [filteredPoints]);

  const baseValues = useMemo(() => {
    if (filteredPoints.length === 0) return {} as Record<string, number>;
    const firstPoint = filteredPoints[0];
    return Object.fromEntries(
      Object.entries(firstPoint)
        .filter(([key]) => key !== "timestamp")
        .map(([key, value]) => [key, Number(value) || 0]),
    );
  }, [filteredPoints]);

  const processedPoints = useMemo(() => {
    if (chartMode === "value" || filteredPoints.length === 0) {
      return filteredPoints;
    }

    return filteredPoints.map((point) => {
      const nextPoint: ChartPoint = { timestamp: point.timestamp };
      for (const key of seriesKeys) {
        const current = Number(point[key] ?? 0);
        const base = baseValues[key] ?? 0;
        const safeBase = base === 0 ? 1 : base;
        nextPoint[key] = ((current - base) / safeBase) * 100;
      }
      return nextPoint;
    });
  }, [chartMode, filteredPoints, seriesKeys, baseValues]);

  const colorMap = useMemo(() => {
    const map: Record<string, string> = {};
    seriesKeys.forEach((key, index) => {
      if (key === "total_value") {
        map[key] = "#7c3aed";
      } else {
        map[key] = SERIES_PALETTE[(index + 1) % SERIES_PALETTE.length];
      }
    });
    return map;
  }, [seriesKeys]);

  const latestValues = useMemo(() => {
    if (rawPoints.length === 0) return {} as Record<string, number>;
    const lastPoint = rawPoints[rawPoints.length - 1];
    return Object.fromEntries(
      seriesKeys.map((key) => [key, Number(lastPoint[key] ?? 0)]),
    );
  }, [rawPoints, seriesKeys]);

  const totalLatest = latestValues["total_value"] ?? 0;
  const totalFirst = baseValues["total_value"] ?? totalLatest;
  const totalChange = totalLatest - totalFirst;
  const totalChangePct =
    totalFirst === 0 ? 0 : (totalChange / totalFirst) * 100;

  const countdown = getCountdown(SEASON_ONE_POINT_FIVE, now);

  return (
    <div className="flex min-h-screen flex-col bg-[#f6f1ea] text-[#1f1a12]">
      <header className="border-b border-[#d4c2a8]/70 bg-[#f9f3ea] px-6 py-4">
        <div className="mx-auto flex max-w-6xl flex-col gap-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="text-xl font-semibold tracking-tight">
              Alpha Arena <span className="font-normal">by</span>{" "}
              <span className="font-bold italic">Nofi</span>
            </div>
            <nav className="flex items-center gap-6 text-sm font-medium uppercase tracking-[0.2em] text-[#5a4431]">
              <a className="hover:text-black" href="#">
                Live
              </a>
              <a className="hover:text-black" href="#">
                Blog
              </a>
              <a className="hover:text-black" href="#">
                About Nofi
              </a>
            </nav>
          </div>
          <div className="flex flex-wrap gap-3 text-sm">
            {TICKERS.map((ticker) => (
              <div
                key={ticker.symbol}
                className="flex items-center gap-2 rounded-full border border-[#d4c2a8] bg-white/70 px-4 py-1.5 shadow-sm"
              >
                <span className="font-semibold">{ticker.symbol}</span>
                <span>{ticker.price.toLocaleString()}</span>
                <span
                  className={`text-xs font-semibold ${
                    ticker.change >= 0 ? "text-emerald-600" : "text-rose-600"
                  }`}
                >
                  {ticker.change >= 0 ? "▲" : "▼"} {Math.abs(ticker.change)}%
                </span>
              </div>
            ))}
          </div>
        </div>
      </header>

      <main className="mx-auto flex w-full max-w-6xl flex-1 flex-col gap-6 px-6 py-8">
        <section className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_320px]">
          <div className="rounded-xl border border-[#d4c2a8]/70 bg-white/90 p-6 shadow-sm backdrop-blur">
            <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
              <div className="flex flex-col gap-1">
                <div className="flex items-center gap-3 text-sm uppercase tracking-[0.3em] text-[#5a4431]/80">
                  <button
                    type="button"
                    className={`rounded-full border px-3 py-1 font-medium ${
                      chartMode === "value"
                        ? "border-[#7c3aed] bg-[#7c3aed]/10 text-[#4c1d95]"
                        : "border-transparent text-[#5a4431]"
                    }`}
                    onClick={() => setChartMode("value")}
                  >
                    $
                  </button>
                  <button
                    type="button"
                    className={`rounded-full border px-3 py-1 font-medium ${
                      chartMode === "percentage"
                        ? "border-[#7c3aed] bg-[#7c3aed]/10 text-[#4c1d95]"
                        : "border-transparent text-[#5a4431]"
                    }`}
                    onClick={() => setChartMode("percentage")}
                  >
                    %
                  </button>
                </div>
                <h2 className="text-2xl font-semibold uppercase tracking-[0.4em] text-[#1f1a12]/90">
                  Total Account Value
                </h2>
                <p className="text-sm text-[#5a4431]/70">Season 1 Benchmark</p>
              </div>
              <div className="flex items-center gap-3">
                <button
                  type="button"
                  className={`rounded-full border px-4 py-1 text-xs font-semibold uppercase tracking-[0.2em] ${
                    timeRange === "all"
                      ? "border-[#7c3aed] bg-[#7c3aed]/10 text-[#4c1d95]"
                      : "border-[#d4c2a8] text-[#5a4431]"
                  }`}
                  onClick={() => setTimeRange("all")}
                >
                  All
                </button>
                <button
                  type="button"
                  className={`rounded-full border px-4 py-1 text-xs font-semibold uppercase tracking-[0.2em] ${
                    timeRange === "72h"
                      ? "border-[#7c3aed] bg-[#7c3aed]/10 text-[#4c1d95]"
                      : "border-[#d4c2a8] text-[#5a4431]"
                  }`}
                  onClick={() => setTimeRange("72h")}
                >
                  72h
                </button>
              </div>
            </div>

            <div className="mb-4 flex flex-wrap items-center gap-6">
              <div className="text-3xl font-semibold text-[#4c1d95]">
                {formatCurrency(totalLatest)}
              </div>
              <div
                className={`text-sm font-medium ${
                  totalChange >= 0 ? "text-emerald-600" : "text-rose-600"
                }`}
              >
                {totalChange >= 0 ? "+" : "-"}
                {formatCurrency(Math.abs(totalChange))}
                {" · "}
                {totalChangePct >= 0 ? "+" : "-"}
                {Math.abs(totalChangePct).toFixed(2)}%
              </div>
            </div>

            <div className="h-80 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={processedPoints}>
                  <XAxis
                    dataKey="timestamp"
                    tickFormatter={(value) =>
                      format(new Date(value), "MMM d")
                    }
                    stroke="#8b7355"
                    tickLine={false}
                    axisLine={{ stroke: "#d4c2a8" }}
                  />
                  <YAxis
                    stroke="#8b7355"
                    tickLine={false}
                    axisLine={{ stroke: "#d4c2a8" }}
                    tickFormatter={(value) =>
                      chartMode === "value"
                        ? formatCurrency(Number(value))
                        : formatPercent(Number(value))
                    }
                    width={chartMode === "value" ? 120 : 80}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#fff9f0",
                      border: "1px solid #d4c2a8",
                      borderRadius: "12px",
                      boxShadow: "0 10px 30px rgba(31, 26, 18, 0.08)",
                    }}
                    formatter={(value: number, name) => [
                      chartMode === "value"
                        ? formatCurrency(value)
                        : formatPercent(value),
                      name === "total_value" ? "Total" : name,
                    ]}
                    labelFormatter={(label) =>
                      format(new Date(label), "MMM d, yyyy HH:mm")
                    }
                  />
                  {chartMode === "value" && totalFirst > 0 ? (
                    <ReferenceLine
                      y={totalFirst}
                      stroke="#594f43"
                      strokeDasharray="4 6"
                      strokeOpacity={0.4}
                    />
                  ) : null}
                  {seriesKeys.map((key) => (
                    <Line
                      key={key}
                      type="monotone"
                      dataKey={key}
                      name={key === "total_value" ? "Total" : key}
                      dot={false}
                      stroke={colorMap[key]}
                      strokeWidth={key === "total_value" ? 3 : 2}
                      activeDot={{ r: 5 }}
                    />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            </div>

            <div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {seriesKeys.map((key) => (
                <div key={key} className="flex items-center gap-3 text-sm">
                  <span
                    className="inline-flex h-3 w-3 rounded-full"
                    style={{ backgroundColor: colorMap[key] }}
                  />
                  <div className="flex flex-col">
                    <span className="font-semibold uppercase tracking-[0.2em] text-[#5a4431]/80">
                      {key === "total_value" ? "Total" : key}
                    </span>
                    <span className="text-[#5a4431]/70">
                      {chartMode === "value"
                        ? formatCurrency(latestValues[key] ?? 0)
                        : (() => {
                            const latest = latestValues[key] ?? 0;
                            const base = baseValues[key] ?? 0;
                            const safeBase = base === 0 ? 1 : base;
                            const changePct = ((latest - base) / safeBase) * 100;
                            return formatPercent(changePct);
                          })()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <aside className="flex flex-col gap-4 rounded-xl border border-[#d4c2a8]/70 bg-white/90 p-6 shadow-sm backdrop-blur">
            <div>
              <div className="text-xs font-semibold uppercase tracking-[0.3em] text-[#5a4431]/70">
                Countdown to Season 1.5
              </div>
              <div className="mt-2 text-2xl font-semibold text-[#4c1d95]">
                {countdown.days.toString().padStart(2, "0")}d{" "}
                {countdown.hours.toString().padStart(2, "0")}h{" "}
                {countdown.minutes.toString().padStart(2, "0")}m{" "}
                {countdown.seconds.toString().padStart(2, "0")}s
              </div>
            </div>
            <div className="h-px bg-[#d4c2a8]/60" />
            <div className="space-y-4 text-sm leading-relaxed text-[#4a3727]">
              <p>
                Season 1 concluded on{" "}
                <strong>
                  {format(SEASON_ONE_CONCLUDED, "MMM d, yyyy 'at' h:mm a 'EST'")}
                </strong>
                . We learned how each LLM navigated live markets — trade
                frequency, risk bias, and long/short ratios.
              </p>
              <p>
                Season 1.5 arrives later this month with improved benchmarks,
                memory, and an expanded asset universe. Expect multiple
                simultaneous competitions and richer qualitative data.
              </p>
              <p>
                Follow Nofi on X and join the waitlist to be first in line for
                launch news and product access.
              </p>
            </div>
            <div className="mt-auto">
              <a
                className="inline-flex w-full items-center justify-center rounded-full border border-[#4c1d95] bg-[#7c3aed]/10 px-4 py-2 text-sm font-semibold text-[#4c1d95] transition hover:bg-[#4c1d95]/10"
                href="#"
              >
                Join the Platform Waitlist →
              </a>
            </div>
          </aside>
        </section>

        <footer className="rounded-xl border border-[#d4c2a8]/70 bg-white/80 px-6 py-4 text-sm text-[#5a4431]/80 shadow-sm backdrop-blur">
          Alpha Arena Season 1 is now over. Season 1.5 launches soon with richer
          analytics, long-term memory, and a broader asset set. Stay tuned.
        </footer>
      </main>
    </div>
  );
}

export default Dashboard;
