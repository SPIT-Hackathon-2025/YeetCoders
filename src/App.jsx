import { BrowserRouter as Router, Route, Routes } from "react-router-dom"
import { ClerkProvider } from "@clerk/clerk-react"
import Navbar from "./components/Navbar"
import LandingPage from "./components/LandingPage"
import "./index.css";
import WorkflowBuilder from "./components/WorkflowBuilder";
import Templates from "./components/Templates";
import Marketplace from "./components/Marketplace";
import Features from "./components/Features";

const clerkPubKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY

function App() {
  return (
    <ClerkProvider publishableKey={clerkPubKey}>
      <Router>
        <div className="min-h-screen bg-gray-100">
          <Navbar />
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/workflow/:workflowId" element={<WorkflowBuilder />} />
            <Route path="/templates" element={<Templates />} />
            <Route path="/workflowbuilder" element={<WorkflowBuilder />} />
            <Route path="/marketplace" element={<Marketplace />} />
            <Route path="/features" element={<Features />} />
          </Routes>
        </div>
      </Router>
    </ClerkProvider>
  )
}

export default App

