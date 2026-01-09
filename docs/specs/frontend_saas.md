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
* **Migration Path:** MVP uses PostgreSQL. Architecture must use an ORM (SQLModel/SQLAlchemy) to allow seamless portability across supported relational backends without code changes.

### Plugin Navigation (Workspace)
* **Sidebar:** The left navigation MUST list enabled plugins for the active workspace.
* **Routing:** Each plugin entry MUST link to `/plugins/{plugin_id}`.
* **Placeholders:** Plugin pages MAY render placeholder content until plugin-specific UI is implemented.
