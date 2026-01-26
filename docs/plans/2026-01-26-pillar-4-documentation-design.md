# Pillar 4: Documentation - Design Document

**Date:** 2026-01-26
**Issue:** #5
**Pillar:** Documentation

## Overview

Implementation of the fourth pillar for the agent readiness scoring system. This pillar evaluates documentation quality, comprehensiveness, and AI-agent readiness across multiple documentation types.

## Architecture

### Pillar Structure

The `DocumentationPillar` class inherits from `Pillar` and implements documentation-aware checking:

1. **File Discovery**: Find documentation files (README, AGENTS.md, CONTRIBUTING.md, etc.)
2. **Content Analysis**: Analyze structure, completeness, and agent-readiness
3. **Quality Metrics**: Measure documentation quality indicators
4. **Coverage Assessment**: Determine what areas are documented

### Data Structure

```python
@dataclass
class DocumentationAssets:
    readme: Path | None      # README.md location
    agents_md: Path | None   # AGENTS.md location
    contributing: Path | None
    docs_dir: Path | None    # docs/ or documentation/ directory
    api_docs: Path | None    # API documentation
    architecture: Path | None
    changelog: Path | None
```

### Documentation File Patterns

Core documentation files:
- `README.md` - Project overview (mandatory)
- `AGENTS.md` - AI agent readiness guide
- `CONTRIBUTING.md` - Contribution guidelines
- `ARCHITECTURE.md` or `docs/architecture/` - Architecture documentation
- `CHANGELOG.md` or `HISTORY.md` - Version history
- `docs/` directory - General documentation
- `API.md` - API documentation
- `.github/CODE_OF_CONDUCT.md` - Code of conduct

## Check Implementation

### Level 1 - Functional (Repository-wide)

**Check: `check_readme_exists()`**
- **Purpose**: Verify README.md exists in repository root
- **Detection**:
  - Look for README.md (case-insensitive)
  - Check for README in formats: .md, .rst, .txt
- **Returns**: Single CheckResult for the repository
- **Pass Criteria**: README file found in root
- **Example**: "README.md found"

### Level 2 - Documented (Repository-wide)

**Check: `check_readme_quality()`**
- **Purpose**: Verify README has minimum quality/completeness
- **Detection**:
  - Minimum length (500 characters)
  - Contains key sections: project description, installation, usage
  - Has code examples
  - Has badges or status info
- **Returns**: Single CheckResult for the repository
- **Pass Criteria**: README has minimum 2 of 4 quality indicators
- **Example**: "README.md includes description, installation, and examples"

**Check: `check_agents_md_exists()`**
- **Purpose**: Verify AGENTS.md exists (AI agent readiness guide)
- **Detection**:
  - Look for AGENTS.md in root directory
  - Check .github/ or docs/ if not in root
- **Returns**: Single CheckResult for the repository
- **Pass Criteria**: AGENTS.md file found
- **Example**: "AGENTS.md found at root"

**Check: `check_contributing_exists()`**
- **Purpose**: Verify contribution guidelines exist
- **Detection**:
  - Look for CONTRIBUTING.md
  - Check .github/CONTRIBUTING.md
  - Also accept contributing guidelines in README section
- **Returns**: Single CheckResult for the repository
- **Pass Criteria**: Contributing documentation found
- **Example**: "CONTRIBUTING.md found"

### Level 3 - Standardized (Repository-wide)

**Check: `check_agents_md_quality()`**
- **Purpose**: Verify AGENTS.md has comprehensive agent readiness information
- **Detection**:
  - Minimum length (200 characters)
  - Contains key sections:
    - How agents work with this codebase
    - Architecture/project overview
    - Key file locations
    - Development setup
    - Running tests
  - Specific to codebase (not generic)
- **Returns**: Single CheckResult for the repository
- **Pass Criteria**: AGENTS.md has minimum 3 key sections with content
- **Example**: "AGENTS.md includes architecture, setup, and test instructions"

