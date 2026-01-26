# Pillar 6: Debugging & Observability Design Document

**Date**: January 26, 2026
**Status**: In Progress
**Coverage Target**: 85%+
**Test Count Target**: 35+ tests

## Overview

The **Debugging & Observability Pillar** evaluates how well a codebase supports troubleshooting, monitoring, and understanding system behavior. Good debugging and observability means:

- Issues can be diagnosed quickly through logs and error messages
- System behavior is visible at runtime
- Errors provide actionable information
- Debugging tools and profiles are available
- Performance insights are captured

## What We're Measuring

### Level 1: Functional (Basic Logging)
**Goal**: Basic logging exists but may be inconsistent

Checks:
- ✅ **Logging configuration exists**: Logger setup found (logging.conf, log4j, winston, etc.)
- ✅ **Error handling present**: Try-catch/error handling in source files

### Level 2: Documented (Logging Standards)
**Goal**: Logging approach is documented and reasonably consistent

Checks:
- ✅ **Logging documented**: README or AGENTS.md explains logging setup
- ✅ **Error messages descriptive**: Sample error messages contain context
- ✅ **Debug mode available**: DEBUG flag or debug logging level
- ✅ **Structured logging indicators**: Use of structured logging libraries

### Level 3: Standardized (Comprehensive Observability)
**Goal**: Logging and error handling follow consistent patterns

Checks:
- ✅ **Health check endpoint**: /health or similar monitoring endpoint
- ✅ **Request/response logging**: Logging of HTTP requests or API calls
- ✅ **Performance metrics**: Timing/latency measurements in code
- ✅ **Error context preserved**: Stack traces and error chains maintained

### Level 4: Optimized (Advanced Monitoring)
**Goal**: Production-ready observability with deep insights

Checks:
- ✅ **Log aggregation config**: ELK, Datadog, CloudWatch, etc.
- ✅ **Distributed tracing**: OpenTelemetry, Jaeger, or similar
- ✅ **Custom metrics**: Business metrics logging (conversions, events, etc.)
- ✅ **Alert configuration**: Alerts for errors/failures

### Level 5: Autonomous (Self-Healing & Insight)
**Goal**: System proactively monitors itself and provides deep insights

Checks:
- ✅ **Profiling tools configured**: pprof, flame graphs, async_profiler
- ✅ **Memory/CPU monitoring**: Runtime performance tracking
- ✅ **Log analysis**: Automated log parsing/anomaly detection
- ✅ **Feedback loops**: Logs feed back into system optimization

## Architecture

### Class Structure

```python
class DebuggingObservabilityPillar(Pillar):
    name: str = "Debugging & Observability"
    weight: float = 1.0

    # Discovery
    def _discover_observability_setup(target_dir: Path) -> dict

    # Level 1: Functional
    def _check_logging_configuration_exists(target_dir: Path) -> CheckResult
    def _check_error_handling_present(target_dir: Path) -> CheckResult

    # Level 2: Documented
    def _check_logging_documented(target_dir: Path) -> CheckResult
    def _check_error_messages_descriptive(target_dir: Path) -> CheckResult
    def _check_debug_mode_available(target_dir: Path) -> CheckResult
    def _check_structured_logging_indicators(target_dir: Path) -> CheckResult

    # Level 3: Standardized
    def _check_health_check_endpoint(target_dir: Path) -> CheckResult
    def _check_request_logging(target_dir: Path) -> CheckResult
    def _check_performance_metrics(target_dir: Path) -> CheckResult
    def _check_error_context_preserved(target_dir: Path) -> CheckResult

    # Level 4: Optimized
    def _check_log_aggregation_config(target_dir: Path) -> CheckResult
    def _check_distributed_tracing(target_dir: Path) -> CheckResult
    def _check_custom_metrics(target_dir: Path) -> CheckResult
    def _check_alert_configuration(target_dir: Path) -> CheckResult

    # Level 5: Autonomous
    def _check_profiling_tools_configured(target_dir: Path) -> CheckResult
    def _check_memory_cpu_monitoring(target_dir: Path) -> CheckResult
    def _check_log_analysis(target_dir: Path) -> CheckResult
    def _check_feedback_loops(target_dir: Path) -> CheckResult
```

### Discovery Logic (`_discover_observability_setup`)

Returns dict with keys:
- `logger_config_files`: List of logging config files found
- `logging_library_found`: Dict of language → logging library detected
- `error_handling_rate`: Approximate % of functions with error handling
- `health_check_endpoint`: Path to health check implementation
- `structured_logging`: Detected structured logging (JSON, etc.)
- `monitoring_config`: Config files for monitoring tools
- `tracing_config`: OpenTelemetry or distributed tracing config
- `metrics_libraries`: Detected metrics libraries
- `readme_content`: README.md content
- `agents_content`: AGENTS.md content
- `source_files`: List of main source files for analysis

## Detailed Check Implementations

