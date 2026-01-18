import { BrowserRouter, Routes, Route } from "react-router-dom"
import Home from "./pages/Home/Home"
import GameInfo from "./pages/GameInfo/GameInfo"

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/game/:gameId" element={<GameInfo />} />
      </Routes>
    </BrowserRouter>
  )
}

