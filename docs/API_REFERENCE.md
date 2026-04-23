# API Reference

BrainSystem-AutoEvolution RESTful API Documentation

---

## Overview

BrainSystem provides 11 API endpoints for intelligent agent integration:

- **Core Intelligence**: 5 endpoints (semantic search, scheme recommendation, conflict detect)
- **Knowledge Graph**: 3 endpoints (entity operations)
- **Self-Evolution**: 3 endpoints (experiment parser, pattern miner, autoresearch)
- **Gateway Integration**: 1 endpoint (brain hook)

---

## Base URL

```
http://localhost:5000
```

---

## Authentication

Currently no authentication required (for development mode).
Future versions will support API key authentication.

---

## API Endpoints

### 1. Semantic Search

**Endpoint**: `/semantic_search`
**Method**: `POST`
**Description**: Hybrid search using vector + knowledge graph

**Request Body**:
```json
{
  "query": "how to optimize stock analysis system",
  "top_k": 5,
  "corpus": "all"  // "wiki", "memory", or "all"
}
```

**Response**:
```json
{
  "status": 200,
  "query": "how to optimize stock analysis system",
  "intent": "optimization",
  "confidence": 0.9899,
  "nodes": [
    {
      "id": "method_001",
      "type": "method",
      "name": "cache_optimization",
      "score": 0.95,
      "attributes": {
        "improvement": "-97.1%",
        "target": "response_time"
      }
    }
  ],
  "total": 1,
  "response_time_ms": 5.2
}
```

**Example**:
```bash
curl -X POST http://localhost:5000/semantic_search \
  -H "Content-Type: application/json" \
  -d '{"query":"stock analysis optimization","top_k":5}'
```

---

### 2. Scheme Recommendation

**Endpoint**: `/scheme_recommendation`
**Method**: `POST`
**Description**: Recommend optimization schemes based on context

**Request Body**:
```json
{
  "context": {
    "problem": "slow response time",
    "current_metrics": {
      "response_time_ms": 180,
      "accuracy": 55.5
    },
    "target_metrics": {
      "response_time_ms": 10,
      "accuracy": 95
    }
  },
  "top_k": 3
}
```

**Response**:
```json
{
  "status": 200,
  "schemes": [
    {
      "id": "scheme_001",
      "name": "cache_optimization",
      "priority": 1,
      "estimated_improvement": {
        "response_time": "-97.1%",
        "accuracy": "+88.8%"
      },
      "steps": [
        "Implement result_cache",
        "Add intent normalization",
        "Enable vector embedding"
      ]
    }
  ],
  "total": 1
}
```

---

### 3. Conflict Detection

**Endpoint**: `/conflict_detect`
**Method**: `POST`
**Description**: Detect conflicts between schemes

**Request Body**:
```json
{
  "schemes": ["cache_optimization", "deep_analysis", "parallel_processing"]
}
```

**Response**:
```json
{
  "status": 200,
  "conflicts": [
    {
      "scheme_1": "cache_optimization",
      "scheme_2": "deep_analysis",
      "conflict_type": "resource_competition",
      "severity": "medium",
      "resolution": "Prioritize cache_optimization (higher ROI)"
    }
  ],
  "total": 1
}
```

---

### 4. Brain Hook (Gateway Integration)

**Endpoint**: `/brain/hook`
**Method**: `POST`
**Description**: Gateway decision routing for intelligent agent

**Request Body**:
```json
{
  "request_id": "req_001",
  "user_input": "分析沪深300股票",
  "timestamp": "2026-04-23T13:00:00"
}
```

**Response**:
```json
{
  "status": 200,
  "decision": {
    "intent": "stock_analysis",
    "confidence": 0.9899,
    "route_to": "analyzer_v4.py",
    "parameters": {
      "index": "沪深300",
      "action": "analyze"
    },
    "estimated_time_ms": 5.2
  }
}
```

**Example**:
```bash
curl -X POST http://localhost:5000/brain/hook \
  -H "Content-Type: application/json" \
  -d '{"user_input":"分析股票","request_id":"test001"}'
```

---

### 5. Knowledge Parse (Experiment Parser)

**Endpoint**: `/knowledge/parse`
**Method**: `POST`
**Description**: Parse experiment file and add to knowledge graph

**Request Body**:
```json
{
  "experiment_file": "experiment_1_cache.py",
  "parse_mode": "full"
}
```

**Response**:
```json
{
  "status": 200,
  "experiment": "experiment_1_cache",
  "nodes_added": [
    {
      "type": "experiment",
      "name": "experiment_1",
      "focus": "cache_optimization"
    },
    {
      "type": "method",
      "name": "result_cache",
      "improvement": "-97.1%"
    }
  ],
  "relations_added": [
    {
      "source": "experiment_1",
      "target": "result_cache",
      "relation": "validates"
    }
  ],
  "total_nodes": 2,
  "total_relations": 1
}
```

---

### 6. Knowledge Mine (Pattern Miner)

**Endpoint**: `/knowledge/mine`
**Method**: `POST`
**Description**: Mine patterns from knowledge graph

**Request Body**:
```json
{
  "mine_type": "optimization",
  "min_confidence": 0.8,
  "limit": 10
}
```