**Check: `check_api_documentation()`**
- **Purpose**: Verify API/module documentation exists
- **Detection**:
  - Look for API.md or API documentation in docs/
  - Check for docstrings in main modules (sample 10% of modules)
  - Check for Sphinx/MkDocs configuration
- **Returns**: Single CheckResult for the repository
- **Pass Criteria**: API docs found or docstrings in majority of key modules
- **Example**: "API.md found" or "Docstrings present in modules"

**Check: `check_architecture_documented()`**
- **Purpose**: Verify architecture/design documentation exists
- **Detection**:
  - Look for ARCHITECTURE.md
  - Check docs/architecture/ directory
  - Check for architecture description in AGENTS.md
  - Check for system diagrams or design docs
- **Returns**: Single CheckResult for the repository
- **Pass Criteria**: Architecture documentation found in any location
- **Example**: "Architecture documented in ARCHITECTURE.md"

### Level 4 - Optimized (Repository-wide)

**Check: `check_documentation_coverage()`**
- **Purpose**: Verify documentation covers all major components
- **Detection**:
  - Calculate percentage of directories with README or documentation
  - Check for main entry points documentation
  - Verify database/data structure documentation
  - Check for deployment/DevOps documentation
- **Returns**: Single CheckResult for the repository
- **Pass Criteria**: >=60% of major components documented
- **Example**: "Documentation covers 75% of major components"

**Check: `check_changelog_exists()`**
- **Purpose**: Verify changelog/version history exists
- **Detection**:
  - Look for CHANGELOG.md, HISTORY.md, NEWS.md
  - Check if recent entries exist (modified in last 6 months)
- **Returns**: Single CheckResult for the repository
- **Pass Criteria**: Changelog found and recently updated
- **Example**: "CHANGELOG.md exists and updated recently"

**Check: `check_inline_documentation()`**
- **Purpose**: Verify code has inline documentation/comments
- **Detection**:
  - Sample 10% of Python files, 10% of JS files, 10% of other
  - Count lines with comments/docstrings
  - Calculate documentation density (doc lines / total lines)
- **Returns**: Single CheckResult for the repository
- **Pass Criteria**: >=20% of sampled code has comments/docstrings
- **Example**: "Code has inline documentation (25% coverage)"

### Level 5 - Autonomous (Repository-wide)

**Check: `check_code_of_conduct()`**
- **Purpose**: Verify code of conduct exists
- **Detection**:
  - Look for CODE_OF_CONDUCT.md
  - Check .github/CODE_OF_CONDUCT.md
  - Check for conduct guidelines in CONTRIBUTING.md
- **Returns**: Single CheckResult for the repository
- **Pass Criteria**: Code of conduct document found
- **Example**: "CODE_OF_CONDUCT.md found"

**Check: `check_auto_generated_docs()`**
- **Purpose**: Verify documentation generation is configured
- **Detection**:
  - Look for Sphinx configuration (conf.py, sphinx/)
  - Look for MkDocs configuration (mkdocs.yml)
  - Look for TypeDoc/JSDoc configuration (typedoc.json, jsdoc.json)
  - Check for doc generation in CI pipeline
- **Returns**: Single CheckResult for the repository
- **Pass Criteria**: Doc generation tool configured
- **Example**: "MkDocs configured with docs/ directory"

**Check: `check_examples_and_tutorials()`**
- **Purpose**: Verify examples and tutorials exist
- **Detection**:
  - Look for examples/ or tutorials/ directory
  - Check for code examples in README
  - Check for Jupyter notebooks or tutorial files
  - Count example projects or demo files
- **Returns**: Single CheckResult for the repository
- **Pass Criteria**: Examples or tutorials found
- **Example**: "examples/ directory with 5 sample projects"

## Error Handling & Edge Cases

### Graceful Degradation

