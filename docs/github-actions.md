# GitHub Actions Guide

This guide shows how to integrate SkillCI into your GitHub Actions workflows for automated Skill testing and quality gates.

---

## Basic Setup

### 1. Install SkillCI in Your Workflow

```yaml
- name: Install SkillCI
  run: pip install -e .[dev]
```

For LLM mode, install the LLM extra:

```yaml
- name: Install SkillCI with LLM support
  run: pip install -e .[llm]
```

### 2. Configure Python Version

SkillCI requires Python 3.10+:

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: "3.11"
```

---

## Workflow Examples

### Local Mode Workflow

Run only local rule-based trigger checks (no API calls required):

```yaml
name: SkillCI Local

on:
  pull_request:
    paths:
      - "**/SKILL.md"
      - "**/skillci.yaml"
      - "skills/**"

jobs:
  skillci-local:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      
      - name: Install SkillCI
        run: pip install -e .[dev]
      
      - name: Run Local Trigger Test
        run: skillci test examples/api-doc-writer --mode local
      
      - name: Generate Report
        run: skillci report examples/api-doc-writer --format markdown --output report.md
      
      - name: Upload Report
        uses: actions/upload-artifact@v4
        with:
          name: skillci-report
          path: report.md
```

### LLM Mode Workflow

Run LLM-based trigger judgment (requires API key):

```yaml
name: SkillCI LLM

on:
  pull_request:
    paths:
      - "**/SKILL.md"
      - "**/skillci.yaml"
      - "skills/**"

jobs:
  skillci-llm:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      
      - name: Install SkillCI with LLM support
        run: pip install -e .[llm]
      
      - name: Run LLM Trigger Test
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: skillci test examples/api-doc-writer --mode llm --provider openai
      
      - name: Generate Report
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: skillci report examples/api-doc-writer --format markdown --output report.md
      
      - name: Upload Report
        uses: actions/upload-artifact@v4
        with:
          name: skillci-report
          path: report.md
```

### Both Mode Workflow

Run both local and LLM checks, comparing their results:

```yaml
name: SkillCI Both

on:
  pull_request:
    paths:
      - "**/SKILL.md"
      - "**/skillci.yaml"
      - "skills/**"

jobs:
  skillci-both:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      
      - name: Install SkillCI with LLM support
        run: pip install -e .[llm]
      
      - name: Run Both Mode Test
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: skillci test examples/api-doc-writer --mode both --provider openai
      
      - name: Generate Report
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: skillci report examples/api-doc-writer --format markdown --output report.md
      
      - name: Upload Report
        uses: actions/upload-artifact@v4
        with:
          name: skillci-report
          path: report.md
```

---

## Configuration

### OPENAI_API_KEY Secret

To use LLM mode, configure your API key as a GitHub repository secret:

1. Go to your repository → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `OPENAI_API_KEY`
4. Value: Your OpenAI API key (or compatible provider key)
5. Click "Add secret"

Then reference it in your workflow:

```yaml
env:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

### Custom API Endpoint

If using a custom OpenAI-compatible API:

1. Add `OPENAI_BASE_URL` as a repository secret
2. Use it in your workflow:

```yaml
env:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  OPENAI_BASE_URL: ${{ secrets.OPENAI_BASE_URL }}
```

### Paths Trigger Conditions

Limit workflow runs to relevant file changes:

```yaml
on:
  pull_request:
    paths:
      - "**/SKILL.md"
      - "**/skillci.yaml"
      - "skills/**"
      - "examples/**"
```

Common path patterns:
- `**/SKILL.md` - Any SKILL.md file
- `**/skillci.yaml` - Any SkillCI config
- `skills/**` - Skill directories
- `examples/**` - Example skills

### Caching Dependencies

Speed up workflows by caching Python dependencies:

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: "3.11"
    cache: "pip"

- name: Install SkillCI
  run: pip install -e .[llm]
```

### Caching LLM Results

SkillCI caches LLM results by default when `judge.cache: true` in config. To persist cache between runs:

```yaml
- name: Cache SkillCI LLM results
  uses: actions/cache@v4
  with:
    path: .skillci/cache
    key: skillci-${{ runner.os }}-${{ hashFiles('**/skillci.yaml') }}
    restore-keys: |
      skillci-${{ runner.os }}-
