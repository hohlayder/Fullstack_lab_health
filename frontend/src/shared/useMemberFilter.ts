import { useSearchParams } from 'react-router'
import { familyMembers } from '../entities/demoData'

export function useMemberFilter(allowAll = true) {
  const [searchParams, setSearchParams] = useSearchParams()
  const requested = searchParams.get('member')
  const memberId = familyMembers.some((member) => member.id === requested)
    ? requested!
    : allowAll
      ? 'all'
      : familyMembers[0].id

  function setMemberId(value: string) {
    setSearchParams((current) => {
      const next = new URLSearchParams(current)
      if (value === 'all') next.delete('member')
      else next.set('member', value)
      return next
    })
  }

  return [memberId, setMemberId] as const
}
