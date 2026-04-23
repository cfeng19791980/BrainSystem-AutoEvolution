# -*- coding: utf-8 -*-
"""
OpenClaw AutoResearch - Simplified Version
基于 Karpathy autoresearch 的自主优化循环

用法:
    python autoresearch_simple.py --target brain_entry.py --metric response_time

工作流程:
    1. 测量基线指标
    2. Agent修改代码
    3. 运行测试
    4. 对比指标
    5. 保留改进/丢弃恶化
    6. 无限循环
"""

import os
import sys
import time
import json
import subprocess
import argparse
from datetime import datetime
from pathlib import Path

# 配置
RESULTS_FILE = Path(__file__).parent / "autoresearch_results.tsv"
TIME_BUDGET = 300  # 5分钟
MAX_EXPERIMENTS = 100  # 默认100次实验

class AutoResearchLoop:
    def __init__(self, target_file, metric_func, metric_name="metric"):
        self.target_file = Path(target_file)
        self.metric_func = metric_func
        self.metric_name = metric_name
        self.results = []
        self.baseline = None
        self.experiment_count = 0
        
        # 初始化
        self._init_results_file()
        self._backup_original()
    
    def _init_results_file(self):
        """初始化结果文件"""
        if not RESULTS_FILE.exists():
            with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
                f.write("timestamp\texperiment\tmetric\tstatus\tdescription\n")
    
    def _backup_original(self):
        """备份原始文件"""
        backup_path = self.target_file.with_suffix('.py.original')
        if not backup_path.exists():
            import shutil
            shutil.copy(self.target_file, backup_path)
            print(f"[SETUP] Original backed up to: {backup_path}")
    
    def _log_result(self, metric, status, description=""):
        """记录结果"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        with open(RESULTS_FILE, 'a', encoding='utf-8') as f:
            f.write(f"{timestamp}\t{self.experiment_count}\t{metric:.6f}\t{status}\t{description}\n")
        
        self.results.append({
            'timestamp': timestamp,
            'experiment': self.experiment_count,
            'metric': metric,
            'status': status,
            'description': description
        })
        
        print(f"[LOG] Exp#{self.experiment_count}: {metric:.6f} ({status})")
    
    def measure_baseline(self):
        """测量基线"""
        print("\n[Baseline Measurement]")
        self.baseline = self.metric_func()
        self._log_result(self.baseline, "baseline", "initial measurement")
        print(f"  Baseline {self.metric_name}: {self.baseline:.6f}")
        return self.baseline
    
    def run_experiment(self, modification_desc=""):
        """运行单次实验"""
        self.experiment_count += 1
        print(f"\n[Experiment #{self.experiment_count}]")
        print(f"  Modification: {modification_desc}")
        
        # 测量新指标
        try:
            start_time = time.time()
            new_metric = self.metric_func()
            elapsed = time.time() - start_time
            
            # 决策
            if new_metric < self.baseline:
                status = "keep"
                self.baseline = new_metric
                print(f"  IMPROVED! {self.metric_name}: {new_metric:.6f} < {self.baseline:.6f}")
            elif new_metric == self.baseline:
                status = "equal"
                print(f"  NO CHANGE: {self.metric_name}: {new_metric:.6f}")
            else:
                status = "discard"
                print(f"  WORSE: {self.metric_name}: {new_metric:.6f} > {self.baseline:.6f}")
                # 回滚（需要实现）
            
            self._log_result(new_metric, status, modification_desc)
            
            return new_metric, status
            
        except Exception as e:
            print(f"  CRASH: {e}")
            self._log_result(0, "crash", str(e)[:50])
            return None, "crash"
    
    def run_loop(self, modifications=None, max_experiments=MAX_EXPERIMENTS):
        """运行优化循环"""
        print("\n" + "="*60)
        print("AutoResearch Loop Starting")
        print("="*60)
        print(f"  Target: {self.target_file}")
        print(f"  Metric: {self.metric_name}")
        print(f"  Baseline: {self.baseline:.6f}")
        print(f"  Max Experiments: {max_experiments}")
        print("="*60)
        
        if modifications is None:
            # 默认修改列表
            modifications = [
                "optimize loop",
                "reduce memory",
                "cache results",
                "parallel process",
                "simplify logic",
            ]
        
        for i in range(max_experiments):
            mod = modifications[i % len(modifications)]
            self.run_experiment(mod)
            
            # 每次实验后暂停一下
            time.sleep(1)
        
        print("\n" + "="*60)
        print("AutoResearch Loop Complete")
        print("="*60)
        self.print_summary()
    
    def print_summary(self):
        """打印摘要"""
        keeps = [r for r in self.results if r['status'] == 'keep']
        discards = [r for r in self.results if r['status'] == 'discard']
        crashes = [r for r in self.results if r['status'] == 'crash']
        
        print(f"\n  Total Experiments: {self.experiment_count}")
        print(f"  Improvements: {len(keeps)}")
        print(f"  Discards: {len(discards)}")
        print(f"  Crashes: {len(crashes)}")
        print(f"  Final {self.metric_name}: {self.baseline:.6f}")
        
        if self.results:
            initial = self.results[0]['metric']
            improvement = (initial - self.baseline) / initial * 100
            print(f"  Total Improvement: {improvement:.2f}%")


# ============================================================
# 示例评估函数
# ============================================================

def example_metric_func():
    """示例评估函数 - 测量响应时间"""
    import requests
    try:
        start = time.time()
        r = requests.get('http://127.0.0.1:5002/health', timeout=5)
        elapsed = time.time() - start
        return elapsed * 1000  # 返回毫秒
    except:
        return 9999  # 失败返回高值


def example_metric_func_accuracy():
    """示例评估函数 - 测量准确率"""
    import requests
    try:
        r = requests.post('http://127.0.0.1:5002/entry', 
                         json={'content': '测试', 'sessionKey': 'test'},
                         timeout=5)
        result = r.json()
        confidence = result.get('brain_context', {}).get('intent', {}).get('confidence', 0)
        return 1 - confidence  # 越低越好
    except:
        return 1  # 失败返回1


# ============================================================
# Main
# ============================================================

def main():
    parser = argparse.ArgumentParser(description='OpenClaw AutoResearch')
    parser.add_argument('--target', type=str, default='brain_entry.py', help='Target file to optimize')
    parser.add_argument('--metric', type=str, default='response_time', help='Metric to optimize')
    parser.add_argument('--max', type=int, default=10, help='Max experiments')
    
    args = parser.parse_args()
    
    # 选择评估函数
    if args.metric == 'response_time':
        metric_func = example_metric_func
    elif args.metric == 'accuracy':
        metric_func = example_metric_func_accuracy
    else:
        print(f"Unknown metric: {args.metric}")
        return
    
    # 创建优化循环
    loop = AutoResearchLoop(
        target_file=args.target,
        metric_func=metric_func,
        metric_name=args.metric
    )
    
    # 测量基线
    loop.measure_baseline()
    
    # 运行循环
    loop.run_loop(max_experiments=args.max)


if __name__ == "__main__":
    main()