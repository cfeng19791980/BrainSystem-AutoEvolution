# -*- coding: utf-8 -*-
"""
BrainSystem Regression Test Runner
Auto-run all regression tests after self-evolution updates
"""
import sys
import os
import subprocess
import json
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

REGRESSION_DIR = Path(__file__).parent
RESULTS_FILE = Path(__file__).parent.parent / "data" / "regression_results.json"

def run_single_test(test_file):
    """Run a single regression test file"""
    result = {
        "file": test_file.name,
        "status": "unknown",
        "duration_ms": 0,
        "error": None
    }
    
    start_time = datetime.now()
    
    try:
        proc = subprocess.run(
            [sys.executable, str(test_file)],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(test_file.parent)
        )
        
        duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        result["duration_ms"] = round(duration_ms, 2)
        
        if proc.returncode == 0:
            result["status"] = "pass"
            # Extract pass/fail from output
            if "[PASS]" in proc.stdout:
                result["status"] = "pass"
            elif "[FAIL]" in proc.stdout:
                result["status"] = "fail"
                result["error"] = "Test assertion failed"
        else:
            result["status"] = "fail"
            result["error"] = proc.stderr[:500] if proc.stderr else "Unknown error"
            
    except subprocess.TimeoutExpired:
        result["status"] = "timeout"
        result["error"] = "Test exceeded 60s timeout"
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)[:200]
    
    return result

def run_all_regression_tests():
    """Run all regression tests in the directory"""
    print("=" * 60)
    print("BrainSystem Regression Test Suite")
    print("=" * 60)
    
    # Find all test files
    test_files = list(REGRESSION_DIR.glob("test_*.py"))
    
    if not test_files:
        print("No regression tests found!")
        return {"total": 0, "passed": 0, "failed": 0, "tests": []}
    
    print(f"\nFound {len(test_files)} regression tests")
    
    results = {
        "run_time": datetime.now().isoformat(),
        "total": len(test_files),
        "passed": 0,
        "failed": 0,
        "tests": []
    }
    
    for test_file in sorted(test_files):
        print(f"\nRunning: {test_file.name}...")
        result = run_single_test(test_file)
        results["tests"].append(result)
        
        if result["status"] == "pass":
            results["passed"] += 1
            print(f"  [PASS] {result['duration_ms']}ms")
        else:
            results["failed"] += 1
            print(f"  [{result['status'].upper()}] {result['error'][:100]}")
    
    # Summary
    print("\n" + "=" * 60)
    print(f"Regression Test Summary")
    print(f"  Total: {results['total']}")
    print(f"  Passed: {results['passed']}")
    print(f"  Failed: {results['failed']}")
    print(f"  Pass Rate: {results['passed']/results['total']*100:.1f}%")
    print("=" * 60)
    
    # Save results
    save_results(results)
    
    return results

def save_results(results):
    """Save regression results to JSON"""
    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\nResults saved to: {RESULTS_FILE}")

def check_regression_status():
    """Check if last regression passed"""
    if not RESULTS_FILE.exists():
        return None
    
    with open(RESULTS_FILE, "r", encoding="utf-8") as f:
        results = json.load(f)
    
    return results.get("failed", 0) == 0

if __name__ == "__main__":
    results = run_all_regression_tests()
    
    # Return exit code based on results
    if results["failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)