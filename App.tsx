import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Layout } from "./components/Layout";

// Import your page components
// import ExecutiveOverview from "./pages/ExecutiveOverview";
// import DrugInvestigation from "./pages/DrugInvestigation";
// import SafetySignals from "./pages/SafetySignals";
// import SignalInvestigation from "./pages/SignalInvestigation";
// import AIHelper from "./pages/AIHelper";

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Layout>
          <Routes>
            {/* <Route path="/" element={<ExecutiveOverview />} /> */}
            {/* <Route path="/drugs" element={<DrugInvestigation />} /> */}
            {/* <Route path="/signals" element={<SafetySignals />} /> */}
            {/* <Route path="/signals/:drug/:reaction" element={<SignalInvestigation />} /> */}
            {/* <Route path="/ai" element={<AIHelper />} /> */}
          </Routes>
        </Layout>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;