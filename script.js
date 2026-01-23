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

/* Hero Decode Control - Direct Show */
let heroPlayed = false;
let decodingFinished = false;
let frontDecoded = false;
let hasPlayedOnce = false;

function playHeroAnimation() {
  if (heroPlayed) return;

  const backCodeEl = document.querySelector(".hero-code-back code");
  if (!backCodeEl) return;

  heroPlayed = true;
  hasPlayedOnce = true;

  // Show title immediately - STATIC
  const title = "AI Dev Agent — Developer Productivity Loop (Current)\n\n";
  backCodeEl.textContent = title;

  // Wait 1.5 seconds, then decode the rest
  setTimeout(() => {
    const stepsText = `[1] Ingest repository snapshots and test results provided manually
[2] Analyse failing tests and error logs
[3] Build focused code context around detected failures
[4] Generate multiple candidate fix suggestions
[5] Rank and explain proposed solutions
[6] Apply changes in an isolated working branch
[7] Re-run tests to validate fixes
[8] Produce structured reports and developer recommendations`;

    // Reset decodeRunning to allow fresh decode
    decodeRunning = false;

    // Create temporary element for decoding only the steps
    const tempEl = document.createElement("span");

    decodeText(tempEl, stepsText, 20);

    // Update backCodeEl as decoding progresses
    const checkInterval = setInterval(() => {
      backCodeEl.textContent = title + tempEl.textContent;

      if (!decodeRunning) {
        clearInterval(checkInterval);
        decodingFinished = true;

        // Wait 1 seconds after decoding finishes before showing button
        setTimeout(() => {
          const flipButton = document.querySelector(".flip-button");
          if (flipButton) {
            flipButton.classList.add("visible");
          }
        }, 300);
      }
    }, 20);
  }, 1500);
}

function playFrontAnimation() {
  const frontCodeEl = document.querySelector(".hero-code-front-text");
  const flipButtonFront = document.querySelector(".flip-button-front");
  if (!frontCodeEl) return;

  // Clear and hide button
  frontCodeEl.textContent = "";
  if (flipButtonFront) {
    flipButtonFront.classList.remove("visible");
  }

  // Show title immediately - STATIC
  const title = "AI Dev Agent — Developer Productivity Loop (Target)\n\n";
  frontCodeEl.textContent = title;

  // Wait 1.5 seconds, then decode the rest
  setTimeout(() => {
    playFrontAnimationDecoding();
  }, 1500);
}

function playFrontAnimationDecoding() {
  const frontCodeEl = document.querySelector(".hero-code-front-text");
  const title = "AI Dev Agent — Developer Productivity Loop (Target)\n\n";

  const stepsText = `[1] Continuously monitor repository activity and CI pipelines
[2] Automatically detect failures across tests and runtime signals
[3] Maintain deep contextual understanding of large codebases
[4] Propose safe, context-aware code fixes aligned with existing patterns
[5] Validate fixes through automated testing and iteration
[6] Manage isolated branches and version control operations
[7] Generate pull requests with clear explanations and reports
[8] Act as a persistent AI debugging and development companion`;

  decodeRunning = false;

  const tempEl = document.createElement("span");
  decodeText(tempEl, stepsText, 20);

  const checkInterval = setInterval(() => {
    frontCodeEl.textContent = title + tempEl.textContent;

    if (!decodeRunning) {
      clearInterval(checkInterval);

      setTimeout(() => {
        const flipButtonFront = document.querySelector(".flip-button-front");
        if (flipButtonFront) {
          flipButtonFront.classList.add("visible");
        }
      }, 300);
    }
  }, 20);
}

function playBackAnimationDecoding() {
  const backCodeEl = document.querySelector(".hero-code-back code");
  const title = "AI Dev Agent — Developer Productivity Loop (Current)\n\n";

  const stepsText = `[1] Ingest repository and test results
[2] Analyse failing tests and error logs
[3] Build relevant code context around failures
[4] Generate multiple candidate fix suggestions
[5] Rank and explain proposed solutions
[6] Apply changes in an isolated working branch
[7] Re-run tests to validate fixes
[8] Produce structured reports for developer review`;

  decodeRunning = false;

  const tempEl = document.createElement("span");

  decodeText(tempEl, stepsText, 20);

  const checkInterval = setInterval(() => {
    backCodeEl.textContent = title + tempEl.textContent;

    if (!decodeRunning) {
      clearInterval(checkInterval);

      setTimeout(() => {
        const flipButton = document.querySelector(".flip-button");
        if (flipButton) {
          flipButton.classList.add("visible");
        }
      }, 300);
    }
  }, 20);
}

