// Detect mobile devices
const isMobile = window.matchMedia("(max-width: 768px)").matches;

function initApp() {
  /* ===============================
     Mobile Menu
  =============================== */
  const menuToggle = document.querySelector(".menu-toggle");
  const navLinks = document.querySelector(".nav-links");

  if (menuToggle && navLinks) {
    menuToggle.addEventListener("click", () => {
      const isExpanded = menuToggle.getAttribute("aria-expanded") === "true";
      menuToggle.setAttribute("aria-expanded", String(!isExpanded));
      navLinks.classList.toggle("active");
    });

    navLinks.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => {
        menuToggle.setAttribute("aria-expanded", "false");
        navLinks.classList.remove("active");
      });
    });
  }

  /* ===============================
     Dynamic Year
  =============================== */
  const year = document.getElementById("currentYear");
  if (year) {
    year.textContent = new Date().getFullYear();
  }

  /* ===============================
     Project Card Hover (desktop)
  =============================== */
  if (!isMobile) {
    document.querySelectorAll(".project-card").forEach((card) => {
      card.addEventListener("mouseenter", () => {
        card.style.transform = "translateY(-10px) scale(1.02)";
      });

      card.addEventListener("mouseleave", () => {
        card.style.transform = "translateY(0) scale(1)";
      });
    });
  }

  /* ===============================
     Smooth Scroll
  =============================== */
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      const targetId = this.getAttribute("href");
      if (!targetId || targetId === "#") return;

      const target = document.querySelector(targetId);
      if (!target) return;

      e.preventDefault();

      window.scrollTo({
        top: target.offsetTop - 80,
        behavior: "smooth",
      });
    });
  });

  /* ===============================
     Navbar Scroll Behavior (desktop)
  =============================== */
  const navbar = document.querySelector(".navbar");
  if (!navbar || isMobile) return;

  let lastScroll = 0;

  window.addEventListener("scroll", () => {
    const current = window.pageYOffset;

    if (current <= 0) {
      navbar.style.transform = "translateY(0)";
      navbar.style.boxShadow = "none";
      lastScroll = current;
      return;
    }

    if (current > lastScroll) {
      navbar.style.transform = "translateY(-100%)";
    } else {
      navbar.style.transform = "translateY(0)";
      navbar.style.boxShadow = "0 10px 30px rgba(0,0,0,0.15)";
    }

    lastScroll = current;
  });
}

/* ===============================
   Safe DOM Ready
=============================== */
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initApp);
} else {
  initApp();
}
