# Contributing to BrainSystem-AutoEvolution

Thank you for your interest in contributing to BrainSystem! 🎉

## Ways to Contribute

### 1. Submit Experiments
- Create new experiment files in `data/experiments/`
- Follow experiment naming convention: `experiment_{number}_{focus}.py`
- Include performance metrics in experiment results
- Patterns will be auto-mined into optimization rules

### 2. Report Issues
- Use GitHub Issues for bug reports
- Include performance metrics and logs
- Provide reproduction steps
- Tag with appropriate labels (bug, performance, documentation)

### 3. Improve Documentation
- Enhance README.md clarity
- Add new use case examples
- Create tutorials and guides
- Translate documentation

### 4. Optimize Performance
- Benchmark current performance
- Propose optimization strategies
- Validate improvements with experiments
- Document performance gains

### 5. Share Use Cases
- Add real-world application examples
- Share integration experiences
- Create case study documentation
- Contribute to `examples/` directory

---

## Development Workflow

### Getting Started

1. **Fork the repository**
```bash
git clone https://github.com/YOUR_USERNAME/BrainSystem-AutoEvolution.git
cd BrainSystem-AutoEvolution
```

2. **Create a branch**
```bash
git checkout -b feature/your-feature-name
```

3. **Make changes**
- Follow code style guidelines
- Add tests if applicable
- Update documentation

4. **Test your changes**
```bash
python -m pytest tests/
python scripts/benchmark.py
```

5. **Submit a Pull Request**
- Provide clear description
- Link related issues
- Include performance metrics
- Wait for review

---

## Code Style Guidelines

### Python Code
- Use UTF-8 encoding header: `# -*- coding: utf-8 -*-`
- Follow PEP 8 conventions
- Add docstrings for functions
- Include type hints where possible
- Use meaningful variable names

### Example
```python
# -*- coding: utf-8 -*-
"""
Pattern mining module for BrainSystem
"""

def mine_patterns(experiment_data: dict) -> list:
    """
    Mine patterns from experiment data.
    
    Args:
        experiment_data: Dictionary containing experiment results
        
    Returns:
        List of discovered patterns with quality scores
    """
    patterns = []
    # Implementation
    return patterns
```

### Documentation
- Use Markdown format
- Include examples and code snippets
- Add performance metrics where applicable
- Keep language clear and concise

---

## Performance Testing

### Required Benchmarks
Before submitting PRs that affect performance:

1. **Run baseline benchmark**
```bash
python scripts/benchmark.py --baseline
```

2. **Run optimized benchmark**
```bash
python scripts/benchmark.py --optimized
```

3. **Compare results**
- Response time improvement
- Accuracy changes
- Memory usage
- Stability metrics

4. **Include benchmark results in PR**
- Before/After metrics
- Percentage improvement
- Stability analysis

---

## Experiment Guidelines

### Naming Convention
```
experiment_{number}_{focus_area}.py

Examples:
- experiment_1_cache.py (response cache optimization)
- experiment_2_bottleneck.py (bottleneck analysis)
- experiment_3_deep.py (deep intent optimization)
```

### Required Structure
```python
# -*- coding: utf-8 -*-
"""
Experiment {number}: {Focus Area}
Author: {Your Name}
Date: {YYYY-MM-DD}
"""

def run_experiment():
    """
    Run experiment and return results.
    """
    # Setup
    # Execution
    # Measurement
    # Validation
    
    return {
        'metric': value,
        'improvement': percentage,
        'status': 'success' or 'failed'
    }

if __name__ == '__main__':
    results = run_experiment()
    print(f"Result: {results}")
```

---

## Documentation Guidelines

### README Updates
- Keep star history chart updated
- Add new benchmarks to comparison table
- Update project stats
- Include new use cases

### API Documentation
- Document all parameters
- Include request/response examples
- Add error handling notes
- Provide usage guidelines

### Architecture Documentation
- Update diagrams for new features
- Explain new components
- Include performance impact
- Add integration details

---

## Pull Request Review Process

### Review Criteria
1. **Code Quality**: Clean, readable, well-documented
2. **Performance**: No degradation, improvements documented
3. **Tests**: New features tested, existing tests pass
4. **Documentation**: Updated README/API docs
5. **Compatibility**: Works across platforms

### Review Timeline
- Initial review: 1-3 days
- Feedback response: 1-2 days
- Final approval: 1-2 days
- Merge: Within 1 week

---

## Community Standards

### Be Respectful
- Use welcoming language
- Be patient with new contributors
- Provide constructive feedback
- Help others learn

### Be Transparent
- Disclose conflicts of interest
- Acknowledge external contributions
- Document decision rationale
- Share performance data openly

### Be Collaborative
- Help review others' PRs
- Share knowledge and experience
- Participate in discussions
- Build community together

---

## Recognition

### Contributors Hall of Fame
- Listed in README.md
- Acknowledged in CHANGELOG.md
- Featured in documentation

### Significant Contributions
- Major performance improvements (>10%)
- New core features
- Comprehensive documentation
- Multiple high-quality PRs

---

## Questions?

- **Email**: 10341731@qq.com
- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For general questions and ideas

---

**Thank you for contributing to BrainSystem!**

Your contributions help make AI systems more intelligent, efficient, and self-evolving.

---

**Updated**: 2026-04-23
**Maintainer**: 付郁 (@cfeng19791980)