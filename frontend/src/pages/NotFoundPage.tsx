import { Button, Typography } from '@mui/material'
import ArrowBackRoundedIcon from '@mui/icons-material/ArrowBackRounded'
import { Link } from 'react-router'

export function NotFoundPage() {
  return (
    <section className="not-found">
      <span className="error-number">404</span>
      <Typography variant="h1">Страница не найдена</Typography>
      <Typography color="text.secondary" sx={{ mt: 1.5, mb: 3 }}>
        Проверьте адрес или вернитесь к расписанию семьи.
      </Typography>
      <Button
        component={Link}
        to="/schedule"
        variant="contained"
        startIcon={<ArrowBackRoundedIcon />}
      >
        Вернуться к расписанию
      </Button>
    </section>
  )
}
