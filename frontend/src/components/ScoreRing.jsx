import { useEffect, useState } from "react";
import styles from "./ScoreRing.module.css";

const RADIUS = 34;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

function getBadge(score) {
  if (score >= 75) return { label: "Good",    cls: styles.badgeGood };
  if (score >= 50) return { label: "Fair",    cls: styles.badgeMid  };
  return              { label: "Needs work", cls: styles.badgeLow  };
}

function getStrokeColor(score) {
  if (score >= 75) return "var(--success)";
  if (score >= 50) return "#F0B800";
  return "var(--error)";
}

export default function ScoreRing({ score = 0, label }) {
  const [animated, setAnimated] = useState(0);

  useEffect(() => {
    const raf = requestAnimationFrame(() => setAnimated(score));
    return () => cancelAnimationFrame(raf);
  }, [score]);

  const offset = CIRCUMFERENCE * (1 - animated / 100);
  const badge  = getBadge(score);
  const color  = getStrokeColor(score);

  return (
    <div className={styles.card}>
      <div className={styles.ringWrapper}>
        <svg
          className={styles.svg}
          width="88"
          height="88"
          viewBox="0 0 88 88"
          aria-label={`${label}: ${score} out of 100`}
        >
          <circle
            className={styles.trackCircle}
            cx="44"
            cy="44"
            r={RADIUS}
          />
          <circle
            className={styles.progressCircle}
            cx="44"
            cy="44"
            r={RADIUS}
            stroke={color}
            strokeDasharray={CIRCUMFERENCE}
            strokeDashoffset={offset}
          />
        </svg>
        <div className={styles.scoreLabel}>
          <span className={styles.scoreValue}>{score}</span>
          <span className={styles.scoreMax}>/100</span>
        </div>
      </div>
      <span className={styles.cardLabel}>{label}</span>
      <span className={`${styles.cardBadge} ${badge.cls}`}>{badge.label}</span>
    </div>
  );
}
