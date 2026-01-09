from datetime import datetime
from app.domain.article import Article, Author

def test_article_model_creation():
    author = Author(name="Saulo")
    article = Article(
        id="123",
        title="Test Title",
        authors=[author],
        summary="Summary",
        published=datetime.now(),
        updated=datetime.now(),
        categories=["cs.CL"],
        link="http://test.com",
        pdf_link="http://test.com/pdf",
    )

    assert article.title == "Test Title"
    assert article.authors[0].name == "Saulo"
    assert "cs.CL" in article.categories
