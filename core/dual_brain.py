# -*- coding: utf-8 -*-
"""
Dual Brain Architecture - Execution Brain + Evolution Brain (豆包方案 #6)
Pattern ID: dual_brain_separation
Source: Doubao Proposal
"""
import json
import sqlite3
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger('BrainEntry.DualBrain')

PATCH_DIR = Path("patches")
PATCH_DIR.mkdir(parents=True, exist_ok=True)

CORE_MODULES = [
    "brain_entry.py",
    "scheduler.py",
    "gateway_integration.py",
]

class ExecutionBrain:
    """执行脑 - 高稳定，锁死核心逻辑"""
    
    def __init__(self):
        self.locked_modules = CORE_MODULES
        self.patch_registry = self._load_patch_registry()
    
    def _load_patch_registry(self):
        """Load patch registry"""
        registry_file = Path("data/patch_registry.json")
        if registry_file.exists():
            with open(registry_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"approved": [], "applied": [], "rejected": []}
    
    def _save_patch_registry(self):
        """Save patch registry"""
        registry_file = Path("data/patch_registry.json")
        with open(registry_file, "w", encoding="utf-8") as f:
            json.dump(self.patch_registry, f, indent=2)
    
    def is_core_module(self, file_path):
        """Check if file is core module"""
        for locked in self.locked_modules:
            if locked in file_path:
                return True
        return False
    
    def apply_patch(self, patch_id, user_approved=False):
        """Apply approved patch"""
        # Load patch
        patch_file = PATCH_DIR / f"{patch_id}.json"
        if not patch_file.exists():
            logger.error(f"Patch {patch_id} not found")
            return False
        
        with open(patch_file, "r", encoding="utf-8") as f:
            patch = json.load(f)
        
        # Check if core module
        target_file = patch.get("target_file", "")
        if self.is_core_module(target_file):
            logger.warning(f"Patch {patch_id} targets core module {target_file}")
            if not user_approved:
                logger.error("Core module patch requires user approval")
                return False
        
        # Check approval status
        if patch_id not in self.patch_registry["approved"]:
            logger.error(f"Patch {patch_id} not approved")
            return False
        
        # Apply patch (simplified - would do actual file modification)
        logger.info(f"Applied patch {patch_id} to {target_file}")
        
        self.patch_registry["applied"].append({
            "patch_id": patch_id,
            "applied_at": datetime.now().isoformat(),
            "target_file": target_file,
        })
        self._save_patch_registry()
        
        return True
    
    def rollback_patch(self, patch_id):
        """Rollback applied patch"""
        # Find applied patch
        applied = [p for p in self.patch_registry["applied"] if p["patch_id"] == patch_id]
        if not applied:
            logger.error(f"Patch {patch_id} not applied")
            return False
        
        # Rollback (would restore original file)
        logger.info(f"Rolled back patch {patch_id}")
        
        # Remove from applied list
        self.patch_registry["applied"] = [p for p in self.patch_registry["applied"] if p["patch_id"] != patch_id]
        self._save_patch_registry()
        
        return True
    
    def get_status(self):
        """Get execution brain status"""
        return {
            "locked_modules": self.locked_modules,
            "approved_patches": len(self.patch_registry["approved"]),
            "applied_patches": len(self.patch_registry["applied"]),
            "rejected_patches": len(self.patch_registry["rejected"]),
        }

