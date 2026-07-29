# Installation Guide

Install the tools needed to run GamerHive locally.

## Docker Desktop

Docker lets you run the entire stack (frontend, backend, database, cache) without installing Python or Node locally. **Recommended for first-time setup.**

### Download & Install

👉 **[Download Docker Desktop](https://www.docker.com/products/docker-desktop)**

Pick your OS (Mac, Windows, or Linux).

### Verify installation

After installing, open a terminal and run:

```bash
docker --version
docker compose --version
```

You should see version numbers (e.g., `Docker version 24.0.0`).

---

## Node.js (for frontend development)

Needed if you want to:
- Run the Next.js frontend without Docker
- Install frontend dependencies
- Modify frontend code

### Download & Install

👉 **[Download Node.js 20+ (LTS recommended)](https://nodejs.org/)**

Choose the LTS (Long Term Support) version.

### Verify installation

```bash
node --version
npm --version
```

You should see version numbers (e.g., `v20.11.0`).

---

## Python 3.12 (for backend development)

Needed if you want to:
- Run the Django backend without Docker
- Install backend dependencies
- Modify Django code or management commands

### Download & Install

👉 **[Download Python 3.12](https://www.python.org/downloads/)**

#### macOS (Homebrew)

If you use Homebrew:

```bash
brew install python@3.12
```

#### Windows

Run the installer from the link above. **Make sure to check "Add Python to PATH"** during installation.

#### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install python3.12 python3.12-venv
```

### Verify installation

```bash
python3.12 --version
```

You should see version `3.12.x`.

### Create a virtual environment

Always use a virtual environment to keep dependencies isolated:

```bash
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Your terminal prompt should now show `(venv)` at the start.

### Install backend dependencies

With your virtual environment activated:

```bash
pip install -r backend/requirements.txt
```

---

## Git

You likely already have Git, but if not:

👉 **[Download Git](https://git-scm.com/)**

Verify:

```bash
git --version
```

---

## Summary

| Tool | Purpose | Required? |
|------|---------|-----------|
| **Docker Desktop** | Run everything in containers | ✅ (recommended) |
| **Node.js 20+** | Run frontend locally | ❌ (if using Docker) |
| **Python 3.12** | Run backend locally | ❌ (if using Docker) |
| **Git** | Clone the repo | ✅ |

**Using Docker?** Just install Docker and Git. Docker handles the rest.

**Local development?** Install all four plus follow the [Local Development guide](./LOCAL_DEVELOPMENT.md).

---

[← Back to setup guide](./SETUP.md)
