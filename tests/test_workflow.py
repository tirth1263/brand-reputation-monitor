from pathlib import Path

from workflow import (
    BrandReport,
    BrightDataClient,
    MemoryStore,
    NebiusBrandAnalyzer,
    NewsArticle,
    extract_json_payload,
    is_public_http_url,
    normalize_keywords,
)


def test_normalize_keywords_adds_company_and_deduplicates() -> None:
    result = normalize_keywords("news, Reviews; news\ncontroversy", "Acme")
    assert result == ["Acme news", "Acme Reviews", "Acme controversy"]


def test_normalize_keywords_preserves_existing_company() -> None:
    assert normalize_keywords("Acme launch", "Acme") == ["Acme launch"]


def test_public_url_validation_rejects_local_addresses() -> None:
    assert is_public_http_url("https://news.example.com/story")
    assert not is_public_http_url("http://localhost:8501")
    assert not is_public_http_url("file:///tmp/story")


def test_extract_json_from_markdown_fence() -> None:
    assert extract_json_payload('Result:\n```json\n{"score": 72}\n```') == {"score": 72}


def test_parse_google_news_html() -> None:
    html = """
    <div><a href="https://news.example.com/acme"><h3>Acme launches a product</h3></a>
    <span>A concise news description.</span></div>
    """
    results = BrightDataClient._parse_serp_html(html)
    assert results[0]["title"] == "Acme launches a product"
    assert results[0]["url"] == "https://news.example.com/acme"


def test_agent_output_cannot_replace_verified_url() -> None:
    source = NewsArticle(
        source_id="abc123",
        title="Verified headline",
        url="https://trusted.example.com/story",
        source="trusted.example.com",
        snippet="A verified snippet.",
    )
    malicious_output = {
        "overall_sentiment": "positive",
        "reputation_score": 80,
        "executive_summary": "Coverage is favorable.",
        "article_results": [
            {
                "source_id": "abc123",
                "url": "https://invented.example.com/fake",
                "summary": "The launch was received well.",
                "sentiment": "positive",
                "sentiment_score": 0.8,
                "sentiment_drivers": ["Launch reception"],
                "insights": ["Sustain momentum"],
            }
        ],
        "strategic_insights": ["Momentum is building"],
        "risks": [],
        "opportunities": ["Extend the story"],
        "recommendations": ["Brief spokespeople"],
    }
    report = NebiusBrandAnalyzer._build_report("Acme", ["Acme news"], [source], malicious_output)
    assert report.articles[0].url == "https://trusted.example.com/story"


def test_memory_store_persists_report(tmp_path: Path) -> None:
    database = tmp_path / "memory.db"
    store = MemoryStore(database_path=database)
    report = BrandReport(
        company="Acme",
        keywords=["Acme news"],
        created_at="2026-01-01T00:00:00+00:00",
        overall_sentiment="neutral",
        reputation_score=50,
        executive_summary="A test report.",
        articles=[],
        strategic_insights=[],
        risks=[],
        opportunities=[],
        recommendations=[],
    )
    store.save_report(report)
    assert store.recent_reports()[0].company == "Acme"
