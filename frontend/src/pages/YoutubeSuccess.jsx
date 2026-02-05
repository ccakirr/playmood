import { useEffect } from "react";
import { useSearchParams } from "react-router-dom";

const YoutubeSuccess = () => {
  const [searchParams] = useSearchParams();
  const playlistId = searchParams.get("playlist");

  useEffect(() => {
    if (playlistId) {
      // Redirect to YouTube after a brief moment
      const youtubeUrl = `https://www.youtube.com/playlist?list=${playlistId}`;
      setTimeout(() => {
        window.location.href = youtubeUrl;
      }, 1500);
    }
  }, [playlistId]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-base-200 to-base-300">
      <div className="text-center space-y-6">
        <div className="text-6xl">🎉</div>
        <h1 className="text-3xl font-bold">Playlist Created!</h1>
        <p className="text-base-content/70">Redirecting to YouTube...</p>
        <span className="loading loading-spinner loading-lg"></span>
      </div>
    </div>
  );
};

export default YoutubeSuccess;
