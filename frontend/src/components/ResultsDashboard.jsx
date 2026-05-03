export default function ResultsDashboard({ result }) {
  if (!result) return null;

  if (result.status === "error") {
    return <p style={{ color: "red" }}>Error: {result.message}</p>;
  }

  return (
    <div style={{ marginTop: "2rem" }}>
      <h2>Results</h2>

      <h3>Scores</h3>
      <p>Overall: {result.scores.overall_score}</p>
      <p>Speaking: {result.scores.speaking_score}</p>
      <p>Eye Contact: {result.scores.gaze_score}</p>

      <h3>Feedback</h3>
      <ul>
        {result.feedback.map((f, i) => (
          <li key={i}>{f}</li>
        ))}
      </ul>

      <h3>Transcript</h3>
      <p>{result.transcript}</p>
    </div>
  );
}