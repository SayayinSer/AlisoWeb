# AI Agent Orchestration & Workspace Rules - AlisoWeb (Entorno03)

Este documento define la capa de orquestación de inteligencia artificial y reglas operativas para el proyecto **AlisoWeb** ("Aliso Soluciones") dentro del ecosistema multi-agente.

---

## 1. Misión del Proyecto y Arquitectura Técnica
**AlisoWeb** es el portal web corporativo para **Aliso Soluciones** (Consultoría especializada en GeneXus 18, Enterprise AI y modernización de software).

- **Frontend**: Single Page Application corporativa en HTML5 semántico, CSS3 moderno (Variables/Tokens, Responsive, Glassmorphism, Dark/Light Mode) y Vanilla JS.
- **Backend API**: FastAPI (Python 3.10+/3.14), SQLAlchemy 2.0, Pydantic v2, SQLAdmin para gestión de contenidos.
- **Base de Datos**: MySQL / MariaDB (con soporte para SQLite en desarrollo/testing).
- **Despliegue Objetivo**: Servidores estándar / Hosting compartido con cPanel vía CloudLinux y Passenger WSGI (`passenger_wsgi.py`), o servidores LAMP/Docker.

---

## 2. Mapa de SKILLs Prioritarias para Entorno03
El entorno cuenta con las **92 Skills** del catálogo maestro en `.agents/skills/`. Para este proyecto rigen con máxima prioridad:

| Especialidad | Skills Principales | Rol del Agente |
| :--- | :--- | :--- |
| **Frontend Moderno & UI/UX** | `frontend-moderno`, `frontend-design` | Lead Frontend Engineer (Estética visual superior, accesibilidad, micro-animaciones, SEO) |
| **APIs Backend (Python)** | `fastapi-expert`, `fullstack-python-app` | Senior Backend Engineer (FastAPI, Lifespan, Pydantic v2, Async) |
| **Bases de Datos Relacionales** | `sql-expert`, `convert-ia-db-snapshot` | Database Specialist (MySQL/MariaDB DDL, consultas optimizadas, índices) |
| **Hosting & Servidores Estándar** | `lamp-expert`, `lamp-web-deployer`, `infra-deploy-manager` | Deployment & Web Server Specialist (cPanel, Apache, Nginx, Passenger WSGI) |
| **DevOps & Automatización** | `devops-expert` | Automation & CI/CD Packaging Specialist |
| **Testing & Calidad** | `convert-ia-characterization-tester`, `agentic-looping-engineering` | QA & Verification Engineer (Pytest, End-to-End browser checks) |
| **Gobernanza & Contexto** | `software-architect-expert`, `project-context-vault` | Master Architect & Context Manager |

---

## 3. Reglas de Desarrollo y Calidad
1. **Estética y Experiencia Visual**: El diseño debe verse prémium, sobrio y alineado al Manual de Marca ALISO (paleta verde #6AA439, verde oscuro #316234, rojo corporativo #A11129, tipografía Plus Jakarta Sans). No usar `alert()` para notificaciones de usuario.
2. **Estándares Backend**:
   - Pydantic v2 estricto usando `ConfigDict(from_attributes=True)`.
   - Gestor asíncrono moderno `lifespan(app: FastAPI)` para eventos de inicio/apagado.
   - Manejo de fechas UTC mediante `datetime.now(timezone.utc)`.
   - Compatibilidad de despliegue con Passenger WSGI (`passenger_wsgi.py`).
3. **Validación Determinística**:
   - Todo cambio en backend debe pasar la suite de pruebas unitarias (`pytest`).
   - Todo cambio en frontend debe verificarse en el navegador con 0 errores de consola.
