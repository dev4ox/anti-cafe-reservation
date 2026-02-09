(() => {
  const storageKey = "theme";
  const root = document.documentElement;
  const media = window.matchMedia("(prefers-color-scheme: dark)");

  const getSystemTheme = () => (media.matches ? "dark" : "light");
  const getMode = () => localStorage.getItem(storageKey) || "system";

  const updateButtons = (mode, theme) => {
    const labelText =
      mode === "system"
        ? "Тема: Системная"
        : theme === "dark"
        ? "Тема: Темная"
        : "Тема: Светлая";

    document.querySelectorAll("[data-theme-toggle]").forEach((button) => {
      const label = button.querySelector("[data-theme-label]");
      if (label) {
        label.textContent = labelText;
      }
      button.setAttribute("aria-pressed", theme === "dark");
      button.dataset.themeMode = mode;
    });
  };

  const applyTheme = (mode) => {
    const theme = mode === "system" ? getSystemTheme() : mode;
    root.setAttribute("data-theme", theme);
    root.setAttribute("data-bs-theme", theme);
    updateButtons(mode, theme);
  };

  const setMode = (mode) => {
    localStorage.setItem(storageKey, mode);
    applyTheme(mode);
  };

  document.addEventListener("click", (event) => {
    const setButton = event.target.closest("[data-theme-set]");
    if (setButton) {
      const mode = setButton.getAttribute("data-theme-set");
      setMode(mode);
      return;
    }

    const toggle = event.target.closest("[data-theme-toggle]");
    if (toggle) {
      const currentTheme = root.getAttribute("data-theme") || getSystemTheme();
      const next = currentTheme === "dark" ? "light" : "dark";
      setMode(next);
    }
  });

  media.addEventListener("change", () => {
    if (getMode() === "system") {
      applyTheme("system");
    }
  });

  document.addEventListener("DOMContentLoaded", () => {
    applyTheme(getMode());
  });
})();
