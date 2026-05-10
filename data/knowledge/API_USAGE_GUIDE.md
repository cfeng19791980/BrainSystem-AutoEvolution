# API使用指南

## 11个API端点详细用法

---

## Base URL

```
http://localhost:5000
```

---

## 1. Semantic Search API

**端点**: `/semantic_search`
**用途**: 混合检索（Vector + Knowledge Graph）

### Request

```bash
curl -X POST http://localhost:5000/semantic_search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "如何优化股票分析系统",
    "top_k": 5,
    "corpus": "all"
  }'
```

### Response

```json
{
  "status": 200,
  "query": "如何优化股票分析系统",
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
    },
    {
      "id": "method_002",
      "type": "method",
      "name": "deep_analysis",
      "score": 0.92,
      "attributes": {
        "improvement": "+88.8%",
        "target": "intent_accuracy"
      }
    }
  ],
  "total": 2,
  "response_time_ms": 5.2
}
```

### Python SDK

```python
from brain_system import BrainClient

client = BrainClient()
result = client.semantic_search("stock analysis optimization")

print(f"Intent: {result['intent']}")
print(f"Confidence: {result['confidence']}")
print(f"Nodes: {result['nodes']}")
```

### Best Practices

```
1. Query normalization: 使用标准关键词
2. Top-K tuning: 5-10 optimal range
3. Corpus selection: "all" for comprehensive results
4. Cache utilization: Repeated queries cached
```

---

## 2. Scheme Recommendation API

**端点**: `/scheme_recommendation`
**用途**: 推荐优化方案

### Request

```bash
curl -X POST http://localhost:5000/scheme_recommendation \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

### Response

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
      ],
      "confidence": 0.97
    },
    {
      "id": "scheme_002",
      "name": "deep_analysis",
      "priority": 2,
      "estimated_improvement": {
        "accuracy": "+88.8%"
      },
      "steps": [
        "Expand NORMALIZE_KEYWORDS",
        "Add intent taxonomy",
        "Build knowledge graph"
      ],
      "confidence": 0.98
    }
  ],
  "total": 2
}
```

### Use Cases

```
1. Performance troubleshooting
2. Architecture optimization
3. Strategy planning
4. Resource allocation
```

---

## 3. Conflict Detection API

**端点**: `/conflict_detect`
**用途**: 检测方案冲突

### Request

```bash
curl -X POST http://localhost:5000/conflict_detect \
  -H "Content-Type: application/json" \
  -d '{
    "schemes": ["cache_optimization", "deep_analysis", "parallel_processing"]
  }'
```

### Response

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
  "recommendations": [
    "Execute cache_optimization first",
    "Wait for cache stabilization before deep_analysis"
  ],
  "total": 1
}
```

### Conflict Types

| Type | Severity | Resolution |
|------|----------|------------|
| resource_competition | medium | Prioritize by ROI |
| dependency_conflict | high | Resolve dependency first |
| timing_conflict | low | Execute sequentially |

---

## 4. Brain Hook API (Gateway Integration)

**端点**: `/brain/hook`
**用途**: Gateway智能路由

### Request

```bash
curl -X POST http://localhost:5000/brain/hook \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "req_001",
    "user_input": "分析沪深300股票",
    "timestamp": "2026-04-23T14:00:00"
  }'
```

### Response

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
  },
  "metadata": {
    "cache_hit": false,
    "intent_normalized": "analyze"
  }
}
```

### Gateway Integration

```python
# Gateway system integration
from brain_system import BrainHook

hook = BrainHook()

def gateway_router(user_input):
    decision = hook.get_decision(user_input)
    
    # Route based on intent
    handler = decision['route_to']
    params = decision['parameters']
    
    # Execute handler
    result = execute_handler(handler, params)
    
    return result
```

---

## 5. Knowledge Parse API (Experiment Parser)

**端点**: `/knowledge/parse`
**用途**: 解析实验文件添加到知识图谱

### Request

```bash
curl -X POST http://localhost:5000/knowledge/parse \
  -H "Content-Type: application/json" \
  -d '{
    "experiment_file": "experiment_1_cache.py",
    "parse_mode": "full"
  }'
```

### Response

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
      "relation": "validates",
      "weight": 0.95
    }
  ],
  "total_nodes": 2,
  "total_relations": 1,
  "quality_score": 0.92
}
```

### Parse Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| full | Complete parsing | Detailed experiment analysis |
| quick | Quick extraction | Rapid experiment import |
| validation | Validation only | Experiment check |

---

## 6. Knowledge Mine API (Pattern Miner)

**端点**: `/knowledge/mine`
**用途**: 挖掘优化Pattern

### Request

```bash
curl -X POST http://localhost:5000/knowledge/mine \
  -H "Content-Type: application/json" \
  -d '{
    "mine_type": "optimization",
    "min_confidence": 0.8,
    "limit": 10
  }'
```

### Response

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
      "applicable_to": ["stock_analysis", "data_fetch"],
      "quality_score": 0.92
    },
    {
      "id": "pattern_002",
      "type": "optimization",
      "rule": "deep_intent → accuracy_boost",
      "confidence": 0.98,
      "evidence": ["experiment_3", "experiment_6"],
      "applicable_to": ["intent_recognition"],
      "quality_score": 0.96
    }
  ],
  "mined": 2,
  "total_patterns": 10
}
```

