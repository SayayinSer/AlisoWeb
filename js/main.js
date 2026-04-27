/* ============================================
   ALISO WEB SOLUTION — main.js
   ============================================ */

// ── CONFIG ──
const API_BASE = 'http://localhost:8001/api';

// ══════════════════════════════
// HEADER SCROLL EFFECT
// ══════════════════════════════
const header = document.getElementById('header');
window.addEventListener('scroll', () => {
  header.classList.toggle('scrolled', window.scrollY > 60);
});

// ══════════════════════════════
// MOBILE NAV TOGGLE
// ══════════════════════════════
const hamburger = document.getElementById('navHamburger');
const navLinks = document.getElementById('navLinks');

hamburger.addEventListener('click', () => {
  hamburger.classList.toggle('active');
  navLinks.classList.toggle('open');
  document.body.style.overflow = navLinks.classList.contains('open') ? 'hidden' : '';
});

// Close mobile nav on link click
navLinks.querySelectorAll('.nav__link').forEach(link => {
  link.addEventListener('click', () => {
    hamburger.classList.remove('active');
    navLinks.classList.remove('open');
    document.body.style.overflow = '';
  });
});

// ══════════════════════════════
// DARK MODE TOGGLE
// ══════════════════════════════
const themeToggle = document.getElementById('themeToggle');
const prefersDark = localStorage.getItem('theme') === 'dark' ||
  (!localStorage.getItem('theme') && window.matchMedia('(prefers-color-scheme: dark)').matches);

if (prefersDark) {
  document.documentElement.classList.add('dark');
  themeToggle.textContent = '☀️';
}

themeToggle.addEventListener('click', () => {
  const isDark = document.documentElement.classList.toggle('dark');
  themeToggle.textContent = isDark ? '☀️' : '🌙';
  localStorage.setItem('theme', isDark ? 'dark' : 'light');
});

// ══════════════════════════════
// REVEAL ON SCROLL (IntersectionObserver)
// ══════════════════════════════
const revealElements = document.querySelectorAll('.reveal');
const revealObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      revealObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

revealElements.forEach(el => revealObserver.observe(el));

// ══════════════════════════════
// TESTIMONIALS SLIDER
// ══════════════════════════════
const track = document.getElementById('testimonialsTrack');
const navBtns = document.querySelectorAll('#testimonialsNav button');
let currentSlide = 0;

function goToSlide(index) {
  currentSlide = index;
  track.style.transform = `translateX(-${index * 100}%)`;
  navBtns.forEach((btn, i) => btn.classList.toggle('active', i === index));
}

navBtns.forEach(btn => {
  btn.addEventListener('click', () => goToSlide(parseInt(btn.dataset.index)));
});

// Auto-advance
setInterval(() => {
  goToSlide((currentSlide + 1) % navBtns.length);
}, 6000);

// ══════════════════════════════
// FAQ ACCORDION
// ══════════════════════════════
document.querySelectorAll('.faq-item__question').forEach(btn => {
  btn.addEventListener('click', () => {
    const item = btn.parentElement;
    const wasOpen = item.classList.contains('open');
    // Close all
    document.querySelectorAll('.faq-item').forEach(i => i.classList.remove('open'));
    // Toggle current
    if (!wasOpen) item.classList.add('open');
  });
});

// ══════════════════════════════
// CONTACT FORM — sends to FastAPI
// ══════════════════════════════
const contactForm = document.getElementById('contactForm');
const formFields = document.getElementById('formFields');
const formSuccess = document.getElementById('formSuccess');

contactForm.addEventListener('submit', async (e) => {
  e.preventDefault();

  // Validate
  let hasError = false;
  contactForm.querySelectorAll('[required]').forEach(field => {
    const group = field.closest('.form-group');
    if (!field.value.trim()) {
      group.classList.add('error');
      hasError = true;
    } else {
      group.classList.remove('error');
    }
  });

  // Email validation
  const emailField = document.getElementById('email');
  const emailGroup = emailField.closest('.form-group');
  if (emailField.value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailField.value)) {
    emailGroup.classList.add('error');
    hasError = true;
  }

  if (hasError) return;

  // Collect data
  const data = {
    nombre: document.getElementById('nombre').value.trim(),
    apellido: document.getElementById('apellido').value.trim(),
    email: document.getElementById('email').value.trim(),
    empresa: document.getElementById('empresa').value.trim(),
    servicio: document.getElementById('servicio').value,
    mensaje: document.getElementById('mensaje').value.trim(),
  };

  try {
    const submitBtn = contactForm.querySelector('button[type="submit"]');
    submitBtn.textContent = 'Enviando...';
    submitBtn.disabled = true;

    const response = await fetch(`${API_BASE}/contact`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    if (response.ok) {
      formFields.style.display = 'none';
      formSuccess.classList.add('show');
    } else {
      const err = await response.json();
      alert('Error al enviar: ' + (err.detail || 'Intente nuevamente'));
      submitBtn.textContent = 'Enviar Mensaje →';
      submitBtn.disabled = false;
    }
  } catch (error) {
    alert('No se pudo conectar con el servidor. Verifique que el backend esté en ejecución.');
    const submitBtn = contactForm.querySelector('button[type="submit"]');
    submitBtn.textContent = 'Enviar Mensaje →';
    submitBtn.disabled = false;
  }
});

// Clear error on input and add success state
contactForm.querySelectorAll('input, textarea, select').forEach(field => {
  field.addEventListener('input', () => {
    const group = field.closest('.form-group');
    group.classList.remove('error');
    
    // Simple real-time feedback
    if (field.hasAttribute('required') && field.value.trim().length > 0) {
      let isValid = true;
      if (field.type === 'email') {
        isValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(field.value);
      }
      
      if (isValid) {
        group.classList.add('success');
      } else {
        group.classList.remove('success');
      }
    } else {
      group.classList.remove('success');
    }
  });
});

// ══════════════════════════════
// SMOOTH SCROLL for anchor links
// ══════════════════════════════
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', (e) => {
    const target = document.querySelector(anchor.getAttribute('href'));
    if (target) {
      e.preventDefault();
      const headerHeight = header.offsetHeight;
      const targetPos = target.getBoundingClientRect().top + window.scrollY - headerHeight - 20;
      window.scrollTo({ top: targetPos, behavior: 'smooth' });
    }
  });
});
