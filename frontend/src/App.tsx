import { Routes, Route } from "react-router-dom"

import Layout from "./components/Layout"

import LoginPage from "./pages/LoginPage"
import RegisterPage from "./pages/RegisterPage"
import Dashboard from "./pages/Dashboard"
import ViewJobDetails from "./pages/ViewJobDetails"

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/jobs/:id" element={<ViewJobDetails />} />
      </Routes>
    </Layout>
  )
}

export default App