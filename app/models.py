from sqlmodel import Field, SQLModel
from datetime import datetime

class Article(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str  = Field(index=True)
    url: str
    published_date: datetime
    description: str
    source: str
    created_at: datetime | None = Field(default_factory=datetime.utcnow)
    # type: str
