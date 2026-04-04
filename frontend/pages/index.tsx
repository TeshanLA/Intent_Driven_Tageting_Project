import Head from "next/head";

import { ArticleCard } from "../components/ArticleCard";
import { Layout } from "../components/Layout";
import { fetchArticles } from "../lib/api";
import { groupArticlesByCategory } from "../lib/grouping";
import type { Article } from "../lib/types";

type HomePageProps = {
  articles: Article[];
  backendUnavailable: boolean;
};

export default function HomePage({ articles, backendUnavailable }: HomePageProps) {
  const grouped = groupArticlesByCategory(articles);

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

        {Object.entries(grouped).map(([category, categoryArticles]) => (
          <section className="category-section" key={category}>
            <div className="section-header">
              <h2>{category}</h2>
              <span>{categoryArticles.length} articles</span>
            </div>
            <div className="card-grid">
              {categoryArticles.map((article) => (
                <ArticleCard key={article.slug} article={article} />
              ))}
            </div>
          </section>
        ))}
      </Layout>
    </>
  );
}

export async function getServerSideProps() {
  try {
    const articles = await fetchArticles();
    return { props: { articles, backendUnavailable: false } };
  } catch {
    return { props: { articles: [], backendUnavailable: true } };
  }
}
