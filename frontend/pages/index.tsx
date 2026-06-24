import Head from "next/head";

import { ArticleCard } from "../components/ArticleCard";
import { Layout } from "../components/Layout";
import { fetchArticles } from "../lib/api";
import type { Article } from "../lib/types";

type HomePageProps = {
  articles: Article[];
  backendUnavailable: boolean;
};

export default function HomePage({ articles, backendUnavailable }: HomePageProps) {
  const mixedArticles = mixArticlesByCategory(articles);

  return (
    <>
      <Head>
        <title>Publisher Demo</title>
      </Head>
      <Layout>
        <section className="hero">
          <p className="eyebrow">Privacy-Preserving Ad Demo</p>
          <h1>Demo publisher site with session-based ad recommendations</h1>
          <p className="hero-copy">
            Browse articles across categories and see how a first-party, session-level recommendation flow can work
            without persistent user identity.
          </p>
          {backendUnavailable ? (
            <p className="backend-warning">
              Backend unavailable. Start the FastAPI server on <code>http://localhost:8000</code> and refresh.
            </p>
          ) : null}
        </section>

        <section className="category-section">
          <div className="section-header">
            <h2>All Articles</h2>
            <span>{mixedArticles.length} articles</span>
          </div>
          <div className="card-grid">
            {mixedArticles.map((article) => (
              <ArticleCard key={article.slug} article={article} />
            ))}
          </div>
        </section>
      </Layout>
    </>
  );
}

function mixArticlesByCategory(articles: Article[]) {
  const buckets = new Map<string, Article[]>();

  articles.forEach((article) => {
    const categoryArticles = buckets.get(article.category) || [];
    categoryArticles.push(article);
    buckets.set(article.category, categoryArticles);
  });

  const mixed: Article[] = [];
  let hasRemaining = true;

  while (hasRemaining) {
    hasRemaining = false;

    for (const categoryArticles of buckets.values()) {
      const nextArticle = categoryArticles.shift();
      if (!nextArticle) {
        continue;
      }

      mixed.push(nextArticle);
      hasRemaining = true;
    }
  }

  return mixed;
}

export async function getServerSideProps() {
  try {
    const articles = await fetchArticles();
    return { props: { articles, backendUnavailable: false } };
  } catch {
    return { props: { articles: [], backendUnavailable: true } };
  }
}
