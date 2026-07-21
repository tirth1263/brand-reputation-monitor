"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";

type Sentiment = "positive" | "negative" | "neutral";
type Article = {
  sourceId: string;
  title: string;
  url: string;
  publisher: string;
  summary: string;
  sentiment: Sentiment;
  sentimentScore: number;
  drivers: string[];
  insights: string[];
};
type Report = {
  company: string;
  keywords: string[];
  createdAt: string;
  overallSentiment: Sentiment;
  reputationScore: number;
  executiveSummary: string;
  strategicInsights: string[];
  risks: string[];
  opportunities: string[];
  recommendations: string[];
  articles: Article[];
  isDemo: boolean;
};

const demoReport: Report = {
  company: "Northstar Coffee (demo)",
  keywords: ["news", "sustainability"],
  createdAt: new Date().toISOString(),
  overallSentiment: "positive",
  reputationScore: 78,
  executiveSummary:
    "This fictional preview demonstrates a finished intelligence brief. Run a live analysis with your own API keys to collect current, attributable coverage.",
  strategicInsights: [
    "Sustainability is the strongest fictional reputation driver in this preview.",
    "Evidence quality matters as much as the claim itself.",
    "Expansion messaging works best when connected to local outcomes.",
  ],
  risks: ["Vague packaging language could create a credibility gap."],
  opportunities: ["Turn sourcing data into a reusable public proof point."],
  recommendations: [
    "Create a claim-verification page with definitions and methodology.",
    "Prepare a concise media fact sheet for regional expansion.",
    "Track recurring questions and update the public FAQ monthly.",
  ],
  articles: [
    { sourceId: "demo-1", title: "Fictional preview: Sourcing program earns community attention", url: "", publisher: "Demo publication", summary: "Illustrative positive coverage emphasizes transparent sourcing and local partnerships.", sentiment: "positive", sentimentScore: 0.82, drivers: ["Supplier transparency", "Community partnerships"], insights: ["Make sourcing proof easy to verify."] },
    { sourceId: "demo-2", title: "Fictional preview: Brand announces regional expansion", url: "", publisher: "Demo business desk", summary: "Illustrative factual coverage describes planned store openings without strong judgment.", sentiment: "neutral", sentimentScore: 0.05, drivers: ["Factual expansion announcement"], insights: ["Tie growth to measurable local impact."] },
    { sourceId: "demo-3", title: "Fictional preview: Customers question packaging claims", url: "", publisher: "Demo consumer journal", summary: "Illustrative critical coverage asks for clearer evidence behind packaging language.", sentiment: "negative", sentimentScore: -0.61, drivers: ["Unclear environmental claim"], insights: ["Publish third-party validation."] },
  ],
  isDemo: true,
};

function List({ items, empty }: { items: string[]; empty: string }) {
  if (!items?.length) return <p className="muted">{empty}</p>;
  return <ul>{items.map((item, index) => <li key={`${item}-${index}`}>{item}</li>)}</ul>;
}

