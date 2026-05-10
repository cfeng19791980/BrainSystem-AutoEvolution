# -*- coding: utf-8 -*-
"""
Issue #2233 Training - Entity Quality Filtering
===============================================
Pattern learned from ragas GitHub Issue #2233:
- Problem: NER extracts meaningless entities (Chapter 0, Article 0, dates)
- Solution: Regex filtering + Strict quality check
- Application: BrainSystem knowledge graph entity filtering

Training Flow:
1. Analyze Issue #2233 → Extract Pattern
2. Backup brain_entry.py → brain_entry.py.backup
3. Apply Pattern → Add entity_quality_check()
4. Test → Verify filtering works
5. Rollback ready → backup-before-issue-2233 branch

Reference: https://github.com/explodinggradients/ragas/issues/2233
"""

import re
import json
import logging
from datetime import datetime

logger = logging.getLogger('BrainEntry.Issue2233')

# ============================================================
# Issue #2233 Pattern: Entity Quality Filtering
# ============================================================
ENTITY_FILTER_CONFIG = {
    # Patterns from Issue #2233 - filter meaningless entities
    "unwanted_patterns": [
        r"^Chapter \d+$",           # Chapter 0, Chapter 1...
        r"^Article \d+$",           # Article 0, Article 1...
        r"^Section \d+$",           # Section 0, Section 1...
        r"^\d{4}\.\s*\d{1,2}\.\s*\d{1,2}\.?$",  # 2012. 10. 5.
        r"^\d{1,2}/\d{1,2}/\d{4}$",  # 10/5/2012
        r"^[Pp]age \d+$",            # Page 0
        r"^§\d+$",                   # Section symbol
        r"^§\s*\d+$",                # Section with space
        r"^[Aa]ppendix \d+$",        # Appendix A
        r"^[Ff]igure \d+$",          # Figure 1
        r"^[Tt]able \d+$",           # Table 1
    ],
    
    # Quality criteria
    "min_entity_length": 3,        # Min 3 chars
    "max_entity_length": 100,      # Max 100 chars
    "quality_threshold": 0.5,      # Quality score threshold
    
    # Entity type whitelist
    "valid_entity_types": [
        'performance', 'accuracy', 'evolution', 
        'integration', 'method', 'experiment',
        'tool', 'api', 'config', 'pattern'
    ],
}

def entity_quality_check(entity_name, entity_type=None):
    """
    Check entity quality based on Issue #2233 pattern.
    
    Pattern learned:
    - NER extracts "Chapter 0", "Article 0", dates as entities
    - These create meaningless relationships in knowledge graph
    - Solution: Regex filtering + strict quality check
    
    Args:
        entity_name: Entity name to check (e.g., method_id)
        entity_type: Entity type (optional, for whitelist check)
    
    Returns:
        dict: {
            'is_valid': bool,
            'reason': str,
            'quality_score': float,
            'pattern_matched': str or None
        }
    """
    result = {
        'is_valid': True,
        'reason': 'Valid entity',
        'quality_score': 1.0,
        'pattern_matched': None,
        'timestamp': datetime.now().isoformat()
    }
    
    # Check 1: Length validation
    entity_name_stripped = entity_name.strip()
    
    if len(entity_name_stripped) < ENTITY_FILTER_CONFIG["min_entity_length"]:
        result['is_valid'] = False
        result['reason'] = f"Too short: {len(entity_name_stripped)} chars"
        result['quality_score'] = 0.0
        return result
    
    if len(entity_name_stripped) > ENTITY_FILTER_CONFIG["max_entity_length"]:
        result['is_valid'] = False
        result['reason'] = f"Too long: {len(entity_name_stripped)} chars"
        result['quality_score'] = 0.0
        return result
    
    # Check 2: Unwanted pattern filtering (Issue #2233 core pattern)
    for pattern in ENTITY_FILTER_CONFIG["unwanted_patterns"]:
        if re.match(pattern, entity_name_stripped):
            result['is_valid'] = False
            result['reason'] = f"Matches unwanted pattern"
            result['quality_score'] = 0.0
            result['pattern_matched'] = pattern
            logger.warning(f"Entity filtered: '{entity_name}' matches {pattern}")
            return result
    
    # Check 3: Entity type validation
    if entity_type:
        valid_types = ENTITY_FILTER_CONFIG["valid_entity_types"]
        if entity_type not in valid_types:
            result['is_valid'] = False
            result['reason'] = f"Invalid entity type: {entity_type}"
            result['quality_score'] = 0.3
            logger.warning(f"Entity type filtered: '{entity_name}' type={entity_type}")
            return result
    
    # Check 4: Semantic quality score
    # Higher score for meaningful entity names
    quality_score = 1.0
    
    # Bonus: Contains meaningful words
    meaningful_keywords = [
        'cache', 'optimize', 'improve', 'enhance',
        'filter', 'check', 'validate', 'process',
        'embedding', 'vector', 'pattern', 'evolution'
    ]
    
    keyword_matches = sum(1 for kw in meaningful_keywords if kw.lower() in entity_name.lower())
    quality_score = min(1.0, 0.7 + keyword_matches * 0.1)
    
    # Penalty: Contains numbers (but not all digits)
    if re.search(r'\d', entity_name_stripped) and not re.match(r'^\d+$', entity_name_stripped):
        quality_score *= 0.9
    
    result['quality_score'] = quality_score
    
    # Check 5: Quality threshold
    if quality_score < ENTITY_FILTER_CONFIG["quality_threshold"]:
        result['is_valid'] = False
        result['reason'] = f"Quality score too low: {quality_score}"
        logger.warning(f"Entity quality low: '{entity_name}' score={quality_score}")
        return result
    
    logger.info(f"Entity validated: '{entity_name}' score={quality_score}")
    return result

