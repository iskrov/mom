interface ThemeToggleProps {
  isDark: boolean
  onToggle: () => void
}

export function ThemeToggle({ isDark, onToggle }: ThemeToggleProps) {
  return (
    <button className="theme-toggle" onClick={onToggle} type="button">
      {isDark ? 'Light' : 'Dark'}
    </button>
  )
}
