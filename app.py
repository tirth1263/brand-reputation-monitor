"""Streamlit interface for the Brand Reputation Monitor."""

from __future__ import annotations

import html
import json
import os
from datetime import datetime
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

from workflow import (
    CONFIG,
    BrandReport,
    MemoryStore,
    get_demo_report,
    normalize_keywords,
    run_brand_monitoring,
)

ROOT = Path(__file__).resolve().parent

st.set_page_config(
    page_title="Brand Reputation Monitor",
    page_icon=str(ROOT / "assets" / "logo.svg"),
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap');

        :root {
          --ink: #f4f7fb;
          --muted: #91a4ba;
          --panel: rgba(13, 27, 42, .78);
          --line: rgba(148, 163, 184, .16);
          --purple: #8b5cf6;
          --cyan: #22d3ee;
        }
        html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
        h1, h2, h3 { font-family: 'Manrope', sans-serif !important; letter-spacing: -.035em; }
        .stApp {
          background:
            radial-gradient(circle at 85% -10%, rgba(124, 58, 237, .22), transparent 32rem),
            radial-gradient(circle at -8% 30%, rgba(34, 211, 238, .09), transparent 27rem),
            #07111f;
        }
        [data-testid="stSidebar"] {
          background: rgba(7, 17, 31, .94);
          border-right: 1px solid var(--line);
        }
        [data-testid="stSidebar"] [data-testid="stImage"] img { max-width: 58px; }
        .block-container { max-width: 1240px; padding-top: 2.1rem; padding-bottom: 5rem; }
        .brand-lockup { display: flex; align-items: center; gap: .7rem; margin: .25rem 0 1.6rem; }
        .brand-mark { width: 11px; height: 32px; border-radius: 99px; background: linear-gradient(#a78bfa, #22d3ee); box-shadow: 0 0 25px rgba(139,92,246,.55); }
        .brand-name { font-family: Manrope,sans-serif; font-weight: 800; font-size: 1.02rem; letter-spacing: -.02em; }
        .brand-kicker { color: var(--muted); font-size: .72rem; text-transform: uppercase; letter-spacing: .14em; }
        .hero { padding: 1.6rem 0 1.15rem; }
        .eyebrow { color: #67e8f9; font-weight: 700; font-size: .73rem; letter-spacing: .16em; text-transform: uppercase; margin-bottom: .65rem; }
        .hero h1 { font-size: clamp(2.25rem, 5vw, 4.25rem); line-height: .98; max-width: 850px; margin: 0 0 1rem; }
        .hero h1 span { background: linear-gradient(100deg, #c4b5fd, #67e8f9); -webkit-background-clip: text; color: transparent; }
        .hero p { color: #a9b7c8; font-size: 1.08rem; max-width: 730px; line-height: 1.7; }
        .trust-row { display: flex; flex-wrap: wrap; gap: .55rem; margin-top: 1.2rem; }
        .trust-pill { border: 1px solid var(--line); background: rgba(13,27,42,.62); border-radius: 99px; padding: .42rem .72rem; color: #c8d4e2; font-size: .78rem; }
        .trust-dot { display:inline-block; width:6px; height:6px; border-radius:50%; background:#22d3ee; margin-right:7px; box-shadow:0 0 10px #22d3ee; }
        .panel, [data-testid="stMetric"], [data-testid="stExpander"] {
          background: var(--panel); border: 1px solid var(--line); border-radius: 16px;
        }
        .panel { padding: 1.25rem 1.35rem; }
        [data-testid="stMetric"] { padding: 1rem 1.05rem; }
        [data-testid="stMetricLabel"] { color: var(--muted); }
        [data-testid="stMetricValue"] { font-family: Manrope,sans-serif; letter-spacing: -.04em; }
        [data-testid="stTabs"] [data-baseweb="tab-list"] { gap: 1.25rem; border-bottom: 1px solid var(--line); }
        [data-testid="stTabs"] [data-baseweb="tab"] { padding-left: 0; padding-right: 0; }
        .section-label { color: #91a4ba; font-size: .72rem; text-transform: uppercase; letter-spacing: .13em; font-weight: 700; margin: 1.2rem 0 .5rem; }
        .summary { font-size: 1.02rem; color: #dbe5ef; line-height: 1.75; }
        .signal-card { min-height: 155px; padding: 1rem 1.1rem; border: 1px solid var(--line); border-radius: 15px; background: rgba(13,27,42,.65); }
        .signal-card.risk { border-top: 2px solid #fb7185; }
        .signal-card.opportunity { border-top: 2px solid #34d399; }
        .signal-card h4 { margin: 0 0 .7rem; font-family: Manrope,sans-serif; }
        .signal-card ul { padding-left: 1.1rem; color: #b9c7d5; line-height: 1.55; }
        .sentiment { display:inline-flex; align-items:center; gap:.36rem; border-radius:99px; padding:.25rem .58rem; font-size:.72rem; font-weight:700; text-transform:uppercase; letter-spacing:.08em; }
        .sentiment.positive { color:#6ee7b7; background:rgba(16,185,129,.12); }
        .sentiment.negative { color:#fda4af; background:rgba(244,63,94,.12); }
        .sentiment.neutral { color:#cbd5e1; background:rgba(148,163,184,.12); }
        .source-title { font-family: Manrope,sans-serif; font-weight:700; font-size:1.02rem; color:#edf3f8; }
        .source-meta { color:#8195aa; font-size:.78rem; margin:.25rem 0 .8rem; }
        .demo-banner { border:1px solid rgba(251,191,36,.32); background:rgba(245,158,11,.08); border-radius:13px; padding:.85rem 1rem; color:#fde68a; margin:.5rem 0 1.2rem; }
        .step { display:flex; gap:.85rem; align-items:flex-start; margin-bottom:1rem; }
        .step-num { flex:0 0 30px; height:30px; display:grid; place-items:center; border-radius:9px; background:rgba(139,92,246,.18); color:#c4b5fd; font-weight:700; }
        .step strong { color:#e9eff6; } .step span { display:block; color:#91a4ba; font-size:.84rem; margin-top:.15rem; }
        .footer { color:#6f839a; text-align:center; font-size:.78rem; margin-top:4rem; padding-top:1.4rem; border-top:1px solid var(--line); }
        .stButton button, .stDownloadButton button { border-radius: 11px; min-height: 2.7rem; font-weight: 700; }
        .stButton button[kind="primary"] { background: linear-gradient(100deg,#7c3aed,#2563eb); border:0; box-shadow:0 10px 30px rgba(124,58,237,.22); }
        [data-testid="stChatMessage"] { background:rgba(13,27,42,.55); border:1px solid var(--line); border-radius:15px; }
        a { color:#67e8f9 !important; }
        #MainMenu, footer, header { visibility:hidden; }
        @media (max-width: 700px) { .block-container { padding: 1rem; } .hero h1 { font-size:2.5rem; } }
        </style>
        """,
        unsafe_allow_html=True,
    )


def safe(value: object) -> str:
    return html.escape(str(value))


def init_state() -> None:
    defaults = {
        "report_json": "",
        "chat_messages": [],
        "company_input": "",
        "keywords_input": "news, reviews, controversy, announcement",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def current_report() -> BrandReport | None:
    if not st.session_state.report_json:
        return None
    try:
        return BrandReport.model_validate_json(st.session_state.report_json)
    except ValueError:
        st.session_state.report_json = ""
        return None


def render_sidebar() -> tuple[str, str, str, str]:
    with st.sidebar:
        st.image(str(ROOT / "assets" / "logo.svg"), width=56)
        st.markdown(
            """
            <div class="brand-lockup">
              <div class="brand-mark"></div>
              <div><div class="brand-name">REPUTATION / AI</div><div class="brand-kicker">Evidence intelligence</div></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("### Live analysis setup")
        st.caption("Keys stay in this browser session and are never written to the repository.")
        nebius_key = st.text_input(
            "Nebius API key",
            value=os.getenv("NEBIUS_API_KEY", ""),
            type="password",
            placeholder="Enter Nebius key",
        )
        brightdata_key = st.text_input(
            "Bright Data API key",
            value=os.getenv("BRIGHTDATA_API_KEY", ""),
            type="password",
            placeholder="Enter Bright Data key",
        )
        with st.expander("Advanced zones"):
            serp_zone = st.text_input(
                "SERP zone",
                value=os.getenv("BRIGHTDATA_SERP_ZONE", CONFIG["bright_data"]["serp_zone"]),
            )
            unlocker_zone = st.text_input(
                "Web Unlocker zone",
                value=os.getenv("BRIGHTDATA_UNLOCKER_ZONE", CONFIG["bright_data"]["unlocker_zone"]),
            )
            st.caption(f"Model: {CONFIG['nebius']['model']}")

        ready = bool(nebius_key and brightdata_key)
        status_color = "#34d399" if ready else "#fbbf24"
        status_text = "Ready for live analysis" if ready else "Two keys needed for live analysis"
        st.markdown(
            f'<div style="margin:.8rem 0 1rem;color:{status_color};font-size:.8rem">● {status_text}</div>',
            unsafe_allow_html=True,
        )
        if st.button("Explore dashboard preview", width="stretch"):
            st.session_state.report_json = get_demo_report().model_dump_json()
            st.session_state.chat_messages = []
            st.rerun()
        if current_report() and st.button("Clear current report", width="stretch"):
            st.session_state.report_json = ""
            st.session_state.chat_messages = []
            st.rerun()

        st.markdown("---")
        st.caption("Built with Bright Data · Nebius · Agno · Memori")
        st.link_button(
            "View source on GitHub",
            "https://github.com/tirth1263/brand-reputation-monitor",
            width="stretch",
        )
    st.session_state["_nebius_runtime_key"] = nebius_key
    return nebius_key, brightdata_key, serp_zone, unlocker_zone


def render_hero() -> None:
    st.markdown(
        """
        <section class="hero">
          <div class="eyebrow">Realtime signal intelligence</div>
          <h1>Know what the world says <span>before it shapes your brand.</span></h1>
          <p>Turn current news coverage into an evidence-backed reputation brief: verified sources, sentiment drivers, emerging risks, and the actions that matter next.</p>
          <div class="trust-row">
            <div class="trust-pill"><span class="trust-dot"></span>Live web research</div>
            <div class="trust-pill"><span class="trust-dot"></span>No fabricated URLs</div>
            <div class="trust-pill"><span class="trust-dot"></span>Persistent context</div>
            <div class="trust-pill"><span class="trust-dot"></span>Actionable intelligence</div>
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_monitor_form(
    nebius_key: str, brightdata_key: str, serp_zone: str, unlocker_zone: str
) -> None:
    report = current_report()
    heading = "Run a new monitor" if report else "Launch your first monitor"
    wrapper = st.expander(heading, expanded=not bool(report)) if report else st.container()
    with wrapper:
        with st.form("monitor_form"):
            left, right = st.columns([0.42, 0.58], gap="large")
            with left:
                company = st.text_input(
                    "Company or brand",
                    value=st.session_state.company_input,
                    placeholder="e.g. Apple",
                )
                max_articles = st.slider("Maximum sources", 3, 12, 8)
            with right:
                keywords = st.text_area(
                    "Monitoring angles",
                    value=st.session_state.keywords_input,
                    placeholder="news, reviews, controversy, announcement",
                    height=119,
                    help="Separate keywords with commas or new lines. The company name is added automatically.",
                )
            submitted = st.form_submit_button(
                "Analyze live reputation", type="primary", width="stretch"
            )
        if submitted:
            st.session_state.company_input = company
            st.session_state.keywords_input = keywords
            if not nebius_key or not brightdata_key:
                st.error("Add both API keys in the sidebar to run a live analysis.")
                return
            if not normalize_keywords(keywords, company):
                st.error("Add at least one monitoring keyword.")
                return
            progress_bar = st.progress(0, text="Preparing research workflow")

            def update_progress(value: float, label: str) -> None:
                progress_bar.progress(min(int(value * 100), 100), text=label)

            try:
                result = run_brand_monitoring(
                    company=company,
                    keywords=keywords,
                    nebius_api_key=nebius_key,
                    brightdata_api_key=brightdata_key,
                    serp_zone=serp_zone,
                    unlocker_zone=unlocker_zone,
                    max_articles=max_articles,
                    progress=update_progress,
                )
            except Exception as exc:
                progress_bar.empty()
                message = (
                    str(exc).replace(nebius_key, "[redacted]").replace(brightdata_key, "[redacted]")
                )
                st.error(f"Analysis could not be completed: {message}")
            else:
                st.session_state.report_json = result.model_dump_json()
                st.session_state.chat_messages = []
                st.rerun()


def sentiment_chart(report: BrandReport) -> go.Figure:
    counts = report.sentiment_counts
    fig = go.Figure(
        data=[
            go.Pie(
                labels=["Positive", "Neutral", "Negative"],
                values=[counts["positive"], counts["neutral"], counts["negative"]],
                hole=0.72,
                marker={"colors": ["#34d399", "#64748b", "#fb7185"]},
                textinfo="label+value",
                hovertemplate="%{label}: %{value}<extra></extra>",
            )
        ]
    )
    fig.update_layout(
        height=290,
        margin={"l": 10, "r": 10, "t": 20, "b": 15},
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#cbd5e1", "family": "DM Sans"},
        annotations=[
            {
                "text": f"<b>{len(report.articles)}</b><br><span style='font-size:11px'>sources</span>",
                "x": 0.5,
                "y": 0.5,
                "showarrow": False,
                "font": {"size": 24, "color": "#f4f7fb"},
            }
        ],
    )
    return fig


def render_list(items: list[str], empty_text: str) -> str:
    if not items:
        return f"<p style='color:#8195aa'>{safe(empty_text)}</p>"
    return "<ul>" + "".join(f"<li>{safe(item)}</li>" for item in items) + "</ul>"


def render_report(report: BrandReport) -> None:
    if report.is_demo:
        st.markdown(
            '<div class="demo-banner">Preview mode — all names, headlines, and findings below are fictional. Add API keys and run a live monitor for current, verified evidence.</div>',
            unsafe_allow_html=True,
        )

    tab_report, tab_advisor, tab_history = st.tabs(
        ["Intelligence report", "Follow-up advisor", "History & methodology"]
    )
    with tab_report:
        st.markdown(
            f'<div class="section-label">Latest brief · {safe(report.company)}</div>',
            unsafe_allow_html=True,
        )
        counts = report.sentiment_counts
        metric_columns = st.columns(5)
        metric_columns[0].metric("Reputation score", f"{report.reputation_score}/100")
        metric_columns[1].metric("Verified sources", len(report.articles))
        metric_columns[2].metric("Positive", counts["positive"])
        metric_columns[3].metric("Neutral", counts["neutral"])
        metric_columns[4].metric("Negative", counts["negative"])

        st.markdown('<div class="section-label">Executive readout</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="panel summary">{safe(report.executive_summary)}</div>',
            unsafe_allow_html=True,
        )

        chart_column, insight_column = st.columns([0.38, 0.62], gap="large")
        with chart_column:
            st.markdown('<div class="section-label">Coverage mix</div>', unsafe_allow_html=True)
            st.plotly_chart(
                sentiment_chart(report), width="stretch", config={"displayModeBar": False}
            )
        with insight_column:
            st.markdown(
                '<div class="section-label">Strategic signals</div>', unsafe_allow_html=True
            )
            for index, insight in enumerate(report.strategic_insights, 1):
                st.markdown(
                    f'<div class="step"><div class="step-num">{index}</div><div><strong>{safe(insight)}</strong></div></div>',
                    unsafe_allow_html=True,
                )

        risk_col, opportunity_col = st.columns(2, gap="large")
        with risk_col:
            st.markdown(
                f'<div class="signal-card risk"><h4>Risk radar</h4>{render_list(report.risks, "No material risks identified in the collected coverage.")}</div>',
                unsafe_allow_html=True,
            )
        with opportunity_col:
            st.markdown(
                f'<div class="signal-card opportunity"><h4>Opportunity map</h4>{render_list(report.opportunities, "No clear opportunities identified yet.")}</div>',
                unsafe_allow_html=True,
            )

        st.markdown(
            '<div class="section-label">Recommended next moves</div>', unsafe_allow_html=True
        )
        for index, recommendation in enumerate(report.recommendations, 1):
            st.markdown(
                f'<div class="step"><div class="step-num">{index}</div><div><strong>{safe(recommendation)}</strong><span>Prioritized from the evidence in this report.</span></div></div>',
                unsafe_allow_html=True,
            )

        st.markdown('<div class="section-label">Source intelligence</div>', unsafe_allow_html=True)
        for article in report.articles:
            icon = {"positive": "↗", "negative": "↘", "neutral": "→"}[article.sentiment]
            with st.expander(f"{icon}  {article.title}"):
                st.markdown(
                    f'<span class="sentiment {article.sentiment}">{article.sentiment}</span>'
                    f'<div class="source-meta">{safe(article.source)} · {safe(article.published_at or "Date not provided")}</div>'
                    f'<div class="summary">{safe(article.summary)}</div>',
                    unsafe_allow_html=True,
                )
                if article.sentiment_drivers:
                    st.markdown("**Sentiment drivers:** " + " · ".join(article.sentiment_drivers))
                if article.insights:
                    st.markdown("**Brand implications**")
                    for insight in article.insights:
                        st.markdown(f"- {insight}")
                if report.is_demo:
                    st.caption(
                        "Illustrative source — no external article is claimed in preview mode."
                    )
                else:
                    st.link_button("Open original source ↗", article.url)

        export_col, timestamp_col = st.columns([0.25, 0.75])
        with export_col:
            st.download_button(
                "Download report JSON",
                data=json.dumps(report.model_dump(), indent=2),
                file_name=f"{report.company.lower().replace(' ', '-')}-reputation-report.json",
                mime="application/json",
                width="stretch",
            )
        with timestamp_col:
            try:
                generated = datetime.fromisoformat(report.created_at).strftime(
                    "%b %d, %Y · %H:%M UTC"
                )
            except ValueError:
                generated = report.created_at
            st.caption(
                f"Generated {generated}. Findings reflect only the sources collected at run time."
            )

    with tab_advisor:
        render_advisor(report)

    with tab_history:
        render_history(report)


def render_advisor(report: BrandReport) -> None:
    st.markdown("### Ask the report")
    if report.is_demo:
        st.info(
            "Follow-up AI is disabled for the fictional preview. Run a live monitor to start a context-aware conversation."
        )
        return
    st.caption(
        "The advisor searches persistent context before answering and stays grounded in this report's verified sources."
    )
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    prompt = st.chat_input("Ask about sentiment, risks, sources, or next actions")
    if prompt:
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        nebius_key = st.session_state.get("_nebius_runtime_key", "") or os.getenv(
            "NEBIUS_API_KEY", ""
        )
        with st.chat_message("assistant"), st.spinner("Searching memory and evidence…"):
            try:
                answer = MemoryStore(nebius_key).answer_follow_up(prompt, report)
            except Exception as exc:
                answer = f"I couldn't answer this follow-up: {exc}"
            st.markdown(answer)
        st.session_state.chat_messages.append({"role": "assistant", "content": answer})


def render_history(report: BrandReport) -> None:
    st.markdown("### Persistent intelligence")
    try:
        memory = MemoryStore()
        reports = memory.recent_reports(8)
    except Exception as exc:
        st.warning(f"History is unavailable: {exc}")
        reports = []
        memory = None
    if reports:
        for past in reports:
            counts = past.sentiment_counts
            with st.expander(
                f"{past.company} · {past.reputation_score}/100 · {past.created_at[:10]}"
            ):
                st.write(past.executive_summary)
                st.caption(
                    f"{len(past.articles)} sources · {counts['positive']} positive · "
                    f"{counts['neutral']} neutral · {counts['negative']} negative"
                )
    else:
        st.caption("Live reports will appear here after the first completed analysis.")

    st.markdown("### How evidence moves through the system")
    st.image(str(ROOT / "assets" / "architecture.svg"), width="stretch")
    st.markdown(
        """
        1. **Collect:** Bright Data's SERP zone retrieves current Google News results for your keywords.
        2. **Verify and read:** Only returned public URLs are retained; Web Unlocker extracts accessible article copy.
        3. **Analyze:** An Agno agent running on Nebius classifies sentiment and produces structured reputation signals.
        4. **Remember:** Memori with SQLite stores conversation context, while an auditable local report log supports history.

        Live analysis never accepts model-generated links. The application attaches URLs from the collection step to the model's source IDs after analysis.
        """
    )
    if memory:
        st.caption(f"Active persistence layer: {memory.provider_label}")


def main() -> None:
    inject_styles()
    init_state()
    nebius_key, brightdata_key, serp_zone, unlocker_zone = render_sidebar()
    render_hero()
    render_monitor_form(nebius_key, brightdata_key, serp_zone, unlocker_zone)
    report = current_report()
    if report:
        render_report(report)
    else:
        st.markdown('<div class="section-label">What you get</div>', unsafe_allow_html=True)
        columns = st.columns(3, gap="large")
        cards = [
            (
                "01",
                "Evidence, not noise",
                "Every live finding traces back to an exact URL collected during research.",
            ),
            (
                "02",
                "Signals, not summaries",
                "Understand sentiment drivers, reputation risks, and strategic opportunities.",
            ),
            (
                "03",
                "Context that compounds",
                "Persistent memory keeps follow-up answers consistent across your monitoring workflow.",
            ),
        ]
        for column, (number, title, body) in zip(columns, cards, strict=True):
            with column:
                st.markdown(
                    f'<div class="panel"><div class="eyebrow">{number}</div><h3>{safe(title)}</h3><p style="color:#91a4ba;line-height:1.6">{safe(body)}</p></div>',
                    unsafe_allow_html=True,
                )

    st.markdown(
        '<div class="footer">Brand Reputation Monitor · Evidence-first intelligence for modern brand teams</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
