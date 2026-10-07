import { Avatar } from '@mui/material'
import type { FamilyMember } from '../../entities/types'

export function PersonAvatar({ member, size = 36 }: { member: FamilyMember; size?: number }) {
  return (
    <Avatar
      aria-hidden="true"
      sx={{
        width: size,
        height: size,
        bgcolor: member.background,
        color: member.color,
        fontSize: size / 3,
        fontWeight: 800,
      }}
    >
      {member.initials}
    </Avatar>
  )
}
