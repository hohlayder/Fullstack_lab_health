import { FormControl, InputLabel, Select } from '@mui/material'
import { useId } from 'react'
import { familyMembers } from '../../entities/demoData'

export function MemberFilter({
  value,
  onChange,
  allowAll = true,
}: {
  value: string
  onChange: (value: string) => void
  allowAll?: boolean
}) {
  const id = useId()
  return (
    <FormControl size="small" sx={{ minWidth: 200, width: { xs: '100%', sm: 'auto' } }}>
      <InputLabel htmlFor={id}>Член семьи</InputLabel>
      <Select
        native
        value={value}
        onChange={(event) => onChange(event.target.value)}
        label="Член семьи"
        inputProps={{ id }}
      >
        {allowAll && <option value="all">Вся семья</option>}
        {familyMembers.map((member) => (
          <option key={member.id} value={member.id}>
            {member.fullName}
          </option>
        ))}
      </Select>
    </FormControl>
  )
}
