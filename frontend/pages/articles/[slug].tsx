import Head from "next/head";
import { useEffect, useRef, useState } from "react";

import { AdSlot } from "../../components/AdSlot";
import { Layout } from "../../components/Layout";
import { fetchAd, fetchArticle } from "../../lib/api";
import { getSessionId } from "../../lib/session";
import { sendTrackingBeacon, trackEvent } from "../../lib/tracking";
import type { Ad, Article } from "../../lib/types";

type ArticlePageProps = {
  article: Article;
};

export default function ArticlePage({ article }: ArticlePageProps) {
  const [ad, setAd] = useState<Ad | null>(null);
  const startTimeRef = useRef<number>(Date.now());
  const maxScrollDepthRef = useRef<number>(0);
  const hasFlushedEngagementRef = useRef<boolean>(false);
  const milestoneStateRef = useRef<Record<number, boolean>>({
    0.25: false,
    0.5: false,
    0.75: false,
    1: false
  });

  useEffect(() => {
    const sessionId = getSessionId();
    startTimeRef.current = Date.now();
    maxScrollDepthRef.current = 0;
    hasFlushedEngagementRef.current = false;
    milestoneStateRef.current = { 0.25: false, 0.5: false, 0.75: false, 1: false };

    void trackEvent({
      sessionId,
      eventType: "page_view",
      articleSlug: article.slug,
      articleCategory: article.category,
      metadata: {}
    });

    void fetchAd({
      session_id: sessionId,
      article_slug: article.slug,
      article_title: article.title,
      article_category: article.category,
      article_text: article.body
    })
      .then(setAd)
      .catch(() => setAd(null));

    const flushEngagement = () => {
      if (hasFlushedEngagementRef.current) {
        return;
      }

      hasFlushedEngagementRef.current = true;
      const dwellTimeSeconds = Math.max(1, Math.round((Date.now() - startTimeRef.current) / 1000));
      const completion = Number((maxScrollDepthRef.current * 0.9).toFixed(2));

      const sent = sendTrackingBeacon({
        sessionId,
        eventType: "engagement",
        articleSlug: article.slug,
        articleCategory: article.category,
        metadata: {
          dwell_time_seconds: dwellTimeSeconds,
          scroll_depth_ratio: maxScrollDepthRef.current,
          estimated_completion_ratio: completion
        }
      });

      if (!sent) {
        void trackEvent({
          sessionId,
          eventType: "engagement",
          articleSlug: article.slug,
          articleCategory: article.category,
          metadata: {
            dwell_time_seconds: dwellTimeSeconds,
            scroll_depth_ratio: maxScrollDepthRef.current,
            estimated_completion_ratio: completion
          }
        });
      }
    };

    const onScroll = () => {
      const scrollable = document.documentElement.scrollHeight - window.innerHeight;
      const ratio = scrollable > 0 ? Math.min(window.scrollY / scrollable, 1) : 0;
      const roundedRatio = Number(ratio.toFixed(2));
      maxScrollDepthRef.current = Math.max(maxScrollDepthRef.current, roundedRatio);

      [0.25, 0.5, 0.75, 1].forEach((milestone) => {
        if (!milestoneStateRef.current[milestone] && roundedRatio >= milestone) {
          milestoneStateRef.current[milestone] = true;
          void trackEvent({
            sessionId,
            eventType: "scroll_depth",
            articleSlug: article.slug,
            articleCategory: article.category,
            metadata: {
              scroll_depth_ratio: milestone
            }
          });
        }
      });
    };

    const onPageHide = () => {
      flushEngagement();
    };

    window.addEventListener("scroll", onScroll);
    window.addEventListener("pagehide", onPageHide);

    return () => {
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("pagehide", onPageHide);
      flushEngagement();
    };
  }, [article.body, article.category, article.slug, article.title]);

  return (
    <>
      <Head>
        <title>{article.title}</title>
      </Head>
      <Layout>
        <article className="article-shell">
          <div className="article-meta">
            <span className="category-pill">{article.category}</span>
            <span>Demo article</span>
          </div>
          <h1>{article.title}</h1>
          <p className="article-excerpt">{article.excerpt}</p>

          <AdSlot ad={ad} article={article} />

          <div className="article-body">
            {article.body.split(". ").map((paragraph, index) => (
              <p key={`${article.slug}-${index}`}>{paragraph.trim().endsWith(".") ? paragraph.trim() : `${paragraph.trim()}.`}</p>
            ))}
          </div>
        </article>
      </Layout>
    </>
  );
}

export async function getServerSideProps(context: { params?: { slug?: string } }) {
  const slug = context.params?.slug;
  if (!slug) {
    return { notFound: true };
  }

  try {
    const article = await fetchArticle(slug);
    return { props: { article } };
  } catch {
    return { notFound: true };
  }
}
