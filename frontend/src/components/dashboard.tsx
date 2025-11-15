"use client";

import { useMemo, useState } from "react";
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
import type {
  ChartPoint,
  HistoricalDashboardData,
  HistoricalTimeframe,
  MultiAssetPerformance,
} from "@/lib/types";

type ChartMode = "value" | "percentage";

const ORDERED_TIMEFRAMES: HistoricalTimeframe[] = ["5m", "15m", "1h", "daily"];

const TIMEFRAME_LABELS: Record<HistoricalTimeframe, string> = {
  "5m": "5 Min",
  "15m": "15 Min",
  "1h": "1 Hour",
  daily: "1 Day",
};

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

type DashboardProps = {
  data: HistoricalDashboardData;
};

function formatCurrency(value: number) {
  return Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
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

export function Dashboard({ data }: DashboardProps) {
  const [chartMode, setChartMode] = useState<ChartMode>("value");
  const [timeframe, setTimeframe] = useState<HistoricalTimeframe>(() => {
    const available = ORDERED_TIMEFRAMES.filter(
      (tf) => data.timeframes[tf]?.timestamps?.length
    );
    if (available.includes(data.defaultTimeframe)) {
      return data.defaultTimeframe;
    }
    return available[0] ?? ORDERED_TIMEFRAMES[0];
  });

  const availableTimeframes = useMemo(
    () =>
      ORDERED_TIMEFRAMES.filter(
        (tf) => data.timeframes[tf]?.timestamps?.length
      ),
    [data.timeframes]
  );

  const symbolList = useMemo(
    () => data.tickers.map((ticker) => ticker.symbol).join(", "),
    [data.tickers]
  );

  const activeDataset = useMemo<MultiAssetPerformance>(() => {
    const preferred = data.timeframes[timeframe];
    if (preferred?.timestamps?.length) {
      return preferred;
    }

    for (const candidate of availableTimeframes) {
      const dataset = data.timeframes[candidate];
      if (dataset?.timestamps?.length) {
        return dataset;
      }
    }

    return {
      timestamps: [],
      total_value: [],
      assets: {},
      metadata: { time_range: timeframe, data_points: 0 },
    };
  }, [data.timeframes, timeframe, availableTimeframes]);

  const rawPoints = useMemo(() => buildPoints(activeDataset), [activeDataset]);

  const seriesKeys = useMemo(() => {
    if (rawPoints.length === 0) return [];
    return Object.keys(rawPoints[0]).filter((key) => key !== "timestamp");
  }, [rawPoints]);

  const baseValues = useMemo(() => {
    if (rawPoints.length === 0) return {} as Record<string, number>;
    const firstPoint = rawPoints[0];
    return Object.fromEntries(
      Object.entries(firstPoint)
        .filter(([key]) => key !== "timestamp")
        .map(([key, value]) => [key, Number(value) || 0])
    );
  }, [rawPoints]);

  const processedPoints = useMemo(() => {
    if (chartMode === "value" || rawPoints.length === 0) {
      return rawPoints;
    }

    return rawPoints.map((point) => {
      const nextPoint: ChartPoint = { timestamp: point.timestamp };
      for (const key of seriesKeys) {
        const current = Number(point[key] ?? 0);
        const base = baseValues[key] ?? 0;
        const safeBase = base === 0 ? 1 : base;
        nextPoint[key] = ((current - base) / safeBase) * 100;
      }
      return nextPoint;
    });
  }, [chartMode, rawPoints, seriesKeys, baseValues]);

  const activeMetadata = activeDataset.metadata ?? {};
  const timeframeLabel = TIMEFRAME_LABELS[timeframe] ?? timeframe;
  const tooltipDatePattern =
    timeframe === "daily" ? "MMM d, yyyy" : "MMM d, yyyy HH:mm";
  const xAxisFormatter = useMemo(
    () => (value: string) => {
      const date = new Date(value);
      if (Number.isNaN(date.getTime())) {
        return value;
      }
      if (timeframe === "daily") {
        return format(date, "MMM d");
      }
      return format(date, "MMM d HH:mm");
    },
    [timeframe]
  );

  const startDateLabel =
    activeMetadata.start_date &&
    !Number.isNaN(Date.parse(activeMetadata.start_date))
      ? format(new Date(activeMetadata.start_date), tooltipDatePattern)
      : "—";
  const endDateLabel =
    activeMetadata.end_date &&
    !Number.isNaN(Date.parse(activeMetadata.end_date))
      ? format(new Date(activeMetadata.end_date), tooltipDatePattern)
      : "—";
  const dataPointsCount = activeMetadata.data_points ?? rawPoints.length;
  const latestTimestamp =
    rawPoints.length > 0 ? rawPoints[rawPoints.length - 1].timestamp : null;
  const lastUpdatedLabel =
    latestTimestamp && !Number.isNaN(Date.parse(latestTimestamp))
      ? format(new Date(latestTimestamp), tooltipDatePattern)
      : "—";

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
      seriesKeys.map((key) => [key, Number(lastPoint[key] ?? 0)])
    );
  }, [rawPoints, seriesKeys]);

  const totalLatest = latestValues["total_value"] ?? 0;
  const totalFirst = baseValues["total_value"] ?? totalLatest;
  const totalChange = totalLatest - totalFirst;
  const totalChangePct =
    totalFirst === 0 ? 0 : (totalChange / totalFirst) * 100;

  return (
    <div className="flex min-h-screen flex-col bg-[#f6f1ea] text-[#1f1a12]">
      <header className="border-b border-[#d4c2a8]/70 bg-[#f9f3ea] px-6 py-4">
        <div className="mx-auto flex max-w-6xl flex-col gap-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="text-xl font-semibold tracking-tight">
              AI Trading Agent <span className="font-normal">·</span>{" "}
              <span className="font-bold italic">Indian Equities</span>
            </div>
            <nav className="flex items-center gap-6 text-sm font-medium uppercase tracking-[0.2em] text-[#5a4431]">
              <a className="hover:text-black" href="#">
                Overview
              </a>
              <a className="hover:text-black" href="#">
                Strategies
              </a>
              <a className="hover:text-black" href="#">
                Research
              </a>
            </nav>
          </div>
          <div className="flex flex-wrap gap-3 text-sm">
            {data.tickers.map((ticker) => {
              const changeClass =
                ticker.changePct >= 0 ? "text-emerald-600" : "text-rose-600";
              const direction = ticker.changePct >= 0 ? "▲" : "▼";
              const absoluteChange = Math.abs(ticker.changePct).toFixed(2);
              return (
                <div
                  key={ticker.symbol}
                  className="flex items-center gap-2 rounded-full border border-[#d4c2a8] bg-white/70 px-4 py-1.5 shadow-sm"
                >
                  <span className="font-semibold">{ticker.symbol}</span>
                  <span>{formatCurrency(ticker.price)}</span>
                  <span className={`text-xs font-semibold ${changeClass}`}>
                    {direction} {absoluteChange}%
                  </span>
                </div>
              );
            })}
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
                    ₹
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
                  Combined Market Value
                </h2>
                <p className="text-sm text-[#5a4431]/70">
                  Equal-weighted basket · {timeframeLabel} data
                </p>
              </div>
              <div className="flex items-center gap-3">
                {availableTimeframes.map((option) => (
                  <button
                    key={option}
                    type="button"
                    className={`rounded-full border px-4 py-1 text-xs font-semibold uppercase tracking-[0.2em] ${
                      timeframe === option
                        ? "border-[#7c3aed] bg-[#7c3aed]/10 text-[#4c1d95]"
                        : "border-[#d4c2a8] text-[#5a4431]"
                    }`}
                    onClick={() => setTimeframe(option)}
                  >
                    {TIMEFRAME_LABELS[option]}
                  </button>
                ))}
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
                {formatPercent(totalChangePct)}
              </div>
            </div>

            <div className="h-80 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={processedPoints}>
                  <XAxis
                    dataKey="timestamp"
                    tickFormatter={xAxisFormatter}
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
                      (() => {
                        const date = new Date(label);
                        if (Number.isNaN(date.getTime())) {
                          return label;
                        }
                        return format(date, tooltipDatePattern);
                      })()
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
                            const changePct =
                              ((latest - base) / safeBase) * 100;
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
                Dataset Coverage
              </div>
              <div className="mt-3 space-y-2 text-sm text-[#4a3727]">
                <div className="flex items-center justify-between">
                  <span className="uppercase tracking-[0.2em] text-[#5a4431]/70">
                    Start
                  </span>
                  <span className="font-medium text-[#1f1a12]">
                    {startDateLabel}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="uppercase tracking-[0.2em] text-[#5a4431]/70">
                    End
                  </span>
                  <span className="font-medium text-[#1f1a12]">
                    {endDateLabel}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="uppercase tracking-[0.2em] text-[#5a4431]/70">
                    Points
                  </span>
                  <span className="font-medium text-[#1f1a12]">
                    {dataPointsCount.toLocaleString()}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="uppercase tracking-[0.2em] text-[#5a4431]/70">
                    Last Update
                  </span>
                  <span className="font-medium text-[#1f1a12]">
                    {lastUpdatedLabel}
                  </span>
                </div>
              </div>
            </div>
            <div className="h-px bg-[#d4c2a8]/60" />
            <div className="space-y-4 text-sm leading-relaxed text-[#4a3727]">
              <p>
                {timeframeLabel} candles aggregated across{" "}
                <strong>{symbolList || "—"}</strong>. Values track an
                equal-weighted basket in rupees.
              </p>
              <p>
                Toggle timeframes to compare intraday momentum with the broader
                daily trend. Percentage mode normalises each series to its first
                value for cleaner relative comparisons.
              </p>
              <p>
                The raw CSVs live in{" "}
                <code className="rounded bg-[#f2eadf] px-2 py-0.5 text-xs">
                  historical_data/
                </code>
                . Update them to refresh this dashboard or to try new assets.
              </p>
            </div>
            <div className="mt-auto">
              <a
                className="inline-flex w-full items-center justify-center rounded-full border border-[#4c1d95] bg-[#7c3aed]/10 px-4 py-2 text-sm font-semibold text-[#4c1d95] transition hover:bg-[#4c1d95]/10"
                href="#"
              >
                View Data Guide →
              </a>
            </div>
          </aside>
        </section>

        <footer className="rounded-xl border border-[#d4c2a8]/70 bg-white/80 px-6 py-4 text-sm text-[#5a4431]/80 shadow-sm backdrop-blur">
          Historical OHLC data for {symbolList || "NSE equities"} powers this AI
          trading dashboard. Replace the CSVs in `historical_data/` to refresh
          the view or experiment with new universes.
        </footer>
      </main>
    </div>
  );
}

export default Dashboard;
