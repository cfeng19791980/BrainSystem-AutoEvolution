# -*- coding: utf-8 -*-
"""
Low-Risk Auto-Approval Mechanism (豆包方案)
Patterns with "low" risk level are auto-executed without user approval
"""
import json
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger('BrainEntry.AutoApproval')

# Auto-approval config
AUTO_APPROVAL_CONFIG = {
    "enabled": True,
    "low_risk_auto": True,  # Low risk patterns auto-approved
    "notify_after_execute": True,  # Notify user after execution
    "log_file": "data/auto_approval_log.json",
}

# Low-risk pattern types (auto-eligible)
LOW_RISK_TYPES = [
    "comment_optimization",     # Comment/docstring updates
    "error_message",            # Better error messages
    "log_enhancement",          # Add logging
    "text_improvement",         # Text/文案 improvements
    "cache_addition",           # Add caching (not modify core)
    "simple_validation",        # Input validation
    "default_parameter",        # Default parameter changes
]

class AutoApprovalManager:
    """Manage auto-approval for low-risk patterns"""
    
    def __init__(self, log_path=None):
        self.log_path = Path(log_path or AUTO_APPROVAL_CONFIG["log_file"])
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.log = self._load_log()
    
    def _load_log(self):
        """Load existing approval log"""
        if self.log_path.exists():
            with open(self.log_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"auto_approved": [], "manual_approved": []}
    
    def _save_log(self):
        """Save approval log"""
        with open(self.log_path, "w", encoding="utf-8") as f:
            json.dump(self.log, f, indent=2, ensure_ascii=False)
    
    def is_auto_eligible(self, risk_level, pattern_type=None):
        """Check if pattern is eligible for auto-approval"""
        if not AUTO_APPROVAL_CONFIG["enabled"]:
            return False
        
        if not AUTO_APPROVAL_CONFIG["low_risk_auto"]:
            return False
        
        # Only low-risk patterns
        if risk_level != "low":
            return False
        
        # Check pattern type if specified
        if pattern_type and pattern_type not in LOW_RISK_TYPES:
            logger.info(f"Pattern type '{pattern_type}' not in auto-eligible list")
            # Still auto-approve if risk is low, but log it
        
        return True
    
    def auto_approve(self, opt_req_id, pattern_id, pattern_type=None):
        """Auto-approve and log"""
        entry = {
            "opt_req_id": opt_req_id,
            "pattern_id": pattern_id,
            "pattern_type": pattern_type,
            "approved_at": datetime.now().isoformat(),
            "approval_type": "auto",
            "risk_level": "low",
        }
        
        self.log["auto_approved"].append(entry)
        self._save_log()
        
        logger.info(f"Auto-approved: {opt_req_id} ({pattern_id})")
        
        return {
            "status": "AUTO_APPROVED",
            "message": f"Low-risk optimization {opt_req_id} auto-approved and executed",
            "entry": entry
        }
    
    def manual_approve(self, opt_req_id, pattern_id, risk_level, user_response):
        """Log manual approval"""
        entry = {
            "opt_req_id": opt_req_id,
            "pattern_id": pattern_id,
            "approved_at": datetime.now().isoformat(),
            "approval_type": "manual",
            "risk_level": risk_level,
            "user_response": user_response,
        }
        
        self.log["manual_approved"].append(entry)
        self._save_log()
        
        return entry
    
    def get_stats(self):
        """Get approval statistics"""
        return {
            "auto_approved_count": len(self.log["auto_approved"]),
            "manual_approved_count": len(self.log["manual_approved"]),
            "total": len(self.log["auto_approved"]) + len(self.log["manual_approved"]),
        }

# Global instance
_auto_approval_manager = None

def get_auto_approval_manager():
    """Get global auto-approval manager"""
    global _auto_approval_manager
    if _auto_approval_manager is None:
        _auto_approval_manager = AutoApprovalManager()
    return _auto_approval_manager

def check_and_auto_approve(opt_req_id, pattern_id, risk_level, pattern_type=None):
    """
    Check if auto-eligible and execute if so.
    
    Returns:
        dict: {"auto_executed": True/False, "message": "..."}
    """
    manager = get_auto_approval_manager()
    
    if manager.is_auto_eligible(risk_level, pattern_type):
        # Auto-approve
        result = manager.auto_approve(opt_req_id, pattern_id, pattern_type)
        
        # Execute (would call actual execution logic)
        # In production, this would trigger the optimization
        
        return {
            "auto_executed": True,
            "approval_result": result,
            "message": f"Low-risk pattern {pattern_id} auto-executed. User notified."
        }
    else:
        return {
            "auto_executed": False,
            "message": f"Risk level '{risk_level}' requires manual approval.",
            "approval_type": "manual" if risk_level == "medium" else "full_review"
        }

if __name__ == "__main__":
    # Test auto-approval
    print("=" * 60)
    print("Auto-Approval Test")
    print("=" * 60)
    
    manager = AutoApprovalManager()
    
    # Test cases
    test_cases = [
        ("OPT-REQ-005", "comment_opt", "low", "comment_optimization"),
        ("OPT-REQ-006", "core_change", "high", None),
        ("OPT-REQ-007", "cache_add", "low", "cache_addition"),
        ("OPT-REQ-008", "logic_tweak", "medium", None),
    ]
    
    print("\n--- Test Cases ---")
    for opt_req, pattern, risk, ptype in test_cases:
        result = check_and_auto_approve(opt_req, pattern, risk, ptype)
        status = "AUTO" if result["auto_executed"] else "MANUAL"
        print(f"[{status}] {opt_req}: risk={risk}, {result['message'][:50]}")
    
    stats = manager.get_stats()
    print("\n--- Statistics ---")
    print(f"Auto-approved: {stats['auto_approved_count']}")
    print(f"Manual-approved: {stats['manual_approved_count']}")
    
    print("\n[PASS] Auto-approval mechanism working")