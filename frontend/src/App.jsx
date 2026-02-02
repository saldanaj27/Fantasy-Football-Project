import { BrowserRouter, Routes, Route } from "react-router-dom"
import Home from "./pages/Home/Home"
import GameInfo from "./pages/GameInfo/GameInfo"
import Players from "./pages/Players/Players"
import Rankings from "./pages/Rankings/Rankings"
import StartSit from "./pages/StartSit/StartSit"

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/game/:gameId" element={<GameInfo />} />
        <Route path="/players" element={<Players />} />
        <Route path="/rankings" element={<Rankings />} />
        <Route path="/start-sit" element={<StartSit />} />
      </Routes>
    </BrowserRouter>
  )
}

