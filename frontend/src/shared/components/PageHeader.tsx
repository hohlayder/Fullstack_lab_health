import { Typography } from '@mui/material'
import type { ReactNode } from 'react'

export function PageHeader({
  eyebrow,
  title,
  description,
  action,
}: {
  eyebrow: string
  title: string
  description: string
  action?: ReactNode
}) {
  return (
    <header className="page-header screen-only">
      <div>
        <Typography className="eyebrow" component="p">
          {eyebrow}
        </Typography>
        <Typography variant="h1">{title}</Typography>
        <Typography color="text.secondary" sx={{ mt: 1 }}>
          {description}
        </Typography>
      </div>
      {action}
    </header>
  )
}
