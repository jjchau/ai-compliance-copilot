import Dashboard from "./pages/Dashboard";

function App() {
  return (
    // This wrapper handles the full-width constraints of your layout cleanly
    <div className="w-full min-h-screen bg-slate-950">
      <Dashboard />
    </div>
  );
}

export default App;