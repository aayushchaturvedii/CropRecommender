
import React, { useState } from "react";
import ReactDOM from "react-dom/client";

function App() {
  const [coordinates, setCoordinates] = useState("");
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchRecommendations = async () => {
    setLoading(true);
    const [lat, lng] = coordinates.split(",").map((val) => parseFloat(val.trim()));
    try {
      const response = await fetch("http://localhost:8000/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ lat, lng }),
      });
      const data = await response.json();
      setRecommendations(data.recommendations);
    } catch (error) {
      console.error("Error:", error);
      alert("Error fetching recommendations");
    }
    setLoading(false);
  };

  return (
    <div style={{ padding: 20, fontFamily: "Arial" }}>
      <h1>🌾 Crop Recommender</h1>
      <input
        type="text"
        placeholder="Enter coordinates (lat,lng)"
        value={coordinates}
        onChange={(e) => setCoordinates(e.target.value)}
        style={{ padding: 8, marginRight: 10 }}
      />
      <button onClick={fetchRecommendations} disabled={loading}>
        {loading ? "Analyzing..." : "Analyze"}
      </button>

      <ul>
        {recommendations.map((rec, i) => (
          <li key={i}>
            <strong>{rec.crop}</strong> — Profit: ₹{rec.profit}, Scalability: {rec.scalability}
          </li>
        ))}
      </ul>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