- **Missing README**: Level 1 fails with clear message "README not found"
- **Empty documentation**: Pass based on existence, not content if unreadable
- **Special characters**: Handle encoding issues gracefully
- **Very large files**: Don't process files >1MB, estimate quality
- **Symlinked docs**: Follow symlinks if they point to documentation

### Edge Cases

1. **Monorepo structure**: Check for docs at root and per-package levels
2. **Multiple languages**: Check for docs in multiple languages
3. **Non-Markdown docs**: Accept RST, Asciidoc, plain text
4. **Bare minimum projects**: Pass Level 1-2 with just README
5. **Very new projects**: Consider project age when evaluating documentation

### Content Quality Detection

For text analysis:
- Ignore commented-out code
- Detect section headers (## or ----)
- Measure readability (avoid purely technical jargon)
- Check for links (especially to setup guides)
- Validate code examples are recent/valid

## File Organization

```
src/agent_readiness/
├── pillars/
│   ├── __init__.py
│   ├── style.py
│   ├── build.py
│   ├── testing.py
│   └── documentation.py    # DocumentationPillar implementation
├── models.py
├── pillar.py
├── scanner.py
└── cli.py

tests/
└── pillars/
    ├── test_style.py
    ├── test_build.py
    ├── test_testing.py
    └── test_documentation.py  # DocumentationPillar tests
```

## Testing Strategy

### Unit Tests

Test each check function with fixture directories:

```python
def test_check_readme_exists_found()
def test_check_readme_exists_not_found()
def test_check_readme_quality_excellent()
def test_check_readme_quality_poor()
def test_check_agents_md_exists_found()
def test_check_agents_md_quality_complete()
def test_check_api_documentation_found()
def test_check_architecture_documented()
def test_check_documentation_coverage()
def test_check_changelog_exists()
def test_check_inline_documentation()
def test_check_code_of_conduct()
def test_check_auto_generated_docs()
def test_check_examples_and_tutorials()
```

### Integration Tests

```python
def test_scanner_with_documentation_pillar()
def test_documentation_pillar_with_well_documented_project()
def test_documentation_pillar_with_minimal_project()
```

### Fixture Repos

- `fixtures/docs-complete/` - Fully documented project (AGENTS.md, README, docs/, API docs)
- `fixtures/docs-minimal/` - Only README.md
- `fixtures/docs-none/` - No documentation
- `fixtures/docs-agents-focused/` - Great AGENTS.md but minimal README
- `fixtures/docs-with-examples/` - Includes examples/ and tutorials/

## Implementation Plan

1. Create `documentation.py` in pillars directory
2. Implement `DocumentationPillar` class skeleton
3. Implement file/directory discovery
4. Implement Level 1 checks (README exists)
5. Implement Level 2 checks (README quality, AGENTS.md, CONTRIBUTING)
6. Implement Level 3 checks (AGENTS quality, API docs, architecture)
7. Implement Level 4 checks (coverage, changelog, inline docs)
8. Implement Level 5 checks (CoC, auto-generated docs, examples)
9. Write comprehensive unit tests
10. Create test fixtures with various documentation setups
11. Integration tests
12. Update scanner to register DocumentationPillar
13. Manual testing with real repositories

## Success Criteria

- [ ] All 10+ checks implemented and tested
- [ ] Supports README, AGENTS.md, docs/, and inline documentation
- [ ] Correctly detects documentation quality indicators
- [ ] Handles edge cases gracefully (encoding, symlinks, monorepos)
- [ ] Tests achieve >85% coverage
- [ ] DocumentationPillar can be registered with Scanner
- [ ] Works on real-world repositories with various documentation styles

## Future Enhancements

- AI-powered documentation quality assessment (semantic analysis)
- Documentation freshness detection (git blame on docs)
- Multi-language documentation detection
- Integration with readthedocs or similar platforms
- Screenshot/diagram detection in documentation
- Search capability in documentation index
- Documentation consistency checking (terminology, formatting)
