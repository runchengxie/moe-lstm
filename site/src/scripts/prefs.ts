type Lang = "zh" | "en";
type ThemeChoice = "light" | "dark" | "system";

const root = document.documentElement;
const themeQuery = window.matchMedia("(prefers-color-scheme: dark)");

function isLang(value: string | null): value is Lang {
  return value === "zh" || value === "en";
}

function isTheme(value: string | null): value is ThemeChoice {
  return value === "light" || value === "dark" || value === "system";
}

function currentLang(): Lang {
  return root.lang === "en" ? "en" : "zh";
}

function currentTheme(): ThemeChoice {
  return isTheme(root.dataset.theme ?? null) ? (root.dataset.theme as ThemeChoice) : "system";
}

function resolvedDark(): boolean {
  const choice = currentTheme();
  if (choice === "dark") return true;
  if (choice === "light") return false;
  return themeQuery.matches;
}

function syncChrome(): void {
  const lang = currentLang();
  const title = lang === "en" ? root.dataset.titleEn : root.dataset.titleZh;
  const description = lang === "en" ? root.dataset.descEn : root.dataset.descZh;
  if (title) document.title = title;
  const descriptionMeta = document.querySelector('meta[name="description"]');
  if (descriptionMeta && description) descriptionMeta.setAttribute("content", description);
  const themeMeta = document.querySelector('meta[name="theme-color"]');
  if (themeMeta) themeMeta.setAttribute("content", resolvedDark() ? "#121417" : "#f3efe6");

  document.querySelectorAll<HTMLButtonElement>("[data-set-lang]").forEach((button) => {
    button.setAttribute("aria-pressed", button.dataset.setLang === lang ? "true" : "false");
  });
  const theme = currentTheme();
  document.querySelectorAll<HTMLButtonElement>("[data-set-theme]").forEach((button) => {
    button.setAttribute("aria-pressed", button.dataset.setTheme === theme ? "true" : "false");
  });
}

function store(key: string, value: string): void {
  try {
    localStorage.setItem(key, value);
  } catch {
    // Private mode can reject localStorage. The choice still applies for this view.
  }
}

document.querySelectorAll<HTMLButtonElement>("[data-set-lang]").forEach((button) => {
  button.addEventListener("click", () => {
    const next = button.dataset.setLang ?? "zh";
    if (!isLang(next)) return;
    root.lang = next;
    store("moe-lang", next);
    syncChrome();
  });
});

document.querySelectorAll<HTMLButtonElement>("[data-set-theme]").forEach((button) => {
  button.addEventListener("click", () => {
    const next = button.dataset.setTheme ?? "system";
    if (!isTheme(next)) return;
    root.dataset.theme = next;
    store("moe-theme", next);
    syncChrome();
  });
});

themeQuery.addEventListener("change", () => {
  if (currentTheme() === "system") syncChrome();
});

syncChrome();
