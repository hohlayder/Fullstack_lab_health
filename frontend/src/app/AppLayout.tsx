import { Suspense, useEffect, useState } from 'react'
import { Avatar, Badge, Button, Drawer, IconButton, Tooltip, Typography } from '@mui/material'
import CalendarMonthRoundedIcon from '@mui/icons-material/CalendarMonthRounded'
import PeopleOutlineRoundedIcon from '@mui/icons-material/PeopleOutlineRounded'
import MedicationOutlinedIcon from '@mui/icons-material/MedicationOutlined'
import NotificationsNoneRoundedIcon from '@mui/icons-material/NotificationsNoneRounded'
import DescriptionOutlinedIcon from '@mui/icons-material/DescriptionOutlined'
import FavoriteBorderRoundedIcon from '@mui/icons-material/FavoriteBorderRounded'
import MenuRoundedIcon from '@mui/icons-material/MenuRounded'
import ArrowOutwardRoundedIcon from '@mui/icons-material/ArrowOutwardRounded'
import { Link, NavLink, Outlet, useLocation } from 'react-router'
import { useDemo } from '../features/demo/demoContext'

const navigation = [
  { to: '/schedule', label: 'Расписание', icon: CalendarMonthRoundedIcon },
  { to: '/family', label: 'Моя семья', icon: PeopleOutlineRoundedIcon },
  { to: '/medications', label: 'Лекарства', icon: MedicationOutlinedIcon },
  { to: '/reminders', label: 'Напоминания', icon: NotificationsNoneRoundedIcon },
  { to: '/doctor', label: 'Список для врача', icon: DescriptionOutlinedIcon },
]

export function AppLayout() {
  const [menuOpen, setMenuOpen] = useState(false)
  const { intakes } = useDemo()
  const { pathname } = useLocation()
  const currentPage =
    navigation.find((item) => item.to === pathname)?.label ?? 'Страница не найдена'
  const remaining = intakes.filter((intake) => !intake.taken).length

  useEffect(() => {
    document.title = `${currentPage} · Близкие`
  }, [currentPage])

  const sidebar = (
    <div className="sidebar-content">
      <Link
        to="/schedule"
        className="brand"
        onClick={() => setMenuOpen(false)}
        aria-label="Близкие — на расписание"
      >
        <span className="brand-mark">
          <FavoriteBorderRoundedIcon />
        </span>
        <span>
          близкие<span className="brand-caption">Забота по расписанию</span>
        </span>
      </Link>
      <div className="workspace-label">СЕМЕЙНОЕ ПРОСТРАНСТВО</div>
      <nav aria-label="Основная навигация" className="navigation">
        {navigation.map(({ to, label, icon: Icon }) => (
          <NavLink
            to={to}
            key={to}
            onClick={() => setMenuOpen(false)}
            className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
          >
            <Icon sx={{ fontSize: 21 }} />
            <span>{label}</span>
            {to === '/reminders' && (
              <span className="nav-count" aria-hidden="true">
                {remaining}
              </span>
            )}
          </NavLink>
        ))}
      </nav>
      <div className="sidebar-note">
        <span className="note-icon">
          <DescriptionOutlinedIcon />
        </span>
        <Typography variant="h3" sx={{ mt: 1.5 }}>
          Собираетесь к врачу?
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1, mb: 1.5 }}>
          Возьмите с собой список лекарств и расписание приёмов.
        </Typography>
        <Button
          component={Link}
          to="/doctor"
          onClick={() => setMenuOpen(false)}
          endIcon={<ArrowOutwardRoundedIcon />}
          size="small"
          sx={{ px: 0 }}
        >
          Подготовить список
        </Button>
      </div>
      <div className="sidebar-footer">
        <span className="status-dot" />
        Демонстрационная версия
      </div>
    </div>
  )

  return (
    <div className="app-shell">
      <a href="#main-content" className="skip-link">
        Перейти к содержимому
      </a>
      <aside className="app-sidebar">{sidebar}</aside>
      <Drawer
        open={menuOpen}
        onClose={() => setMenuOpen(false)}
        sx={{ display: { md: 'none' } }}
        slotProps={{ paper: { sx: { width: 264 } } }}
      >
        {sidebar}
      </Drawer>
      <div className="app-body">
        <div className="app-topbar">
          <div className="topbar-left">
            <IconButton
              aria-label="Открыть меню"
              onClick={() => setMenuOpen(true)}
              sx={{ display: { md: 'none' }, ml: -1 }}
            >
              <MenuRoundedIcon />
            </IconButton>
            <span className="breadcrumb">
              Моя семья <span>/</span> <strong>{currentPage}</strong>
            </span>
          </div>
          <div className="topbar-right">
            <span className="demo-label">Демо · 7 октября 2026</span>
            <Tooltip title="Открыть напоминания">
              <IconButton component={Link} to="/reminders" aria-label="Открыть напоминания">
                <Badge badgeContent={remaining} color="primary">
                  <NotificationsNoneRoundedIcon />
                </Badge>
              </IconButton>
            </Tooltip>
            <Avatar
              sx={{
                width: 34,
                height: 34,
                bgcolor: '#dff3eb',
                color: '#176b5b',
                fontSize: 12,
                fontWeight: 800,
              }}
            >
              АС
            </Avatar>
          </div>
        </div>
        <main id="main-content" className="app-main" tabIndex={-1} key={pathname}>
          <Suspense fallback={<Typography role="status">Загружаем экран…</Typography>}>
            <Outlet />
          </Suspense>
        </main>
        <footer className="app-footer">
          Близкие · Учебный проект<span>Все данные и назначения вымышлены</span>
        </footer>
      </div>
    </div>
  )
}
