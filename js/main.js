
// ── FETCH DYNAMIC VERTICAL APPS ──
async function loadVerticalApps() {
  const container = document.getElementById('appsGrid');
  if (!container) return;

  try {
    const res = await fetch(`${API_BASE}/vertical-apps`);
    if (res.ok) {
      const apps = await res.json();
      if (Array.isArray(apps) && apps.length > 0) {
        container.innerHTML = '';
        apps.forEach((app, i) => {
          const badgeClass = app.badge.includes('Clientes') ? 'app-card__badge--clients' :
                             app.badge.includes('Beta') ? 'app-card__badge--beta' : '';
          
          const card = document.createElement('article');
          card.className = `app-card reveal reveal-delay-${(i % 4) + 1} visible`;
          card.innerHTML = `
            <div class="app-card__header">
              <span class="app-card__icon">${app.icono || '⚡'}</span>
              <span class="app-card__badge ${badgeClass}">${app.badge}</span>
            </div>
            <h3 class="app-card__title">${app.nombre}</h3>
            <span class="app-card__cat">${app.categoria}</span>
            <p class="app-card__desc">${app.descripcion}</p>
            <a href="${app.subdominio_url}" target="_blank" rel="noopener" class="app-card__btn">Ingresar a la Plataforma ↗</a>
          `;
          container.appendChild(card);
        });
      }
    }
  } catch (err) {
    console.debug("Soluciones verticales dinámicas no disponibles, usando tarjetas base.", err);
  }
}
/* ============================================
   ALISO WEB SOLUTION — main.js
   Modernizado con Sistema Toast y API Backend
   ============================================ */

// ── CONFIG ──
const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' || window.location.protocol === 'file:';
const API_BASE = isLocal ? 'http://127.0.0.1:8001/api' : '/api';

