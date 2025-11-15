# Docker Setup Guide - AI Trading System

## Overview

This guide explains how to run the complete AI Trading System using Docker Compose, including:
- PostgreSQL database
- Redis cache
- FastAPI backend (trading application)
- Streamlit frontend (dashboard)

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                 AI Trading Network                       │
│                                                          │
│  ┌──────────┐  ┌─────────┐  ┌──────────┐  ┌──────────┐│
│  │PostgreSQL│  │  Redis  │  │ FastAPI  │  │Streamlit ││
│  │   :5432  │  │  :6379  │  │  :8000   │  │  :8501   ││
│  └──────────┘  └─────────┘  └──────────┘  └──────────┘│
│       │             │             │              │      │
│       └─────────────┴─────────────┴──────────────┘      │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Services

### 1. PostgreSQL (Database)
- **Container**: `ai_trading_postgres`
- **Port**: `5432`
- **Image**: `postgres:15-alpine`
- **Credentials**:
  - User: `username`
  - Password: `password`
  - Database: `ai_trading`

### 2. Redis (Cache)
- **Container**: `ai_trading_redis`
- **Port**: `6379`
- **Image**: `redis:7-alpine`

### 3. FastAPI Backend (Trading App)
- **Container**: `ai_trading_app`
- **Port**: `8000`
- **Dockerfile**: `Dockerfile`
- **Features**:
  - Trading logic and strategies
  - Market data management
  - LLM integration
  - API endpoints

### 4. Streamlit Frontend (Dashboard)
- **Container**: `ai_trading_frontend`
- **Port**: `8501`
- **Dockerfile**: `Dockerfile.frontend`
- **Features**:
  - Portfolio visualization
  - Multi-asset performance charts
  - Trading history
  - LLM decision tracking
  - System controls

## Quick Start

### Prerequisites

- Docker Desktop installed
- Docker Compose v2.0+
- `.env` file with required API keys

### 1. Clone and Navigate

```bash
cd /Users/aayushkaayushumar/Desktop/ai-trading-agent-indian-market
```

### 2. Build and Start All Services

```bash
docker-compose up --build -d
```

This will:
1. Build the backend application
2. Build the frontend dashboard
3. Start PostgreSQL and Redis
4. Wait for databases to be healthy
5. Start the backend API
6. Start the frontend dashboard

### 3. Access the Services

- **Frontend Dashboard**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

### 4. Check Service Status

```bash
# View all running containers
docker-compose ps

# View logs from all services
docker-compose logs -f

# View logs from specific service
docker-compose logs -f frontend
docker-compose logs -f app
```

## Service Details

### Frontend Configuration

The Streamlit dashboard automatically connects to the backend using the internal Docker network:

- **Environment Variable**: `API_BASE_URL=http://app:8000`
- **Auto-refresh**: Every 30 seconds
- **Port**: 8501 (external and internal)

### Backend Configuration

The FastAPI backend connects to PostgreSQL and Redis:

- **Database URL**: `postgresql://username:password@postgres:5432/ai_trading`
- **Redis URL**: `redis://redis:6379/0`
- **Port**: 8000

### Network Configuration

All services run on the same Docker network: `ai_trading_network`

This allows services to communicate using container names:
- Frontend → Backend: `http://app:8000`
- Backend → PostgreSQL: `postgres:5432`
- Backend → Redis: `redis:6379`

## Common Commands

### Start Services

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d frontend

# Start with logs visible
docker-compose up
```

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v

# Stop specific service
docker-compose stop frontend
```

### View Logs

```bash
# All services
docker-compose logs -f

# Frontend only
docker-compose logs -f frontend

# Backend only
docker-compose logs -f app

# Last 100 lines
docker-compose logs --tail=100 frontend
```

### Rebuild Services

```bash
# Rebuild all services
docker-compose build

# Rebuild specific service
docker-compose build frontend

# Rebuild and restart
docker-compose up --build -d
```

### Execute Commands in Containers

```bash
# Access backend container shell
docker exec -it ai_trading_app bash

# Access PostgreSQL
docker exec -it ai_trading_postgres psql -U username -d ai_trading

# Access Redis CLI
docker exec -it ai_trading_redis redis-cli
```

## Health Checks

All services include health checks:

### PostgreSQL
- **Check**: `pg_isready -U username -d ai_trading`
- **Interval**: 5s
- **Retries**: 5

### Redis
- **Check**: `redis-cli ping`
- **Interval**: 5s
- **Retries**: 5

### Frontend
- **Check**: `curl -f http://localhost:8501/_stcore/health`
- **Interval**: 30s
- **Start Period**: 10s

## Troubleshooting

### Frontend Can't Connect to Backend

**Problem**: Dashboard shows "Unable to connect to backend"

**Solutions**:
1. Check if backend is running:
   ```bash
   docker-compose ps app
   ```

2. Check backend logs:
   ```bash
   docker-compose logs app
   ```

