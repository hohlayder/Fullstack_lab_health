export interface FamilyMember {
  id: string
  firstName: string
  fullName: string
  relation: string
  age: number
  initials: string
  color: string
  background: string
}

export interface Medication {
  id: string
  memberId: string
  name: string
  form: string
  dose: string
  times: string[]
  course: string
  instructions: string
}

export interface Intake {
  id: string
  medicationId: string
  time: string
  taken: boolean
}