// ── TOAST NOTIFICATION UTILITY ──
function showToast(message, type = 'success', duration = 4000) {
  const container = document.getElementById('toastContainer');
  if (!container) return;

  const icons = {
    success: '✅',
    error: '❌',
    info: 'ℹ️',
    warning: '⚠️'
  };

  const toast = document.createElement('div');
  toast.className = `toast toast--${type}`;
  toast.innerHTML = `<span>${icons[type] || 'ℹ️'}</span><span>${message}</span>`;
  container.appendChild(toast);

  // Trigger animation
  requestAnimationFrame(() => {
    toast.classList.add('show');
  });

  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

// ── FETCH DYNAMIC SETTINGS ──
async function loadSettings() {
  try {
    const res = await fetch(`${API_BASE}/settings`);
    if (res.ok) {
      const data = await res.json();
      document.querySelectorAll('[data-setting]').forEach(el => {
        const key = el.getAttribute('data-setting');
        if (data[key]) {
          el.textContent = data[key];
          if (el.tagName === 'A' && el.getAttribute('href')?.startsWith('mailto:')) {
            el.href = 'mailto:' + data[key];
          } else if (el.tagName === 'A' && el.getAttribute('href')?.startsWith('tel:')) {
            el.href = 'tel:' + data[key];
          }
        }
      });
    }
  } catch (error) {
    console.debug("Configuraciones dinámicas no cargadas (modo estático).", error);
  }
}

// ── FETCH DYNAMIC TESTIMONIALS ──
async function loadDynamicTestimonials() {
  try {
    const res = await fetch(`${API_BASE}/testimonials`);
    if (res.ok) {
      const items = await res.json();
      if (Array.isArray(items) && items.length > 0) {
        const track = document.getElementById('testimonialsTrack');
        const nav = document.getElementById('testimonialsNav');
        if (!track || !nav) return;

        track.innerHTML = '';
        nav.innerHTML = '';

        items.forEach((t, i) => {
          const initials = t.cliente.split(' ').map(w => w[0]).join('').substring(0, 2).toUpperCase();
          const card = document.createElement('div');
          card.className = 'testimonial-card';
          card.innerHTML = `
            <p class="testimonial-card__quote">"${t.comentario}"</p>
            <div class="testimonial-card__author">
              <div class="testimonial-card__avatar">${initials}</div>
              <div>
                <div class="testimonial-card__name">${t.cliente}</div>
                <div class="testimonial-card__role">${t.empresa_puesto || 'Cliente Corporativo'}</div>
              </div>
            </div>
          `;
          track.appendChild(card);

          const dot = document.createElement('button');
          dot.dataset.index = i;
          dot.setAttribute('aria-label', `Testimonio ${i + 1}`);
          if (i === 0) dot.classList.add('active');
          dot.addEventListener('click', () => goToSlide(i));
          nav.appendChild(dot);
        });
      }
    }
  } catch (err) {
    console.debug("Testimonios dinámicos no disponibles, usando base estática.", err);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  loadSettings();
  loadDynamicTestimonials();
});

// ══════════════════════════════
// HEADER SCROLL EFFECT
// ══════════════════════════════
const header = document.getElementById('header');
if (header) {
  window.addEventListener('scroll', () => {
    header.classList.toggle('scrolled', window.scrollY > 60);
  });
}

// ══════════════════════════════
// MOBILE NAV TOGGLE
// ══════════════════════════════
const hamburger = document.getElementById('navHamburger');
const navLinks = document.getElementById('navLinks');

if (hamburger && navLinks) {
  hamburger.addEventListener('click', () => {
    hamburger.classList.toggle('active');
    navLinks.classList.toggle('open');
    document.body.style.overflow = navLinks.classList.contains('open') ? 'hidden' : '';
  });

  navLinks.querySelectorAll('.nav__link').forEach(link => {
    link.addEventListener('click', () => {
      hamburger.classList.remove('active');
      navLinks.classList.remove('open');
      document.body.style.overflow = '';
    });
  });
}

// ══════════════════════════════
// DARK MODE TOGGLE
// ══════════════════════════════
const themeToggle = document.getElementById('themeToggle');
if (themeToggle) {
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
}

// ══════════════════════════════
// REVEAL ON SCROLL
// ══════════════════════════════
const revealElements = document.querySelectorAll('.reveal');
if (revealElements.length > 0) {
  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        revealObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

  revealElements.forEach(el => revealObserver.observe(el));
}

// ══════════════════════════════
// TESTIMONIALS SLIDER
// ══════════════════════════════
const track = document.getElementById('testimonialsTrack');
let currentSlide = 0;

function goToSlide(index) {
  const navBtns = document.querySelectorAll('#testimonialsNav button');
  if (!track || navBtns.length === 0) return;
  currentSlide = index;
  track.style.transform = `translateX(-${index * 100}%)`;
  navBtns.forEach((btn, i) => btn.classList.toggle('active', i === index));
}

const navBtns = document.querySelectorAll('#testimonialsNav button');
navBtns.forEach(btn => {
  btn.addEventListener('click', () => goToSlide(parseInt(btn.dataset.index)));
});

setInterval(() => {
  const navBtns = document.querySelectorAll('#testimonialsNav button');
  if (navBtns.length > 1) {
    goToSlide((currentSlide + 1) % navBtns.length);
  }
}, 6000);

// ══════════════════════════════
// FAQ ACCORDION
// ══════════════════════════════
document.querySelectorAll('.faq-item__question').forEach(btn => {
  btn.addEventListener('click', () => {
    const item = btn.parentElement;
    const wasOpen = item.classList.contains('open');
    document.querySelectorAll('.faq-item').forEach(i => i.classList.remove('open'));
    if (!wasOpen) item.classList.add('open');
  });
});

// ══════════════════════════════
// CONTACT FORM
// ══════════════════════════════
const contactForm = document.getElementById('contactForm');
const formFields = document.getElementById('formFields');
const formSuccess = document.getElementById('formSuccess');

if (contactForm) {
  contactForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    let hasError = false;
    contactForm.querySelectorAll('[required]').forEach(field => {
      const group = field.closest('.form-group');
      if (!field.value.trim()) {
        group?.classList.add('error');
        hasError = true;
      } else {
        group?.classList.remove('error');
      }
    });

    const emailField = document.getElementById('email');
    const emailGroup = emailField ? emailField.closest('.form-group') : null;
    if (emailField && emailField.value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailField.value)) {
      emailGroup?.classList.add('error');
      hasError = true;
    }

    if (hasError) {
      showToast('Por favor, revise los campos requeridos.', 'error');
      return;
    }

    const data = {
      nombre: document.getElementById('nombre').value.trim(),
      apellido: document.getElementById('apellido').value.trim(),
      email: document.getElementById('email').value.trim(),
      empresa: document.getElementById('empresa').value.trim(),
      servicio: document.getElementById('servicio').value,
      mensaje: document.getElementById('mensaje').value.trim(),
    };

    const submitBtn = contactForm.querySelector('button[type="submit"]');
    const originalBtnText = submitBtn.textContent;
    submitBtn.textContent = 'Enviando...';
    submitBtn.disabled = true;

    try {
      const response = await fetch(`${API_BASE}/contact`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });

      if (response.ok) {
        if (formFields) formFields.style.display = 'none';
        if (formSuccess) formSuccess.classList.add('show');
        showToast('¡Mensaje enviado con éxito! Nos comunicaremos en breve.', 'success');
      } else {
        const err = await response.json().catch(() => ({ detail: 'Error en el servidor.' }));
        showToast(err.detail || 'Error al enviar mensaje.', 'error');
        submitBtn.textContent = originalBtnText;
        submitBtn.disabled = false;
      }
    } catch (error) {
      showToast('No se pudo conectar con el servidor. Intente nuevamente más tarde.', 'error');
      submitBtn.textContent = originalBtnText;
      submitBtn.disabled = false;
    }
  });

  contactForm.querySelectorAll('input, textarea, select').forEach(field => {
    field.addEventListener('input', () => {
      const group = field.closest('.form-group');
      group?.classList.remove('error');
      if (field.hasAttribute('required') && field.value.trim().length > 0) {
        let isValid = true;
        if (field.type === 'email') {
          isValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(field.value);
        }
        if (isValid) {
          group?.classList.add('success');
        } else {
          group?.classList.remove('success');
        }
      } else {
        group?.classList.remove('success');
      }
    });
  });
}

