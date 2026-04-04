import Link from "next/link";

import type { Article } from "../lib/types";

export function ArticleCard({ article }: { article: Article }) {
  return (
    <Link className="article-card" href={`/articles/${article.slug}`}>
      <div className="article-card-top">
        <span className="category-pill">{article.category}</span>
      </div>
      <h3>{article.title}</h3>
      <p>{article.excerpt}</p>
      <span className="read-more">Read article</span>
    </Link>
  );
}
