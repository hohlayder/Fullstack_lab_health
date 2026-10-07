import { Button, Chip, Paper, Typography } from '@mui/material'
import ArrowForwardRoundedIcon from '@mui/icons-material/ArrowForwardRounded'
import FavoriteBorderRoundedIcon from '@mui/icons-material/FavoriteBorderRounded'
import { Link } from 'react-router'
import { familyMembers, getMedication, medications } from '../entities/demoData'
import { useDemo } from '../features/demo/demoContext'
import { PageHeader } from '../shared/components/PageHeader'
import { PersonAvatar } from '../shared/components/PersonAvatar'

export function FamilyPage() {
  const { intakes } = useDemo()
  return (
    <>
      <PageHeader
        eyebrow="ТЕ, КТО РЯДОМ"
        title="Моя семья"
        description="Индивидуальные назначения. Общая забота."
        action={<Chip label="3 члена семьи" variant="outlined" />}
      />
      <div className="family-grid">
        {familyMembers.map((member) => {
          const memberMedicines = medications.filter((medicine) => medicine.memberId === member.id)
          const memberIntakes = intakes.filter(
            (intake) => getMedication(intake.medicationId).memberId === member.id,
          )
          const taken = memberIntakes.filter((intake) => intake.taken).length
          const next = memberIntakes.find((intake) => !intake.taken)
          return (
            <Paper
              component="section"
              aria-label={member.fullName}
              className="panel family-card"
              key={member.id}
            >
              <div className="family-card-top">
                <PersonAvatar member={member} size={64} />
                <Chip
                  label={member.relation}
                  size="small"
                  sx={{ color: member.color, bgcolor: member.background }}
                />
              </div>
              <Typography variant="h2" sx={{ mt: 2.5 }}>
                {member.fullName}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                {member.age} {member.age === 24 ? 'года' : member.age === 62 ? 'года' : 'лет'}
              </Typography>
              <div className="family-details">
                <div>
                  <span>Лекарств по расписанию</span>
                  <strong>{memberMedicines.length}</strong>
                </div>
                <div>
                  <span>Приёмов отмечено</span>
                  <strong>
                    {taken} из {memberIntakes.length}
                  </strong>
                </div>
              </div>
              <div className="next-intake">
                <span className="status-dot" />
                <span>{next ? `Ближайший приём в ${next.time}` : 'Все приёмы отмечены'}</span>
              </div>
              <Button
                component={Link}
                to={`/schedule?member=${member.id}`}
                variant="contained"
                fullWidth
                endIcon={<ArrowForwardRoundedIcon />}
                sx={{ mt: 2.5 }}
              >
                Открыть расписание
              </Button>
              <Button
                component={Link}
                to={`/medications?member=${member.id}`}
                fullWidth
                sx={{ mt: 0.5 }}
              >
                Посмотреть лекарства
              </Button>
            </Paper>
          )
        })}
      </div>
      <Paper className="family-note">
        <FavoriteBorderRoundedIcon sx={{ fontSize: 32, color: 'primary.main' }} />
        <div>
          <Typography variant="h3">Каждому — своё расписание</Typography>
          <Typography color="text.secondary" sx={{ mt: 0.5 }}>
            Выберите близкого, чтобы увидеть только его приёмы. Общее расписание всегда доступно в
            разделе «Расписание».
          </Typography>
        </div>
      </Paper>
    </>
  )
}