// ══════════════════════════════
// NEWSLETTER SUBSCRIPTION
// ══════════════════════════════
const newsletterForm = document.getElementById('newsletterForm');
if (newsletterForm) {
  newsletterForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const input = document.getElementById('newsletterEmail');
    const btn = document.getElementById('newsletterSubmitBtn');
    if (!input || !input.value) return;

    const email = input.value.trim();
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      showToast('Ingrese un correo electrónico válido.', 'error');
      return;
    }

    const originalText = btn.textContent;
    btn.textContent = 'Enviando...';
    btn.disabled = true;

    try {
      const res = await fetch(`${API_BASE}/newsletter`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      });

      if (res.status === 201) {
        showToast('¡Gracias por suscribirse a nuestro radar tecnológico!', 'success');
        input.value = '';
      } else if (res.status === 409) {
        showToast('Este correo ya se encuentra registrado en el newsletter.', 'info');
      } else {
        const err = await res.json().catch(() => ({ detail: 'Error al procesar la solicitud.' }));
        showToast(err.detail || 'Ocurrió un error inesperado.', 'error');
      }
    } catch (err) {
      showToast('Error de conexión con el servidor. Intente más tarde.', 'error');
    } finally {
      btn.textContent = originalText;
      btn.disabled = false;
    }
  });
}

// ══════════════════════════════
// SMOOTH SCROLL
// ══════════════════════════════
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', (e) => {
    const href = anchor.getAttribute('href');
    if (!href || href === '#') return;
    const target = document.querySelector(href);
    if (target) {
      e.preventDefault();
      const headerHeight = header ? header.offsetHeight : 80;
      const targetPos = target.getBoundingClientRect().top + window.scrollY - headerHeight - 20;
      window.scrollTo({ top: targetPos, behavior: 'smooth' });
    }
  });
});

