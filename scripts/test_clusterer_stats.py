# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r"C:\Users\Administrator\.openclaw\brain-system\core")

import issue_clusterer

clusterer = issue_clusterer.get_issue_clusterer()
stats = clusterer.get_dual_kb_stats()
print(f"Stats from issue_clusterer: {stats}")
print(f"DB paths: {issue_clusterer.ISSUE_KB_DB}, {issue_clusterer.PR_REVIEW_KB_DB}")
print(f"DB exists: {issue_clusterer.ISSUE_KB_DB.exists()}, {issue_clusterer.PR_REVIEW_KB_DB.exists()}")