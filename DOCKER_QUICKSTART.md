# Docker Quick Start - AI Trading System with Frontend

## 🚀 One Command Setup

```bash
docker-compose up --build -d
```

## 📊 Access Your Services

Once all services are running:

| Service | URL | Description |
|---------|-----|-------------|
| **Dashboard** | http://localhost:8501 | Streamlit frontend with portfolio graphs |
| **API** | http://localhost:8000 | FastAPI backend |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| **PostgreSQL** | localhost:5432 | Database (user: username, password: password) |
| **Redis** | localhost:6379 | Cache |

## 📦 What Gets Started

```
✅ PostgreSQL Database (port 5432)
✅ Redis Cache (port 6379)
✅ FastAPI Backend (port 8000)
✅ Streamlit Dashboard (port 8501)
```

## 🎯 Common Commands

### Start Everything
```bash
docker-compose up -d
```

### View Logs
```bash
# All services
docker-compose logs -f

# Just the dashboard
docker-compose logs -f frontend

# Just the backend
docker-compose logs -f app
```

### Stop Everything
```bash
docker-compose down
```

### Restart a Service
```bash
docker-compose restart frontend
```

### Check Status
```bash
docker-compose ps
```

## 🔍 Verify Installation

1. **Check all containers are running:**
   ```bash
   docker-compose ps
   ```
   You should see 4 containers: postgres, redis, app, frontend

2. **Check backend is healthy:**
   ```bash
   curl http://localhost:8000/api/health
   ```

3. **Open the dashboard:**
   Open http://localhost:8501 in your browser

## 📈 Using the Dashboard

The Streamlit dashboard includes:

- **Dashboard**: Overview with multi-asset performance chart
- **Portfolio**: Detailed portfolio view with time range filters (ALL, 72h, 24h)
- **Trades**: Trading history and analytics
- **LLM Decisions**: View AI trading decisions
- **System Control**: Start/stop trading, system status

### Key Features

✅ Multi-asset portfolio graph (like Alpha Arena)
✅ Interactive hover tooltips
✅ Time range filtering
✅ Real-time updates (30s refresh)
✅ Clean, professional UI

## 🛠️ Troubleshooting

### Dashboard Won't Load

```bash
# Check frontend logs
docker-compose logs frontend

# Restart frontend
docker-compose restart frontend
```

### Backend Connection Error

```bash
# Check backend is running
docker-compose ps app

# View backend logs
docker-compose logs app

# Test backend directly
curl http://localhost:8000/api/health
```

### Database Issues

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# View PostgreSQL logs
docker-compose logs postgres

# Access PostgreSQL directly
docker exec -it ai_trading_postgres psql -U username -d ai_trading
```

### Port Already in Use

If port 8501 is already in use, edit `docker-compose.yml`:

```yaml
frontend:
  ports:
    - "8502:8501"  # Change external port to 8502
```

## 🔄 Update Code

If you modify code:

```bash
# Rebuild and restart
docker-compose up --build -d

# Or just rebuild frontend
docker-compose build frontend
docker-compose up -d frontend
```

## 🧹 Clean Restart

```bash
# Stop and remove containers (keeps data)
docker-compose down

# Rebuild and start
docker-compose up --build -d

# OR: Complete reset (DELETES DATA)
docker-compose down -v
docker-compose up --build -d
```

## 📊 Architecture

```
┌─────────────────────────────────────────┐
│     Browser: http://localhost:8501      │
└────────────────┬────────────────────────┘
                 │
                 ▼
          ┌──────────────┐
          │  Frontend    │  Port 8501
          │  (Streamlit) │
          └──────┬───────┘
                 │ API calls
                 ▼
          ┌──────────────┐
          │   Backend    │  Port 8000
          │  (FastAPI)   │
          └──┬───────┬───┘
             │       │
      ┌──────▼───┐ ┌▼──────┐
      │PostgreSQL│ │ Redis │
      │   :5432  │ │ :6379 │
      └──────────┘ └───────┘
```

## 📝 Environment Variables

The frontend automatically connects to the backend using Docker networking.

**Default Configuration:**
- Frontend → Backend: `http://app:8000` (internal)
- External Access: `http://localhost:8501` (frontend), `http://localhost:8000` (backend)

## 🎨 Dashboard Features

### Multi-Asset Portfolio Chart

The dashboard includes a professional multi-line chart showing:
- Total account value (main line)
- Individual asset performance (colored lines)
- Interactive tooltips on hover
- Time range filters (ALL, 72h, 24h)

This matches the Alpha Arena style visualization!

## 📚 More Information

- Full documentation: `DOCKER_SETUP_GUIDE.md`
- Portfolio graph implementation: `PORTFOLIO_GRAPH_IMPLEMENTATION.md`

## ✅ Quick Checklist

- [ ] Docker Desktop installed and running
- [ ] `.env` file created with API keys
- [ ] Run `docker-compose up --build -d`
- [ ] Wait ~30 seconds for all services to start
- [ ] Access dashboard at http://localhost:8501
- [ ] Verify backend at http://localhost:8000/docs

## 🆘 Need Help?

```bash
# View all logs
docker-compose logs -f

# Check service status
docker-compose ps

# Restart everything
docker-compose restart
```

---

**Quick Start Time**: ~2 minutes (first build), ~30 seconds (subsequent starts)
**Services**: 4 containers on 1 network
**Ports**: 5432, 6379, 8000, 8501
