import {
  Brain,
  ShieldCheck
} from "lucide-react";


function Navbar() {
  return (
    <nav className="navbar">

      <div className="brand">

        <div className="brand-icon">
          <Brain size={22} />
        </div>

        <div>
          <h1>Buy or Wait?</h1>
          <span>AI financial decision assistant</span>
        </div>

      </div>


      <div className="nav-status">

        <ShieldCheck size={18} />

        <span>
          Safety-first analysis
        </span>

      </div>

    </nav>
  );
}


export default Navbar;