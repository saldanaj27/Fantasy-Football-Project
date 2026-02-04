import { BrowserRouter, Routes, Route } from "react-router-dom"
import NavBar from "./components/NavBar/NavBar"
import Landing from "./pages/Landing/Landing"
import Scores from "./pages/Scores/Scores"
import GameInfo from "./pages/GameInfo/GameInfo"
import Players from "./pages/Players/Players"
import Rankings from "./pages/Rankings/Rankings"
import StartSit from "./pages/StartSit/StartSit"

export default function App() {
  return (
    <BrowserRouter>
      <NavBar />
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/scores" element={<Scores />} />
        <Route path="/game/:gameId" element={<GameInfo />} />
        <Route path="/players" element={<Players />} />
        <Route path="/rankings" element={<Rankings />} />
        <Route path="/start-sit" element={<StartSit />} />
      </Routes>
    </BrowserRouter>
  )
}