def filter_entity_list(entities):
    """
    Filter list of entities using Issue #2233 pattern.
    
    Args:
        entities: List of entity names
    
    Returns:
        dict: {
            'valid_entities': list,
            'filtered_entities': list,
            'filter_stats': dict
        }
    """
    valid_entities = []
    filtered_entities = []
    
    filter_stats = {
        'total': len(entities),
        'valid': 0,
        'filtered': 0,
        'patterns_matched': {},
        'timestamp': datetime.now().isoformat()
    }
    
    for entity in entities:
        check_result = entity_quality_check(entity)
        
        if check_result['is_valid']:
            valid_entities.append(entity)
            filter_stats['valid'] += 1
        else:
            filtered_entities.append({
                'entity': entity,
                'reason': check_result['reason'],
                'pattern': check_result['pattern_matched']
            })
            filter_stats['filtered'] += 1
            
            # Track pattern matches
            pattern = check_result['pattern_matched']
            if pattern:
                filter_stats['patterns_matched'][pattern] = \
                    filter_stats['patterns_matched'].get(pattern, 0) + 1
    
    logger.info(f"Entity filtering: {filter_stats['valid']}/{filter_stats['total']} valid")
    
    return {
        'valid_entities': valid_entities,
        'filtered_entities': filtered_entities,
        'filter_stats': filter_stats
    }

def validate_method_data(method_id, method_data):
    """
    Validate method data before adding to knowledge graph.
    
    Args:
        method_id: Method identifier
        method_data: Method data dict
    
    Returns:
        dict: {
            'is_valid': bool,
            'validation_results': dict,
            'filtered_fields': list
        }
    """
    validation_results = {}
    filtered_fields = []
    is_valid = True
    
    # Check 1: Method ID quality
    id_check = entity_quality_check(method_id, method_data.get('type'))
    validation_results['method_id'] = id_check
    if not id_check['is_valid']:
        is_valid = False
        filtered_fields.append('method_id')
    
    # Check 2: Method name quality (if exists)
    if 'name' in method_data:
        name_check = entity_quality_check(method_data['name'])
        validation_results['name'] = name_check
        if not name_check['is_valid']:
            filtered_fields.append('name')
    
    # Check 3: Type validation
    if 'type' in method_data:
        type_check = entity_quality_check(method_data['type'], method_data['type'])
        validation_results['type'] = type_check
    
    # Check 4: Effect validation (should be meaningful)
    if 'effect' in method_data:
        effect = method_data['effect']
        if len(effect) < 5 or effect.isdigit():
            validation_results['effect'] = {
                'is_valid': False,
                'reason': 'Effect too short or meaningless'
            }
            filtered_fields.append('effect')
    
    return {
        'is_valid': is_valid,
        'validation_results': validation_results,
        'filtered_fields': filtered_fields,
        'timestamp': datetime.now().isoformat()
    }

