import { Routes, Route } from "react-router-dom"

import Layout from "./components/Layout"

import LoginPage from "./pages/LoginPage"
import RegisterPage from "./pages/RegisterPage"
import Dashboard from "./pages/Dashboard"
import ViewJobDetails from "./pages/ViewJobDetails"
import EditJob from "./pages/EditJob"
import ViewJobRun from "./pages/ViewJobRun"

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/jobs/:id" element={<ViewJobDetails />} />
        <Route path="/jobs/:id/edit" element={<EditJob />} />
        <Route path="/jobs/new" element={<EditJob />} />
        <Route path="/jobs/runs/:id" element={<ViewJobRun />} />
      </Routes>
    </Layout>
  )
}

export default App