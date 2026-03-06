import { Routes, Route } from "react-router-dom";
import InputLayer from "./components/InputLayer";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import YoutubeSuccess from "./pages/YoutubeSuccess";
import MyPlaylists from "./pages/MyPlaylists";

function App() {
  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/" element={<InputLayer />} />
        <Route path="/youtube-success" element={<YoutubeSuccess />} />
        <Route path="/my-playlists" element={<MyPlaylists />} />
      </Routes>
      <Footer />
    </>
  );
}

export default App;
