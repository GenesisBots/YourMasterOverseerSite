console.log("YourMasterOverseer static site loaded.");

// Highlight the current page in the navigation.
document.addEventListener("DOMContentLoaded", () => {
  const currentFile = window.location.pathname.split("/").pop() || "index.html";
  const navLinks = document.querySelectorAll("nav .links a[href]");

  navLinks.forEach((link) => {
    const href = link.getAttribute("href");
    if (!href || href.startsWith("http")) return;
    if (href === currentFile) {
      link.classList.add("active");
      link.setAttribute("aria-current", "page");
    }
  });

  // Improve lead form reliability on slower/mobile connections:
  // lock submit button immediately and avoid accidental duplicate submissions.
  const leadForms = document.querySelectorAll("form[data-lead-form]");
  leadForms.forEach((form) => {
    form.addEventListener("submit", () => {
      const submitBtn = form.querySelector("button[type='submit']");
      const status = form.querySelector(".form-status");
      if (!submitBtn) return;

      submitBtn.disabled = true;
      const originalLabel = submitBtn.getAttribute("data-submit-label") || submitBtn.textContent || "Submit";
      submitBtn.textContent = "Submitting...";
      status.textContent = "Submitting your request...";

      // If the network hangs and no redirect happens, restore after timeout.
      window.setTimeout(() => {
        if (submitBtn.disabled) {
          submitBtn.disabled = false;
          submitBtn.textContent = originalLabel;
          status.textContent = "Network is slow. Please try submitting again.";
        }
      }, 15000);
    });
  });
});