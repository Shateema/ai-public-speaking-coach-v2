import { useState } from "react";
import VideoUpload from "./components/VideoUpload";
import ResultsDashboard from "./components/ResultsDashboard";

function App() {
  const [result, setResult] = useState(null);

  return (
    <div style={{ padding: "2rem", textAlign: "center" }}>
      <h1>AI Speaking Coach</h1>

      <VideoUpload onResult={setResult} />
      <ResultsDashboard result={result} />
    </div>
  );
}

export default App;