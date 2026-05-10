# -*- coding: utf-8 -*-
"""
Regression Test for Issue #2233 - NER Over-extraction
Pattern: entity_filter_regex
"""
import sys
import re

def test_entity_filter_regex():
    """Test entity_filter_regex pattern from ragas #2233"""
    print("=" * 60)
    print("Regression Test: Issue #2233 (entity_filter_regex)")
    print("=" * 60)
    
    # Pattern implementation
    ENTITY_FILTER_PATTERNS = [
        r'^Chapter\s+\d+',      # Chapter X
        r'^Article\s+\d+',      # Article X
        r'^Section\s+\d+',      # Section X
        r'^\d{4}-\d{2}-\d{2}$', # Dates (YYYY-MM-DD)
        r'^\d{1,2}/\d{1,2}/\d{2,4}$', # Dates (MM/DD/YYYY)
        r'^[A-Z]\.\s*\d+',      # A.1, B.2
        r'^Figure\s+\d+',       # Figure X
        r'^Table\s+\d+',        # Table X
        r'^Page\s+\d+',         # Page X
        r'^Appendix\s+[A-Z]$',  # Appendix A
    ]
    
    def filter_entity(entity_name):
        """Filter meaningless entities"""
        for pattern in ENTITY_FILTER_PATTERNS:
            if re.match(pattern, entity_name.strip()):
                return True
        return False
    
    # Test cases
    test_entities = [
        ("Chapter 1", True, "Should filter chapter"),
        ("Article 2", True, "Should filter article"),
        ("2026-04-23", True, "Should filter date"),
        ("A.1", True, "Should filter section number"),
        ("Figure 3", True, "Should filter figure"),
        ("Table 1", True, "Should filter table"),
        ("Python", False, "Should keep real entity"),
        ("Machine Learning", False, "Should keep real entity"),
        ("NVIDIA", False, "Should keep real entity"),
        ("BrainSystem", False, "Should keep real entity"),
    ]
    
    print("\n--- Test Cases ---")
    passed = 0
    failed = 0
    
    for entity, expected_filter, reason in test_entities:
        result = filter_entity(entity)
        status = "PASS" if result == expected_filter else "FAIL"
        
        if result == expected_filter:
            passed += 1
        else:
            failed += 1
        
        action = "filtered" if result else "kept"
        print(f"[{status}] {entity}: {action} ({reason})")
    
    print("\n--- Summary ---")
    print(f"Total: {len(test_entities)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Pass Rate: {passed/len(test_entities)*100:.1f}%")
    
    if failed == 0:
        print("\n[PASS] All entity filter tests passed")
        return True
    else:
        print("\n[FAIL] Some tests failed")
        return False

if __name__ == "__main__":
    success = test_entity_filter_regex()
    sys.exit(0 if success else 1)