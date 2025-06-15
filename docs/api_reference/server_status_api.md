# Server Status API

**Base Path:** `/v1/serverstatus`

Provides health checks and system status information for Knowledge Forge services.

## Get Server Status

**Endpoint:** `GET /v1/serverstatus`

Returns the current health status of all Knowledge Forge services and components.

```bash
curl "http://localhost:10000/v1/serverstatus"
```

**Response:**

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": 1699061776,
  "uptime": 86400,
  "services": {
    "database": "connected",
    "vector_store": "operational", 
    "llm_service": "available",
    "embedding_service": "available",
    "file_storage": "operational",
    "task_queue": "running"
  },
  "metrics": {
    "active_responses": 5,
    "queued_tasks": 12,
    "total_files_processed": 1543,
    "total_vector_stores": 23,
    "memory_usage_mb": 2048,
    "cpu_usage_percent": 15.5
  },
  "features": {
    "response_api": true,
    "file_search": true,
    "web_search": true,
    "document_finder": true,
    "streaming": true,
    "citations": true
  }
}
```

**Field Descriptions:**

- `status` (string): Overall system health (`healthy`, `degraded`, `unhealthy`)
- `version` (string): Knowledge Forge version number
- `timestamp` (integer): Unix timestamp of status check
- `uptime` (integer): Server uptime in seconds
- `services` (object): Status of individual services
- `metrics` (object): Real-time system metrics
- `features` (object): Available features and capabilities

**Service Status Values:**

- `connected` - Service connected and operational
- `operational` - Service running normally  
- `available` - Service accessible
- `running` - Service executing normally
- `degraded` - Service operational but with issues
- `unavailable` - Service not accessible
- `failed` - Service not functioning

## Health Check

**Endpoint:** `GET /v1/serverstatus/health`

Simplified health check endpoint for monitoring and load balancers.

```bash
curl "http://localhost:10000/v1/serverstatus/health"
```

**Response (Healthy):**

```json
{
  "status": "healthy",
  "timestamp": 1699061776
}
```

**Response (Unhealthy):**

```json
{
  "status": "unhealthy", 
  "timestamp": 1699061776,
  "issues": [
    "Database connection failed",
    "LLM service unavailable"
  ]
}
```

**HTTP Status Codes:**

- `200 OK` - System healthy
- `503 Service Unavailable` - System unhealthy or degraded

## Usage

### Monitoring Integration

```bash
# Basic health check
curl -f "http://localhost:10000/v1/serverstatus/health" || alert "Knowledge Forge is down"

# Detailed status with metrics
curl "http://localhost:10000/v1/serverstatus" | jq '.services'
```

### Load Balancer Configuration

```nginx
upstream knowledge_forge {
    server localhost:10000;
}

location /health {
    access_log off;
    proxy_pass http://knowledge_forge/v1/serverstatus/health;
    proxy_connect_timeout 1s;
    proxy_timeout 1s;
}
```

### Service Dependencies

The server status reflects the health of these critical dependencies:

- **Database**: PostgreSQL for metadata and history
- **Vector Store**: FAISS/Cloud vector databases
- **LLM Service**: AI model endpoints
- **Embedding Service**: Text embedding generation
- **File Storage**: Document and asset storage
- **Task Queue**: Background job processing

A failure in any critical service will result in `degraded` or `unhealthy` status.

---

*Use this endpoint to monitor Knowledge Forge deployment health and integrate with your monitoring infrastructure.*