/* Flip button handlers */
let flipButton = null;
let flipButtonFront = null;
let heroCodeInner = null;

function handleFlipToFront(e) {
  e.stopPropagation();

  if (flipButton) {
    flipButton.classList.remove("visible");
  }
  if (flipButtonFront) {
    flipButtonFront.classList.remove("visible");
  }

  const backCodeEl = document.querySelector(".hero-code-back code");
  if (backCodeEl) {
    backCodeEl.textContent = "";
  }

  if (heroCodeInner) {
    heroCodeInner.classList.add("flipped");
  }

  setTimeout(() => {
    const frontCodeEl = document.querySelector(".hero-code-front-text");
    if (frontCodeEl) {
      const title = "AI Dev Agent — Developer Productivity Loop (Target)\n\n";
      frontCodeEl.textContent = title;
    }

    setTimeout(() => {
      playFrontAnimationDecoding();
    }, 1000);
  }, 400);
}

function handleFlipToBack(e) {
  e.stopPropagation();

  if (flipButton) {
    flipButton.classList.remove("visible");
  }
  if (flipButtonFront) {
    flipButtonFront.classList.remove("visible");
  }

  const frontCodeEl = document.querySelector(".hero-code-front-text");
  if (frontCodeEl) {
    frontCodeEl.textContent = "";
  }

  if (heroCodeInner) {
    heroCodeInner.classList.remove("flipped");
  }

  setTimeout(() => {
    const backCodeEl = document.querySelector(".hero-code-back code");
    if (backCodeEl) {
      const title = "AI Dev Agent — Developer Productivity Loop (Current)\n\n";
      backCodeEl.textContent = title;
    }

    setTimeout(() => {
      playBackAnimationDecoding();
    }, 1000);
  }, 400);
}

function setupFlipCard() {
  flipButton = document.querySelector(".flip-button");
  flipButtonFront = document.querySelector(".flip-button-front");
  heroCodeInner = document.querySelector(".hero-code-inner");

  if (!flipButton || !flipButtonFront || !heroCodeInner) return;

  // Remove old listeners to prevent duplicates
  flipButton.removeEventListener("click", handleFlipToFront);
  flipButtonFront.removeEventListener("click", handleFlipToBack);

  // Add listeners
  flipButton.addEventListener("click", handleFlipToFront);
  flipButtonFront.addEventListener("click", handleFlipToBack);
}

function resetHeroAnimation() {
  const backCodeEl = document.querySelector(".hero-code-back code");
  const frontCodeEl = document.querySelector(".hero-code-front-text");
  const heroCodeInner = document.querySelector(".hero-code-inner");
  const flipButton = document.querySelector(".flip-button");
  const flipButtonFront = document.querySelector(".flip-button-front");

  if (backCodeEl) {
    heroPlayed = false;
    decodingFinished = false;
    decodeRunning = false;
    backCodeEl.textContent = "";
  }

  if (frontCodeEl) {
    frontDecoded = false;
    frontCodeEl.textContent = "";
  }

  if (heroCodeInner) {
    heroCodeInner.classList.remove("flipped");
  }

  if (flipButton) {
    flipButton.classList.remove("visible");
  }

  if (flipButtonFront) {
    flipButtonFront.classList.remove("visible");
  }
}

/* Auto-decode on scroll visibility */
let isFirstCardView = true;

function setupCardVisibilityObserver() {
  const card = document.querySelector(".hero-code");
  if (!card) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          // Only play animation on first view
          if (!heroPlayed && !hasPlayedOnce) {
            setTimeout(playHeroAnimation, 0);
            isFirstCardView = false;
          }
          // If animation has already played once, don't restart it
        } else {
          // Don't reset when scrolling away
          // This preserves the decoded state when returning
        }
      });
    },
    { threshold: 0.1 }, // Trigger when at least 10% is visible
  );

  observer.observe(card);
}

/* Main App Init */
function initApp() {
  /* Hide hero code text initially */
  const heroCodeEl = document.querySelector(".hero-code-back code");
  if (heroCodeEl) {
    heroCodeEl.textContent = ""; // Empty on load
  }

  const frontCodeEl = document.querySelector(".hero-code-front-text");
  if (frontCodeEl) {
    frontCodeEl.textContent = ""; // Empty on load
  }

  /* Setup flip card */
  setupFlipCard();

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

  // Setup auto-decode on scroll visibility
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
  