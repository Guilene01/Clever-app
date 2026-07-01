// Editor enhancements: autofocus the first marked input in any newly-swapped editor.
document.addEventListener("htmx:afterSwap", (event) => {
  const target = (event as CustomEvent).detail?.target as HTMLElement | undefined;
  if (!target) return;
  const focusTarget = target.querySelector<HTMLInputElement | HTMLTextAreaElement>("[data-autofocus]");
  focusTarget?.focus();
});

export {};
