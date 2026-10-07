import { useState } from 'react'
import type { ReactNode } from 'react'
import { initialIntakes } from '../../entities/demoData'
import { DemoContext } from './demoContext'

export function DemoProvider({ children }: { children: ReactNode }) {
  const [intakes, setIntakes] = useState(initialIntakes)

  function toggleIntake(id: string) {
    setIntakes((current) =>
      current.map((intake) => (intake.id === id ? { ...intake, taken: !intake.taken } : intake)),
    )
  }

  return <DemoContext.Provider value={{ intakes, toggleIntake }}>{children}</DemoContext.Provider>
}