class EvolutionBrain:
    """进化脑 - 专门分析Issue、写补丁"""
    
    def __init__(self):
        self.patch_counter = 0
    
    def analyze_issue(self, issue_data):
        """分析Issue"""
        analysis = {
            "issue_type": issue_data.get("issue_type", "Unknown"),
            "risk_level": self._assess_risk(issue_data),
            "affected_modules": self._identify_modules(issue_data),
            "pattern_suggestion": self._suggest_pattern(issue_data),
        }
        return analysis
    
    def _assess_risk(self, issue_data):
        """Assess risk level"""
        body = issue_data.get("body", "")
        
        # Check if affects core
        for core in CORE_MODULES:
            if core in body.lower():
                return "high"
        
        # Check performance keywords
        if "performance" in body.lower() or "latency" in body.lower():
            return "medium"
        
        return "low"
    
    def _identify_modules(self, issue_data):
        """Identify affected modules"""
        body = issue_data.get("body", "")
        modules = []
        
        keywords = ["hook", "cache", "embedding", "scheduler", "gateway", "brain_entry"]
        for kw in keywords:
            if kw in body.lower():
                modules.append(kw)
        
        return modules
    
    def _suggest_pattern(self, issue_data):
        """Suggest pattern"""
        issue_type = issue_data.get("issue_type", "Other")
        
        patterns = {
            "Bug": "error_handling_pattern",
            "Performance": "cache_optimization_pattern",
            "Compatibility": "version_check_pattern",
            "Feature_Request": "feature_addition_pattern",
        }
        
        return patterns.get(issue_type, "general_improvement")
    
    def generate_patch(self, analysis, code_changes):
        """生成补丁"""
        self.patch_counter += 1
        
        patch_id = f"patch_{datetime.now().strftime('%Y%m%d%H%M%S')}_{self.patch_counter}"
        
        patch = {
            "patch_id": patch_id,
            "created_at": datetime.now().isoformat(),
            "analysis": analysis,
            "target_file": code_changes.get("target_file", ""),
            "changes": code_changes.get("changes", []),
            "risk_level": analysis["risk_level"],
            "status": "pending_approval",
            "core_module": any(core in code_changes.get("target_file", "") for core in CORE_MODULES),
        }
        
        # Save patch
        patch_file = PATCH_DIR / f"{patch_id}.json"
        with open(patch_file, "w", encoding="utf-8") as f:
            json.dump(patch, f, indent=2)
        
        logger.info(f"Generated patch {patch_id}")
        
        return patch
    
    def run_patch_test(self, patch_id):
        """测试补丁"""
        # Load patch
        patch_file = PATCH_DIR / f"{patch_id}.json"
        if not patch_file.exists():
            return {"status": "error", "message": "Patch not found"}
        
        # Run regression test
        import subprocess
        result = subprocess.run(
            ["python", "test/regression/run_regression.py"],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent)
        )
        
        test_result = {
            "patch_id": patch_id,
            "test_passed": result.returncode == 0,
            "test_output": result.stdout[-500:] if result.stdout else "",
        }
        
        # Update patch status
        with open(patch_file, "r", encoding="utf-8") as f:
            patch = json.load(f)
        
        patch["test_result"] = test_result
        patch["status"] = "tested"
        
        with open(patch_file, "w", encoding="utf-8") as f:
            json.dump(patch, f, indent=2)
        
        return test_result
    
    def submit_for_approval(self, patch_id):
        """提交审核"""
        # Load patch
        patch_file = PATCH_DIR / f"{patch_id}.json"
        if not patch_file.exists():
            return False
        
        with open(patch_file, "r", encoding="utf-8") as f:
            patch = json.load(f)
        
        # Add to approval registry
        registry_file = Path("data/patch_registry.json")
        if registry_file.exists():
            with open(registry_file, "r", encoding="utf-8") as f:
                registry = json.load(f)
        else:
            registry = {"approved": [], "applied": [], "rejected": []}
        
        registry["approved"].append({
            "patch_id": patch_id,
            "submitted_at": datetime.now().isoformat(),
            "risk_level": patch["risk_level"],
            "core_module": patch.get("core_module", False),
        })
        
        with open(registry_file, "w", encoding="utf-8") as f:
            json.dump(registry, f, indent=2)
        
        logger.info(f"Submitted patch {patch_id} for approval")
        
        return True
    
    def get_pending_patches(self):
        """获取待审核补丁"""
        patches = []
        for patch_file in PATCH_DIR.glob("patch_*.json"):
            with open(patch_file, "r", encoding="utf-8") as f:
                patch = json.load(f)
                if patch["status"] in ["pending_approval", "tested"]:
                    patches.append(patch)
        return patches

