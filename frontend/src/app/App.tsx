import { CssBaseline, ThemeProvider } from '@mui/material'
import { lazy } from 'react'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router'
import { DemoProvider } from '../features/demo/DemoProvider'
import { AppLayout } from './AppLayout'
import { theme } from './theme'
import './styles.css'

const SchedulePage = lazy(() =>
  import('../pages/SchedulePage').then((module) => ({ default: module.SchedulePage })),
)
const FamilyPage = lazy(() =>
  import('../pages/FamilyPage').then((module) => ({ default: module.FamilyPage })),
)
const MedicationsPage = lazy(() =>
  import('../pages/MedicationsPage').then((module) => ({ default: module.MedicationsPage })),
)
const RemindersPage = lazy(() =>
  import('../pages/RemindersPage').then((module) => ({ default: module.RemindersPage })),
)
const DoctorPage = lazy(() =>
  import('../pages/DoctorPage').then((module) => ({ default: module.DoctorPage })),
)
const NotFoundPage = lazy(() =>
  import('../pages/NotFoundPage').then((module) => ({ default: module.NotFoundPage })),
)

export function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <DemoProvider>
          <Routes>
            <Route element={<AppLayout />}>
              <Route index element={<Navigate to="/schedule" replace />} />
              <Route path="schedule" element={<SchedulePage />} />
              <Route path="family" element={<FamilyPage />} />
              <Route path="medications" element={<MedicationsPage />} />
              <Route path="reminders" element={<RemindersPage />} />
              <Route path="doctor" element={<DoctorPage />} />
              <Route path="*" element={<NotFoundPage />} />
            </Route>
          </Routes>
        </DemoProvider>
      </BrowserRouter>
    </ThemeProvider>
  )
}
