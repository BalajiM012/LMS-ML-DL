// JavaScript for index.html functionality

// API endpoints - handle both file and server protocols
function getAPIBaseURL() {
  const protocol = window.location.protocol;
  const hostname = window.location.hostname;

  if (protocol === "file:") {
    // When running as file, use localhost:5000
    return "http://localhost:5000";
  } else {
    // When running from server, use current origin
    return window.location.origin;
  }
}

const API_BASE_URL = getAPIBaseURL();

// Check if API is available
async function checkAPIAvailability() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/health`, {
      method: "GET",
      mode: "cors",
      cache: "no-cache",
    });
    return response.ok;
  } catch (error) {
    console.log("API server not available, using demo data");
    return false;
  }
}

// Fetch library statistics with better error handling
async function fetchLibraryStats() {
  const apiAvailable = await checkAPIAvailability();

  if (!apiAvailable) {
    // Use demo data when API is not available
    console.log("Using demo data for statistics");
    updateStats({
      total_books: 1250,
      total_students: 340,
      books_issued: 89,
      available_books: 1161,
    });
    return;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/stats`, {
      method: "GET",
      mode: "cors",
      cache: "no-cache",
    });

    if (response.ok) {
      const data = await response.json();
      if (data.success) {
        updateStats(data.data);
      } else {
        throw new Error("API returned error");
      }
    } else {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
  } catch (error) {
    console.error("Error fetching stats:", error);
    // Fallback to demo data
    updateStats({
      total_books: 1250,
      total_students: 340,
      books_issued: 89,
      available_books: 1161,
    });
  }
}

// Update statistics on the page
function updateStats(data) {
  const elements = {
    "total-books": data.total_books || 0,
    "total-students": data.total_students || 0,
    "books-issued": data.books_issued || 0,
    "available-books": data.available_books || 0,
  };

  Object.entries(elements).forEach(([id, value]) => {
    const element = document.getElementById(id);
    if (element) {
      animateNumber(element, 0, value, 2000);
    }
  });
}

// Animate number counting
function animateNumber(element, start, end, duration) {
  const startTime = performance.now();
  const difference = end - start;

  function updateNumber(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);

    // Easing function for smooth animation
    const easeOutQuart = 1 - Math.pow(1 - progress, 4);
    const current = Math.floor(start + difference * easeOutQuart);

    element.textContent = current.toLocaleString();

    if (progress < 1) {
      requestAnimationFrame(updateNumber);
    }
  }

  requestAnimationFrame(updateNumber);
}

// Smooth scrolling for navigation links
function setupSmoothScrolling() {
  const links = document.querySelectorAll('a[href^="#"]');

  links.forEach((link) => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      const targetId = link.getAttribute("href").substring(1);
      const targetElement = document.getElementById(targetId);

      if (targetElement) {
        targetElement.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      }
    });
  });
}

// Initialize the page
document.addEventListener("DOMContentLoaded", () => {
  fetchLibraryStats();
  setupSmoothScrolling();

  // Add loading animation
  document.body.classList.add("loaded");
});

// Add some interactive features
document.addEventListener("DOMContentLoaded", () => {
  // Add hover effects to feature cards
  const featureCards = document.querySelectorAll(".feature-card");
  featureCards.forEach((card) => {
    card.addEventListener("mouseenter", () => {
      card.style.transform = "translateY(-5px) scale(1.02)";
    });

    card.addEventListener("mouseleave", () => {
      card.style.transform = "translateY(0) scale(1)";
    });
  });

  // Add intersection observer for animations
  const observerOptions = {
    threshold: 0.1,
    rootMargin: "0px 0px -50px 0px",
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("animate-in");
      }
    });
  }, observerOptions);

  // Observe elements for animation
  document.querySelectorAll(".feature-card, .stat-card").forEach((el) => {
    observer.observe(el);
  });
});

// Utility functions
function formatNumber(num) {
  return num.toLocaleString();
}

function showNotification(message, type = "info") {
  // Create notification element
  const notification = document.createElement("div");
  notification.className = `notification notification-${type}`;
  notification.textContent = message;

  // Add styles
  Object.assign(notification.style, {
    position: "fixed",
    top: "20px",
    right: "20px",
    padding: "1rem 2rem",
    borderRadius: "4px",
    color: "white",
    fontWeight: "bold",
    zIndex: "1000",
    transform: "translateX(100%)",
    transition: "transform 0.3s ease",
  });

  // Set background color based on type
  const colors = {
    info: "#2563eb",
    success: "#10b981",
    warning: "#f59e0b",
    error: "#ef4444",
  };
  notification.style.backgroundColor = colors[type] || colors.info;

  document.body.appendChild(notification);

  // Animate in
  setTimeout(() => {
    notification.style.transform = "translateX(0)";
  }, 100);

  // Remove after 3 seconds
  setTimeout(() => {
    notification.style.transform = "translateX(100%)";
    setTimeout(() => {
      document.body.removeChild(notification);
    }, 300);
  }, 3000);
}