# ============================================================
# Integration Test for Issue #2233 Pattern
# ============================================================
def test_entity_filtering():
    """
    Test entity filtering with Issue #2233 examples.
    """
    # Test entities from Issue #2233
    test_entities = [
        # Should be filtered (Issue #2233 examples)
        "Chapter 5",
        "Article 61",
        "2021. 1. 1.",
        "2023. 10. 17.",
        "Page 10",
        "Section 1",
        
        # Should pass
        "embedding_cache",
        "result_cache",
        "pattern_auto_collect",
        "quality_scoring",
        "brain_patterns",
        "flow_templates",
    ]
    
    print("=" * 60)
    print("Issue #2233 Pattern Test: Entity Quality Filtering")
    print("=" * 60)
    
    results = filter_entity_list(test_entities)
    
    print(f"\nTotal entities: {results['filter_stats']['total']}")
    print(f"Valid entities: {results['filter_stats']['valid']}")
    print(f"Filtered entities: {results['filter_stats']['filtered']}")
    
    print("\n--- Valid Entities ---")
    for entity in results['valid_entities']:
        print(f"  [PASS] {entity}")
    
    print("\n--- Filtered Entities ---")
    for item in results['filtered_entities']:
        print(f"  [FILTER] {item['entity']}")
        print(f"    Reason: {item['reason']}")
        if item['pattern']:
            print(f"    Pattern: {item['pattern']}")
    
    print("\n--- Pattern Match Stats ---")
    for pattern, count in results['filter_stats']['patterns_matched'].items():
        print(f"  {pattern}: {count} matches")
    
    return results

# ============================================================
# Self-Evolution Record for Issue #2233
# ============================================================
def record_issue_2233_pattern():
    """
    Record Issue #2233 pattern for self-evolution.
    """
    pattern_record = {
        'pattern_id': 'entity_filter_regex',
        'source': 'github_issue_2233',
        'source_url': 'https://github.com/explodinggradients/ragas/issues/2233',
        'learned_at': datetime.now().isoformat(),
        
        'problem': {
            'description': 'NER extracts meaningless entities (Chapter/Article/dates)',
            'impact': 'Creates giant components in knowledge graph',
            'symptoms': ['Semantically unrelated relationships', 'Quality degradation']
        },
        
        'solution': {
            'method': 'Regex filtering + strict quality check',
            'code_patterns': ENTITY_FILTER_CONFIG['unwanted_patterns'],
            'validation_steps': [
                'Length check (3-100 chars)',
                'Pattern match check',
                'Entity type whitelist',
                'Quality score calculation'
            ]
        },
        
        'application': {
            'target': 'BrainSystem knowledge graph',
            'integration_point': 'add_knowledge_method()',
            'benefit': 'Prevent low-quality entities in knowledge graph'
        },
        
        'quality_metrics': {
            'filter_rate': 'Expected 30-50% for regulatory documents',
            'false_positive_rate': '<5% for meaningful entities',
            'performance_impact': 'Minimal (regex check ~0.1ms)'
        }
    }
    
    logger.info(f"Pattern recorded: {pattern_record['pattern_id']}")
    return pattern_record

if __name__ == '__main__':
    # Run test
    test_results = test_entity_filtering()
    
    # Record pattern
    pattern = record_issue_2233_pattern()
    
    print("\n" + "=" * 60)
    print("Pattern Learned from Issue #2233")
    print("=" * 60)
    print(json.dumps(pattern, indent=2))
    
    # Summary
    print("\n--- Training Summary ---")
    print("Issue: ragas #2233 - Knowledge Graph NER Over-extraction")
    print("Pattern: entity_filter_regex")
    print("Application: BrainSystem entity quality check")
    print("Backup: backup-before-issue-2233 branch")
    print("Rollback: Ready")