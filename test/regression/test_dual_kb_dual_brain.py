# -*- coding: utf-8 -*-
"""
Regression Test for OPT-REQ-005/006/007 - Simplified
"""
import sys
import sqlite3
from pathlib import Path

BASE_DIR = Path(r"C:\Users\Administrator\.openclaw\brain-system")

def test_dual_kb_dual_brain():
    """Test dual KB and dual brain databases"""
    print("=" * 60)
    print("Regression Test: OPT-REQ-005/006/007")
    print("=" * 60)
    
    results = []
    
    # Test Issue KB
    print("\n--- Issue KB Database ---")
    issue_kb = BASE_DIR / "data" / ".issue_kb.db"
    if issue_kb.exists():
        conn = sqlite3.connect(str(issue_kb))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"Tables: {[t[0] for t in tables]}")
        print("[PASS] Issue KB database exists")
        conn.close()
        results.append(True)
    else:
        print("[FAIL] Issue KB database not found")
        results.append(False)
    
    # Test PR Review KB
    print("\n--- PR Review KB Database ---")
    pr_kb = BASE_DIR / "data" / ".pr_review_kb.db"
    if pr_kb.exists():
        conn = sqlite3.connect(str(pr_kb))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"Tables: {[t[0] for t in tables]}")
        print("[PASS] PR Review KB database exists")
        conn.close()
        results.append(True)
    else:
        print("[FAIL] PR Review KB database not found")
        results.append(False)
    
    # Test Discussion KB
    print("\n--- Discussion KB Database ---")
    disc_kb = BASE_DIR / "data" / ".discussion_kb.db"
    if disc_kb.exists():
        conn = sqlite3.connect(str(disc_kb))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"Tables: {[t[0] for t in tables]}")
        print("[PASS] Discussion KB database exists")
        conn.close()
        results.append(True)
    else:
        print("[FAIL] Discussion KB database not found")
        results.append(False)
    
    # Test Changelog KB
    print("\n--- Changelog KB Database ---")
    cl_kb = BASE_DIR / "data" / ".changelog_kb.db"
    if cl_kb.exists():
        conn = sqlite3.connect(str(cl_kb))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"Tables: {[t[0] for t in tables]}")
        print("[PASS] Changelog KB database exists")
        conn.close()
        results.append(True)
    else:
        print("[FAIL] Changelog KB database not found")
        results.append(False)
    
    # Test Evolution KB
    print("\n--- Evolution KB Database ---")
    evol_kb = BASE_DIR / "data" / ".evolution_kg.db"
    if evol_kb.exists():
        conn = sqlite3.connect(str(evol_kb))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"Tables: {[t[0] for t in tables]}")
        print("[PASS] Evolution KB database exists")
        conn.close()
        results.append(True)
    else:
        print("[FAIL] Evolution KB database not found")
        results.append(False)
    
    # Test Patch Registry
    print("\n--- Patch Registry ---")
    patch_reg = BASE_DIR / "data" / "patch_registry.json"
    if patch_reg.exists():
        print("[PASS] Patch registry exists")
        results.append(True)
    else:
        print("[FAIL] Patch registry not found")
        results.append(False)
    
    # Test Patches Directory
    print("\n--- Patches Directory ---")
    patches_dir = BASE_DIR / "patches"
    if patches_dir.exists():
        patches = list(patches_dir.glob("patch_*.json"))
        print(f"Patches found: {len(patches)}")
        print("[PASS] Patches directory exists")
        results.append(True)
    else:
        print("[FAIL] Patches directory not found")
        results.append(False)
    
    # Summary
    print("\n--- Summary ---")
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n[PASS] All dual KB + dual brain databases created")
        return True
    else:
        print("\n[FAIL] Some databases missing")
        return False

if __name__ == "__main__":
    success = test_dual_kb_dual_brain()
    sys.exit(0 if success else 1)