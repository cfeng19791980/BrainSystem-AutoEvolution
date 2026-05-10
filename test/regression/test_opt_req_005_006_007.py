# -*- coding: utf-8 -*-
"""
Regression Test for OPT-REQ-005/006/007 - Dual KB + Dual Brain
"""
import sys
from pathlib import Path

def test_dual_kb_dual_brain():
    """Test dual KB and dual brain architecture"""
    print("=" * 60)
    print("Regression Test: OPT-REQ-005/006/007")
    print("=" * 60)
    
    results = []
    
    # Test Issue Clusterer
    print("\n--- Issue Clusterer ---")
    try:
        import issue_clusterer
        clusterer = issue_clusterer.get_issue_clusterer()
        stats = clusterer.get_dual_kb_stats()
        print(f"Issue KB: {stats['issue_kb_count']}")
        print(f"PR Review KB: {stats['pr_review_kb_count']}")
        print("[PASS] Issue Clusterer initialized")
        results.append(True)
    except Exception as e:
        print(f"[FAIL] Issue Clusterer: {e}")
        results.append(False)
    
    # Test Dual Brain
    print("\n--- Dual Brain ---")
    try:
        import dual_brain
        exec_brain = dual_brain.get_execution_brain()
        evol_brain = dual_brain.get_evolution_brain()
        reviewer = dual_brain.get_patch_reviewer()
        
        status = exec_brain.get_status()
        print(f"Locked modules: {len(status['locked_modules'])}")
        
        # Test core module check
        is_core = exec_brain.is_core_module("brain_entry.py")
        print(f"brain_entry.py is core: {is_core}")
        
        if is_core:
            print("[PASS] Core module protection works")
        else:
            print("[FAIL] Core module should be protected")
            results.append(False)
        
        results.append(True)
    except Exception as e:
        print(f"[FAIL] Dual Brain: {e}")
        results.append(False)
    
    # Test Learning Source Expander
    print("\n--- Learning Source Expander ---")
    try:
        import learning_source_expander
        expander = learning_source_expander.get_learning_source_expander()
        stats = expander.get_all_kb_stats()
        print(f"Discussions: {stats['discussion_count']}")
        print(f"Changelogs: {stats['changelog_count']}")
        print("[PASS] Learning Source Expander initialized")
        results.append(True)
    except Exception as e:
        print(f"[FAIL] Learning Source Expander: {e}")
        results.append(False)
    
    # Summary
    print("\n--- Summary ---")
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n[PASS] All dual KB + dual brain tests passed")
        return True
    else:
        print("\n[FAIL] Some tests failed")
        return False

if __name__ == "__main__":
    BASE_DIR = Path(__file__).parent.parent
    sys.path.insert(0, str(BASE_DIR))
    sys.path.insert(0, str(BASE_DIR / "core"))
    success = test_dual_kb_dual_brain()
    sys.exit(0 if success else 1)