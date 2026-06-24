import Head from "next/head";
import { useEffect, useState } from "react";

import { DashboardCard } from "../components/DashboardCard";
import { Layout } from "../components/Layout";
import { fetchDashboardSummaryForSession, getEmptyDashboardSummary } from "../lib/api";
import { getSessionId } from "../lib/session";
import type { DashboardSummary } from "../lib/types";

export default function DashboardPage() {
  const [summary, setSummary] = useState<DashboardSummary>(getEmptyDashboardSummary());
  const [backendUnavailable, setBackendUnavailable] = useState(false);

  useEffect(() => {
    const sessionId = getSessionId();

    void fetchDashboardSummaryForSession(sessionId)
      .then((nextSummary) => {
        setSummary(nextSummary);
        setBackendUnavailable(false);
      })
      .catch(() => {
        setSummary(getEmptyDashboardSummary());
        setBackendUnavailable(true);
      });
  }, []);

  return (
    <>
      <Head>
        <title>Publisher Dashboard</title>
      </Head>
      <Layout>
        <section className="section-header dashboard-header">
          <div>
            <p className="eyebrow">Publisher Dashboard</p>
            <h1>Prototype performance summary</h1>
            {backendUnavailable ? (
              <p className="backend-warning">
                Backend unavailable. Start the FastAPI server on <code>http://localhost:8000</code> and refresh.
              </p>
            ) : null}
          </div>
          <div className="status-badge">Inference: {summary.inference_mode}</div>
        </section>

        <section className="metrics-grid">
          <DashboardCard label="Article Views" value={summary.total_article_views} />
          <DashboardCard label="Ad Impressions" value={summary.total_ad_impressions} />
          <DashboardCard label="Ad Clicks" value={summary.total_ad_clicks} />
          <DashboardCard label="CTR" value={`${summary.ctr}%`} />
        </section>

        <section className="leaderboard-grid">
          <Leaderboard title="Top Viewed Articles" items={summary.top_viewed_articles} />
          <Leaderboard title="Top Served Ads" items={summary.top_served_ads} />
          <Leaderboard title="Top Categories" items={summary.top_categories} />
        </section>
      </Layout>
    </>
  );
}

function Leaderboard({ title, items }: { title: string; items: { label: string; value: number }[] }) {
  return (
    <div className="leaderboard-card">
      <h2>{title}</h2>
      {items.length === 0 ? (
        <p className="empty-copy">No data yet. Browse articles to generate demo metrics.</p>
      ) : (
        <ul className="leaderboard-list">
          {items.map((item) => (
            <li key={item.label}>
              <span>{item.label}</span>
              <strong>{item.value}</strong>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
