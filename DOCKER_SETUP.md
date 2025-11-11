# Docker Setup Guide

This guide explains how to run the entire AI Trading System using Docker Compose.

## Prerequisites

- Docker installed and running
- Docker Compose installed
- `.env` file configured with your API keys

## Quick Start

Start all services (PostgreSQL, Redis, and the Trading App) with a single command:

```bash
docker-compose up -d --build
```

This command will:
1. Build the application Docker image
2. Start PostgreSQL database
3. Start Redis cache
4. Wait for PostgreSQL and Redis to be healthy
5. Run database setup automatically
6. Start the trading application

## Accessing the Application

Once all containers are running:

- **API Documentation**: http://localhost:8000/docs
- **API Endpoint**: http://localhost:8000
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## Useful Commands

### View logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f app
docker-compose logs -f postgres
docker-compose logs -f redis
```

### Stop all services
```bash
docker-compose down
```

### Stop and remove volumes (clean slate)
```bash
docker-compose down -v
```

### Restart a specific service
```bash
docker-compose restart app
```

### Check service status
```bash
docker-compose ps
```

### Rebuild without cache
```bash
docker-compose build --no-cache
docker-compose up -d
```

## Environment Variables

The application uses environment variables from the `.env` file. Make sure you have configured:

- `DHAN_CLIENT_ID`: Your Dhan API client ID
- `DHAN_ACCESS_TOKEN`: Your Dhan API access token
- `OPENROUTER_API_KEY`: Your OpenRouter API key
- Other configuration as needed

The Docker Compose setup will automatically use these values and also set:
- `DATABASE_URL`: Connection to the PostgreSQL container
- `REDIS_URL`: Connection to the Redis container

## Troubleshooting

### Application fails to start
Check the logs:
```bash
docker-compose logs app
```

### Database connection issues
Ensure PostgreSQL is healthy:
```bash
docker-compose ps
```

Both postgres and redis should show "Up (healthy)" status.

### Rebuild from scratch
```bash
docker-compose down -v
docker-compose up -d --build
```

## Architecture

The Docker Compose setup includes:

1. **PostgreSQL** (postgres:15-alpine)
   - Stores trading data, accounts, strategies
   - Automatically initialized with schema

2. **Redis** (redis:7-alpine)
   - Caches market data
   - Stores session information

3. **Trading App** (Python 3.11)
   - FastAPI web server
   - Trading engine
   - LLM integration
   - Automatic database setup on startup

All services are connected via Docker networking and start in the correct order with health checks.
