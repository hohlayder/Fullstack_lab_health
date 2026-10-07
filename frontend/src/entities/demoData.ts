import type { FamilyMember, Intake, Medication } from './types'

export const DEMO_DATE_LABEL = '7 октября 2026'

export const familyMembers: FamilyMember[] = [
  {
    id: 'anna',
    firstName: 'Анна',
    fullName: 'Анна Соколова',
    relation: 'Я',
    age: 24,
    initials: 'АС',
    color: '#176b5b',
    background: '#dff3eb',
  },
  {
    id: 'elena',
    firstName: 'Елена',
    fullName: 'Елена Соколова',
    relation: 'Мама',
    age: 59,
    initials: 'ЕС',
    color: '#7961a0',
    background: '#efe8f7',
  },
  {
    id: 'mikhail',
    firstName: 'Михаил',
    fullName: 'Михаил Соколов',
    relation: 'Папа',
    age: 62,
    initials: 'МС',
    color: '#9a6b36',
    background: '#faecd9',
  },
]

export const medications: Medication[] = [
  {
    id: 'vitamin-d',
    memberId: 'anna',
    name: 'Витамин D',
    form: 'Капсулы',
    dose: '1 капсула',
    times: ['08:00'],
    course: '01.10–31.10.2026',
    instructions: 'После завтрака',
  },
  {
    id: 'medicine-a',
    memberId: 'elena',
    name: 'Препарат А',
    form: 'Таблетки',
    dose: '1 таблетка',
    times: ['08:30', '20:00'],
    course: '01.10–31.10.2026',
    instructions: 'После еды',
  },
  {
    id: 'magnesium',
    memberId: 'anna',
    name: 'Магний',
    form: 'Таблетки',
    dose: '1 таблетка',
    times: ['13:00'],
    course: '01.10–21.10.2026',
    instructions: 'Во время обеда',
  },
  {
    id: 'medicine-b',
    memberId: 'mikhail',
    name: 'Препарат Б',
    form: 'Таблетки',
    dose: '1 таблетка',
    times: ['14:00'],
    course: '01.10–14.10.2026',
    instructions: 'После обеда',
  },
  {
    id: 'omega',
    memberId: 'mikhail',
    name: 'Омега-3',
    form: 'Капсулы',
    dose: '1 капсула',
    times: ['19:00'],
    course: '01.10–31.10.2026',
    instructions: 'Во время ужина',
  },
]

export const initialIntakes: Intake[] = medications
  .flatMap((medication) =>
    medication.times.map((time) => ({
      id: `${medication.id}-${time}`,
      medicationId: medication.id,
      time,
      taken: time < '12:00',
    })),
  )
  .sort((a, b) => a.time.localeCompare(b.time))

export function getMedication(id: string): Medication {
  const medication = medications.find((item) => item.id === id)
  if (!medication) throw new Error(`Неизвестное лекарство: ${id}`)
  return medication
}

export function getMember(id: string): FamilyMember {
  const member = familyMembers.find((item) => item.id === id)
  if (!member) throw new Error(`Неизвестный член семьи: ${id}`)
  return member
}
