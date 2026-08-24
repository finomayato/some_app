import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { Suspense } from "react"

import { MetricsService } from "@/client"
import Forbidden from "@/components/Common/Forbidden"
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import useAuth from "@/hooks/useAuth"

function getMetricsQueryOptions() {
  return {
    queryFn: async () => (await MetricsService.readMetrics()).data,
    queryKey: ["metrics"],
  }
}

export const Route = createFileRoute("/_layout/metrics")({
  component: Metrics,
  head: () => ({
    meta: [
      {
        title: "Metrics - FastAPI Template",
      },
    ],
  }),
})

function MetricCard({ label, value }: { label: string; value: number }) {
  return (
    <Card>
      <CardHeader>
        <CardDescription>{label}</CardDescription>
        <CardTitle className="text-3xl tabular-nums">{value}</CardTitle>
      </CardHeader>
    </Card>
  )
}

function MetricsContent() {
  const { data: metrics } = useSuspenseQuery(getMetricsQueryOptions())

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <MetricCard label="Total users" value={metrics.users} />
      <MetricCard label="Active users" value={metrics.active_users} />
      <MetricCard label="Total items" value={metrics.items} />
    </div>
  )
}

function PendingMetrics() {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {Array.from({ length: 3 }).map((_, index) => (
        <Skeleton key={index} className="h-28 rounded-xl" />
      ))}
    </div>
  )
}

function Metrics() {
  const { isLoading, hasPermission } = useAuth()

  if (isLoading) {
    return <PendingMetrics />
  }

  if (!hasPermission("metrics:read")) {
    return <Forbidden />
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Metrics</h1>
        <p className="text-muted-foreground">
          An overview of activity across the app
        </p>
      </div>
      <Suspense fallback={<PendingMetrics />}>
        <MetricsContent />
      </Suspense>
    </div>
  )
}
