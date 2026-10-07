import { Button, Chip, CircularProgress, Paper, Typography } from '@mui/material'
import CheckRoundedIcon from '@mui/icons-material/CheckRounded'
import CalendarTodayOutlinedIcon from '@mui/icons-material/CalendarTodayOutlined'
import MedicationOutlinedIcon from '@mui/icons-material/MedicationOutlined'
import CheckCircleOutlineRoundedIcon from '@mui/icons-material/CheckCircleOutlineRounded'
import AccessTimeRoundedIcon from '@mui/icons-material/AccessTimeRounded'
import ArrowForwardRoundedIcon from '@mui/icons-material/ArrowForwardRounded'
import { Link } from 'react-router'
import { getMedication, getMember } from '../entities/demoData'
import { useDemo } from '../features/demo/demoContext'
import { MemberFilter } from '../shared/components/MemberFilter'
import { PageHeader } from '../shared/components/PageHeader'
import { PersonAvatar } from '../shared/components/PersonAvatar'
import { useMemberFilter } from '../shared/useMemberFilter'

const periods = [
  { title: 'Утро', caption: 'до 12:00', start: '00:00', end: '12:00', symbol: '☀' },
  { title: 'День', caption: '12:00–18:00', start: '12:00', end: '18:00', symbol: '◐' },
  { title: 'Вечер', caption: 'после 18:00', start: '18:00', end: '24:00', symbol: '☾' },
]

export function SchedulePage() {
  const { intakes, toggleIntake } = useDemo()
  const [memberId, setMemberId] = useMemberFilter()
  const filtered = intakes.filter(
    (intake) => memberId === 'all' || getMedication(intake.medicationId).memberId === memberId,
  )
  const taken = filtered.filter((intake) => intake.taken).length
  const remaining = filtered.length - taken
  const next = filtered.find((intake) => !intake.taken)
  const stats = [
    {
      label: 'Приёмов на день',
      value: filtered.length,
      icon: MedicationOutlinedIcon,
      className: 'mint',
    },
    { label: 'Уже принято', value: taken, icon: CheckCircleOutlineRoundedIcon, className: 'lilac' },
    { label: 'Осталось принять', value: remaining, icon: AccessTimeRoundedIcon, className: 'sand' },
  ]

  return (
    <>
      <PageHeader
        eyebrow="СРЕДА, 7 ОКТЯБРЯ"
        title="Расписание на сегодня"
        description="Все приёмы вашей семьи — в одном месте."
        action={
          <Button
            component={Link}
            to="/medications"
            variant="outlined"
            endIcon={<ArrowForwardRoundedIcon />}
          >
            Все лекарства
          </Button>
        }
      />
      <section className="schedule-hero" aria-label="Прогресс приёмов">
        <div className="hero-copy">
          <div className="hero-tag">
            <span className="status-dot" />
            ЗАБОТА КАЖДЫЙ ДЕНЬ
          </div>
          <Typography variant="h2" className="hero-title">
            Спокойнее, когда всё
            <br className="desktop-break" /> по расписанию.
          </Typography>
          <Typography sx={{ mt: 1.5, maxWidth: 450 }} color="text.secondary">
            {next
              ? `Следующий приём в ${next.time}. Небольшие отметки помогают не упустить главное.`
              : 'Все приёмы на сегодня отмечены. Расписание выполнено.'}
          </Typography>
        </div>
        <div className="progress-ring">
          <CircularProgress
            variant="determinate"
            value={100}
            size={124}
            thickness={3}
            sx={{ color: '#d2e9dd', position: 'absolute' }}
          />
          <CircularProgress
            aria-label="Доля принятых лекарств"
            variant="determinate"
            value={filtered.length ? (taken / filtered.length) * 100 : 0}
            size={124}
            thickness={3}
          />
          <div className="progress-label">
            <strong>
              {taken}
              <span> / {filtered.length}</span>
            </strong>
            <small>приёмов отмечено</small>
          </div>
        </div>
      </section>
      <div className="stats-grid">
        {stats.map(({ label, value, icon: Icon, className }) => (
          <Paper className="stat-card" key={label}>
            <span className={`stat-icon ${className}`}>
              <Icon />
            </span>
            <div>
              <Typography variant="body2" color="text.secondary">
                {label}
              </Typography>
              <Typography component="p" className="stat-value">
                {value}
              </Typography>
            </div>
          </Paper>
        ))}
      </div>
      <Paper className="panel schedule-panel" component="section" aria-label="Приёмы лекарств">
        <div className="schedule-toolbar">
          <div className="section-heading">
            <CalendarTodayOutlinedIcon sx={{ fontSize: 19 }} />
            <Typography variant="h2">План на день</Typography>
            <Chip label="7 октября" size="small" variant="outlined" />
          </div>
          <MemberFilter value={memberId} onChange={setMemberId} />
        </div>
        {periods.map((period) => {
          const items = filtered.filter(
            (intake) => intake.time >= period.start && intake.time < period.end,
          )
          if (!items.length) return null
          return (
            <section key={period.title} className="schedule-section" aria-label={period.title}>
              <div className="period-heading">
                <span aria-hidden="true">{period.symbol}</span>
                <Typography variant="h3">{period.title}</Typography>
                <span className="period-caption">{period.caption}</span>
              </div>
              {items.map((intake) => {
                const medicine = getMedication(intake.medicationId)
                const member = getMember(medicine.memberId)
                return (
                  <div className={`intake-row${intake.taken ? ' is-taken' : ''}`} key={intake.id}>
                    <time className="intake-time" dateTime={`2026-10-07T${intake.time}`}>
                      {intake.time}
                    </time>
                    <div className="intake-medicine">
                      <Typography variant="h3">{medicine.name}</Typography>
                      <Typography variant="body2" color="text.secondary">
                        {medicine.dose} <span className="dot-separator">·</span>{' '}
                        {medicine.instructions}
                      </Typography>
                    </div>
                    <div className="intake-person">
                      <PersonAvatar member={member} size={30} />
                      <span>{member.firstName}</span>
                    </div>
                    <div className="intake-action">
                      <Button
                        size="small"
                        className={intake.taken ? 'taken-button' : ''}
                        variant={intake.taken ? 'text' : 'outlined'}
                        startIcon={intake.taken ? <CheckRoundedIcon /> : undefined}
                        aria-pressed={intake.taken}
                        aria-label={`${intake.taken ? 'Отменить отметку' : 'Отметить как принято'}: ${medicine.name}, ${member.firstName}, ${intake.time}`}
                        onClick={() => toggleIntake(intake.id)}
                      >
                        {intake.taken ? 'Принято' : 'Принять'}
                      </Button>
                    </div>
                  </div>
                )
              })}
            </section>
          )
        })}
        <div className="panel-footnote">
          <span className="status-dot" />
          Отметки в демоверсии сбрасываются при обновлении страницы.
        </div>
      </Paper>
    </>
  )
}