3. Verify backend health:
   ```bash
   curl http://localhost:8000/api/health
   ```

### Database Connection Issues

**Problem**: Backend can't connect to PostgreSQL

**Solutions**:
1. Check PostgreSQL is healthy:
   ```bash
   docker-compose ps postgres
   ```

2. View PostgreSQL logs:
   ```bash
   docker-compose logs postgres
   ```

3. Manually test connection:
   ```bash
   docker exec -it ai_trading_postgres pg_isready -U username
   ```

### Port Already in Use

**Problem**: Error: "Port 8501 is already allocated"

**Solutions**:
1. Find process using the port:
   ```bash
   lsof -i :8501
   ```

2. Kill the process or change port in `docker-compose.yml`:
   ```yaml
   ports:
     - "8502:8501"  # Change external port
   ```

### Container Keeps Restarting

**Problem**: Service constantly restarts

**Solutions**:
1. Check logs for errors:
   ```bash
   docker-compose logs frontend
   ```

2. Check health status:
   ```bash
   docker inspect ai_trading_frontend | grep -A 10 Health
   ```

3. Disable restart policy temporarily:
   ```yaml
   restart: "no"
   ```

## Data Persistence

### Volumes

Data is persisted in Docker volumes:

- `postgres_data`: PostgreSQL database files
- `redis_data`: Redis cache files

### Backup Database

```bash
# Backup PostgreSQL
docker exec ai_trading_postgres pg_dump -U username ai_trading > backup.sql

# Restore PostgreSQL
cat backup.sql | docker exec -i ai_trading_postgres psql -U username -d ai_trading
```

### Reset Data

```bash
# WARNING: This deletes all data!
docker-compose down -v
docker-compose up -d
```

## Environment Variables

### Required in `.env` file:

```bash
# Dhan API Keys (per account)
DHAN_CLIENT_ID_1=your_client_id
DHAN_ACCESS_TOKEN_1=your_access_token

# LLM API Keys
OPENROUTER_API_KEY=your_openrouter_key
OPENAI_API_KEY=your_openai_key  # Optional
ANTHROPIC_API_KEY=your_anthropic_key  # Optional

# Trading Configuration
TRADING_ENABLED=false
```

### Docker Compose Environment Variables:

These are set automatically in `docker-compose.yml`:

- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `API_BASE_URL`: Backend API URL (for frontend)

## Development vs Production

### Development Mode

```bash
# Mount local code for live editing
docker-compose -f docker-compose.dev.yml up
```

Create `docker-compose.dev.yml`:
```yaml
services:
  frontend:
    volumes:
      - ./frontend:/app/frontend
    command: streamlit run frontend/dashboard.py --server.port=8501 --server.address=0.0.0.0
```

### Production Mode

```bash
# Use optimized images, no volume mounts
docker-compose up -d
```

## Monitoring

### Check Resource Usage

```bash
# All containers
docker stats

# Specific container
docker stats ai_trading_frontend
```

### View Health Status

```bash
# All services
docker-compose ps

# Detailed inspect
docker inspect ai_trading_frontend
```

## Scaling

### Run Multiple Frontend Instances

```bash
docker-compose up -d --scale frontend=3
```

Note: You'll need to configure a load balancer for this to work properly.

## Security

### Default Credentials

⚠️ **WARNING**: Change default PostgreSQL credentials before production!

Edit `docker-compose.yml`:
```yaml
environment:
  POSTGRES_USER: your_secure_username
  POSTGRES_PASSWORD: your_secure_password
```

### Network Isolation

Services are isolated in `ai_trading_network`. Only exposed ports are accessible from host.

### Environment Variables

Never commit `.env` file to version control. Use `.env.example` as template.

## Updates

### Update Service Images

```bash
# Pull latest base images
docker-compose pull

# Rebuild with new images
docker-compose up --build -d
```

### Update Application Code

```bash
# Rebuild and restart
docker-compose up --build -d

# Or rebuild specific service
docker-compose build frontend
docker-compose up -d frontend
```

## Complete Restart

```bash
# Clean restart (keeps data)
docker-compose down
docker-compose up --build -d

# Fresh start (deletes data)
docker-compose down -v
docker-compose up --build -d
```

## Files Overview

### Docker Files

- `Dockerfile` - Backend application container
- `Dockerfile.frontend` - Frontend dashboard container
- `docker-compose.yml` - Multi-container orchestration
- `.dockerignore` - Files to exclude from build context

### Configuration Files

- `requirements.txt` - Python dependencies
- `.env` - Environment variables (create from `.env.example`)

## Next Steps

1. ✅ Start all services: `docker-compose up -d`
2. ✅ Access dashboard: http://localhost:8501
3. ✅ Configure trading accounts in the UI
4. ✅ Monitor logs: `docker-compose logs -f`
5. ✅ Test portfolio graph visualization

---

**Last Updated**: 2025-11-11
**Status**: ✅ Ready for Use
**Containers**: 4 (PostgreSQL, Redis, Backend, Frontend)