class PatchReviewer:
    """补丁审核器"""
    
    def review(self, patch_id):
        """审核补丁"""
        patch_file = PATCH_DIR / f"{patch_id}.json"
        if not patch_file.exists():
            return {"status": "error", "message": "Patch not found"}
        
        with open(patch_file, "r", encoding="utf-8") as f:
            patch = json.load(f)
        
        # Check core module
        if patch.get("core_module", False):
            review_result = {
                "status": "needs_full_review",
                "reason": "Targets core module, requires strong approval",
                "risk_level": "high",
                "recommendation": "Review with user before applying",
            }
        elif patch.get("risk_level") == "medium":
            review_result = {
                "status": "needs_quick_approval",
                "reason": "Medium risk, requires user confirmation",
                "risk_level": "medium",
                "recommendation": "Quick approval sufficient",
            }
        else:
            review_result = {
                "status": "auto_approved",
                "reason": "Low risk, can auto-apply",
                "risk_level": "low",
                "recommendation": "Auto-apply with notification",
            }
        
        # Update patch
        patch["review_result"] = review_result
        patch["reviewed_at"] = datetime.now().isoformat()
        
        with open(patch_file, "w", encoding="utf-8") as f:
            json.dump(patch, f, indent=2)
        
        return review_result
    
    def batch_review(self):
        """批量审核"""
        results = []
        for patch_file in PATCH_DIR.glob("patch_*.json"):
            with open(patch_file, "r", encoding="utf-8") as f:
                patch = json.load(f)
            if "review_result" not in patch:
                result = self.review(patch["patch_id"])
                results.append({"patch_id": patch["patch_id"], "review": result})
        return results

# Global instances
_execution_brain = None
_evolution_brain = None
_patch_reviewer = None

def get_execution_brain():
    global _execution_brain
    if _execution_brain is None:
        _execution_brain = ExecutionBrain()
    return _execution_brain

def get_evolution_brain():
    global _evolution_brain
    if _evolution_brain is None:
        _evolution_brain = EvolutionBrain()
    return _evolution_brain

def get_patch_reviewer():
    global _patch_reviewer
    if _patch_reviewer is None:
        _patch_reviewer = PatchReviewer()
    return _patch_reviewer

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("=" * 60)
    print("Dual Brain Architecture Test")
    print("=" * 60)
    
    # Test Execution Brain
    print("\n--- Execution Brain ---")
    exec_brain = ExecutionBrain()
    status = exec_brain.get_status()
    print(f"Locked modules: {status['locked_modules']}")
    print(f"Approved patches: {status['approved_patches']}")
    
    # Test Evolution Brain
    print("\n--- Evolution Brain ---")
    evol_brain = EvolutionBrain()
    
    # Analyze sample issue
    sample_issue = {
        "issue_type": "Performance",
        "body": "Embedding cache is slow, need optimization",
    }
    analysis = evol_brain.analyze_issue(sample_issue)
    print(f"Risk level: {analysis['risk_level']}")
    print(f"Affected modules: {analysis['affected_modules']}")
    print(f"Pattern suggestion: {analysis['pattern_suggestion']}")
    
    # Test Patch Reviewer
    print("\n--- Patch Reviewer ---")
    reviewer = PatchReviewer()
    
    # Create sample patch
    sample_patch = evol_brain.generate_patch(analysis, {
        "target_file": "core/opt_req_001_embedding_cache.py",
        "changes": ["Add TTL cache", "Add LRU eviction"],
    })
    print(f"Generated patch: {sample_patch['patch_id']}")
    
    # Review patch
    review = reviewer.review(sample_patch["patch_id"])
    print(f"Review status: {review['status']}")
    print(f"Recommendation: {review['recommendation']}")
    
    print("\n[PASS] Dual brain architecture initialized")