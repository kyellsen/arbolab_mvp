# SaaS Frontend & Architecture Specs

## UI/UX Requirements (SaaS Layer)

### Responsive Design Strategy
The frontend must follow a **Mobile-First** approach using Tailwind CSS breakpoints.
* **Mobile (Default):** Single-column layouts, stacked elements, hamburger menus, large touch targets (min 44px height).
* **Desktop (`md:` and up):** Sidebar navigation, grid layouts, dense data tables.
* **Goal:** The application must be fully functional on a tablet/smartphone in the field (data collection) and on a desktop in the office (report generation).

### User Management & Workspace Mapping
* **SaaS Database (OLTP):** Stores Users, Credentials (Hashed), and Project-Permissions.
* **Separation:** This database is strictly separated from the Domain Data (DuckDB).
* **Migration Path:** MVP uses SQLite (`saas.db`). Architecture must use an ORM (SQLModel/SQLAlchemy) to allow seamless switch to PostgreSQL later without code changes.
