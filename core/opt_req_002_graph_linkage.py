# -*- coding: utf-8 -*-
"""
OPT-REQ-002: Graph Entity Linkage Pattern
==========================================
Source: ragflow #8587 - How to optimize the graph (entity/relation optimization)
Pattern ID: graph_entity_linkage
Approved: 2026-04-23

Problem:
- Knowledge graph entities are discrete (no relations)
- Entities don't form effective relationships
- Multi-hop reasoning fails due to disconnected graph

Solution:
- Auto-link similar entities based on embedding similarity
- Add minimum relation count constraint
- Add entity similarity threshold configuration
"""

import json
import logging
import math
from datetime import datetime

logger = logging.getLogger('BrainEntry.OptReq002')

# ============================================================
# Pattern: graph_entity_linkage
# ============================================================
GRAPH_LINKAGE_CONFIG = {
    "enabled": True,
    "similarity_threshold": 0.7,  # Min similarity for auto-link (cosine)
    "min_relations_per_entity": 2,  # Ensure each entity has at least 2 relations
    "linkage_method": "embedding_similarity",  # How to determine similarity
    "max_new_links_per_entity": 3,  # Max 3 new links per discrete entity
    "relation_type": "SIMILAR_TO",  # Relation type for auto-created links
    "confidence_threshold": 0.5,  # Min confidence for auto-link
}

