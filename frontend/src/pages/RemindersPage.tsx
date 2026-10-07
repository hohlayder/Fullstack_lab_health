import { useState } from 'react'
import { Alert, Button, FormControlLabel, Paper, Switch, Typography } from '@mui/material'
import NotificationsNoneRoundedIcon from '@mui/icons-material/NotificationsNoneRounded'
import ArrowForwardRoundedIcon from '@mui/icons-material/ArrowForwardRounded'
import { Link } from 'react-router'
import { getMedication, getMember } from '../entities/demoData'
import { useDemo } from '../features/demo/demoContext'
import { EmptyState } from '../shared/components/EmptyState'
import { PageHeader } from '../shared/components/PageHeader'
import { PersonAvatar } from '../shared/components/PersonAvatar'

export function RemindersPage() {
  const { intakes } = useDemo()
  const [enabled, setEnabled] = useState(true)
  const [repeat, setRepeat] = useState(true)
  const upcoming = intakes.filter((intake) => !intake.taken)
  return (
    <>
      <PageHeader
        eyebrow="НЕ УПУСТИТЬ ГЛАВНОЕ"
        title="Напоминания"
        description="Ближайшие приёмы и настройки уведомлений."
        action={
          <Button
            component={Link}
            to="/schedule"
            variant="outlined"
            endIcon={<ArrowForwardRoundedIcon />}
          >
            К расписанию
          </Button>
        }
      />
      <div className="reminders-grid">
        <Paper component="section" className="panel" aria-label="Ближайшие напоминания">
          <div className="schedule-toolbar">
            <Typography variant="h2">Ближайшие приёмы</Typography>
            <span className="count-label">Осталось: {upcoming.length}</span>
          </div>
          {!enabled && (
            <Alert severity="info" sx={{ m: 2 }}>
              В макете напоминания приостановлены. Расписание остаётся доступным.
            </Alert>
          )}
          {upcoming.length === 0 ? (
            <EmptyState
              title="На сегодня всё принято"
              description="Все приёмы отмечены в расписании."
            />
          ) : (
            upcoming.map((intake) => {
              const medicine = getMedication(intake.medicationId)
              const member = getMember(medicine.memberId)
              return (
                <div className="reminder-row" key={intake.id}>
                  <span className="reminder-icon">
                    <NotificationsNoneRoundedIcon />
                  </span>
                  <div className="reminder-copy">
                    <Typography variant="h3">{medicine.name}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      {medicine.dose} · {medicine.instructions}
                    </Typography>
                    <div className="reminder-person">
                      <PersonAvatar member={member} size={22} />
                      <span>{member.firstName}</span>
                    </div>
                  </div>
                  <time className="reminder-time" dateTime={`2026-10-07T${intake.time}`}>
                    {intake.time}
                  </time>
                </div>
              )
            })
          )}
          <div className="panel-footnote">
            Принятые лекарства исчезают из списка ближайших напоминаний.
          </div>
        </Paper>
        <Paper
          component="section"
          className="panel settings-panel"
          aria-label="Настройки напоминаний"
        >
          <span className="stat-icon mint">
            <NotificationsNoneRoundedIcon />
          </span>
          <Typography variant="h2" sx={{ mt: 2 }}>
            Как напоминать
          </Typography>
          <div className="setting-row">
            <FormControlLabel
              label="Напоминания в приложении"
              labelPlacement="start"
              control={<Switch checked={enabled} onChange={(_, checked) => setEnabled(checked)} />}
            />
            <Typography variant="body2" color="text.secondary">
              Показывать уведомление ко времени приёма.
            </Typography>
          </div>
          <div className="setting-row">
            <FormControlLabel
              label="Повторное напоминание"
              labelPlacement="start"
              control={
                <Switch
                  checked={repeat}
                  disabled={!enabled}
                  onChange={(_, checked) => setRepeat(checked)}
                />
              }
            />
            <Typography variant="body2" color="text.secondary">
              Напомнить ещё раз через 10 минут без отметки «принято».
            </Typography>
          </div>
          <Alert severity="info" icon={false} sx={{ mt: 2, fontSize: '0.78rem' }}>
            Это макет уведомлений. Настоящие напоминания в демоверсии не отправляются.
          </Alert>
        </Paper>
      </div>
    </>
  )
}
