# -*- coding: utf-8 -*-
"""
Evolution Logger - Private Growth Knowledge Base (豆包方案 #8)
Records self-evolution history for closed-loop memory
"""
import json
import sqlite3
import logging
from datetime import datetime
from pathlib import Path

_log = logging.getLogger('BrainEntry.EvolutionLogger')

EVOLUTION_LOG_DIR = Path("data/evolution_history")
EVOLUTION_LOG_DIR.mkdir(parents=True, exist_ok=True)

EVOLUTION_KG_DB = Path(__file__).parent.parent / "data" / ".evolution_kg.db"

class EvolutionLogger:
    """Evolution Logger - Records self-evolution history"""
    
    def __init__(self):
        self._init_kg_db()
    
    def _init_kg_db(self):
        """Initialize evolution KG database"""
        if not EVOLUTION_KG_DB.exists():
            conn = sqlite3.connect(str(EVOLUTION_KG_DB))
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute('''CREATE TABLE evolution_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                opt_req_id TEXT,
                pattern_id TEXT,
                issue_link TEXT,
                effect TEXT,
                error TEXT,
                lesson TEXT,
                timestamp TEXT NOT NULL,
                rollback_needed INTEGER DEFAULT 0,
                version TEXT
            )''')
            
            cursor.execute('''CREATE TABLE evolution_embeddings (
                entry_id INTEGER PRIMARY KEY,
                embedding TEXT,
                FOREIGN KEY (entry_id) REFERENCES evolution_entries(id)
            )''')
            
            conn.commit()
            conn.close()
            _log.info("Created evolution KG database")
    
    def log_success(self, opt_req_id, pattern_id, effect, issue_link=None, version=None):
        """Log successful evolution"""
        entry = {
            "type": "success",
            "opt_req_id": opt_req_id,
            "pattern_id": pattern_id,
            "effect": effect,
            "issue_link": issue_link or "",
            "timestamp": datetime.now().isoformat(),
            "version": version or "v1.0.0",
            "rollback_needed": 0,
        }
        
        self._save_entry(entry)
        self._save_to_file(entry, "success")
        
        import logging
        log = logging.getLogger('BrainEntry.EvolutionLogger')
        log.info(f"Logged success: {opt_req_id} ({pattern_id})")
        
        return entry
    
    def log_failure(self, opt_req_id, error, rollback_needed=False, lesson=None, version=None):
        """Log failed evolution with复盘"""
        entry = {
            "type": "failure",
            "opt_req_id": opt_req_id,
            "error": error,
            "lesson": lesson or self._extract_lesson(error),
            "timestamp": datetime.now().isoformat(),
            "version": version or "v1.0.0",
            "rollback_needed": 1 if rollback_needed else 0,
        }
        
        self._save_entry(entry)
        self._save_to_file(entry, "failure")
        
        import logging
        log = logging.getLogger('BrainEntry.EvolutionLogger')
        log.warning(f"Logged failure: {opt_req_id} (rollback={rollback_needed})")
        
        return entry
    
    def _extract_lesson(self, error):
        """Extract lesson from error"""
        lessons = {
            "column": "Check database schema before INSERT",
            "encoding": "Use UTF-8 encoding in all Python scripts",
            "import": "Clear __pycache__ when adding new routes",
            "timeout": "Add timeout handling for long operations",
            "permission": "Check file permissions before write",
        }
        
        for key, lesson in lessons.items():
            if key in str(error).lower():
                return lesson
        
        return "General error handling needed"
    
    def _save_entry(self, entry):
        """Save entry to KG database"""
        conn = sqlite3.connect(str(EVOLUTION_KG_DB))
        cursor = conn.cursor()
        
        cursor.execute('''INSERT INTO evolution_entries (
            type, opt_req_id, pattern_id, issue_link, effect, error, lesson,
            timestamp, rollback_needed, version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
            entry["type"],
            entry.get("opt_req_id", ""),
            entry.get("pattern_id", ""),
            entry.get("issue_link", ""),
            entry.get("effect", ""),
            entry.get("error", ""),
            entry.get("lesson", ""),
            entry["timestamp"],
            entry.get("rollback_needed", 0),
            entry.get("version", "v1.0.0"),
        ))
        
        entry_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return entry_id
    
    def _save_to_file(self, entry, entry_type):
        """Save entry to file log"""
        log_file = EVOLUTION_LOG_DIR / f"{entry_type}_log.json"
        
        logs = []
        if log_file.exists():
            with open(log_file, "r", encoding="utf-8") as f:
                logs = json.load(f)
        
        logs.append(entry)
        
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
    
    def search_history(self, query, limit=10):
        """Search evolution history"""
        conn = sqlite3.connect(str(EVOLUTION_KG_DB))
        cursor = conn.cursor()
        
        # Simple keyword search
        cursor.execute('''SELECT * FROM evolution_entries 
            WHERE opt_req_id LIKE ? OR pattern_id LIKE ? OR error LIKE ? OR lesson LIKE ?
            ORDER BY timestamp DESC LIMIT ?''', 
            (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%", limit))
        
        results = cursor.fetchall()
        conn.close()
        
        entries = []
        for r in results:
            entries.append({
                "id": r[0],
                "type": r[1],
                "opt_req_id": r[2],
                "pattern_id": r[3],
                "issue_link": r[4],
                "effect": r[5],
                "error": r[6],
                "lesson": r[7],
                "timestamp": r[8],
                "rollback_needed": r[9],
                "version": r[10],
            })
        
        return entries
    
    def get_similar_cases(self, opt_req_id, limit=5):
        """Find similar historical cases"""
        # Extract pattern from opt_req_id
        pattern = opt_req_id.split("-")[-1] if "-" in opt_req_id else opt_req_id
        
        return self.search_history(pattern, limit)
    
    def get_statistics(self):
        """Get evolution statistics"""
        conn = sqlite3.connect(str(EVOLUTION_KG_DB))
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM evolution_entries WHERE type='success'")
        success_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM evolution_entries WHERE type='failure'")
        failure_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM evolution_entries WHERE rollback_needed=1")
        rollback_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total": success_count + failure_count,
            "success": success_count,
            "failure": failure_count,
            "rollback_needed": rollback_count,
            "success_rate": success_count / (success_count + failure_count) if (success_count + failure_count) > 0 else 0,
        }
    
    def generate_report(self):
        """Generate evolution history report"""
        stats = self.get_statistics()
        
        report = f"""# Evolution History Report

## Statistics

| Metric | Value |
|--------|-------|
| Total Evolutions | {stats['total']} |
| Success | {stats['success']} |
| Failure | {stats['failure']} |
| Rollback Needed | {stats['rollback_needed']} |
| Success Rate | {stats['success_rate']:.1%} |

## Recent Success Entries

"""
        
        successes = self.search_history("", limit=5)
        for entry in [e for e in successes if e["type"] == "success"]:
            report += f"- {entry['opt_req_id']}: {entry['pattern_id']} ({entry['effect']})\n"
        
        report += "\n## Lessons Learned\n\n"
        
        conn = sqlite3.connect(str(EVOLUTION_KG_DB))
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT lesson FROM evolution_entries WHERE lesson IS NOT NULL AND lesson != ''")
        lessons = cursor.fetchall()
        conn.close()
        
        for lesson in lessons[:10]:
            report += f"- {lesson[0]}\n"
        
        return report

# Global instance
_evolution_logger = None

def get_evolution_logger():
    """Get global evolution logger"""
    global _evolution_logger
    if _evolution_logger is None:
        _evolution_logger = EvolutionLogger()
    return _evolution_logger

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("=" * 60)
    print("Evolution Logger Test")
    print("=" * 60)
    
    logger = EvolutionLogger()
    
    # Test logging
    print("\n--- Test Success Log ---")
    logger.log_success(
        opt_req_id="OPT-REQ-001",
        pattern_id="embedding_auto_cache",
        effect="-47.6% latency",
        issue_link="https://github.com/typesense/typesense/issues/1932"
    )
    
    print("\n--- Test Failure Log ---")
    logger.log_failure(
        opt_req_id="OPT-REQ-TEST",
        error="column mismatch: table has 22 columns",
        rollback_needed=True
    )
    
    print("\n--- Test Search ---")
    results = logger.search_history("embedding")
    print(f"Found {len(results)} entries for 'embedding'")
    
    print("\n--- Statistics ---")
    stats = logger.get_statistics()
    for k, v in stats.items():
        print(f"{k}: {v}")
    
    print("\n--- Report ---")
    report = logger.generate_report()
    print(report[:500])
    
    print("\n[PASS] Evolution logger working")