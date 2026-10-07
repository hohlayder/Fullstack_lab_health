import { expect, test } from '@playwright/test'

test('all main screens support navigation, reload and browser history', async ({ page }) => {
  const errors: string[] = []
  page.on('pageerror', (error) => errors.push(error.message))
  await page.goto('/')
  await expect(page).toHaveURL(/\/schedule$/)
  const navigation = page.getByRole('navigation', { name: 'Основная навигация' })
  const screens = [
    ['Моя семья', 'Моя семья', '/family'],
    ['Лекарства', 'Лекарства семьи', '/medications'],
    ['Напоминания', 'Напоминания', '/reminders'],
    ['Список для врача', 'Список для врача', '/doctor'],
    ['Расписание', 'Расписание на сегодня', '/schedule'],
  ]
  for (const [label, title, path] of screens) {
    await navigation.getByRole('link', { name: label, exact: true }).click()
    await expect(page).toHaveURL(new RegExp(`${path}$`))
    await expect(page.getByRole('heading', { name: title, exact: true })).toBeVisible()
    await page.reload()
    await expect(page.getByRole('heading', { name: title, exact: true })).toBeVisible()
  }
  await page.goBack()
  await expect(page.getByRole('heading', { name: 'Список для врача', exact: true })).toBeVisible()
  expect(errors).toEqual([])
})

test('family links and filters isolate the chosen person', async ({ page }) => {
  await page.goto('/family')
  await page
    .getByRole('region')
    .filter({ hasText: 'Елена Соколова' })
    .getByRole('link', { name: 'Открыть расписание' })
    .click()
  await expect(page).toHaveURL(/\/schedule\?member=elena$/)
  await expect(page.getByLabel('Член семьи')).toHaveValue('elena')
  await expect(page.getByRole('button', { name: /Препарат А, Елена/ })).toHaveCount(2)
  await expect(page.getByRole('button', { name: /Магний, Анна/ })).toHaveCount(0)
  await page.getByLabel('Член семьи').selectOption('anna')
  await expect(page.getByRole('heading', { name: 'Магний', exact: true })).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Препарат А', exact: true })).toHaveCount(0)
  await page.goto('/medications?member=mikhail')
  await expect(page.getByRole('table').getByRole('row')).toHaveCount(3)
  await expect(page.getByRole('table')).toContainText('Омега-3')
  await expect(page.getByRole('table')).not.toContainText('Витамин D')
  await page.goto('/doctor?member=invalid')
  await expect(page.getByLabel('Член семьи')).toHaveValue('anna')
  await expect(page.getByRole('article')).toContainText('Анна Соколова')
})

test('an intake updates counters, reminders and report and resets after reload', async ({
  page,
}) => {
  await page.goto('/schedule')
  await page
    .getByRole('button', { name: 'Отметить как принято: Магний, Анна, 13:00', exact: true })
    .click()
  const undo = page.getByRole('button', {
    name: 'Отменить отметку: Магний, Анна, 13:00',
    exact: true,
  })
  await expect(undo).toHaveAttribute('aria-pressed', 'true')
  await expect(page.locator('.stat-card').filter({ hasText: 'Уже принято' })).toContainText('3')
  const navigation = page.getByRole('navigation', { name: 'Основная навигация' })
  await navigation.getByRole('link', { name: 'Напоминания', exact: true }).click()
  await expect(page.getByRole('heading', { name: 'Магний', exact: true })).toHaveCount(0)
  await expect(page.getByText('Осталось: 3', { exact: true })).toBeVisible()
  await navigation.getByRole('link', { name: 'Список для врача', exact: true }).click()
  await expect(page.getByRole('article')).toContainText('Отмечено как принято: 2 из 2 приёмов.')
  await navigation.getByRole('link', { name: 'Расписание', exact: true }).click()
  await undo.click()
  await expect(
    page.getByRole('button', { name: 'Отметить как принято: Магний, Анна, 13:00', exact: true }),
  ).toHaveAttribute('aria-pressed', 'false')
  await page
    .getByRole('button', { name: 'Отметить как принято: Магний, Анна, 13:00', exact: true })
    .click()
  await page.reload()
  await expect(
    page.getByRole('button', { name: 'Отметить как принято: Магний, Анна, 13:00', exact: true }),
  ).toBeVisible()
})

test('reminder settings show their demo state', async ({ page }) => {
  await page.goto('/reminders')
  await page.getByRole('switch', { name: 'Напоминания в приложении', exact: true }).uncheck()
  await expect(page.getByRole('alert').filter({ hasText: 'приостановлены' })).toBeVisible()
  await expect(
    page.getByRole('switch', { name: 'Повторное напоминание', exact: true }),
  ).toBeDisabled()
  await page.getByRole('switch', { name: 'Напоминания в приложении', exact: true }).check()
  await expect(
    page.getByRole('switch', { name: 'Повторное напоминание', exact: true }),
  ).toBeEnabled()
})

test('the doctor list follows the person filter and is ready for printing', async ({ page }) => {
  await page.goto('/doctor')
  await page.getByLabel('Член семьи').selectOption('elena')
  const report = page.getByRole('article')
  await expect(report).toContainText('Елена Соколова')
  await expect(report.getByRole('table')).toContainText('08:30, 20:00')
  await expect(report).not.toContainText('Магний')
  await page.emulateMedia({ media: 'print' })
  await expect(page.getByRole('navigation')).toBeHidden()
  await expect(page.getByRole('button', { name: 'Распечатать', exact: true })).toBeHidden()
  await expect(report).toBeVisible()
  await expect(report.getByRole('heading', { name: 'Список лекарств для врача' })).toBeVisible()
})

test('all screens fit a mobile viewport and the menu closes after navigation', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 })
  for (const route of ['/schedule', '/family', '/medications', '/reminders', '/doctor']) {
    await page.goto(route)
    await expect(page.getByRole('main').getByRole('heading', { level: 1 }).first()).toBeVisible()
    expect(
      await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth),
    ).toBe(true)
  }
  await page.getByRole('button', { name: 'Открыть меню', exact: true }).click()
  const navigation = page.getByRole('navigation', { name: 'Основная навигация' })
  await expect(navigation).toBeVisible()
  await navigation.getByRole('link', { name: 'Расписание', exact: true }).click()
  await expect(page).toHaveURL(/\/schedule$/)
  await expect(navigation).toBeHidden()
})

test('an unknown route shows a recovery screen', async ({ page }) => {
  await page.goto('/missing-page')
  await expect(page.getByRole('heading', { name: 'Страница не найдена' })).toBeVisible()
  await page.getByRole('link', { name: 'Вернуться к расписанию' }).click()
  await expect(page).toHaveURL(/\/schedule$/)
  await expect(page.getByRole('heading', { name: 'Расписание на сегодня' })).toBeVisible()
})
