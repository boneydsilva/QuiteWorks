/* ==========================================================================
   Quietworks - site behaviour
   Plain JS, no dependencies, no build step.

   >>> EDIT THIS BLOCK. Everything you are likely to change lives here. <<<
   ========================================================================== */

const SITE = {
  // Where the contact form posts. Sign up free at https://web3forms.com,
  // paste the access key here, and the form starts emailing you. Until then
  // the form falls back to opening the visitor's email client.
  formAccessKey: "PASTE-YOUR-WEB3FORMS-ACCESS-KEY-HERE",

  // Your details. The email is also hard-coded in the page footers and on the
  // contact page - search the .html files for it if you ever change it. The
  // WhatsApp number lives only here; the links are built from it at runtime.
  email: "boneydsilva@gmail.com",
  whatsapp: "919004213100",          // country code + number, digits only
};

/* --------------------------------------------------------------------------
   1. Theme
   The inline script in each <head> sets data-theme before first paint so the
   page never flashes the wrong colours. This only wires up the button.
   -------------------------------------------------------------------------- */

function currentTheme() {
  const stored = document.documentElement.getAttribute("data-theme");
  if (stored) return stored;
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function initTheme() {
  const btn = document.querySelector(".theme-toggle");
  if (!btn) return;

  btn.addEventListener("click", () => {
    const next = currentTheme() === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    try { localStorage.setItem("qw-theme", next); } catch (e) { /* private mode */ }
    btn.setAttribute("aria-label", next === "dark" ? "Switch to light theme" : "Switch to dark theme");
  });
}

/* --------------------------------------------------------------------------
   2. Header: border appears once the page has scrolled
   -------------------------------------------------------------------------- */

function initHeader() {
  const header = document.querySelector(".site-header");
  if (!header) return;

  const sync = () => header.classList.toggle("scrolled", window.scrollY > 8);
  sync();
  window.addEventListener("scroll", sync, { passive: true });
}

/* --------------------------------------------------------------------------
   3. Mobile navigation
   -------------------------------------------------------------------------- */

function initNav() {
  const toggle = document.querySelector(".nav-toggle");
  const links = document.querySelector(".nav-links");
  if (!toggle || !links) return;

  const isMobile = () => window.matchMedia("(max-width: 860px)").matches;

  const setOpen = (open) => {
    links.hidden = !open;
    toggle.setAttribute("aria-expanded", String(open));
  };

  // Start closed on mobile, always visible on desktop.
  const sync = () => setOpen(!isMobile());
  sync();
  window.addEventListener("resize", sync);

  toggle.addEventListener("click", () => setOpen(links.hidden));
  links.addEventListener("click", (e) => {
    if (e.target.tagName === "A" && isMobile()) setOpen(false);
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && isMobile() && !links.hidden) {
      setOpen(false);
      toggle.focus();
    }
  });
}

/* --------------------------------------------------------------------------
   4. Reveal on scroll
   -------------------------------------------------------------------------- */

function initReveal() {
  const items = document.querySelectorAll(".reveal");
  if (!items.length) return;

  if (!("IntersectionObserver" in window) ||
      window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    items.forEach((el) => el.classList.add("in"));
    return;
  }

  const io = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add("in");
      io.unobserve(entry.target);
    });
  }, { rootMargin: "0px 0px -8% 0px", threshold: 0.05 });

  items.forEach((el) => io.observe(el));
}

/* --------------------------------------------------------------------------
   5. Contact form
   Posts to Web3Forms when a key is configured; otherwise composes a mailto:
   so the form is never a dead end.
   -------------------------------------------------------------------------- */

function initForm() {
  const form = document.querySelector("form[data-contact-form]");
  if (!form) return;

  const status = form.querySelector(".form-status");
  const submit = form.querySelector("button[type=submit]");
  const keyIsSet = SITE.formAccessKey && !SITE.formAccessKey.startsWith("PASTE-");

  const say = (msg, kind) => {
    if (!status) return;
    status.textContent = msg;
    status.className = "form-status " + kind;
    status.hidden = false;
  };

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    // Honeypot: real people leave this empty.
    if (form.querySelector("[name=botcheck]") && form.querySelector("[name=botcheck]").value) return;

    const data = Object.fromEntries(new FormData(form).entries());

    if (!keyIsSet) {
      const body = [
        "Name:    " + (data.name || ""),
        "Company: " + (data.company || ""),
        "Email:   " + (data.email || ""),
        "Phone:   " + (data.phone || ""),
        "PCs:     " + (data.team_size || ""),
        "Asking:  " + (data.enquiry || ""),
        "",
        data.message || "",
      ].join("\n");
      window.location.href =
        "mailto:" + SITE.email +
        "?subject=" + encodeURIComponent("Website enquiry - " + (data.company || data.name || "no name")) +
        "&body=" + encodeURIComponent(body);
      say("Opening your email app. If nothing happens, write to " + SITE.email + " directly.", "busy");
      return;
    }

    say("Sending...", "busy");
    if (submit) submit.disabled = true;

    try {
      const res = await fetch("https://api.web3forms.com/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify({
          access_key: SITE.formAccessKey,
          subject: "Quietworks enquiry - " + (data.company || data.name || "no name"),
          from_name: "Quietworks website",
          ...data,
        }),
      });
      const json = await res.json();

      if (res.ok && json.success) {
        form.reset();
        say("Thanks - that reached us. You will get a reply within one working day.", "ok");
      } else {
        throw new Error(json.message || "Send failed");
      }
    } catch (err) {
      say("That did not send. Please email " + SITE.email + " or message us on WhatsApp.", "err");
    } finally {
      if (submit) submit.disabled = false;
    }
  });
}

/* --------------------------------------------------------------------------
   6. Small conveniences
   -------------------------------------------------------------------------- */

function initMisc() {
  // Current year in the footer.
  document.querySelectorAll("[data-year]").forEach((el) => {
    el.textContent = String(new Date().getFullYear());
  });

  // WhatsApp links built from the config above.
  document.querySelectorAll("[data-whatsapp]").forEach((el) => {
    const text = el.getAttribute("data-whatsapp") || "Hello, I saw the Quietworks website.";
    el.href = "https://wa.me/" + SITE.whatsapp + "?text=" + encodeURIComponent(text);
  });

  // Pre-select the enquiry dropdown from ?about=licence style links.
  const about = new URLSearchParams(window.location.search).get("about");
  const select = document.querySelector("select[name=enquiry]");
  if (about && select) {
    const match = [...select.options].find((o) => o.value === about);
    if (match) select.value = about;
  }
}

/* -------------------------------------------------------------------------- */

document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  initHeader();
  initNav();
  initReveal();
  initForm();
  initMisc();
});
