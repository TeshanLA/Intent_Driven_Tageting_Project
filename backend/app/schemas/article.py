from pydantic import BaseModel


class ArticleResponse(BaseModel):
    slug: str
    title: str
    category: str
    excerpt: str
    body: str

    model_config = {"from_attributes": True}
