import {
  Button,
  Chip,
  IconButton,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tooltip,
  Typography,
} from '@mui/material'
import MedicationOutlinedIcon from '@mui/icons-material/MedicationOutlined'
import ArrowForwardRoundedIcon from '@mui/icons-material/ArrowForwardRounded'
import PrintOutlinedIcon from '@mui/icons-material/PrintOutlined'
import { Link } from 'react-router'
import { getMember, medications } from '../entities/demoData'
import { MemberFilter } from '../shared/components/MemberFilter'
import { PageHeader } from '../shared/components/PageHeader'
import { PersonAvatar } from '../shared/components/PersonAvatar'
import { useMemberFilter } from '../shared/useMemberFilter'

export function MedicationsPage() {
  const [memberId, setMemberId] = useMemberFilter()
  const filtered = medications.filter(
    (medicine) => memberId === 'all' || medicine.memberId === memberId,
  )
  return (
    <>
      <PageHeader
        eyebrow="НАЗНАЧЕНИЯ И КУРСЫ"
        title="Лекарства семьи"
        description="Дозы, время приёма и длительность каждого курса."
        action={
          <Button
            component={Link}
            to={memberId === 'all' ? '/doctor' : `/doctor?member=${memberId}`}
            variant="outlined"
            startIcon={<PrintOutlinedIcon />}
          >
            Список для врача
          </Button>
        }
      />
      <Paper className="panel">
        <div className="schedule-toolbar">
          <div className="section-heading">
            <Typography variant="h2">Текущие назначения</Typography>
            <Chip label={filtered.length} size="small" />
          </div>
          <MemberFilter value={memberId} onChange={setMemberId} />
        </div>
        <Typography className="mobile-table-hint" variant="body2">
          Прокрутите таблицу вправо, чтобы увидеть время и курс.
        </Typography>
        <TableContainer>
          <Table sx={{ minWidth: 680 }} aria-label="Текущие назначения семьи">
            <TableHead>
              <TableRow>
                <TableCell>Лекарство</TableCell>
                <TableCell>Член семьи</TableCell>
                <TableCell>Приём</TableCell>
                <TableCell>Курс</TableCell>
                <TableCell align="right">План</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filtered.map((medicine) => {
                const member = getMember(medicine.memberId)
                return (
                  <TableRow key={medicine.id}>
                    <TableCell>
                      <div className="medicine-name">
                        <span className="medicine-icon">
                          <MedicationOutlinedIcon sx={{ fontSize: 22 }} />
                        </span>
                        <div>
                          <Typography sx={{ fontWeight: 800 }}>{medicine.name}</Typography>
                          <Typography variant="body2" color="text.secondary">
                            {medicine.form} · {medicine.dose}
                          </Typography>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="intake-person">
                        <PersonAvatar member={member} size={30} />
                        <span>{member.firstName}</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="time-chips">
                        {medicine.times.map((time) => (
                          <Chip key={time} label={time} size="small" variant="outlined" />
                        ))}
                      </div>
                      <Typography variant="body2" color="text.secondary" sx={{ mt: 0.7 }}>
                        {medicine.instructions}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{ whiteSpace: 'nowrap' }}>
                        {medicine.course}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Ежедневно
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Tooltip title="Открыть расписание">
                        <IconButton
                          component={Link}
                          to={`/schedule?member=${member.id}`}
                          aria-label={`Расписание: ${medicine.name}, ${member.firstName}`}
                          color="primary"
                          size="small"
                        >
                          <ArrowForwardRoundedIcon />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                )
              })}
            </TableBody>
          </Table>
        </TableContainer>
        <div className="panel-footnote">
          Демонстрационные назначения за октябрь 2026. Все сведения вымышлены.
        </div>
      </Paper>
      <div className="subtle-note">
        <MedicationOutlinedIcon sx={{ fontSize: 18 }} />
        <Typography variant="body2" color="text.secondary">
          Список объединяет назначения семьи. Время и дозы также доступны в расписании каждого
          человека.
        </Typography>
      </div>
    </>
  )
}
