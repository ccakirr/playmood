import React, { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import List from "./List";

const InputLayer = () => {
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const [searchParams, setSearchParams] = useSearchParams();

  // URL'den gelen hataları yakala (YouTube kotası vb.)
  useEffect(() => {
    const urlError = searchParams.get("error");
    if (urlError) {
      setError(decodeURIComponent(urlError));
      searchParams.delete("error");
      setSearchParams(searchParams);
    }
  }, [searchParams, setSearchParams]);

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
        // Backend'deki PlaylistRequest modeline uygun (limit ekledik)
        body: JSON.stringify({ 
          prompt: prompt,
          limit: 15 // Last.fm'den kaç şarkı istediğimizi buraya yazabiliriz
        }),
      });

      if (!response.ok) {
        let message = "Request failed.";
        try {
          const errorPayload = await response.json();
          message = errorPayload?.detail || message;
        } catch {
          message = await response.text();
        }
        throw new Error(message);
      }

      const data = await response.json();
      // 'data' içeriği artık: { playlist_id, mood_keywords, tracks: [{ artist_name, track_name }] }
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
              Describe a mood, artist, or moment. Our AI curates high-quality hits.
            </p>
          </div>

          {/* Input Section */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-base-content/80">
              Playlist Prompt:
            </label>
            <textarea
              placeholder="e.g. I want a romantic R&B playlist for a date night. Slow and sensual vibes."
              rows={4}
              className="mt-2 block w-full rounded-md border border-base-300 bg-base-100 px-3.5 py-2 text-base-content shadow-sm placeholder:text-base-content/40 focus:border-primary focus:ring-primary/30 outline-none transition-all"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && e.ctrlKey) handleSubmit();
              }}
            />
            <div className="flex justify-between items-center">
                <p className="text-xs text-base-content/50">
                    Tip: mention mood, genre, or setting.
                </p>
                <span className="text-xs opacity-40">Press Ctrl + Enter to generate</span>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-between pt-2">
            <button
              className={`btn btn-primary px-8 ${loading ? "btn-disabled" : ""}`}
              onClick={handleSubmit}
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="loading loading-spinner"></span>
                  Analyzing Mood...
                </>
              ) : (
                "Generate Hits"
              )}
            </button>
          </div>

          {/* Status Messages */}
          {error && (
            <div className="alert alert-error shadow-sm">
               <svg xmlns="http://www.w3.org/2000/svg" className="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
               <span>{error}</span>
            </div>
          )}

          {/* Result List */}
          {result && <List result={result} />}
        </div>
      </div>
    </div>
  );
};

export default InputLayer;