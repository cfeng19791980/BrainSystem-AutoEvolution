# -*- coding: utf-8 -*-
"""
Issue Clusterer - Batch crawl and semantic clustering (豆包方案 #3)
Pattern ID: issue_batch_clustering
Source: Doubao Proposal + User Dual-KB Enhancement
"""
import json
import sqlite3
import logging
import requests
from datetime import datetime
from pathlib import Path
from collections import defaultdict

logger = logging.getLogger('BrainEntry.IssueClusterer')

# Target repositories (whitelist)
REPO_WHITELIST = [
    "ragas",           # RAG evaluation
    "typesense",       # Vector search
    "milvus",          # Vector DB
    "ragflow",         # RAG framework
    "langchain",       # LLM framework
    "llamaindex",      # Data framework
]

ISSUE_KB_DB = Path(r"C:\Users\Administrator\.openclaw\brain-system\data\.issue_kb.db")
PR_REVIEW_KB_DB = Path(r"C:\Users\Administrator\.openclaw\brain-system\data\.pr_review_kb.db")

class IssueClusterer:
    """Issue聚类器 - 双库进化架构"""
    
    def __init__(self):
        self._init_issue_kb()
        self._init_pr_review_kb()
    
    def _init_issue_kb(self):
        """Initialize Issue knowledge base"""
        if not ISSUE_KB_DB.exists():
            conn = sqlite3.connect(str(ISSUE_KB_DB))
            cursor = conn.cursor()
            
            cursor.execute('''CREATE TABLE issue_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                repo TEXT NOT NULL,
                issue_number INTEGER,
                title TEXT,
                body TEXT,
                issue_type TEXT,
                core_symptom TEXT,
                trigger_condition TEXT,
                risk_points TEXT,
                state TEXT,
                created_at TEXT,
                closed_at TEXT,
                url TEXT,
                embedding TEXT
            )''')
            
            cursor.execute('''CREATE TABLE issue_clusters (
                cluster_id INTEGER PRIMARY KEY AUTOINCREMENT,
                cluster_type TEXT,
                common_pattern TEXT,
                issue_ids TEXT,
                created_at TEXT
            )''')
            
            conn.commit()
            conn.close()
            logger.info("Created Issue KB database")
    
    def _init_pr_review_kb(self):
        """Initialize PR Review knowledge base (User Enhancement)"""
        if not PR_REVIEW_KB_DB.exists():
            conn = sqlite3.connect(str(PR_REVIEW_KB_DB))
            cursor = conn.cursor()
            
            cursor.execute('''CREATE TABLE pr_review_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                repo TEXT NOT NULL,
                pr_number INTEGER,
                comment_type TEXT,
                change_scope TEXT,
                core_controversy TEXT,
                rejection_reason TEXT,
                best_practice TEXT,
                hard_constraint TEXT,
                created_at TEXT,
                url TEXT,
                embedding TEXT
            )''')
            
            conn.commit()
            conn.close()
            logger.info("Created PR Review KB database")
    
    def crawl_issues(self, repo, limit=50, token=None):
        """Crawl issues from GitHub API"""
        issues = []
        
        try:
            url = f"https://api.github.com/repos/{repo}/issues"
            params = {
                'state': 'closed',
                'per_page': limit,
                'sort': 'updated',
                'direction': 'desc'
            }
            
            headers = {'Accept': 'application/vnd.github.v3+json'}
            if token:
                headers['Authorization'] = f'token {token}'
            
            resp = requests.get(url, params=params, headers=headers, timeout=30)
            data = resp.json()
            
            for issue in data:
                # Extract issue type
                issue_type = self._classify_issue_type(issue)
                
                # Structure issue
                structured = {
                    'repo': repo,
                    'issue_number': issue['number'],
                    'title': issue['title'],
                    'body': issue['body'] or '',
                    'issue_type': issue_type,
                    'core_symptom': self._extract_core_symptom(issue),
                    'trigger_condition': self._extract_trigger(issue),
                    'risk_points': self._extract_risk_points(issue),
                    'state': issue['state'],
                    'created_at': issue['created_at'],
                    'closed_at': issue.get('closed_at', ''),
                    'url': issue['html_url'],
                }
                
                issues.append(structured)
            
            logger.info(f"Crawled {len(issues)} issues from {repo}")
            
        except Exception as e:
            logger.error(f"Crawl failed for {repo}: {e}")
        
        return issues
    
    def _classify_issue_type(self, issue):
        """Classify issue type"""
        title = issue['title'].lower()
        body = (issue['body'] or '').lower()
        
        if 'bug' in title or 'error' in title or 'crash' in title:
            return 'Bug'
        elif 'performance' in title or 'slow' in title or 'latency' in title:
            return 'Performance'
        elif 'compatibility' in title or 'version' in title or 'breaking' in title:
            return 'Compatibility'
        elif 'feature' in title or 'request' in title or 'enhancement' in title:
            return 'Feature_Request'
        else:
            return 'Other'
    
    def _extract_core_symptom(self, issue):
        """Extract core symptom"""
        body = issue['body'] or ''
        # Extract first meaningful line
        lines = [l.strip() for l in body.split('\n') if l.strip() and len(l.strip()) > 10]
        return lines[0][:100] if lines else issue['title'][:100]
    
    def _extract_trigger(self, issue):
        """Extract trigger condition"""
        body = issue['body'] or ''
        keywords = ['when', 'after', 'during', 'while', 'triggered']
        for kw in keywords:
            if kw in body.lower():
                idx = body.lower().find(kw)
                return body[idx:idx+100]
        return ''
    
    def _extract_risk_points(self, issue):
        """Extract potential risk points"""
        body = issue['body'] or ''
        risks = []
        keywords = ['hook', 'cache', 'embedding', 'call', 'api', 'timeout', 'memory']
        for kw in keywords:
            if kw in body.lower():
                risks.append(kw)
        return ','.join(risks) if risks else ''
    
    def crawl_pr_reviews(self, repo, limit=30, token=None):
        """Crawl PR reviews from GitHub API (User Enhancement)"""
        reviews = []
        
        try:
            url = f"https://api.github.com/repos/{repo}/pulls"
            params = {
                'state': 'closed',
                'per_page': limit,
                'sort': 'updated',
                'direction': 'desc'
            }
            
            headers = {'Accept': 'application/vnd.github.v3+json'}
            if token:
                headers['Authorization'] = f'token {token}'
            
            resp = requests.get(url, params=params, headers=headers, timeout=30)
            pulls = resp.json()
            
            for pr in pulls:
                # Get PR comments
                comments_url = pr['comments_url']
                comments_resp = requests.get(comments_url, headers=headers, timeout=30)
                comments = comments_resp.json()
                
                for comment in comments:
                    structured = {
                        'repo': repo,
                        'pr_number': pr['number'],
                        'comment_type': self._classify_comment_type(comment),
                        'change_scope': self._extract_change_scope(comment),
                        'core_controversy': self._extract_controversy(comment),
                        'rejection_reason': self._extract_rejection(comment),
                        'best_practice': self._extract_best_practice(comment),
                        'hard_constraint': self._extract_hard_constraint(comment),
                        'created_at': comment.get('created_at', ''),
                        'url': pr['html_url'],
                    }
                    
                    reviews.append(structured)
            
            logger.info(f"Crawled {len(reviews)} PR reviews from {repo}")
            
        except Exception as e:
            logger.error(f"PR crawl failed for {repo}: {e}")
        
        return reviews
    
    def _classify_comment_type(self, comment):
        """Classify PR comment type"""
        body = comment.get('body', '').lower()
        
        if 'architectural' in body or 'design' in body:
            return 'Architecture'
        elif 'performance' in body or 'slow' in body:
            return 'Performance'
        elif 'compatibility' in body or 'breaking' in body:
            return 'Compatibility'
        elif 'reject' in body or 'reject' in body or 'no' in body:
            return 'Rejection'
        else:
            return 'Review'
    
    def _extract_change_scope(self, comment):
        """Extract change scope"""
        body = comment.get('body', '')
        keywords = ['module', 'file', 'class', 'function', 'dependency', 'config']
        for kw in keywords:
            if kw in body.lower():
                return kw
        return ''
    
    def _extract_controversy(self, comment):
        """Extract core controversy"""
        body = comment.get('body', '')
        keywords = ['coupling', 'performance', 'compatibility', 'maintainability', 'cost']
        for kw in keywords:
            if kw in body.lower():
                idx = body.lower().find(kw)
                return body[idx:idx+100]
        return ''
    
    def _extract_rejection(self, comment):
        """Extract rejection reason"""
        body = comment.get('body', '')
        if 'reject' in body.lower() or 'not' in body.lower():
            lines = [l for l in body.split('\n') if 'reject' in l.lower() or 'not' in l.lower()]
            return lines[0][:100] if lines else ''
        return ''
    
    def _extract_best_practice(self, comment):
        """Extract best practice conclusion"""
        body = comment.get('body', '')
        keywords = ['should', 'recommend', 'best', 'suggest', 'use']
        for kw in keywords:
            if kw in body.lower():
                idx = body.lower().find(kw)
                return body[idx:idx+100]
        return ''
    
    def _extract_hard_constraint(self, comment):
        """Extract hard constraint rules"""
        body = comment.get('body', '')
        keywords = ['must', 'never', 'always', 'required', 'mandatory']
        for kw in keywords:
            if kw in body.lower():
                return kw
        return ''
    
    def save_issues(self, issues):
        """Save issues to KB"""
        conn = sqlite3.connect(str(ISSUE_KB_DB))
        cursor = conn.cursor()
        
        for issue in issues:
            cursor.execute('''INSERT OR REPLACE INTO issue_entries (
                repo, issue_number, title, body, issue_type, core_symptom,
                trigger_condition, risk_points, state, created_at, closed_at, url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
                issue['repo'], issue['issue_number'], issue['title'],
                issue['body'], issue['issue_type'], issue['core_symptom'],
                issue['trigger_condition'], issue['risk_points'],
                issue['state'], issue['created_at'], issue['closed_at'], issue['url']
            ))
        
        conn.commit()
        conn.close()
        logger.info(f"Saved {len(issues)} issues to KB")
    
    def save_pr_reviews(self, reviews):
        """Save PR reviews to KB"""
        conn = sqlite3.connect(str(PR_REVIEW_KB_DB))
        cursor = conn.cursor()
        
        for review in reviews:
            cursor.execute('''INSERT OR REPLACE INTO pr_review_entries (
                repo, pr_number, comment_type, change_scope, core_controversy,
                rejection_reason, best_practice, hard_constraint, created_at, url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
                review['repo'], review['pr_number'], review['comment_type'],
                review['change_scope'], review['core_controversy'],
                review['rejection_reason'], review['best_practice'],
                review['hard_constraint'], review['created_at'], review['url']
            ))
        
        conn.commit()
        conn.close()
        logger.info(f"Saved {len(reviews)} PR reviews to KB")
    
    def cluster_issues_by_type(self):
        """Cluster issues by type"""
        conn = sqlite3.connect(str(ISSUE_KB_DB))
        cursor = conn.cursor()
        
        cursor.execute("SELECT issue_type, COUNT(*) FROM issue_entries GROUP BY issue_type")
        clusters = cursor.fetchall()
        
        cluster_results = []
        for issue_type, count in clusters:
            cursor.execute("SELECT id, title FROM issue_entries WHERE issue_type=?", (issue_type,))
            issues = cursor.fetchall()
            
            cluster_results.append({
                'cluster_type': issue_type,
                'count': count,
                'issue_ids': [i[0] for i in issues],
                'common_pattern': self._extract_common_pattern(issues, issue_type),
            })
        
        conn.close()
        return cluster_results
    
    def _extract_common_pattern(self, issues, issue_type):
        """Extract common pattern from cluster"""
        patterns = {
            'Bug': 'Error handling, null check, boundary condition',
            'Performance': 'Cache, latency, memory optimization',
            'Compatibility': 'Version check, backward compatibility',
            'Feature_Request': 'User experience, API enhancement',
        }
        return patterns.get(issue_type, 'General improvement')
    
    def search_pr_constraints(self, module):
        """Search PR constraints for module (User Enhancement)"""
        conn = sqlite3.connect(str(PR_REVIEW_KB_DB))
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM pr_review_entries WHERE change_scope LIKE ?", (f"%{module}%",))
        results = cursor.fetchall()
        conn.close()
        
        constraints = []
        for r in results:
            constraints.append({
                'hard_constraint': r[7],
                'best_practice': r[6],
                'rejection_reason': r[5],
            })
        
        return constraints
    
    def get_dual_kb_stats(self):
        """Get dual KB statistics"""
        conn_issue = sqlite3.connect(str(ISSUE_KB_DB))
        conn_pr = sqlite3.connect(str(PR_REVIEW_KB_DB))
        
        cursor_issue = conn_issue.cursor()
        cursor_pr = conn_pr.cursor()
        
        cursor_issue.execute("SELECT COUNT(*) FROM issue_entries")
        issue_count = cursor_issue.fetchone()[0]
        
        cursor_pr.execute("SELECT COUNT(*) FROM pr_review_entries")
        pr_count = cursor_pr.fetchone()[0]
        
        conn_issue.close()
        conn_pr.close()
        
        return {
            'issue_kb_count': issue_count,
            'pr_review_kb_count': pr_count,
            'total': issue_count + pr_count,
        }
    
    def generate_cluster_report(self):
        """Generate cluster analysis report"""
        stats = self.get_dual_kb_stats()
        clusters = self.cluster_issues_by_type()
        
        report = f"""# Issue Cluster Report

## Statistics

| Metric | Value |
|--------|-------|
| Issue KB Count | {stats['issue_kb_count']} |
| PR Review KB Count | {stats['pr_review_kb_count']} |
| Total | {stats['total']} |

## Issue Clusters by Type

"""
        
        for cluster in clusters:
            report += f"### {cluster['cluster_type']} ({cluster['count']} issues)\n"
            report += f"- Common Pattern: {cluster['common_pattern']}\n"
            report += f"- Issue IDs: {len(cluster['issue_ids'])} issues\n\n"
        
        return report

# Global instance
_issue_clusterer = None

def get_issue_clusterer():
    """Get global issue clusterer"""
    global _issue_clusterer
    if _issue_clusterer is None:
        _issue_clusterer = IssueClusterer()
    return _issue_clusterer

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("=" * 60)
    print("Issue Clusterer Test")
    print("=" * 60)
    
    clusterer = IssueClusterer()
    
    # Test crawl (without token, limited rate)
    print("\n--- Test Issue KB ---")
    stats = clusterer.get_dual_kb_stats()
    print(f"Issue KB: {stats['issue_kb_count']} entries")
    print(f"PR Review KB: {stats['pr_review_kb_count']} entries")
    
    print("\n--- Test Cluster ---")
    clusters = clusterer.cluster_issues_by_type()
    for c in clusters:
        print(f"  {c['cluster_type']}: {c['count']} issues")
    
    print("\n--- Test Report ---")
    report = clusterer.generate_cluster_report()
    print(report[:300])
    
    print("\n[PASS] Issue clusterer initialized")