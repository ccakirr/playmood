import { Routes, Route } from "react-router-dom";
import InputLayer from "./components/InputLayer";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import YoutubeSuccess from "./pages/YoutubeSuccess";

function App() {
  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/" element={<InputLayer />} />
        <Route path="/youtube-success" element={<YoutubeSuccess />} />
      </Routes>
      <Footer />
    </>
  );
}

export default App;
