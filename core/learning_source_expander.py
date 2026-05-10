# -*- coding: utf-8 -*-
"""
Learning Source Expander - Discussion, PR, Changelog (豆包方案 #7)
Pattern ID: learning_source_expansion
Source: Doubao Proposal + User PR Review Enhancement
"""
import json
import sqlite3
import logging
import requests
from datetime import datetime
from pathlib import Path

logger = logging.getLogger('BrainEntry.LearningSource')

# Whitelist repositories
REPO_WHITELIST = [
    "ragas",
    "typesense",
    "milvus",
    "ragflow",
    "langchain",
    "llamaindex",
]

DISCUSSION_KB_DB = Path("data/.discussion_kb.db")
CHANGELOG_KB_DB = Path("data/.changelog_kb.db")

class LearningSourceExpander:
    """学习源扩展器 - 不止学Issue"""
    
    SOURCES = {
        'issue': 'GitHub Issues API',
        'discussion': 'GitHub Discussions API',
        'pr_review': 'GitHub PR Comments API',
        'changelog': 'GitHub Releases/CHANGELOG.md',
        'rfc': 'Technical RFC Documents',
    }
    
    def __init__(self):
        self._init_discussion_kb()
        self._init_changelog_kb()
    
    def _init_discussion_kb(self):
        """Initialize Discussion KB"""
        if not DISCUSSION_KB_DB.exists():
            conn = sqlite3.connect(str(DISCUSSION_KB_DB))
            cursor = conn.cursor()
            
            cursor.execute('''CREATE TABLE discussion_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                repo TEXT NOT NULL,
                discussion_number INTEGER,
                title TEXT,
                body TEXT,
                category TEXT,
                author TEXT,
                created_at TEXT,
                url TEXT,
                design_decision TEXT,
                embedding TEXT
            )''')
            
            conn.commit()
            conn.close()
            logger.info("Created Discussion KB database")
    
    def _init_changelog_kb(self):
        """Initialize Changelog KB"""
        if not CHANGELOG_KB_DB.exists():
            conn = sqlite3.connect(str(CHANGELOG_KB_DB))
            cursor = conn.cursor()
            
            cursor.execute('''CREATE TABLE changelog_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                repo TEXT NOT NULL,
                version TEXT,
                release_date TEXT,
                changes TEXT,
                breaking_changes TEXT,
                architecture_changes TEXT,
                url TEXT,
                embedding TEXT
            )''')
            
            conn.commit()
            conn.close()
            logger.info("Created Changelog KB database")
    
    def fetch_discussions(self, repo, limit=30, token=None):
        """获取Discussion (GitHub GraphQL API)"""
        discussions = []
        
        try:
            # GitHub GraphQL API for discussions
            url = "https://api.github.com/graphql"
            
            query = '''
            query($repo: String!, $owner: String!, $limit: Int!) {
              repository(owner: $owner, name: $repo) {
                discussions(first: $limit) {
                  nodes {
                    number
                    title
                    body
                    category { name }
                    author { login }
                    createdAt
                    url
                  }
                }
              }
            }
            '''
            
            # Parse repo
            parts = repo.split('/')
            owner = parts[0] if len(parts) > 1 else repo
            name = parts[-1] if len(parts) > 1 else repo
            
            headers = {}
            if token:
                headers['Authorization'] = f'Bearer {token}'
            
            resp = requests.post(url, json={
                'query': query,
                'variables': {'owner': owner, 'name': name, 'limit': limit}
            }, headers=headers, timeout=30)
            
            data = resp.json()
            
            if 'data' in data and data['data']['repository']:
                nodes = data['data']['repository']['discussions']['nodes']
                
                for disc in nodes:
                    discussions.append({
                        'repo': repo,
                        'discussion_number': disc['number'],
                        'title': disc['title'],
                        'body': disc.get('body', ''),
                        'category': disc.get('category', {}).get('name', ''),
                        'author': disc.get('author', {}).get('login', ''),
                        'created_at': disc['createdAt'],
                        'url': disc.get('url', ''),
                        'design_decision': self._extract_design_decision(disc.get('body', '')),
                    })
            
            logger.info(f"Fetched {len(discussions)} discussions from {repo}")
            
        except Exception as e:
            logger.warning(f"Discussion fetch failed for {repo}: {e}")
        
        return discussions
    
    def _extract_design_decision(self, body):
        """提取设计方案"""
        keywords = ['design', 'architecture', 'approach', 'solution', 'trade-off']
        for kw in keywords:
            if kw in body.lower():
                idx = body.lower().find(kw)
                return body[idx:idx+200]
        return ''
    
    def fetch_changelog(self, repo, token=None):
        """获取Changelog"""
        changelogs = []
        
        try:
            # Get releases
            url = f"https://api.github.com/repos/{repo}/releases"
            headers = {'Accept': 'application/vnd.github.v3+json'}
            if token:
                headers['Authorization'] = f'token {token}'
            
            resp = requests.get(url, headers=headers, timeout=30)
            releases = resp.json()
            
            for release in releases[:10]:  # Last 10 releases
                changelogs.append({
                    'repo': repo,
                    'version': release.get('tag_name', ''),
                    'release_date': release.get('published_at', ''),
                    'changes': self._extract_changes(release.get('body', '')),
                    'breaking_changes': self._extract_breaking(release.get('body', '')),
                    'architecture_changes': self._extract_architecture(release.get('body', '')),
                    'url': release.get('html_url', ''),
                })
            
            logger.info(f"Fetched {len(changelogs)} changelog entries from {repo}")
            
        except Exception as e:
            logger.error(f"Changelog fetch failed for {repo}: {e}")
        
        return changelogs
    
    def _extract_changes(self, body):
        """提取变更内容"""
        return body[:500] if body else ''
    
    def _extract_breaking(self, body):
        """提取Breaking Changes"""
        if 'breaking' in body.lower():
            idx = body.lower().find('breaking')
            return body[idx:idx+200]
        return ''
    
    def _extract_architecture(self, body):
        """提取架构变更"""
        keywords = ['architecture', 'refactor', 'migration', 'deprecation']
        for kw in keywords:
            if kw in body.lower():
                idx = body.lower().find(kw)
                return body[idx:idx+100]
        return ''
    
    def save_discussions(self, discussions):
        """保存Discussion到KB"""
        conn = sqlite3.connect(str(DISCUSSION_KB_DB))
        cursor = conn.cursor()
        
        for disc in discussions:
            cursor.execute('''INSERT OR REPLACE INTO discussion_entries (
                repo, discussion_number, title, body, category, author,
                created_at, url, design_decision
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
                disc['repo'], disc['discussion_number'], disc['title'],
                disc['body'], disc['category'], disc['author'],
                disc['created_at'], disc['url'], disc['design_decision']
            ))
        
        conn.commit()
        conn.close()
        logger.info(f"Saved {len(discussions)} discussions to KB")
    
    def save_changelogs(self, changelogs):
        """保存Changelog到KB"""
        conn = sqlite3.connect(str(CHANGELOG_KB_DB))
        cursor = conn.cursor()
        
        for cl in changelogs:
            cursor.execute('''INSERT OR REPLACE INTO changelog_entries (
                repo, version, release_date, changes, breaking_changes,
                architecture_changes, url
            ) VALUES (?, ?, ?, ?, ?, ?, ?)''', (
                cl['repo'], cl['version'], cl['release_date'],
                cl['changes'], cl['breaking_changes'],
                cl['architecture_changes'], cl['url']
            ))
        
        conn.commit()
        conn.close()
        logger.info(f"Saved {len(changelogs)} changelogs to KB")
    
    def search_design_decisions(self, query):
        """检索设计方案"""
        conn = sqlite3.connect(str(DISCUSSION_KB_DB))
        cursor = conn.cursor()
        
        cursor.execute("SELECT title, design_decision FROM discussion_entries WHERE design_decision LIKE ?", (f"%{query}%",))
        results = cursor.fetchall()
        conn.close()
        
        return [{"title": r[0], "decision": r[1]} for r in results]
    
    def search_breaking_changes(self, version_query):
        """检索Breaking Changes"""
        conn = sqlite3.connect(str(CHANGELOG_KB_DB))
        cursor = conn.cursor()
        
        cursor.execute("SELECT version, breaking_changes FROM changelog_entries WHERE breaking_changes LIKE ?", (f"%{version_query}%",))
        results = cursor.fetchall()
        conn.close()
        
        return [{"version": r[0], "breaking": r[1]} for r in results]
    
    def get_all_kb_stats(self):
        """获取所有KB统计"""
        stats = {}
        
        # Discussion KB
        conn = sqlite3.connect(str(DISCUSSION_KB_DB))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM discussion_entries")
        stats['discussion_count'] = cursor.fetchone()[0]
        conn.close()
        
        # Changelog KB
        conn = sqlite3.connect(str(CHANGELOG_KB_DB))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM changelog_entries")
        stats['changelog_count'] = cursor.fetchone()[0]
        conn.close()
        
        stats['total'] = stats['discussion_count'] + stats['changelog_count']
        
        return stats
    
    def generate_learning_report(self):
        """生成学习源报告"""
        stats = self.get_all_kb_stats()
        
        report = f"""# Learning Source Report

## Statistics

| Source | Count |
|--------|-------|
| Discussions | {stats['discussion_count']} |
| Changelogs | {stats['changelog_count']} |
| Total | {stats['total']} |

## Design Decisions Found

"""
        
        decisions = self.search_design_decisions("design")
        for d in decisions[:5]:
            report += f"- {d['title']}: {d['decision'][:50]}...\n"
        
        report += "\n## Breaking Changes\n\n"
        
        breaking = self.search_breaking_changes("breaking")
        for b in breaking[:5]:
            report += f"- {b['version']}: {b['breaking'][:50]}...\n"
        
        return report

# Global instance
_learning_source = None

def get_learning_source_expander():
    global _learning_source
    if _learning_source is None:
        _learning_source = LearningSourceExpander()
    return _learning_source

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("=" * 60)
    print("Learning Source Expander Test")
    print("=" * 60)
    
    expander = LearningSourceExpander()
    
    print("\n--- KB Statistics ---")
    stats = expander.get_all_kb_stats()
    print(f"Discussions: {stats['discussion_count']}")
    print(f"Changelogs: {stats['changelog_count']}")
    
    print("\n--- Search Design Decisions ---")
    decisions = expander.search_design_decisions("architecture")
    print(f"Found {len(decisions)} design decisions")
    
    print("\n--- Search Breaking Changes ---")
    breaking = expander.search_breaking_changes("v1")
    print(f"Found {len(breaking)} breaking changes")
    
    print("\n--- Report ---")
    report = expander.generate_learning_report()
    print(report[:300])
    
    print("\n[PASS] Learning source expander initialized")