### Level 1

#### _check_logging_configuration_exists
- **Severity**: REQUIRED
- **Level**: 1
- **Logic**:
  - Look for logging config files:
    - Python: logging.conf, logging.yaml, pyproject.toml with logging config
    - Node.js: winston config, pino config, bunyan config
    - Go: logrus config, zap config
    - Rust: log config, tracing config
  - At least one must exist
- **Failure message**: "No logging configuration found"
- **Pass message**: "Logging configuration found"

#### _check_error_handling_present
- **Severity**: REQUIRED
- **Level**: 1
- **Logic**:
  - Sample source files for try-catch, error handling patterns
  - Look for: except, catch, Result types, Error types
  - At least 5% of functions should have visible error handling
- **Failure message**: "No error handling patterns detected"
- **Pass message**: "Error handling patterns detected"

### Level 2

#### _check_logging_documented
- **Severity**: RECOMMENDED
- **Level**: 2
- **Logic**:
  - Search README/AGENTS.md for logging setup keywords
  - Keywords: "logging", "logs", "debug", "monitoring"
  - Minimum 100 characters of logging documentation
- **Failure message**: "Logging setup not documented"
- **Pass message**: "Logging setup documented"

#### _check_error_messages_descriptive
- **Severity**: RECOMMENDED
- **Level**: 2
- **Logic**:
  - Scan source code for error messages/exceptions
  - Look for: formatted strings with context, f-strings with variables
  - Avoid generic messages like "Error" or "Failed"
  - At least 50% of errors should include context variables
- **Failure message**: "Error messages lack descriptive context"
- **Pass message**: "Error messages include descriptive context"

#### _check_debug_mode_available
- **Severity**: RECOMMENDED
- **Level**: 2
- **Logic**:
  - Look for DEBUG flag, LOGLEVEL env var, debug mode flag
  - Check: .env.example contains DEBUG, config shows debug setting
  - README mentions debug mode
- **Failure message**: "No debug mode configuration found"
- **Pass message**: "Debug mode available via environment or config"

#### _check_structured_logging_indicators
- **Severity**: OPTIONAL
- **Level**: 2
- **Logic**:
  - Look for structured logging library usage:
    - Python: json.dumps, structlog, pythonjsonlogger
    - Node.js: winston, pino, bunyan (with JSON format)
    - Go: logrus, zap, slog
    - Rust: slog, tracing
  - Also check for JSON output in logs
- **Failure message**: "No structured logging detected"
- **Pass message**: "Structured logging library detected"

### Level 3

#### _check_health_check_endpoint
- **Severity**: OPTIONAL
- **Level**: 3
- **Logic**:
  - Look for /health, /healthz, /status endpoints
  - Search source code for "health" endpoint definitions
  - Check if health check returns JSON status
- **Failure message**: "No health check endpoint found"
- **Pass message**: "Health check endpoint configured"

#### _check_request_logging
- **Severity**: OPTIONAL
- **Level**: 3
- **Logic**:
  - Look for HTTP request/response logging
  - Search for middleware that logs requests
  - Check for: request logging frameworks, middleware
- **Failure message**: "No request logging middleware found"
- **Pass message**: "Request logging configured"

#### _check_performance_metrics
- **Severity**: OPTIONAL
- **Level**: 3
- **Logic**:
  - Search for timing/latency measurement code
  - Look for: time.time, Performance.mark, prometheus metrics
  - Scan for duration, latency, timing keywords
- **Failure message**: "No performance metrics found"
- **Pass message**: "Performance metrics detected"

#### _check_error_context_preserved
- **Severity**: OPTIONAL
- **Level**: 3
- **Logic**:
  - Check if error handling preserves stack traces
  - Look for: exception chaining (raise ... from ...), error wrapping
  - Check for use of structured exceptions with context
- **Failure message**: "Error context may not be preserved"
- **Pass message**: "Error context preservation detected"

### Level 4

#### _check_log_aggregation_config
- **Severity**: OPTIONAL
- **Level**: 4
- **Logic**:
  - Look for log aggregation config files:
    - Datadog agent config
    - ELK stack config (elasticsearch, logstash, kibana)
    - CloudWatch config
    - Splunk forwarder config
    - GCP Cloud Logging config
- **Failure message**: "No log aggregation configuration found"
- **Pass message**: "Log aggregation configured"

#### _check_distributed_tracing
- **Severity**: OPTIONAL
- **Level**: 4
- **Logic**:
  - Look for distributed tracing configuration:
    - OpenTelemetry imports/setup
    - Jaeger client config
    - Zipkin config
    - AWS X-Ray config
  - Check for tracing middleware/instrumentation
- **Failure message**: "No distributed tracing configured"
- **Pass message**: "Distributed tracing configured"

#### _check_custom_metrics
- **Severity**: OPTIONAL
- **Level**: 4
- **Logic**:
  - Look for custom business metrics:
    - Prometheus custom metrics
    - StatsD custom metrics
    - Application-specific event logging
  - Search for keywords: metric, event, counter, gauge, histogram
