import { createContext, useContext } from 'react'
import type { Intake } from '../../entities/types'

export interface DemoState {
  intakes: Intake[]
  toggleIntake: (id: string) => void
}

export const DemoContext = createContext<DemoState | null>(null)

export function useDemo() {
  const context = useContext(DemoContext)
  if (!context) throw new Error('Демонстрационные данные недоступны')
  return context
}
