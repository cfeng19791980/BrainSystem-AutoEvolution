# -*- coding: utf-8 -*-
"""
Regression Test for OPT-REQ-004 - ZZ500 History Fetch
Pattern: zz500_history_fetch
Source: csi10 internal
"""
import sys
import sqlite3
from pathlib import Path

DB_PATH = Path(r"E:\csi10\stocks.db")

def test_zz500_history_fetch():
    """Test zz500_history_fetch pattern"""
    print("=" * 60)
    print("Regression Test: OPT-REQ-004 (zz500_history_fetch)")
    print("=" * 60)
    
    if not DB_PATH.exists():
        print("\n[SKIP] Database not found - skipping test")
        return True  # Skip but don't fail
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Check ZZ500 data count
    print("\n--- Checking ZZ500 Data ---")
    
    cursor.execute("SELECT COUNT(*) FROM index_daily WHERE code='sh.000905'")
    count = cursor.fetchone()[0]
    print(f"ZZ500 records: {count}")
    
    # Check if we have at least 5 days
    if count < 5:
        print("\n[FAIL] ZZ500 data insufficient (need >= 5)")
        conn.close()
        return False
    
    # Get last 5 records
    cursor.execute("""
        SELECT date, close, pct_chg 
        FROM index_daily 
        WHERE code='sh.000905' 
        ORDER BY date DESC LIMIT 5
    """)
    rows = cursor.fetchall()
    
    print("\n--- ZZ500 Last 5 Days ---")
    for r in rows:
        print(f"  {r[0]}: close={r[1]:.2f}, pct={r[2]:.2f}%")
    
    # Calculate 5-day pct
    latest_close = rows[0][1]
    fifth_close = rows[4][1]
    pct_5d = (latest_close - fifth_close) / fifth_close * 100
    
    print(f"\nZZ500 5-day change: {pct_5d:.2f}%")
    
    # Check if pct_5d is valid (not 0)
    if pct_5d == 0:
        print("\n[FAIL] pct_5d is 0 - data may be incorrect")
        conn.close()
        return False
    
    conn.close()
    
    print("\n--- Summary ---")
    print(f"Data count: {count} (>= 5)")
    print(f"pct_5d: {pct_5d:.2f}% (not 0)")
    
    print("\n[PASS] ZZ500 history data is valid")
    return True

if __name__ == "__main__":
    success = test_zz500_history_fetch()
    sys.exit(0 if success else 1)