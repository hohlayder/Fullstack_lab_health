import { mkdir } from 'node:fs/promises'
import path from 'node:path'
import { expect, test } from '@playwright/test'

test('save screenshots of every screen, mobile layouts and the print view', async ({ page }) => {
  const directory = path.resolve('..', 'docs', 'screenshots')
  await mkdir(directory, { recursive: true })
  const screens = [
    ['/schedule', 'Расписание на сегодня', '01-schedule.png'],
    ['/family', 'Моя семья', '02-family.png'],
    ['/medications', 'Лекарства семьи', '03-medications.png'],
    ['/reminders', 'Напоминания', '04-reminders.png'],
    ['/doctor', 'Список для врача', '05-doctor.png'],
    ['/missing-page', 'Страница не найдена', '06-not-found.png'],
  ]
  for (const [route, heading, file] of screens) {
    await page.goto(route)
    await expect(page.getByRole('heading', { name: heading, exact: true })).toBeVisible()
    await page.evaluate(() => document.fonts.ready)
    await page.screenshot({
      path: path.join(directory, file),
      fullPage: true,
      animations: 'disabled',
    })
  }
  await page.setViewportSize({ width: 390, height: 844 })
  for (const [route, file] of [
    ['/schedule', '07-schedule-mobile.png'],
    ['/medications', '08-medications-mobile.png'],
  ]) {
    await page.goto(route)
    await expect(page.locator('.schedule-toolbar')).toBeVisible()
    await page.evaluate(() => document.fonts.ready)
    await page.screenshot({
      path: path.join(directory, file),
      fullPage: true,
      animations: 'disabled',
    })
  }
  await page.setViewportSize({ width: 900, height: 1100 })
  await page.goto('/doctor')
  await expect(page.getByRole('article')).toBeVisible()
  await page.evaluate(() => document.fonts.ready)
  await page.emulateMedia({ media: 'print' })
  await page.screenshot({
    path: path.join(directory, '09-doctor-print.png'),
    fullPage: true,
    animations: 'disabled',
  })
  await page.pdf({
    path: path.join(directory, '..', 'doctor-list-example.pdf'),
    format: 'A4',
    printBackground: true,
  })
})