- **Failure message**: "No custom metrics found"
- **Pass message**: "Custom metrics detected"

#### _check_alert_configuration
- **Severity**: OPTIONAL
- **Level**: 4
- **Logic**:
  - Look for alert configuration:
    - Prometheus alerting rules
    - DataDog monitors config
    - PagerDuty integration
    - Email/Slack alert config
  - Check CI config for alert setup
- **Failure message**: "No alert configuration found"
- **Pass message**: "Alert configuration detected"

### Level 5

#### _check_profiling_tools_configured
- **Severity**: OPTIONAL
- **Level**: 5
- **Logic**:
  - Look for profiling tool configuration:
    - Python: py-spy, cProfile, line_profiler
    - Node.js: clinic.js, autocannon, 0x
    - Go: pprof, graphviz config
    - Rust: perf, flamegraph
  - Check for profiling scripts in package.json or Makefile
- **Failure message**: "No profiling tools configured"
- **Pass message**: "Profiling tools configured"

#### _check_memory_cpu_monitoring
- **Severity**: OPTIONAL
- **Level**: 5
- **Logic**:
  - Look for runtime memory/CPU monitoring:
    - Memory usage tracking
    - CPU profiling setup
    - GC monitoring (for languages with GC)
    - Resource utilization logging
- **Failure message**: "No memory/CPU monitoring found"
- **Pass message**: "Memory and CPU monitoring configured"

#### _check_log_analysis
- **Severity**: OPTIONAL
- **Level**: 5
- **Logic**:
  - Look for log analysis tools/scripts:
    - ELK stack analysis dashboards
    - Splunk saved searches
    - Datadog monitors
    - Custom log parsing scripts
- **Failure message**: "No log analysis tools found"
- **Pass message**: "Log analysis tools configured"

#### _check_feedback_loops
- **Severity**: OPTIONAL
- **Level**: 5
- **Logic**:
  - Check if observability data feeds back into system:
    - Logs trigger alerts that update system state
    - Metrics drive auto-scaling decisions
    - Error patterns influence code deployment
    - Performance data guides optimization efforts
  - Look for: autoscaling config, circuit breaker patterns, adaptive code
- **Failure message**: "No feedback loops from observability detected"
- **Pass message**: "Observability feedback loops configured"

## Test Fixtures

Create 5 fixture directories under `tests/fixtures/`:

### 1. `observability-complete/`
Full observability setup:
- logging.conf with JSON formatting
- Health check endpoint in source code
- Structured logging examples
- prometheus_rules.yml
- Health check script
- Monitoring documented in README

### 2. `observability-basic/`
Minimal logging setup:
- Basic logging config
- Error handling in source
- Debug mode available
- Some error messages with context

### 3. `observability-none/`
No observability setup:
- No logging config
- No structured logging
- Minimal error handling
- No monitoring

### 4. `observability-advanced/`
Advanced monitoring setup:
- OpenTelemetry config
- Prometheus metrics
- Distributed tracing
- Custom metrics
- Alert rules

### 5. `observability-python/`
Python-specific observability:
- logging.yaml config
- loguru setup
- structlog example
- Performance timing
- Health check endpoint

## Testing Strategy

### Unit Tests (35+ tests)
1. Discovery tests (2): All assets found, none found
2. Level 1 tests (4): Logging config, error handling
3. Level 2 tests (8): Documented logging, error messages, debug, structured
4. Level 3 tests (8): Health check, request logging, metrics, error context
5. Level 4 tests (8): Log aggregation, tracing, custom metrics, alerts
6. Level 5 tests (8): Profiling, memory/CPU, log analysis, feedback loops
7. Integration test (1): Full evaluate() with realistic project
8. Import test (1): DebuggingObservabilityPillar importable

### Fixture Usage
Each test uses appropriate fixture from the 5 directories above.

## Implementation Checklist

- [ ] Create design document (this file)
- [ ] Create `src/agent_readiness/pillars/debugging_observability.py` (400+ lines)
- [ ] Update `src/agent_readiness/pillars/__init__.py` to import and export
- [ ] Create 5 test fixture directories with realistic projects
- [ ] Create `tests/pillars/test_debugging_observability.py` (500+ lines, 35+ tests)
- [ ] Run tests and ensure 85%+ coverage
- [ ] Verify all tests pass (should add ~35 tests to suite)
- [ ] Commit with message: "feat(observability): implement Pillar 6"

## Success Criteria

- ✅ All 35+ new tests pass
- ✅ 85%+ code coverage for DebuggingObservabilityPillar
- ✅ All 170+ existing tests still pass
- ✅ Each check returns clear pass/fail with actionable guidance
- ✅ Supports Python, Node, Go, Rust projects
- ✅ Fixture tests reflect realistic observability scenarios