```

---

## PR Comment Integration

### Basic PR Comment

Add test results as a PR comment:

```yaml
- name: Run SkillCI
  id: skillci
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  run: |
    skillci test examples/api-doc-writer --mode both --provider openai --json > report.json
    echo "passed=$(jq -r '.passed' report.json)" >> $GITHUB_OUTPUT

- name: Comment on PR
  if: always()
  uses: actions/github-script@v7
  with:
    script: |
      const fs = require('fs');
      const report = JSON.parse(fs.readFileSync('report.json', 'utf8'));
      const passed = report.passed ? '✅ PASSED' : '❌ FAILED';
      const body = `## SkillCI Check\n\nResult: ${passed}\n\nStatic Health: ${report.static_health.passed ? '✅' : '❌'}\nLocal F1: ${report.local_metrics?.f1?.toFixed(2) || 'N/A'}\nLLM F1: ${report.llm_metrics?.f1?.toFixed(2) || 'N/A'}\nJudge Disagreements: ${report.judge_disagreement_count}`;
      
      github.rest.issues.createComment({
        issue_number: context.issue.number,
        owner: context.repo.owner,
        repo: context.repo.repo,
        body: body
      });
```

---

## Complete Example

Here's a complete workflow combining multiple features:

```yaml
name: SkillCI Quality Gate

on:
  pull_request:
    paths:
      - "**/SKILL.md"
      - "**/skillci.yaml"
      - "skills/**"

jobs:
  skillci:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"
      
      - name: Install SkillCI
        run: pip install -e .[llm]
      
      - name: Cache LLM results
        uses: actions/cache@v4
        with:
          path: .skillci/cache
          key: skillci-${{ runner.os }}-${{ hashFiles('**/skillci.yaml') }}
          restore-keys: |
            skillci-${{ runner.os }}-
      
      - name: Run SkillCI Both Mode
        id: skillci
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          skillci test examples/api-doc-writer --mode both --provider openai --json > report.json
          echo "passed=$(jq -r '.passed' report.json)" >> $GITHUB_OUTPUT
      
      - name: Generate Markdown Report
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: skillci report examples/api-doc-writer --format markdown --output report.md
      
      - name: Upload Report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: skillci-report
          path: |
            report.json
            report.md
      
      - name: Comment on PR
        if: always()
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const report = JSON.parse(fs.readFileSync('report.json', 'utf8'));
            const passed = report.passed ? '✅ PASSED' : '❌ FAILED';
            const body = `## SkillCI Check\n\nResult: ${passed}\n\nStatic Health: ${report.static_health.passed ? '✅' : '❌'}\nLocal F1: ${report.local_metrics?.f1?.toFixed(2) || 'N/A'}\nLLM F1: ${report.llm_metrics?.f1?.toFixed(2) || 'N/A'}\nJudge Disagreements: ${report.judge_disagreement_count}`;
            
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: body
            });
      
      - name: Fail if checks failed
        if: steps.skillci.outputs.passed != 'true'
        run: exit 1
```

---

## Troubleshooting

### Common Issues

1. **`OPENAI_API_KEY` not set**
   - Error: `OPENAI_API_KEY environment variable not set`
   - Solution: Add the secret to your repository settings

2. **Python version too old**
   - Error: `SyntaxError` or unsupported features
   - Solution: Use Python 3.10+ in `actions/setup-python`

3. **LLM timeout**
   - Error: `TimeoutError` or `Request timed out`
   - Solution: Increase `judge.timeout` in `skillci.yaml` or use a faster model

4. **Cache not working**
   - Check if `.skillci/cache` is in `.gitignore`
   - Verify cache key includes relevant config files

### Debug Mode

Enable verbose output for debugging:

```yaml
- name: Run SkillCI with debug
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
    SKILLCI_DEBUG: "1"
  run: skillci test examples/api-doc-writer --mode both --provider openai
```

---

## Best Practices

1. **Use path filters** to avoid unnecessary runs
2. **Cache dependencies** with `actions/setup-python` cache option
3. **Cache LLM results** to reduce API costs
4. **Upload reports** as artifacts for later inspection
5. **Comment on PRs** for immediate feedback
6. **Fail the workflow** if SkillCI checks fail
7. **Use both mode** for comprehensive quality gates
8. **Set appropriate timeouts** for LLM calls