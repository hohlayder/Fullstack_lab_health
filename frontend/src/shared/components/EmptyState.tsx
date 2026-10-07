import { Typography } from '@mui/material'
import CheckCircleOutlineRoundedIcon from '@mui/icons-material/CheckCircleOutlineRounded'

export function EmptyState({ title, description }: { title: string; description: string }) {
  return (
    <div className="empty-state">
      <CheckCircleOutlineRoundedIcon color="primary" sx={{ fontSize: 42 }} />
      <Typography variant="h3" sx={{ mt: 2 }}>
        {title}
      </Typography>
      <Typography color="text.secondary" sx={{ mt: 1 }}>
        {description}
      </Typography>
    </div>
  )
}
