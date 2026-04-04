import type { Article } from "./types";

export function groupArticlesByCategory(articles: Article[]) {
  return articles.reduce<Record<string, Article[]>>((accumulator, article) => {
    accumulator[article.category] = accumulator[article.category] || [];
    accumulator[article.category].push(article);
    return accumulator;
  }, {});
}
