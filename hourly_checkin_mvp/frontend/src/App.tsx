import { BrowserRouter, Route, Routes } from 'react-router-dom'
import CheckinPage from './CheckinPage'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<CheckinPage />} />
        <Route path="/checkin" element={<CheckinPage />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