**Response**:
```json
{
  "status": 200,
  "patterns": [
    {
      "id": "pattern_001",
      "type": "optimization",
      "rule": "cache → response_time_improvement",
      "confidence": 0.95,
      "evidence": ["experiment_1", "experiment_5"],
      "applicable_to": ["stock_analysis", "data_fetch"]
    }
  ],
  "mined": 1,
  "quality_score": 0.92
}
```

---

### 7. AutoResearch Check

**Endpoint**: `/autoresearch/check`
**Method**: `POST`
**Description**: Check experiment validity before execution

**Request Body**:
```json
{
  "experiment_name": "experiment_new",
  "focus_area": "performance",
  "hypothesis": "Deep cache reduces response time"
}
```

**Response**:
```json
{
  "status": 200,
  "valid": true,
  "similar_experiments": [
    {
      "name": "experiment_1_cache",
      "focus": "cache_optimization",
      "result": "-97.1%"
    }
  ],
  "recommendation": "Extend experiment_1 with deep cache layer"
}
```

---

### 8. Get Entity

**Endpoint**: `/get_entity`
**Method**: `GET`
**Description**: Retrieve entity from knowledge graph

**Query Parameters**:
- `id`: Entity ID (required)
- `type`: Entity type (optional)

**Response**:
```json
{
  "status": 200,
  "entity": {
    "id": "method_001",
    "type": "method",
    "name": "cache_optimization",
    "attributes": {
      "improvement": "-97.1%",
      "target": "response_time",
      "confidence": 0.9899
    }
  }
}
```

**Example**:
```bash
curl http://localhost:5000/get_entity?id=method_001
```

---

### 9. Add Entity

**Endpoint**: `/add_entity`
**Method**: `POST`
**Description**: Add entity to knowledge graph

**Request Body**:
```json
{
  "type": "method",
  "name": "deep_analysis",
  "attributes": {
    "accuracy_improvement": "+88.8%",
    "target": "intent_recognition"
  }
}
```

**Response**:
```json
{
  "status": 200,
  "entity_id": "method_002",
  "message": "Entity added successfully"
}
```

---

### 10. Add Relation

**Endpoint**: `/add_relation`
**Method**: `POST`
**Description**: Add relation between entities

**Request Body**:
```json
{
  "source_id": "method_001",
  "target_id": "accuracy_001",
  "relation": "improves",
  "weight": 0.95
}
```

**Response**:
```json
{
  "status": 200,
  "relation_id": "rel_001",
  "message": "Relation added successfully"
}
```

---

### 11. Build Optimization Chain

**Endpoint**: `/build_optimization_chain`
**Method**: `POST`
**Description**: Build optimization chain from target metrics

**Request Body**:
```json
{
  "target_metrics": {
    "response_time_ms": 10,
    "accuracy": 95
  },
  "current_metrics": {
    "response_time_ms": 180,
    "accuracy": 55.5
  }
}
```

**Response**:
```json
{
  "status": 200,
  "chain": [
    {
      "step": 1,
      "method": "cache_optimization",
      "estimated_improvement": "-97.1%",
      "priority": 1
    },
    {
      "step": 2,
      "method": "deep_analysis",
      "estimated_improvement": "+88.8%",
      "priority": 2
    }
  ],
  "total_steps": 2,
  "estimated_total_time": 10.5
}
```

---

## Error Handling

### Common Errors

**400 Bad Request**:
```json
{
  "status": 400,
  "error": "Missing required parameter: query"
}
```

**404 Not Found**:
```json
{
  "status": 404,
  "error": "Entity not found: method_999"
}
```

**500 Internal Server Error**:
```json
{
  "status": 500,
  "error": "Database connection failed"
}
```

---

## Performance Metrics

### Response Time Benchmarks

| Endpoint | Avg Response Time | 95th Percentile |
|----------|-------------------|-----------------|
| `/semantic_search` | 5.2ms | 8.7ms |
| `/brain/hook` | 3.1ms | 5.5ms |
| `/knowledge/parse` | 12.3ms | 15.0ms |
| `/knowledge/mine` | 8.7ms | 12.0ms |

---

## Rate Limits

Current version has no rate limits (development mode).
Future versions will implement:
- 1000 requests/hour for free tier
- 10000 requests/hour for premium tier

---

## Versioning

API version: v1.0.0
All endpoints are stable and backward-compatible.

---

## SDK Examples

### Python SDK
```python
from brain_system import BrainClient

client = BrainClient(base_url="http://localhost:5000")

# Semantic search
result = client.semantic_search("stock analysis optimization")
print(f"Intent: {result['intent']}, Confidence: {result['confidence']}")

# Brain hook
decision = client.brain_hook("分析沪深300股票")
print(f"Route to: {decision['route_to']}")
```

### JavaScript SDK
```javascript
const BrainClient = require('brain-system-client');

const client = new BrainClient('http://localhost:5000');

// Semantic search
const result = await client.semanticSearch('stock analysis');
console.log(result.intent, result.confidence);
```

---

**API Documentation Updated**: 2026-04-23
**Version**: v1.0.0
**Contact**: 10341731@qq.com