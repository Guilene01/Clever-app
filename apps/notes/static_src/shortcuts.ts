// Keyboard shortcuts: 'n' opens a new note (when not typing in an input).
document.addEventListener("keydown", (event) => {
  const target = event.target as HTMLElement | null;
  if (target && ["INPUT", "TEXTAREA"].includes(target.tagName)) return;
  if (event.key === "n") {
    const newBtn = document.querySelector<HTMLButtonElement>("[hx-get*='/notes/new']");
    newBtn?.click();
  }
});

export {};
