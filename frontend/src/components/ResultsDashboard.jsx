import { useState } from "react";
import ScoreRing from "./ScoreRing";
import styles from "./ResultsDashboard.module.css";

/**
 * Parses ai_feedback.details (a plain string) into an array of lines
 * so the existing bullet-list UI can render each point separately.
 * Handles:  "• line\n• line", "- line\n- line", "1. line\n2. line", plain text.
 */
function parseFeedback(text) {
  if (!text || typeof text !== "string") return [];
  const lines = text
    .split("\n")
    .map((l) => l.replace(/^[\s•\-*\d.]+/, "").trim())
    .filter(Boolean);
  return lines.length > 0 ? lines : [text.trim()];
}

/** Interpretation helpers — turn raw numbers into plain-English verdicts */
function getWPMMessage(wpm) {
  if (wpm === 0)    return "No speech detected";
  if (wpm < 110)   return "Too slow — add more energy and pace";
  if (wpm <= 160)  return "Good pace — right in the sweet spot";
  return "Too fast — slow down for clarity";
}

function getFillerMessage(count) {
  if (count === 0)  return "Excellent — zero filler words";
  if (count <= 3)   return "Minimal fillers — minor polish needed";
  if (count <= 7)   return "Noticeable fillers — practice deliberate pausing";
  return "Too many fillers — needs focused practice";
}

function getEyeContactMessage(pct) {
  if (pct >= 70)  return "Strong eye contact — very engaging";
  if (pct >= 40)  return "Decent — aim to look at the camera more";
  return "Low eye contact — connect more with your audience";
}

