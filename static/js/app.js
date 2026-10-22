document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-confirm]").forEach((form) => {
    form.addEventListener("submit", (event) => {
      const message = form.getAttribute("data-confirm") || "Delete this record?";
      if (!window.confirm(message)) {
        event.preventDefault();
      }
    });
  });
});