export default function Home() {
  const staticDeployment = process.env.NEXT_PUBLIC_STATIC_MODE === "true";
  const [report, setReport] = useState<Report>(demoReport);
  const [company, setCompany] = useState("");
  const [keywords, setKeywords] = useState("news, reviews, controversy, announcement");
  const [nebiusKey, setNebiusKey] = useState("");
  const [brightKey, setBrightKey] = useState("");
  const [serpZone, setSerpZone] = useState("sdk_serp");
  const [unlockerZone, setUnlockerZone] = useState("unlocker");
  const [advanced, setAdvanced] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState<"report" | "method">("report");

  useEffect(() => {
    try {
      const stored = window.localStorage.getItem("brand-monitor-last-report");
      if (stored) setReport(JSON.parse(stored));
    } catch {}
  }, []);

  const counts = useMemo(() => ({
    positive: report.articles.filter((article) => article.sentiment === "positive").length,
    neutral: report.articles.filter((article) => article.sentiment === "neutral").length,
    negative: report.articles.filter((article) => article.sentiment === "negative").length,
  }), [report]);

  async function analyze(event: FormEvent) {
    event.preventDefault();
    setError("");
    if (staticDeployment) {
      setError("Live research needs the server-backed Streamlit or Node deployment. This public Pages edition is an interactive product preview.");
      return;
    }
    if (!company.trim() || !keywords.trim()) return setError("Enter a company and monitoring keywords.");
    if (!nebiusKey || !brightKey) return setError("Add both API keys for a live analysis.");
    setLoading(true);
    try {
      const response = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ company, keywords, nebiusKey, brightKey, serpZone, unlockerZone }),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error || "Analysis failed.");
      setReport(payload);
      window.localStorage.setItem("brand-monitor-last-report", JSON.stringify(payload));
      setActiveTab("report");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Analysis failed.");
    } finally {
      setLoading(false);
    }
  }

  function loadPreview() {
    setReport({ ...demoReport, createdAt: new Date().toISOString() });
    window.localStorage.removeItem("brand-monitor-last-report");
  }

  return (
    <main>
      <header className="topbar">
        <a className="brand" href="#top"><span className="brandIcon">⌁</span><span>REPUTATION / AI<small>Evidence intelligence</small></span></a>
        <a className="sourceLink" href="https://github.com/tirth1263/brand-reputation-monitor" target="_blank" rel="noreferrer">GitHub ↗</a>
      </header>

      <section className="hero" id="top">
        <div className="eyebrow">Realtime signal intelligence</div>
        <h1>Know what the world says<br />before it shapes <em>your brand.</em></h1>
        <p>Turn current news coverage into an evidence-backed reputation brief: verified sources, sentiment drivers, emerging risks, and the actions that matter next.</p>
        <div className="pills"><span>● Live web research</span><span>● No fabricated URLs</span><span>● BYOK security</span><span>● Decision-ready output</span></div>
      </section>

      <section className="workspace">
        <aside className="setup card">
          <div className="sectionNumber">01 / CONFIGURE</div>
          <h2>Launch a live monitor</h2>
          <p className="muted">Credentials are sent only to this deployment for the active request and are never saved.</p>
          {staticDeployment && <div className="hostedPreview">Public hosted preview<br /><span>Use the one-click Render deployment for live API research.</span></div>}
          <form onSubmit={analyze}>
            <label>Company or brand<input value={company} onChange={(e) => setCompany(e.target.value)} placeholder="e.g. Apple" /></label>
            <label>Monitoring angles<textarea value={keywords} onChange={(e) => setKeywords(e.target.value)} rows={4} /></label>
            <label>Nebius API key<input type="password" value={nebiusKey} onChange={(e) => setNebiusKey(e.target.value)} placeholder="Enter Nebius key" autoComplete="off" /></label>
            <label>Bright Data API key<input type="password" value={brightKey} onChange={(e) => setBrightKey(e.target.value)} placeholder="Enter Bright Data key" autoComplete="off" /></label>
            <button className="textButton" type="button" onClick={() => setAdvanced(!advanced)}>{advanced ? "−" : "+"} Advanced zones</button>
            {advanced && <div className="advanced"><label>SERP zone<input value={serpZone} onChange={(e) => setSerpZone(e.target.value)} /></label><label>Unlocker zone<input value={unlockerZone} onChange={(e) => setUnlockerZone(e.target.value)} /></label></div>}
            {error && <div className="error">{error}</div>}
            <button className="primary" disabled={loading || staticDeployment}>{loading ? <><span className="spinner" /> Researching live coverage…</> : staticDeployment ? "Live analysis · server deployment" : "Analyze live reputation →"}</button>
            <button className="secondary" type="button" onClick={loadPreview}>Explore fictional preview</button>
            {staticDeployment && <a className="deployLink" href="https://render.com/deploy?repo=https://github.com/tirth1263/brand-reputation-monitor" target="_blank" rel="noreferrer">Deploy the live app on Render ↗</a>}
          </form>
        </aside>

        <div className="intelligence">
          {report.isDemo && <div className="demoNotice">Preview mode — all names, headlines, and findings are fictional.</div>}
          <nav className="tabs"><button className={activeTab === "report" ? "active" : ""} onClick={() => setActiveTab("report")}>Intelligence report</button><button className={activeTab === "method" ? "active" : ""} onClick={() => setActiveTab("method")}>Methodology</button></nav>

          {activeTab === "report" ? <>
            <div className="reportHeading"><div><div className="sectionNumber">LATEST BRIEF</div><h2>{report.company}</h2></div><div className={`sentiment ${report.overallSentiment}`}>{report.overallSentiment}</div></div>
            <div className="metrics">
              <article><span>Reputation score</span><strong>{report.reputationScore}<small>/100</small></strong></article>
              <article><span>Verified sources</span><strong>{report.articles.length}</strong></article>
              <article><span>Positive</span><strong>{counts.positive}</strong></article>
              <article><span>Neutral</span><strong>{counts.neutral}</strong></article>
              <article><span>Negative</span><strong>{counts.negative}</strong></article>
            </div>
            <div className="readout card"><div className="sectionNumber">EXECUTIVE READOUT</div><p>{report.executiveSummary}</p></div>
            <div className="twoColumns">
              <section className="card insights"><div className="sectionNumber">STRATEGIC SIGNALS</div>{report.strategicInsights.map((item, index) => <div className="insight" key={item}><span>{index + 1}</span><p>{item}</p></div>)}</section>
              <section className="card distribution"><div className="sectionNumber">COVERAGE MIX</div><div className="bar"><i style={{ width: `${report.articles.length ? counts.positive / report.articles.length * 100 : 0}%` }} /><i style={{ width: `${report.articles.length ? counts.neutral / report.articles.length * 100 : 0}%` }} /><i style={{ width: `${report.articles.length ? counts.negative / report.articles.length * 100 : 0}%` }} /></div><div className="legend"><span>● Positive</span><span>● Neutral</span><span>● Negative</span></div></section>
            </div>
            <div className="twoColumns"><section className="signalCard risk"><h3>Risk radar</h3><List items={report.risks} empty="No material risks identified." /></section><section className="signalCard opportunity"><h3>Opportunity map</h3><List items={report.opportunities} empty="No clear opportunities identified." /></section></div>
            <section className="recommendations"><div className="sectionNumber">RECOMMENDED NEXT MOVES</div>{report.recommendations.map((item, index) => <div className="nextMove" key={item}><span>0{index + 1}</span><p>{item}</p></div>)}</section>
            <section className="sources"><div className="sectionNumber">SOURCE INTELLIGENCE</div>{report.articles.map((article) => <details key={article.sourceId}><summary><span className={`sentiment ${article.sentiment}`}>{article.sentiment}</span><strong>{article.title}</strong><small>{article.publisher}</small></summary><p>{article.summary}</p>{article.drivers.length > 0 && <p className="muted"><b>Drivers:</b> {article.drivers.join(" · ")}</p>}{article.url ? <a href={article.url} target="_blank" rel="noreferrer">Open original source ↗</a> : <span className="muted">Illustrative source; no external article is claimed.</span>}</details>)}</section>
          </> : <section className="method card"><div className="sectionNumber">EVIDENCE PIPELINE</div><h2>Provenance by construction</h2><ol><li><b>Collect</b><span>Bright Data retrieves current Google News results.</span></li><li><b>Read</b><span>Web Unlocker extracts accessible article content.</span></li><li><b>Analyze</b><span>Nebius produces structured sentiment and brand signals.</span></li><li><b>Verify</b><span>Source URLs are reattached from immutable collection IDs.</span></li><li><b>Remember</b><span>This web edition keeps the last report in your browser; the Python edition adds Memori + SQLite.</span></li></ol></section>}
        </div>
      </section>
      <footer><span>Brand Reputation Monitor</span><span>Bright Data · Nebius · Agno · Memori</span></footer>
    </main>
  );
}