export default function ResultsDashboard({ result }) {
  const [expanded, setExpanded] = useState(false);

  if (!result) return null;

  if (result.status === "error") {
    return (
      <div className={styles.error}>
        <ErrorIcon />
        {result.message || "Something went wrong. Please try again."}
      </div>
    );
  }

  // Log full API response for debugging
  console.log("[SpeakCoach] API response:", result);

  // ── Correct nested field access ──────────────────────────────
  const { scores, metrics = {}, transcript, ai_feedback = {} } = result;

  const overall  = Math.round(scores?.overall_score  ?? 0);
  const speaking = Math.round(scores?.speaking_score ?? 0);
  const gaze     = Math.round(scores?.gaze_score     ?? 0);

  // metrics lives under result.metrics (not top-level)
  const wpmValue = metrics.wpm        ?? 0;
  const fillers  = metrics.filler_count ?? 0;
  // camera_facing_percentage is already 0-100 (not a 0-1 ratio)
  const gazePct  = metrics.camera_facing_percentage ?? gaze;

  // ai_feedback.details is a string — split into bullet lines for the list UI
  const feedbackLines = parseFeedback(ai_feedback.details);

  // WPM bar: ideal 120-160, cap at 200
  const wpmBarPct   = Math.min((wpmValue / 200) * 100, 100);
  const wpmIdeal    = wpmValue >= 120 && wpmValue <= 160;
  const wpmBarColor = wpmIdeal ? "var(--success)" : wpmValue < 100 || wpmValue > 180 ? "var(--error)" : "#F0B800";

  // Filler bar: 0 is perfect, 10+ is red
  const fillerBarPct = Math.max(0, 100 - (fillers / 10) * 100);
  const fillerColor  = fillers === 0 ? "var(--success)" : fillers <= 3 ? "#F0B800" : "var(--error)";

  return (
    <div className={styles.dashboard}>

      {/* ── Row 1: Scores ── */}
      <div className={styles.scoresRow}>
        <ScoreRing score={overall}  label="Overall Score"  />
        <ScoreRing score={speaking} label="Speaking"       />
        <ScoreRing score={gaze}     label="Eye Contact"    />
      </div>

      {/* ── Row 2: Feedback + Metrics ── */}
      <div className={styles.secondRow}>

        {/* Feedback */}
        <div className={styles.panel}>
          <div className={styles.sectionHeader}>
            <span className={styles.sectionIcon}><CoachIcon /></span>
            <span className={styles.sectionTitle}>Coach Feedback</span>
          </div>

          {/* AI summary sentence */}
          {ai_feedback.summary && (
            <p className={styles.feedbackSummary}>{ai_feedback.summary}</p>
          )}

          {feedbackLines.length > 0 ? (
            <ul className={styles.feedbackList}>
              {feedbackLines.map((f, i) => (
                <li key={i} className={styles.feedbackItem}>
                  <span className={styles.feedbackBullet}>
                    <span className={styles.feedbackBulletNum}>{i + 1}</span>
                  </span>
                  <p className={styles.feedbackText}>{f}</p>
                </li>
              ))}
            </ul>
          ) : (
            <p className={styles.feedbackText} style={{ color: "var(--text-muted)", padding: "0.5rem 0" }}>
              No detailed feedback available.
            </p>
          )}
        </div>

        {/* Metrics */}
        <div className={styles.panel}>
          <div className={styles.sectionHeader}>
            <span className={styles.sectionIcon}><MetricsIcon /></span>
            <span className={styles.sectionTitle}>Speech Metrics</span>
          </div>
          <div className={styles.metricsList}>

            {/* WPM */}
            <div className={styles.metric}>
              <div className={styles.metricTop}>
                <span className={styles.metricLabel}>Words per minute</span>
                <span className={styles.metricValue}>
                  {wpmValue}
                  <span className={styles.metricUnit}>WPM</span>
                </span>
              </div>
              <div className={styles.metricBar}>
                <div className={styles.metricFill} style={{ width: `${wpmBarPct}%`, background: wpmBarColor }} />
              </div>
              <span className={styles.metricNote}>{getWPMMessage(wpmValue)}</span>
            </div>

            {/* Filler words */}
            <div className={styles.metric}>
              <div className={styles.metricTop}>
                <span className={styles.metricLabel}>Filler words</span>
                <span className={styles.metricValue}>
                  {fillers}
                  <span className={styles.metricUnit}>used</span>
                </span>
              </div>
              <div className={styles.metricBar}>
                <div className={styles.metricFill} style={{ width: `${fillerBarPct}%`, background: fillerColor }} />
              </div>
              <span className={styles.metricNote}>{getFillerMessage(fillers)}</span>
            </div>

            {/* Gaze */}
            <div className={styles.metric}>
              <div className={styles.metricTop}>
                <span className={styles.metricLabel}>Eye contact</span>
                <span className={styles.metricValue}>
                  {gazePct}
                  <span className={styles.metricUnit}>%</span>
                </span>
              </div>
              <div className={styles.metricBar}>
                <div className={styles.metricFill} style={{ width: `${gazePct}%`, background: gazePct >= 70 ? "var(--success)" : gazePct >= 40 ? "#F0B800" : "var(--error)" }} />
              </div>
              <span className={styles.metricNote}>{getEyeContactMessage(gazePct)}</span>
            </div>

          </div>
        </div>
      </div>

      {/* ── Row 3: Transcript ── */}
      {transcript && (
        <div className={styles.transcriptPanel}>
          <div className={styles.transcriptHeader}>
            <div className={styles.sectionHeader} style={{ marginBottom: 0 }}>
              <span className={styles.sectionIcon}><TranscriptIcon /></span>
              <span className={styles.sectionTitle}>Transcript</span>
            </div>
            <button
              className={styles.transcriptToggle}
              onClick={() => setExpanded(v => !v)}
              aria-expanded={expanded}
            >
              {expanded ? "Collapse" : "Expand"}
              <ChevronIcon expanded={expanded} />
            </button>
          </div>
          <div className={`${styles.transcriptBody} ${expanded ? styles.expanded : ""}`}>
            {transcript}
          </div>
        </div>
      )}
    </div>
  );
}

/* ── Icons ── */
function CoachIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" />
    </svg>
  );
}

function MetricsIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
    </svg>
  );
}

function TranscriptIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
      <polyline points="14 2 14 8 20 8" />
      <line x1="16" y1="13" x2="8" y2="13" />
      <line x1="16" y1="17" x2="8" y2="17" />
      <polyline points="10 9 9 9 8 9" />
    </svg>
  );
}

function ErrorIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10" />
      <line x1="12" y1="8" x2="12" y2="12" />
      <line x1="12" y1="16" x2="12.01" y2="16" />
    </svg>
  );
}

function ChevronIcon({ expanded }) {
  return (
    <svg
      width="12" height="12"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.5"
      strokeLinecap="round"
      style={{ transform: expanded ? "rotate(180deg)" : "rotate(0deg)", transition: "transform 0.2s ease" }}
    >
      <polyline points="6 9 12 15 18 9" />
    </svg>
  );
}
