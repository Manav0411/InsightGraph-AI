import { SignInButton } from "@clerk/nextjs";
import SubscribeForm from "./SubscribeForm";
import "./landing.css";

/**
 * Public marketing landing, shown at `/` to signed-out visitors only
 * (see src/app/page.js). Its visual system is isolated under `.lp-root`
 * and defined in landing.css — it deliberately does not use the app's
 * Tailwind token classes.
 */
export default function Landing() {
  return (
    <div className="lp-root">
      {/* ============ HERO — the overnight run ============ */}
      <header className="lp-hero" id="top">
        <div className="lp-wrap">
          <p className="lp-run-meta">
            run <b>#412</b> · started 02:14 · finished 03:46 · 4 sources
          </p>

          <div className="lp-log" aria-label="Overnight pipeline run log">
            <div className="lp-l">
              <span className="lp-t">02:14</span>
              <span className="lp-a">retriever</span>
              <span className="lp-d">
                pulled <b>1,847</b> raw signals — tavily, hn, arxiv, rss
              </span>
            </div>
            <div className="lp-l">
              <span className="lp-t">02:31</span>
              <span className="lp-a">validator</span>
              <span className="lp-d">
                dropped <b>1,203</b> off-topic / clickbait
              </span>
            </div>
            <div className="lp-l">
              <span className="lp-t">02:39</span>
              <span className="lp-a">ranker</span>
              <span className="lp-d">
                scored 644, boosted your 10 topics, kept top 14
              </span>
            </div>
            <div className="lp-l lp-retry">
              <span className="lp-t">03:02</span>
              <span className="lp-a">evaluator</span>
              <span className="lp-d">too thin → back to retriever, scaled up</span>
            </div>
            <div className="lp-l">
              <span className="lp-t">03:40</span>
              <span className="lp-a">analyzer</span>
              <span className="lp-d">
                14 grounded summaries, 2 with prior-briefing context
              </span>
            </div>
            <div className="lp-l">
              <span className="lp-t">03:44</span>
              <span className="lp-a">evaluator</span>
              <span className="lp-d">pruned 2 weak, balanced by source</span>
            </div>
            <div className="lp-l">
              <span className="lp-t">03:46</span>
              <span className="lp-a">composer</span>
              <span className="lp-d">briefing filed · SQI 61</span>
            </div>
          </div>

          <div className="lp-transform">
            <span className="lp-from">1,847</span>
            <span className="lp-op">→</span>
            <span className="lp-to">12</span>
            <span className="lp-cap">signals in / signals out</span>
          </div>

          <h1>
            You slept. It read everything. Here are <em>the twelve</em>.
          </h1>

          <SubscribeForm onTerm cta="Start free" />
          <p className="lp-fineprint lp-on-term">
            free while in preview · topics take a minute · unsubscribe anytime
          </p>
        </div>
      </header>

      {/* ============ the briefing, as a document ============ */}
      <section className="lp-seg" id="briefing">
        <div className="lp-wrap">
          <div className="lp-seg-head lp-prose">
            <span className="lp-eyebrow">03:46 — filed</span>
            <h2>…and this is what it hands you.</h2>
            <p>
              Not a link dump. A dated document: each signal is a summary, the
              concrete details, and why it matters — against its precedent.
            </p>
          </div>

          <div className="lp-doc">
            <div className="lp-masthead">
              <span className="lp-name">InsightGraph</span>
              <span className="lp-date">Mon 8 Sep 2026 · SQI 61 · ~3m 40s</span>
            </div>
            <div className="lp-rows">
              <div className="lp-r">
                <span className="lp-kicker">top story · tavily</span>
                <h4>
                  Nvidia buys Hugging Face in a $12.9B bet on open-source AI
                </h4>
                <p>
                  Consolidates the model-hosting layer under one vendor; the
                  &ldquo;open&rdquo; commons now has a landlord.
                </p>
              </div>
              <div className="lp-r">
                <span className="lp-kicker">research · arxiv cs.CL</span>
                <h4>
                  Multi-step tool-calling over public APIs: a benchmark and a
                  data recipe
                </h4>
                <p>
                  A new eval for agents that chain real API calls, plus a
                  synthesis method for training data.
                </p>
              </div>
              <div className="lp-r">
                <span className="lp-kicker">community pulse · hacker news</span>
                <h4>
                  &ldquo;Open-source AI is the path forward&rdquo; — but nobody
                  agrees what open means
                </h4>
                <p>
                  The thread is optimistic on open weights; the friction is
                  definitional, not ideological.
                </p>
                <p className="lp-why">
                  <b>Why it matters —</b> sets up the licensing fight that
                  decides whether the next products are built on a commons or on
                  rented APIs. Same tension as June&rsquo;s Meta-weights debate.
                </p>
              </div>
            </div>
            <div className="lp-foot">
              <span>12 signals · 4 sources</span>
              <span>grounding 100% · retry ×1</span>
            </div>
          </div>
          <p className="lp-doc-cap">
            In your inbox at 8:00, or on the web with the full archive behind it.
          </p>
        </div>
      </section>

      <div className="lp-trust">
        <div className="lp-wrap">
          <span className="lp-t-lbl">reads, every night</span>
          <div className="lp-src">
            <span>Hacker{" "}News</span>
            <span>arXiv</span>
            <span>Tavily</span>
            <span>Hugging{" "}Face</span>
            <span>VentureBeat</span>
            <span>MIT{" "}Technology{" "}Review</span>
          </div>
        </div>
      </div>

      {/* ============ the pipeline, as a dark inset ============ */}
      <section className="lp-seg" id="pipeline">
        <div className="lp-wrap">
          <div className="lp-seg-head lp-prose">
            <span className="lp-eyebrow">the machine</span>
            <h2>
              Six agents in a graph. It can send itself <em>back</em>.
            </h2>
            <p>
              Each briefing is one traversal of a LangGraph state machine. If the
              evaluator judges the run too thin or too one-sided, it routes back
              to the retriever and widens the net — once — before it will
              compose.
            </p>
          </div>

          <div className="lp-machine">
            <span className="lp-m-lbl">graph · run #412</span>
            <div className="lp-graph-scroll">
              <div className="lp-graph">
                <svg
                  viewBox="0 0 700 132"
                  role="img"
                  aria-label="Six-node pipeline: retrieve, validate, rank, analyze, evaluate, compose, with a dashed recovery edge from evaluate back to retrieve"
                >
                  <path className="lp-e" d="M110 54 H136" />
                  <path className="lp-e" d="M214 54 H240" />
                  <path className="lp-e" d="M318 54 H344" />
                  <path className="lp-e" d="M422 54 H448" />
                  <path className="lp-e" d="M526 54 H552" />
                  <path className="lp-e-retry" d="M582 74 V106 H52 V74" />
                  <g>
                    <rect className="lp-n-box" x="12" y="36" width="98" height="36" rx="6" />
                    <text className="lp-n-label" x="61" y="59" textAnchor="middle">
                      retrieve
                    </text>
                  </g>
                  <g>
                    <rect className="lp-n-box" x="116" y="36" width="98" height="36" rx="6" />
                    <text className="lp-n-label" x="165" y="59" textAnchor="middle">
                      validate
                    </text>
                  </g>
                  <g>
                    <rect className="lp-n-box" x="220" y="36" width="98" height="36" rx="6" />
                    <text className="lp-n-label" x="269" y="59" textAnchor="middle">
                      rank
                    </text>
                  </g>
                  <g>
                    <rect className="lp-n-box" x="324" y="36" width="98" height="36" rx="6" />
                    <text className="lp-n-label" x="373" y="59" textAnchor="middle">
                      analyze
                    </text>
                  </g>
                  <g>
                    <rect className="lp-n-box" x="428" y="36" width="98" height="36" rx="6" />
                    <text className="lp-n-label" x="477" y="59" textAnchor="middle">
                      evaluate
                    </text>
                  </g>
                  <g>
                    <rect
                      className="lp-n-box"
                      x="532"
                      y="36"
                      width="98"
                      height="36"
                      rx="6"
                      style={{ stroke: "var(--term-signal)", strokeWidth: 2 }}
                    />
                    <text
                      className="lp-n-label"
                      x="581"
                      y="59"
                      textAnchor="middle"
                      style={{ fill: "var(--term-signal)" }}
                    >
                      compose
                    </text>
                  </g>
                </svg>
              </div>
            </div>
            <p className="lp-retry-note">
              <i></i> <b>recovery</b> — the only edge that runs backwards.
            </p>

            <div className="lp-stages">
              <div>
                <b>retrieve</b>Tavily, Hacker News, arXiv and lab RSS, deduped
                into one set.
              </div>
              <div>
                <b>validate</b>Fast yes/no relevance pass. Drops clickbait. Fails
                open.
              </div>
              <div>
                <b>rank</b>Trend score, then your topic boosts and hard
                exclusions.
              </div>
              <div>
                <b>analyze</b>Grounded summary, details, &ldquo;why it
                matters&rdquo; — with vector-memory context.
              </div>
              <div>
                <b>evaluate</b>Prunes weak generations, checks summary vs.
                headline, balances sources.
              </div>
              <div>
                <b>compose</b>Assembles the digest, writes the intro, files it to
                your archive and inbox.
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ============ what you tune ============ */}
      <section className="lp-seg" id="tune">
        <div className="lp-wrap">
          <div className="lp-seg-head lp-prose">
            <span className="lp-eyebrow">your inputs</span>
            <h2>
              You set the beat. It <em>mutes</em> the rest.
            </h2>
          </div>
          <div className="lp-cols">
            <div className="lp-tune-copy">
              <p className="lp-lead">
                Ten topics, picked at onboarding, changed whenever.
              </p>
              <p>
                The ranker adds a fixed boost to anything matching your topics, so
                your beats float to the top of the run.
              </p>
              <p>
                Your exclusion list is stronger: matching signals are dropped in
                the ranker, before the analyzer ever spends a token on them.
              </p>
            </div>
            <div>
              <div className="lp-chips">
                <span className="lp-chip lp-on">ai agents</span>
                <span className="lp-chip lp-on">large language models</span>
                <span className="lp-chip">foundation models</span>
                <span className="lp-chip lp-on">open source ai</span>
                <span className="lp-chip">llm serving</span>
                <span className="lp-chip">rag &amp; vector db</span>
                <span className="lp-chip lp-on">ai hardware</span>
                <span className="lp-chip">alignment &amp; safety</span>
                <span className="lp-chip">llmops</span>
                <span className="lp-chip">multimodal</span>
                <span className="lp-chip">regulation &amp; policy</span>
                <span className="lp-chip lp-on">coding assistants</span>
                <span className="lp-chip">evals</span>
                <span className="lp-chip">startups &amp; funding</span>
                <span className="lp-chip">reasoning &amp; planning</span>
              </div>
              <div className="lp-excl">
                <span className="lp-lbl">excluded — dropped before analysis</span>
                <div className="lp-chips">
                  <span className="lp-chip lp-off">crypto</span>
                  <span className="lp-chip lp-off">nfts</span>
                  <span className="lp-chip lp-off">gaming</span>
                  <span className="lp-chip lp-off">sports</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ============ faq ============ */}
      <section className="lp-seg" id="faq">
        <div className="lp-wrap">
          <div className="lp-seg-head lp-prose">
            <span className="lp-eyebrow">questions</span>
            <h2>The short answers.</h2>
          </div>
          <div className="lp-faq">
            <div className="lp-q">
              <h4>Is it actually free?</h4>
              <p>
                Yes, while it&rsquo;s in preview — no card, no trial timer. If
                that changes you&rsquo;ll get plenty of notice.
              </p>
            </div>
            <div className="lp-q">
              <h4>How is this different from an AI newsletter?</h4>
              <p>
                Those are one editor&rsquo;s picks for everyone. This is a
                pipeline that ranks the day against <em>your</em> topics, cites
                precedent from your past briefings, and drops anything it
                can&rsquo;t ground against a source.
              </p>
            </div>
            <div className="lp-q">
              <h4>What does it read?</h4>
              <p>
                Tavily news, Hacker News, arXiv (cs.AI / cs.CL / cs.LG) and lab
                RSS — Hugging Face, VentureBeat, MIT Technology Review. One
                deduped set per run.
              </p>
            </div>
            <div className="lp-q">
              <h4>Can I change my topics later?</h4>
              <p>
                Any time, from Preferences. The next night&rsquo;s run uses the
                new set.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ============ CTA — schedule a run ============ */}
      <section className="lp-cta" id="schedule">
        <div className="lp-wrap">
          <span className="lp-eyebrow">get started</span>
          <h2>Schedule your first run.</h2>
          <p className="lp-sched">
            next run: <b>tonight, 02:00</b> · your briefing lands 8:00 AM
          </p>
          <SubscribeForm onTerm cta="Subscribe free" />
          <p className="lp-fineprint lp-on-term">
            already have an account?{" "}
            <SignInButton mode="modal">
              <button type="button" style={{ color: "var(--term-signal)" }}>
                sign in
              </button>
            </SignInButton>
          </p>
        </div>
      </section>

      <footer>
        <div className="lp-wrap lp-row">
          <span>© 2026 InsightGraph — one briefing, every morning.</span>
          <div className="lp-fl">
            <a href="https://github.com/Manav0411" target="_blank" rel="noreferrer">
              github
            </a>
            <SignInButton mode="modal">
              <button type="button">sign in</button>
            </SignInButton>
            <a href="#top">top</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
