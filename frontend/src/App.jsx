import { useState } from "react";
import VideoUpload from "./components/VideoUpload";
import ResultsDashboard from "./components/ResultsDashboard";
import styles from "./App.module.css";

function App() {
  const [result, setResult] = useState(null);

  return (
    <div className={styles.app}>
      {/* Header */}
      <header className={styles.header}>
        <span className={styles.logo}>
          <span className={styles.logoIcon}>
            <MicIcon />
          </span>
          <span className={styles.logoText}>SpeakCoach AI</span>
        </span>
        <span className={styles.headerBadge}>Beta</span>
      </header>

      {/* Main */}
      <main className={styles.main}>
        {/* Hero */}
        <section className={styles.hero}>
          <div className={styles.heroEyebrow}>
            <span className={styles.heroPulse} />
            AI-Powered Feedback
          </div>
          <h1 className={styles.heroTitle}>Speak with confidence.</h1>
          <p className={styles.heroSubtitle}>
            Upload your video and get instant AI feedback on your speaking pace,
            filler words, and eye contact — like having a real coach.
          </p>
        </section>

        <VideoUpload onResult={setResult} />

        {result && <div className={styles.divider} />}

        <ResultsDashboard result={result} />
      </main>

      {/* Footer */}
      <footer className={styles.footer}>
        SpeakCoach AI &mdash; Powered by faster-whisper &amp; MediaPipe
      </footer>
    </div>
  );
}

function MicIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <rect x="9" y="2" width="6" height="11" rx="3" />
      <path d="M19 10a7 7 0 01-14 0" />
      <line x1="12" y1="19" x2="12" y2="22" />
      <line x1="8" y1="22" x2="16" y2="22" />
    </svg>
  );
}

export default App;
