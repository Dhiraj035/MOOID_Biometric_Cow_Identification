// =========================================================
// THEME MANAGEMENT SERVICE
// =========================================================

const THEME_KEY = "moo_id_theme";

export function getInitialTheme() {
  try {
    const savedTheme = localStorage.getItem(THEME_KEY);
    if (savedTheme === "dark" || savedTheme === "light") {
      return savedTheme;
    }
  } catch {
    // LocalStorage might be disabled or unavailable
  }
  return "light";
}

export function applyTheme(theme) {
  const activeTheme = theme === "dark" ? "dark" : "light";
  document.documentElement.setAttribute("data-theme", activeTheme);
  try {
    localStorage.setItem(THEME_KEY, activeTheme);
  } catch {
    // ignore storage errors
  }
  // Notify any active listeners
  window.dispatchEvent(new CustomEvent("moo_id_theme_change", { detail: activeTheme }));
  return activeTheme;
}

export function initTheme() {
  const initial = getInitialTheme();
  applyTheme(initial);
  return initial;
}
