import { Routes, Route } from "react-router-dom"

import Layout from "./components/Layout"

import LoginPage from "./pages/LoginPage"
import RegisterPage from "./pages/RegisterPage"
import ViewAccountPage from "./pages/ViewAccountPage"
import DashboardPage from "./pages/DashboardPage"
import ViewJobDetails from "./pages/ViewJobDetailsPage"
import EditJobPage from "./pages/EditJobPage"
import ViewJobRunPage from "./pages/ViewJobRunPage"

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/my-account" element={<ViewAccountPage />} />
        <Route path="/jobs/:id" element={<ViewJobDetails />} />
        <Route path="/jobs/:id/edit" element={<EditJobPage />} />
        <Route path="/jobs/new" element={<EditJobPage />} />
        <Route path="/jobs/runs/:id" element={<ViewJobRunPage />} />
      </Routes>
    </Layout>
  )
}

export default App