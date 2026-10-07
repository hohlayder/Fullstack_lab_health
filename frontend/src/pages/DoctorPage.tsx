import {
  Button,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material'
import PrintOutlinedIcon from '@mui/icons-material/PrintOutlined'
import DescriptionOutlinedIcon from '@mui/icons-material/DescriptionOutlined'
import { DEMO_DATE_LABEL, getMedication, getMember, medications } from '../entities/demoData'
import { useDemo } from '../features/demo/demoContext'
import { MemberFilter } from '../shared/components/MemberFilter'
import { PageHeader } from '../shared/components/PageHeader'
import { useMemberFilter } from '../shared/useMemberFilter'

export function DoctorPage() {
  const [memberId, setMemberId] = useMemberFilter(false)
  const member = getMember(memberId)
  const memberMedicines = medications.filter((medicine) => medicine.memberId === memberId)
  const { intakes } = useDemo()
  const memberIntakes = intakes.filter(
    (intake) => getMedication(intake.medicationId).memberId === memberId,
  )
  const taken = memberIntakes.filter((intake) => intake.taken).length

  return (
    <>
      <PageHeader
        eyebrow="ПОДГОТОВКА К ПРИЁМУ"
        title="Список для врача"
        description="Все текущие назначения на одном листе."
        action={
          <Button
            variant="contained"
            startIcon={<PrintOutlinedIcon />}
            onClick={() => window.print()}
          >
            Распечатать
          </Button>
        }
      />
      <div className="report-toolbar screen-only">
        <MemberFilter value={memberId} onChange={setMemberId} allowAll={false} />
        <Typography variant="body2" color="text.secondary">
          Можно распечатать или сохранить в PDF через окно печати.
        </Typography>
      </div>
      <Paper className="print-sheet" component="article" aria-label="Печатный список лекарств">
        <div className="report-brand">
          <DescriptionOutlinedIcon sx={{ fontSize: 20 }} />
          <span>
            близкие<span className="report-brand-caption">Семейное расписание лекарств</span>
          </span>
        </div>
        <div className="report-title">
          <Typography variant="h1">Список лекарств для врача</Typography>
          <Typography color="text.secondary" sx={{ mt: 0.7 }}>
            Текущие назначения на {DEMO_DATE_LABEL}
          </Typography>
        </div>
        <div className="report-patient">
          <div>
            <span className="report-label">ПАЦИЕНТ</span>
            <Typography variant="h2">{member.fullName}</Typography>
          </div>
          <div>
            <span className="report-label">ВОЗРАСТ</span>
            <Typography sx={{ fontWeight: 700 }}>
              {member.age} {member.age === 59 ? 'лет' : 'года'}
            </Typography>
          </div>
        </div>
        <TableContainer>
          <Table className="report-table" aria-label={`Лекарства для врача: ${member.fullName}`}>
            <TableHead>
              <TableRow>
                <TableCell>Лекарство / доза</TableCell>
                <TableCell>Время</TableCell>
                <TableCell>Курс / примечание</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {memberMedicines.map((medicine) => (
                <TableRow key={medicine.id}>
                  <TableCell>
                    <Typography sx={{ fontWeight: 800 }}>{medicine.name}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      {medicine.dose} · {medicine.form}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" sx={{ fontWeight: 700 }}>
                      {medicine.times.join(', ')}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Ежедневно
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">{medicine.course}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      {medicine.instructions}
                    </Typography>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
        <div className="report-summary">
          <Typography variant="h3">Отметки за {DEMO_DATE_LABEL}</Typography>
          <Typography color="text.secondary" sx={{ mt: 0.7 }}>
            Отмечено как принято: {taken} из {memberIntakes.length} приёмов. Отметки внесены
            пользователем в демонстрационное расписание.
          </Typography>
        </div>
        <div className="doctor-notes">
          <Typography variant="body2" sx={{ fontWeight: 700 }}>
            Заметки на приёме
          </Typography>
          <div />
          <div />
          <div />
        </div>
        <div className="report-footer">
          Учебный макет. Данные и назначения вымышлены.<span>Близкие · {DEMO_DATE_LABEL}</span>
        </div>
      </Paper>
    </>
  )
}
