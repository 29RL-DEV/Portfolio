/* Detect mobile devices - UI behavior only */
function isMobileView() {
  return window.matchMedia("(max-width: 768px)").matches;
}


/* Decode Text Effect - Hero Code */
const decodeChars =
  "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+-={}[]<>?/";

let decodeRunning = false;

function decodeText(element, finalText, speed = 30) {
  if (!element || decodeRunning) return;
  decodeRunning = true;

  let iteration = 0;
  element.textContent = "";
  element.classList.add("decode-cursor");

  const interval = setInterval(() => {
    element.textContent = finalText
      .split("")
      .map((char, index) => {
        if (char === "\n") return "\n";
        if (index < iteration) return finalText[index];
        return decodeChars[Math.floor(Math.random() * decodeChars.length)];
      })
      .join("");

    if (iteration >= finalText.length) {
      clearInterval(interval);
      element.textContent = finalText;
      element.classList.remove("decode-cursor");
      decodeRunning = false;
    }

    iteration++;
  }, speed);
}

/* Hero Flip + Decode Control */
let heroPlayed = false;

function playHeroAnimation() {
  if (heroPlayed) return;

  const card = document.querySelector(".hero-code");
  const backCodeEl = document.querySelector(".hero-code-back code");
  if (!card || !backCodeEl) return;

  heroPlayed = true;

  // Trigger flip instantly
  setTimeout(() => {
    card.classList.add("is-flipped");

    // Start decoding 600ms after flip completes
    setTimeout(() => {
      decodeText(
        backCodeEl,
        `AI Dev Agent - Developer Productivity Loop

[1] Ingest repository and test results
[2] Analyse failures and logs
[3] Build relevant code context
[4] Generate candidate fixes
[5] Rank and explain solutions
[6] Apply changes in isolated branch
[7] Re-run tests
[8] Produce reports and suggestions
`,
        20,
      );
    }, 600);
  }, 0);
}

function resetHeroAnimation() {
  const card = document.querySelector(".hero-code");
  const backCodeEl = document.querySelector(".hero-code-back code");
  if (!card || !backCodeEl) return;

  heroPlayed = false;
  decodeRunning = false;
  card.classList.remove("is-flipped");
  backCodeEl.textContent = "";
}

/* Auto-flip on scroll visibility */
let isFirstCardView = true;

function setupCardVisibilityObserver() {
  const card = document.querySelector(".hero-code");
  if (!card) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          // Card is visible - trigger flip animation if not played yet
          if (!heroPlayed) {
            if (isFirstCardView) {
              // First time - use 1500ms delay
              setTimeout(playHeroAnimation, 1000);
              isFirstCardView = false;
            } else {
              // Returning from scroll - instant
              setTimeout(playHeroAnimation, 0);
            }
          }
        } else {
          // Card is out of view - reset it
          resetHeroAnimation();
        }
      });
    },
    { threshold: 0.1 }, // Trigger when at least 10% is visible
  );

  observer.observe(card);
}

/* Main App Init */
function initApp() {
  /* Mobile Menu */
  const menuToggle = document.querySelector(".menu-toggle");
  const navLinks = document.querySelector(".nav-links");

  if (menuToggle && navLinks) {
    menuToggle.addEventListener("click", () => {
      const expanded = menuToggle.getAttribute("aria-expanded") === "true";
      menuToggle.setAttribute("aria-expanded", String(!expanded));
      navLinks.classList.toggle("active");
    });

    navLinks.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => {
        menuToggle.setAttribute("aria-expanded", "false");
        navLinks.classList.remove("active");
      });
    });
  }

  /* Dynamic Year */
  const yearEl = document.getElementById("currentYear");
  if (yearEl) {
    yearEl.textContent = new Date().getFullYear();
  }

  /* Project Card Hover - desktop only */
  if (!isMobileView()) {
    document.querySelectorAll(".project-card").forEach((card) => {
      card.addEventListener("mouseenter", () => {
        card.style.transform = "translateY(-10px) scale(1.02)";
      });

      card.addEventListener("mouseleave", () => {
        card.style.transform = "translateY(0) scale(1)";
      });
    });
  }

  /* Smooth Scroll */
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

  /* Navbar + Hero Logic with Intersection Observer */
  const navbar = document.querySelector(".navbar");

  // Setup auto-flip on scroll visibility
  setupCardVisibilityObserver();

  if (!navbar) {
    return;
  }

  let lastScroll = 0;

  window.addEventListener("scroll", () => {
    const currentScroll = window.pageYOffset;

    if (currentScroll <= 0) {
      navbar.style.transform = "translateY(0)";
      navbar.style.boxShadow = "none";
      lastScroll = currentScroll;
      return;
    }

    if (currentScroll > lastScroll) {
      navbar.style.transform = "translateY(-100%)";
    } else {
      navbar.style.transform = "translateY(0)";
      navbar.style.boxShadow = "0 10px 30px rgba(0,0,0,0.15)";
    }

    lastScroll = currentScroll;
  });

}

/* DOM Ready */
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initApp);
} else {
  initApp();
}