### Pattern Quality Scoring

```python
# Pattern quality calculation
def calculate_quality(pattern):
    score = (
        pattern['confidence'] * 0.5 +
        len(pattern['evidence']) * 0.3 +
        len(pattern['applicable_to']) * 0.2
    )
    return score

# Quality threshold
MIN_QUALITY = 0.85
high_quality = [p for p in patterns if calculate_quality(p) > MIN_QUALITY]
```

---

## 7. AutoResearch Check API

**端点**: `/autoresearch/check`
**用途**: 验证实验有效性

### Request

```bash
curl -X POST http://localhost:5000/autoresearch/check \
  -H "Content-Type: application/json" \
  -d '{
    "experiment_name": "experiment_new",
    "focus_area": "performance",
    "hypothesis": "Deep cache reduces response time"
  }'
```

### Response

```json
{
  "status": 200,
  "valid": true,
  "similar_experiments": [
    {
      "name": "experiment_1_cache",
      "focus": "cache_optimization",
      "result": "-97.1%"
    },
    {
      "name": "experiment_5_cache",
      "focus": "multi_level_cache",
      "result": "3.1ms"
    }
  ],
  "recommendation": "Extend experiment_1 with deep cache layer",
  "conflicts": []
}
```

### Validation Criteria

```
1. Hypothesis clarity
2. Similar experiment check
3. Resource conflict detection
4. Expected outcome validation
```

---

## 8. Get Entity API

**端点**: `/get_entity`
**用途**: 获取知识图谱实体

### Request

```bash
curl -X GET "http://localhost:5000/get_entity?id=method_001&type=method"
```

### Response

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
    },
    "relations": [
      {
        "target": "accuracy_001",
        "relation": "improves",
        "weight": 0.97
      },
      {
        "target": "experiment_001",
        "relation": "validated_by",
        "weight": 0.95
      }
    ]
  }
}
```

---

## 9. Add Entity API

**端点**: `/add_entity`
**用途**: 添加知识图谱实体

### Request

```bash
curl -X POST http://localhost:5000/add_entity \
  -H "Content-Type: application/json" \
  -d '{
    "type": "method",
    "name": "deep_analysis",
    "attributes": {
      "accuracy_improvement": "+88.8%",
      "target": "intent_recognition"
    }
  }'
```

### Response

```json
{
  "status": 200,
  "entity_id": "method_002",
  "message": "Entity added successfully",
  "total_nodes": 36
}
```

---

## 10. Add Relation API

**端点**: `/add_relation`
**用途**: 添加实体关系

### Request

```bash
curl -X POST http://localhost:5000/add_relation \
  -H "Content-Type: application/json" \
  -d '{
    "source_id": "method_001",
    "target_id": "accuracy_001",
    "relation": "improves",
    "weight": 0.95
  }'
```

### Response

```json
{
  "status": 200,
  "relation_id": "rel_001",
  "message": "Relation added successfully",
  "total_relations": 11
}
```

---

## 11. Build Optimization Chain API

**端点**: `/build_optimization_chain`
**用途**: 构建优化链

### Request

```bash
curl -X POST http://localhost:5000/build_optimization_chain \
  -H "Content-Type: application/json" \
  -d '{
    "target_metrics": {
      "response_time_ms": 10,
      "accuracy": 95
    },
    "current_metrics": {
      "response_time_ms": 180,
      "accuracy": 55.5
    }
  }'
```

### Response

```json
{
  "status": 200,
  "chain": [
    {
      "step": 1,
      "method": "cache_optimization",
      "estimated_improvement": "-97.1%",
      "priority": 1,
      "duration_days": 1
    },
    {
      "step": 2,
      "method": "deep_analysis",
      "estimated_improvement": "+88.8%",
      "priority": 2,
      "duration_days": 2
    }
  ],
  "total_steps": 2,
  "estimated_total_time": 10.5,
  "confidence": 0.95
}
```

---

## API Performance Benchmarks

| API Endpoint | Avg Time | 95th Percentile | Cache Hit |
|--------------|----------|-----------------|-----------|
| /semantic_search | 5.2ms | 8.7ms | 95% |
| /brain/hook | 3.1ms | 5.5ms | 98% |
| /knowledge/parse | 12.3ms | 15.0ms | 0% |
| /knowledge/mine | 8.7ms | 12.0ms | 50% |
| /get_entity | 0.8ms | 1.2ms | 90% |
| /add_entity | 2.5ms | 3.0ms | 0% |
| /add_relation | 2.2ms | 2.8ms | 0% |

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

## SDK Usage

### Python SDK

```python
from brain_system import BrainClient

client = BrainClient(base_url="http://localhost:5000")

# Semantic search
result = client.semantic_search("stock analysis")

# Brain hook
decision = client.brain_hook("分析股票")

# Knowledge parse
parsed = client.knowledge_parse("experiment_file.py")

# Pattern mine
patterns = client.knowledge_mine(min_confidence=0.8)
```

---

## Pattern-Key

`api.usage.guide` - 11个API端点详细使用指南