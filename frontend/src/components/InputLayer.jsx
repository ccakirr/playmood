import React, { useState } from "react";
import List from "./List";

const InputLayer = () => {
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const handleSubmit = async () => {
    if (!prompt.trim()) {
      setError("Describe the playlist vibe you want.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const baseUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";

      const response = await fetch(`${baseUrl}/playlist/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }),
      });

      if (!response.ok) {
        const contentType = response.headers.get("content-type") || "";
        let message = "Request failed.";

        if (contentType.includes("application/json")) {
          const errorPayload = await response.json();
          message = errorPayload?.detail || message;
        } else {
          const text = await response.text();
          message = text || message;
        }

        throw new Error(message);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen w-full items-center justify-center bg-gradient-to-br from-base-200 to-base-300 px-6 py-12">
      <div className="w-full max-w-4xl rounded-2xl border border-base-200 bg-base-100 shadow-2xl">
        <div className="p-8 md:p-10 space-y-8">
          {/* Header */}
          <div className="space-y-3">
            <h1 className="text-4xl font-bold tracking-tight">
              Play<span className="text-primary">Mood</span>
            </h1>
            <p className="max-w-2xl text-base text-base-content/70">
              Describe a mood, artist, or moment. Our AI curates a playlist that
              matches the vibe.
            </p>
          </div>

          {/* Input */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-base-content/80">
              Playlist Prompt:
            </label>
            <textarea
              id="message"
              name="message"
              placeholder="e.g. I want dark, sexy late-night playlist like The Weeknd. Slow tempo, modern R&B."
              rows={4}
              className="mt-2 block w-full rounded-md border border-base-300 bg-base-100 px-3.5 py-2 text-base-content shadow-sm ring-1 ring-transparent placeholder:text-base-content/40 focus:border-primary focus:ring-primary/30"
              value={prompt}
              onChange={(event) => setPrompt(event.target.value)}
            />
            <p className="text-xs text-base-content/50">
              Tip: mention mood, tempo, artists, or setting.
            </p>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-between">
            <button
              className={`btn btn-primary btn-lg ${
                loading ? "btn-disabled" : ""
              }`}
              onClick={handleSubmit}
            >
              {loading ? (
                <>
                  <span className="loading loading-spinner"></span>
                  Generating
                </>
              ) : (
                "Generate playlist"
              )}
            </button>
          </div>

          {/* Error */}
          {error && (
            <div className="rounded-lg border border-error/30 bg-error/10 px-4 py-3 text-error">
              {error}
            </div>
          )}

          {/* Result */}
          <List result={result} />
        </div>
      </div>
    </div>
  );
};

export default InputLayer;