class GraphEntityLinkage:
    """Auto-link discrete entities in knowledge graph - Pattern from ragflow #8587"""
    
    def __init__(self, knowledge_graph):
        self.graph = knowledge_graph
        self.stats = {
            "discrete_entities_found": 0,
            "new_links_created": 0,
            "entities_linked": 0,
        }
    
    def calculate_cosine_similarity(self, vec1, vec2):
        """Calculate cosine similarity between two vectors"""
        if not vec1 or not vec2:
            return 0.0
        
        # Handle dict format {"embedding": [...]}
        if isinstance(vec1, dict):
            vec1 = vec1.get("embedding", [])
        if isinstance(vec2, dict):
            vec2 = vec2.get("embedding", [])
        
        if len(vec1) != len(vec2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def get_entity_relation_count(self):
        """Count relations for each entity"""
        relation_count = {}
        
        for edge in self.graph.get("edges", []):
            from_entity = edge.get("from")
            to_entity = edge.get("to")
            
            if from_entity:
                relation_count[from_entity] = relation_count.get(from_entity, 0) + 1
            if to_entity:
                relation_count[to_entity] = relation_count.get(to_entity, 0) + 1
        
        return relation_count
    
    def find_discrete_entities(self):
        """Find entities with insufficient relations"""
        relation_count = self.get_entity_relation_count()
        nodes = self.graph.get("nodes", {})
        
        discrete_entities = []
        
        for entity_id in nodes:
            count = relation_count.get(entity_id, 0)
            min_relations = GRAPH_LINKAGE_CONFIG["min_relations_per_entity"]
            
            if count < min_relations:
                discrete_entities.append({
                    "id": entity_id,
                    "relation_count": count,
                    "needs_links": min_relations - count
                })
        
        self.stats["discrete_entities_found"] = len(discrete_entities)
        logger.info(f'Found {len(discrete_entities)} discrete entities')
        
        return discrete_entities
    
    def find_similar_entities(self, target_entity_id, threshold=0.7):
        """Find entities similar to target entity based on embedding"""
        nodes = self.graph.get("nodes", {})
        
        target_entity = nodes.get(target_entity_id)
        if not target_entity:
            return []
        
        target_embedding = target_entity.get("embedding")
        if not target_embedding:
            logger.warning(f'Entity {target_entity_id} has no embedding')
            return []
        
        similar_entities = []
        
        for entity_id, entity_data in nodes.items():
            if entity_id == target_entity_id:
                continue
            
            entity_embedding = entity_data.get("embedding")
            if not entity_embedding:
                continue
            
            similarity = self.calculate_cosine_similarity(target_embedding, entity_embedding)
            
            if similarity >= threshold:
                similar_entities.append({
                    "id": entity_id,
                    "similarity": similarity,
                    "type": entity_data.get("type", "unknown")
                })
        
        # Sort by similarity (highest first)
        similar_entities.sort(key=lambda x: x["similarity"], reverse=True)
        
        return similar_entities
    
    def auto_link_entities(self):
        """Auto-link discrete entities to similar entities"""
        if not GRAPH_LINKAGE_CONFIG["enabled"]:
            logger.info('Graph linkage disabled')
            return self.graph
        
        discrete_entities = self.find_discrete_entities()
        new_edges = []
        
        for discrete in discrete_entities:
            entity_id = discrete["id"]
            needs_links = discrete["needs_links"]
            
            # Find similar entities
            threshold = GRAPH_LINKAGE_CONFIG["similarity_threshold"]
            similar_entities = self.find_similar_entities(entity_id, threshold)
            
            # Create new links
            max_links = min(needs_links, GRAPH_LINKAGE_CONFIG["max_new_links_per_entity"])
            links_created = 0
            
            for similar in similar_entities[:max_links]:
                new_edge = {
                    "from": entity_id,
                    "to": similar["id"],
                    "relation": GRAPH_LINKAGE_CONFIG["relation_type"],
                    "confidence": similar["similarity"],
                    "auto_created": True,
                    "created_at": datetime.now().isoformat()
                }
                
                # Only add if confidence meets threshold
                if similar["similarity"] >= GRAPH_LINKAGE_CONFIG["confidence_threshold"]:
                    new_edges.append(new_edge)
                    links_created += 1
                    logger.debug(f'Created link: {entity_id} -> {similar["id"]} (sim={similar["similarity"]:.2f})')
            
            if links_created > 0:
                self.stats["entities_linked"] += 1
                self.stats["new_links_created"] += links_created
        
        # Add new edges to graph
        self.graph["edges"] = self.graph.get("edges", [])
        self.graph["edges"].extend(new_edges)
        
        logger.info(f'Created {len(new_edges)} new links for {self.stats["entities_linked"]} entities')
        
        return self.graph
    
    def get_stats(self):
        """Get linkage statistics"""
        return self.stats
    
    def get_graph_connectivity_metrics(self):
        """Calculate graph connectivity metrics"""
        nodes = self.graph.get("nodes", {})
        edges = self.graph.get("edges", [])
        
        total_entities = len(nodes)
        total_relations = len(edges)
        
        relation_count = self.get_entity_relation_count()
        
        # Connected entities (has at least 1 relation)
        connected = sum(1 for count in relation_count.values() if count > 0)
        
        # Average relations per entity
        avg_relations = total_relations / total_entities if total_entities > 0 else 0
        
        # Discrete entities (no relations)
        discrete = total_entities - connected
        
        return {
            "total_entities": total_entities,
            "total_relations": total_relations,
            "connected_entities": connected,
            "discrete_entities": discrete,
            "connectivity_rate": connected / total_entities if total_entities > 0 else 0,
            "avg_relations_per_entity": avg_relations,
        }


# ============================================================
# Integration Helper Functions
# ============================================================
def optimize_knowledge_graph_linkage(knowledge_graph):
    """
    Optimize knowledge graph by auto-linking discrete entities.
    
    Usage:
        optimized_graph = optimize_knowledge_graph_linkage(knowledge_graph)
    """
    linkage = GraphEntityLinkage(knowledge_graph)
    return linkage.auto_link_entities()


def get_graph_connectivity(knowledge_graph):
    """Get knowledge graph connectivity metrics"""
    linkage = GraphEntityLinkage(knowledge_graph)
    return linkage.get_graph_connectivity_metrics()


# ============================================================
# Test Function
# ============================================================
def test_graph_entity_linkage():
    """Test graph entity linkage optimization"""
    print("=" * 60)
    print("OPT-REQ-002 Test: Graph Entity Linkage")
    print("=" * 60)
    
    # Create test knowledge graph with discrete entities
    test_graph = {
        "nodes": {
            "entity_a": {
                "type": "method",
                "name": "embedding_cache",
                "embedding": [0.1, 0.2, 0.3, 0.4]  # Will be similar to entity_b
            },
            "entity_b": {
                "type": "method",
                "name": "result_cache",
                "embedding": [0.11, 0.21, 0.31, 0.41]  # Similar to entity_a
            },
            "entity_c": {
                "type": "method",
                "name": "pattern_collect",
                "embedding": [0.5, 0.6, 0.7, 0.8]  # Different
            },
            "entity_d": {
                "type": "method",
                "name": "quality_score",
                "embedding": [0.51, 0.61, 0.71, 0.81]  # Similar to entity_c
            },
        },
        "edges": []  # Start with no relations (all discrete)
    }
    
    print("\n--- Initial Graph State ---")
    linkage = GraphEntityLinkage(test_graph)
    initial_metrics = linkage.get_graph_connectivity_metrics()
    
    print(f"Total entities: {initial_metrics['total_entities']}")
    print(f"Total relations: {initial_metrics['total_relations']}")
    print(f"Discrete entities: {initial_metrics['discrete_entities']}")
    print(f"Connectivity rate: {initial_metrics['connectivity_rate']:.2%}")
    
    print("\n--- Running Auto-Linkage ---")
    optimized_graph = linkage.auto_link_entities()
    
    print("\n--- Optimized Graph State ---")
    optimized_metrics = linkage.get_graph_connectivity_metrics()
    linkage_stats = linkage.get_stats()
    
    print(f"Total relations: {optimized_metrics['total_relations']}")
    print(f"Discrete entities found: {linkage_stats['discrete_entities_found']}")
    print(f"New links created: {linkage_stats['new_links_created']}")
    print(f"Entities linked: {linkage_stats['entities_linked']}")
    print(f"Connectivity rate: {optimized_metrics['connectivity_rate']:.2%}")
    
    print("\n--- New Relations Created ---")
    for edge in optimized_graph["edges"]:
        if edge.get("auto_created"):
            print(f"  {edge['from']} -> {edge['to']} (sim={edge['confidence']:.2f})")
    
    print("\n--- Performance Comparison ---")
    connectivity_improvement = (optimized_metrics['connectivity_rate'] - initial_metrics['connectivity_rate']) * 100
    discrete_reduction = initial_metrics['discrete_entities'] - optimized_metrics['discrete_entities']
    
    print(f"Connectivity improvement: {connectivity_improvement:.1f}%")
    print(f"Discrete entities reduced: {discrete_reduction}")
    
    print("\n--- Test Result ---")
    if linkage_stats['new_links_created'] >= 2:  # Expected at least 2 new links
        print("[PASS] Auto-linkage created expected relations")
        return True
    else:
        print("[FAIL] Auto-linkage did not create expected relations")
        return False


if __name__ == '__main__':
    test_result = test_graph_entity_linkage()
    
    # Record pattern
    pattern = {
        "pattern_id": "graph_entity_linkage",
        "source": "github_ragflow_8587",
        "approved_at": "2026-04-23T16:27",
        "status": "implemented",
        "test_result": "pass" if test_result else "fail"
    }
    
    print("\n" + "=" * 60)
    print("Pattern Implementation Record")
    print("=" * 60)
    print(json.dumps(pattern, indent=2))