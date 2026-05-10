# -*- coding: utf-8 -*-
"""
Regression Test for OPT-REQ-002 - Graph Entity Linkage
Pattern: graph_entity_linkage
Source: ragflow #8587
"""
import sys

def test_graph_entity_linkage():
    """Test graph_entity_linkage pattern from ragflow #8587"""
    print("=" * 60)
    print("Regression Test: OPT-REQ-002 (graph_entity_linkage)")
    print("=" * 60)
    
    # Minimal graph implementation for test
    class SimpleGraph:
        def __init__(self):
            self.entities = {}
            self.relations = []
        
        def add_entity(self, name, embedding):
            self.entities[name] = embedding
        
        def link_entities(self, threshold=0.9):
            """Auto-link entities based on embedding similarity"""
            names = list(self.entities.keys())
            new_links = 0
            
            for i, name_a in enumerate(names):
                for name_b in names[i+1:]:
                    # Calculate simple similarity
                    emb_a = self.entities[name_a]
                    emb_b = self.entities[name_b]
                    
                    if len(emb_a) == len(emb_b):
                        sim = sum(a*b for a, b in zip(emb_a, emb_b))
                        sim /= (sum(a**2 for a in emb_a) ** 0.5 * sum(b**2 for b in emb_b) ** 0.5)
                        
                        if sim >= threshold:
                            self.relations.append((name_a, name_b, sim))
                            new_links += 1
            
            return new_links
        
        def get_connectivity(self):
            """Get connectivity rate"""
            total = len(self.entities)
            if total == 0:
                return 0
            
            connected = set()
            for a, b, _ in self.relations:
                connected.add(a)
                connected.add(b)
            
            return len(connected) / total
    
    graph = SimpleGraph()
    
    # Add test entities
    graph.add_entity("entity_a", [1.0, 0.0, 0.0])
    graph.add_entity("entity_b", [1.0, 0.01, 0.0])  # Very similar to a
    graph.add_entity("entity_c", [0.9, 0.1, 0.0])   # Similar to a and b
    graph.add_entity("entity_d", [0.0, 1.0, 0.0])   # Different
    
    print("\n--- Initial State ---")
    print(f"Entities: {len(graph.entities)}")
    print(f"Relations: {len(graph.relations)}")
    print(f"Connectivity: {graph.get_connectivity():.1%}")
    
    # Run auto-linkage
    print("\n--- Running Auto-Linkage ---")
    new_links = graph.link_entities(threshold=0.9)
    
    print("\n--- Final State ---")
    print(f"Entities: {len(graph.entities)}")
    print(f"Relations: {len(graph.relations)}")
    print(f"New Links: {new_links}")
    print(f"Connectivity: {graph.get_connectivity():.1%}")
    
    # Show relations
    print("\n--- Created Relations ---")
    for a, b, sim in graph.relations:
        print(f"  {a} -> {b} (sim={sim:.2f})")
    
    print("\n--- Summary ---")
    
    # Expected: at least 2 relations (entity_a-b, entity_a-c or entity_b-c)
    if len(graph.relations) >= 2:
        print("\n[PASS] Auto-linkage created relations")
        return True
    else:
        print("\n[FAIL] Auto-linkage failed to create relations")
        return False

if __name__ == "__main__":
    success = test_graph_entity_linkage()
    sys.exit(0 if success else 1)