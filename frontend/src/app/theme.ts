import { createTheme } from '@mui/material/styles'

export const theme = createTheme({
  palette: {
    primary: { main: '#137c6b', dark: '#0f5c50', light: '#e6f4ee' },
    secondary: { main: '#7961a0' },
    background: { default: '#f5f7f8', paper: '#ffffff' },
    text: { primary: '#20362f', secondary: '#64756e' },
    divider: '#e7ece9',
    success: { main: '#137c6b' },
  },
  typography: {
    fontFamily: 'Manrope, "Segoe UI", sans-serif',
    h1: { fontSize: '1.9rem', fontWeight: 800, letterSpacing: '-0.055rem', lineHeight: 1.3 },
    h2: { fontSize: '1.3rem', fontWeight: 800, letterSpacing: '-0.025rem' },
    h3: { fontSize: '1.05rem', fontWeight: 800 },
    body1: { fontSize: '0.9rem', lineHeight: 1.65 },
    body2: { fontSize: '0.8rem', lineHeight: 1.6 },
    button: { fontSize: '0.82rem', fontWeight: 700, textTransform: 'none' },
  },
  shape: { borderRadius: 12 },
  components: {
    MuiButton: {
      defaultProps: { disableElevation: true },
      styleOverrides: { root: { borderRadius: 9, padding: '9px 16px' } },
    },
    MuiPaper: {
      defaultProps: { elevation: 0 },
      styleOverrides: { root: { backgroundImage: 'none' } },
    },
    MuiChip: {
      styleOverrides: { root: { fontWeight: 700, fontSize: '0.72rem', borderRadius: 7 } },
    },
    MuiTableCell: {
      styleOverrides: {
        root: { borderColor: '#e7ece9', padding: '18px 16px' },
        head: {
          backgroundColor: '#fafcfb',
          color: '#64756e',
          fontWeight: 700,
          fontSize: '0.72rem',
        },
      },
    },
    MuiOutlinedInput: {
      styleOverrides: { root: { background: '#fff', fontSize: '0.82rem', borderRadius: 9 } },
    },
  },
})
