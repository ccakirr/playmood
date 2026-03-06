import { useEffect, useState } from "react";
import { useSearchParams, Link } from "react-router-dom";

const YoutubeSuccess = () => {
  const [searchParams] = useSearchParams();
  const playlistId = searchParams.get("playlist");
  const youtubeUrl = playlistId
    ? `https://www.youtube.com/playlist?list=${playlistId}`
    : null;

  const [countdown, setCountdown] = useState(5);
  const [redirected, setRedirected] = useState(false);

  useEffect(() => {
    if (!youtubeUrl) return;

    const interval = setInterval(() => {
      setCountdown((c) => {
        if (c <= 1) {
          clearInterval(interval);
          setRedirected(true);
          window.open(youtubeUrl, "_blank");
          return 0;
        }
        return c - 1;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [youtubeUrl]);

  return (
    <div className="flex min-h-[calc(100vh-8rem)] items-center justify-center bg-gradient-to-br from-base-200 to-base-300 px-6 py-12">
      <div className="w-full max-w-md">
        <div className="rounded-2xl border border-base-200 bg-base-100 shadow-2xl p-10 text-center space-y-6">
          {youtubeUrl ? (
            <>
              {/* Icon */}
              <div className="flex items-center justify-center w-20 h-20 rounded-full bg-success/15 text-success mx-auto text-4xl">
                ✓
              </div>

              <div className="space-y-2">
                <h1 className="mt-5 text-2xl font-bold">Playlist Created!</h1>
                <p className="text-base-content/60 text-sm">
                  Your YouTube playlist is ready. Opening in a new tab
                  {!redirected && countdown > 0 && (
                    <>
                      {" "}
                      in{" "}
                      <span className="font-semibold text-primary">
                        {countdown}
                      </span>
                      s…
                    </>
                  )}
                  {redirected && <>.</>}
                </p>
              </div>

              {/* Progress ring */}
              {!redirected && (
                <div className="flex justify-center">
                  <span className="loading loading-ring loading-lg text-primary"></span>
                </div>
              )}

              {/* CTA buttons */}
              <div className="flex flex-col gap-3">
                <a
                  href={youtubeUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn btn-error w-full gap-2"
                >
                  {/* YouTube icon */}
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="currentColor"
                    className="w-5 h-5"
                  >
                    <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z" />
                  </svg>
                  Open on YouTube
                </a>

                <Link to="/" className="btn btn-ghost w-full">
                  ← Generate another playlist
                </Link>
              </div>
            </>
          ) : (
            <>
              {/* Error state */}
              <div className="flex items-center justify-center w-20 h-20 rounded-full bg-error/15 text-error mx-auto text-4xl">
                !
              </div>

              <div className="space-y-2">
                <h1 className="text-2xl font-bold">Something went wrong</h1>
                <p className="text-base-content/60 text-sm">
                  The playlist could not be created on YouTube. This is usually
                  a temporary issue — please try again.
                </p>
              </div>

              <Link to="/" className="btn btn-primary w-full">
                ← Back to Home
              </Link>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default YoutubeSuccess;
