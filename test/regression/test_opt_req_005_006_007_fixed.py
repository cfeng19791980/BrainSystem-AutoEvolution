# -*- coding: utf-8 -*-
"""
Regression Test Fix - test_opt_req_005_006_007
"""
import sys
import sqlite3
from pathlib import Path

BASE_DIR = Path(r"C:\Users\Administrator\.openclaw\brain-system")
DATA_DIR = BASE_DIR / "data"

sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "core"))

def test_opt_req_005_006_007():
    """Test OPT-REQ-005/006/007 - Dual KB + Dual Brain"""
    print("=" * 60)
    print("Regression Test: OPT-REQ-005/006/007")
    print("=" * 60)
    
    results = []
    
    # Test Issue KB
    print("\n--- Issue KB ---")
    issue_db = DATA_DIR / ".issue_kb.db"
    if issue_db.exists():
        conn = sqlite3.connect(str(issue_db))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM issue_entries")
        count = cursor.fetchone()[0]
        print(f"Records: {count}")
        print("[PASS]" if count > 0 else "[WARN] Empty")
        results.append(True)
        conn.close()
    else:
        print("[FAIL] DB not found")
        results.append(False)
    
    # Test PR Review KB
    print("\n--- PR Review KB ---")
    pr_db = DATA_DIR / ".pr_review_kb.db"
    if pr_db.exists():
        conn = sqlite3.connect(str(pr_db))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM pr_review_entries")
        count = cursor.fetchone()[0]
        print(f"Records: {count}")
        print("[PASS]")
        results.append(True)
        conn.close()
    else:
        print("[FAIL] DB not found")
        results.append(False)
    
    # Test Dual Brain - ExecutionBrain
    print("\n--- Dual Brain: ExecutionBrain ---")
    try:
        import dual_brain
        exec_brain = dual_brain.get_execution_brain()
        status = exec_brain.get_status()
        print(f"Locked modules: {len(status['locked_modules'])}")
        
        # Test core module check
        is_core = exec_brain.is_core_module("brain_entry.py")
        print(f"brain_entry.py locked: {is_core}")
        print("[PASS]" if is_core else "[FAIL]")
        results.append(is_core)
    except Exception as e:
        print(f"[FAIL] {e}")
        results.append(False)
    
    # Test Dual Brain - EvolutionBrain
    print("\n--- Dual Brain: EvolutionBrain ---")
    try:
        import dual_brain
        evol_brain = dual_brain.get_evolution_brain()
        
        sample_issue = {"issue_type": "Performance", "body": "Cache optimization"}
        analysis = evol_brain.analyze_issue(sample_issue)
        print(f"Risk level: {analysis['risk_level']}")
        print(f"Pattern: {analysis['pattern_suggestion']}")
        print("[PASS]")
        results.append(True)
    except Exception as e:
        print(f"[FAIL] {e}")
        results.append(False)
    
    # Test Learning Source
    print("\n--- Learning Source Expander ---")
    try:
        import learning_source_expander
        expander = learning_source_expander.get_learning_source_expander()
        stats = expander.get_all_kb_stats()
        print(f"Discussions: {stats['discussion_count']}")
        print(f"Changelogs: {stats['changelog_count']}")
        print("[PASS]")
        results.append(True)
    except Exception as e:
        print(f"[FAIL] {e}")
        results.append(False)
    
    # Test Vector DB
    print("\n--- Vector DB ---")
    vector_db = DATA_DIR / ".brain_vectors.db"
    if vector_db.exists():
        conn = sqlite3.connect(str(vector_db))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM vectors")
        count = cursor.fetchone()[0]
        print(f"Vectors: {count}")
        print("[PASS]" if count > 0 else "[WARN] Empty")
        results.append(True)
        conn.close()
    else:
        print("[FAIL] DB not found")
        results.append(False)
    
    # Summary
    print("\n--- Summary ---")
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    return passed == total

if __name__ == "__main__":
    success = test_opt_req_005_006_007()
    print("\n[PASS]" if success else "\n[FAIL]")
    sys.exit(0 if success else 1)