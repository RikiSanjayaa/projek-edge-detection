# Docker Deployment Guide

Panduan untuk deploy Coin Classification menggunakan Docker.

## Prerequisites

- Docker & Docker Compose
- Node.js 18+ (untuk build frontend)
- Git

---

## Quick Start (Local)

```bash
# 1. Clone repository
git clone https://github.com/RikiSanjayaa/projek-edge-detection.git
cd projek-edge-detection

# 2. Build frontend
cd web
cp .env.docker .env
npm install
npm run build
cd ..

# 3. Start containers
docker compose up -d

# 4. Akses di browser
# http://localhost:3000
```

---

## Server/VPS Deployment

### Minimum Requirements

| Resource | Minimum             | Recommended |
| -------- | ------------------- | ----------- |
| **CPU**  | 1 vCPU (dengan AVX) | 2 vCPU      |
| **RAM**  | 2 GB                | 4 GB        |
| **Disk** | 25 GB               | 50 GB       |

> ⚠️ **Penting**: Server harus support **AVX instructions** untuk TensorFlow.
> VM tanpa AVX (seperti beberapa home server/Proxmox) tidak akan bisa menjalankan TensorFlow.

### Step-by-Step Deployment

#### 1. Setup Server

```bash
# SSH ke server
ssh root@YOUR_SERVER_IP

# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh

# Install Docker Compose plugin
apt install docker-compose-plugin -y

# Verify installation
docker --version
docker compose version
```

#### 2. Install Node.js (untuk build frontend)

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs

# Verify
node --version
npm --version
```

#### 3. Clone & Setup Project

```bash
# Clone repository
git clone https://github.com/RikiSanjayaa/projek-edge-detection.git
cd projek-edge-detection

# Build frontend dengan Docker environment
cd web
cp .env.docker .env
npm install
npm run build
cd ..

# jalankan semua file notebook untuk mendapatkan models, atau copy paste ke folder /models
```

#### 4. Configure Ports (Optional)

Edit `docker-compose.yml` jika port default sudah dipakai:

```yaml
services:
  api:
    ports:
      - "8002:8000" # Ubah 8000 ke port lain
  web:
    ports:
      - "80:80" # Ubah 3000 ke 80 untuk akses tanpa port
```

#### 5. Start Containers

```bash
# Build dan start
docker compose up -d

# Cek status
docker compose ps

# Lihat logs
docker compose logs -f
```

#### 6. Verify

```bash
# Test API health
curl http://localhost:8000/health

# Test via nginx proxy
curl http://localhost:3000/api/health
```

Akses web app di: `http://YOUR_SERVER_IP:3000`

---

## Docker Commands Reference

| Command                           | Description                         |
| --------------------------------- | ----------------------------------- |
| `docker compose up -d`            | Start semua containers (background) |
| `docker compose down`             | Stop dan remove containers          |
| `docker compose restart`          | Restart semua containers            |
| `docker compose restart api`      | Restart API saja                    |
| `docker compose logs -f`          | Lihat logs (real-time)              |
| `docker compose logs -f api`      | Lihat logs API saja                 |
| `docker compose ps`               | Lihat status containers             |
| `docker compose build --no-cache` | Rebuild image dari awal             |
| `docker compose up -d --build`    | Rebuild dan start                   |

---

## Architecture

```
Browser → :3000 (nginx)
              │
              ├── /        → React frontend (static files)
              │
              └── /api/*   → proxy to FastAPI (:8000)
                               │
                               ├── /health
                               └── /predict
```

### Containers

| Container  | Image                        | Port    | Description                        |
| ---------- | ---------------------------- | ------- | ---------------------------------- |
| `coin-api` | Custom (Python + TensorFlow) | 8000    | FastAPI backend                    |
| `coin-web` | nginx:alpine                 | 3000→80 | Static file server + reverse proxy |

---

## Configuration

### Environment Variables

#### API Container

| Variable       | Default   | Description          |
| -------------- | --------- | -------------------- |
| `HOST`         | `0.0.0.0` | Server bind address  |
| `PORT`         | `8000`    | Server port          |
| `CORS_ORIGINS` | `*`       | Allowed CORS origins |

#### Web Container

Frontend menggunakan `/api` sebagai base URL (di-proxy oleh nginx).

File: `web/.env.docker`

```env
VITE_API_URL=/api
```

### Custom CORS

Jika perlu restrict CORS:

```yaml
# docker-compose.yml
services:
  api:
    environment:
      - CORS_ORIGINS=http://localhost:3000,http://YOUR_DOMAIN.com
```

---
