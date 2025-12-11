import { Link } from "react-router-dom";

export default function NavBar() {
  return (
    <nav>
      <Link to="/">Home</Link>
      <Link to="/games">Games</Link>
      <Link to="/players">Players</Link>
    </nav>
  );
}
