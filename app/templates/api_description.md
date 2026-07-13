A REST API for managing personal tasks and daily habits.

### Features

- **Auth** — Register, login, and access protected routes with JWT tokens
- **Tasks** — Create, read, update, delete, and search tasks by title
- **Habits** — Create habits, check in daily, and view streak statistics

### Authentication

Most endpoints require a Bearer token. Register via `POST /auth/register`, then login
via `POST /auth/login` (form data: `username`, `password`) to receive an access token.

Use the token in requests: `Authorization: Bearer <token>`

---

Created by **{{created_by}}** · [GitHub repo]({{github_url}})
