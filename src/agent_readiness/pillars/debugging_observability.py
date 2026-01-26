"""Debugging and Observability pillar implementation."""

import re
from pathlib import Path

from agent_readiness.pillar import Pillar
from agent_readiness.models import CheckResult, Severity


class DebuggingObservabilityPillar(Pillar):
    """Evaluates debugging and observability infrastructure."""

    @property
    def name(self) -> str:
        """Human-readable name of this pillar."""
        return "Debugging & Observability"

    def evaluate(self, target_dir: Path) -> list[CheckResult]:
        """Evaluate the target directory for debugging and observability checks."""
        results = []

        # Discover observability assets
        obs = self._discover_observability_setup(target_dir)

        # Level 1: Functional
        results.append(self._check_logging_configuration_exists(target_dir, obs))
        results.append(self._check_error_handling_present(target_dir, obs))

        # Level 2: Documented
        results.append(self._check_logging_documented(target_dir, obs))
        results.append(self._check_error_messages_descriptive(target_dir, obs))
        results.append(self._check_debug_mode_available(target_dir, obs))
        results.append(self._check_structured_logging_indicators(target_dir, obs))

        # Level 3: Standardized
        results.append(self._check_health_check_endpoint(target_dir, obs))
        results.append(self._check_request_logging(target_dir, obs))
        results.append(self._check_performance_metrics(target_dir, obs))
        results.append(self._check_error_context_preserved(target_dir, obs))

        # Level 4: Optimized
        results.append(self._check_log_aggregation_config(target_dir, obs))
        results.append(self._check_distributed_tracing(target_dir, obs))
        results.append(self._check_custom_metrics(target_dir, obs))
        results.append(self._check_alert_configuration(target_dir, obs))

        # Level 5: Autonomous
        results.append(self._check_profiling_tools_configured(target_dir, obs))
        results.append(self._check_memory_cpu_monitoring(target_dir, obs))
        results.append(self._check_log_analysis(target_dir, obs))
        results.append(self._check_feedback_loops(target_dir, obs))

        return results

    def _discover_observability_setup(self, target_dir: Path) -> dict:
        """Discover available observability and debugging assets.

        Args:
            target_dir: Directory to scan

        Returns:
            Dict with observability configuration information
        """
        logger_config_files = []
        logging_library_found = {}
        error_handling_count = 0
        total_functions = 0
        health_check_endpoint = None
        structured_logging = {}
        monitoring_config = []
        tracing_config = None
        metrics_libraries = set()
        readme_content = ""
        agents_content = ""

        # Find logging config files
        for config in [
            "logging.conf",
            "logging.yaml",
            "logging.json",
            "log4j.properties",
            ".log4jrc",
        ]:
            if (target_dir / config).exists():
                logger_config_files.append(target_dir / config)

        # Check pyproject.toml for logging config
        if (target_dir / "pyproject.toml").exists():
            content = (target_dir / "pyproject.toml").read_text(errors="ignore")
            if "logging" in content.lower():
                logger_config_files.append(target_dir / "pyproject.toml")

        # Find logging libraries in source
        for py_file in target_dir.rglob("*.py"):
            try:
                content = py_file.read_text(errors="ignore")
                if "import logging" in content:
                    logging_library_found["python"] = "logging"
                if "structlog" in content:
                    structured_logging["python"] = "structlog"
                if "loguru" in content:
                    logging_library_found["python"] = "loguru"
            except Exception:
                pass

        # Check package.json for logging libraries
        if (target_dir / "package.json").exists():
            content = (target_dir / "package.json").read_text(errors="ignore")
            for lib in ["winston", "pino", "bunyan"]:
                if lib in content:
                    logging_library_found["node"] = lib
                    structured_logging["node"] = lib

        # Scan for error handling patterns
        for py_file in target_dir.rglob("*.py"):
            try:
                content = py_file.read_text(errors="ignore")
                # Count function definitions
                total_functions += len(re.findall(r"def \w+\(", content))
                # Count error handling
                error_handling_count += content.count("except")
                error_handling_count += content.count("try:")
            except Exception:
                pass

        # Look for health check endpoint
        for src_file in target_dir.rglob("*.py"):
            try:
                content = src_file.read_text(errors="ignore").lower()
                if "/health" in content or "healthz" in content or "health_check" in content:
                    health_check_endpoint = src_file
                    break
            except Exception:
                pass

        # Find monitoring config files
        for config in [
            "prometheus.yml",
            "prometheus_rules.yml",
            "datadog.yaml",
            "jaeger.yml",
            ".monitoring",
        ]:
            if (target_dir / config).exists():
                monitoring_config.append(target_dir / config)

        # Check for tracing config
        for file in target_dir.rglob("*"):
            if "otel" in file.name.lower() or "tracing" in file.name.lower():
                if file.is_file():
                    tracing_config = file
                    break

        # Look for metrics libraries
        if (target_dir / "pyproject.toml").exists():
            content = (target_dir / "pyproject.toml").read_text(errors="ignore")
            if "prometheus" in content:
                metrics_libraries.add("prometheus")
            if "opentelemetry" in content:
                metrics_libraries.add("opentelemetry")

        # Read documentation
        readme = target_dir / "README.md"
        if readme.exists():
            readme_content = readme.read_text(errors="ignore").lower()

        agents = target_dir / "AGENTS.md"
        if agents.exists():
            agents_content = agents.read_text(errors="ignore").lower()

        return {
            "logger_config_files": logger_config_files,
            "logging_library_found": logging_library_found,
            "error_handling_rate": (
                error_handling_count / max(total_functions, 1) * 100
            ),
            "health_check_endpoint": health_check_endpoint,
            "structured_logging": structured_logging,
            "monitoring_config": monitoring_config,
            "tracing_config": tracing_config,
            "metrics_libraries": metrics_libraries,
            "readme_content": readme_content,
            "agents_content": agents_content,
        }

    # Level 1: Functional

    def _check_logging_configuration_exists(
        self, target_dir: Path, obs: dict
    ) -> CheckResult:
        """Check if logging configuration exists."""
        if obs["logger_config_files"] or obs["logging_library_found"]:
            return CheckResult(
                name="Logging configuration exists",
                passed=True,
                message="Logging configuration detected",
                severity=Severity.REQUIRED,
                level=1,
            )
        else:
            return CheckResult(
                name="Logging configuration exists",
                passed=False,
                message="No logging configuration found",
                severity=Severity.REQUIRED,
                level=1,
            )

    def _check_error_handling_present(self, target_dir: Path, obs: dict) -> CheckResult:
        """Check if error handling patterns are present."""
        if obs["error_handling_rate"] > 5:
            return CheckResult(
                name="Error handling present",
                passed=True,
                message=f"Error handling detected ({obs['error_handling_rate']:.1f}% coverage)",
                severity=Severity.REQUIRED,
                level=1,
            )
        else:
            return CheckResult(
                name="Error handling present",
                passed=False,
                message="No error handling patterns detected",
                severity=Severity.REQUIRED,
                level=1,
            )

    # Level 2: Documented

    def _check_logging_documented(self, target_dir: Path, obs: dict) -> CheckResult:
        """Check if logging is documented."""
        content = obs["readme_content"] + obs["agents_content"]

        keywords = ["logging", "logs", "debug", "monitoring"]
        has_keywords = any(keyword in content for keyword in keywords)

        if has_keywords and len(content) > 100:
            return CheckResult(
                name="Logging documented",
                passed=True,
                message="Logging setup documented in README or AGENTS.md",
                severity=Severity.RECOMMENDED,
                level=2,
            )
        else:
            return CheckResult(
                name="Logging documented",
                passed=False,
                message="Logging setup not documented",
                severity=Severity.RECOMMENDED,
                level=2,
            )

    def _check_error_messages_descriptive(
        self, target_dir: Path, obs: dict
    ) -> CheckResult:
        """Check if error messages are descriptive."""
        error_count = 0
        descriptive_count = 0

        for py_file in target_dir.rglob("*.py"):
            try:
                content = py_file.read_text(errors="ignore")
                # Look for raise statements with messages
                raises = re.findall(r'raise \w+\((.*?)\)', content)
                error_count += len(raises)

                # Check if they include variables/context
                for raise_msg in raises:
                    if "{" in raise_msg or "f\"" in raise_msg or "f'" in raise_msg:
                        descriptive_count += 1
            except Exception:
                pass

        if error_count > 0 and descriptive_count / error_count >= 0.5:
            return CheckResult(
                name="Error messages descriptive",
                passed=True,
                message="Error messages include descriptive context",
                severity=Severity.RECOMMENDED,
                level=2,
            )
        elif error_count > 0:
            return CheckResult(
                name="Error messages descriptive",
                passed=False,
                message="Error messages lack descriptive context",
                severity=Severity.RECOMMENDED,
                level=2,
            )
        else:
            return CheckResult(
                name="Error messages descriptive",
                passed=False,
                message="No error messages found to evaluate",
                severity=Severity.RECOMMENDED,
                level=2,
            )

    def _check_debug_mode_available(self, target_dir: Path, obs: dict) -> CheckResult:
        """Check if debug mode is available."""
        content = obs["readme_content"] + obs["agents_content"]

        # Check for DEBUG mentions
        has_debug = "debug" in content

        # Check .env.example
        if (target_dir / ".env.example").exists():
            env_content = (target_dir / ".env.example").read_text(errors="ignore")
            if "debug" in env_content.lower():
                has_debug = True

        # Check config files
        for config_file in ["config.py", "settings.py", ".flaskenv"]:
            if (target_dir / config_file).exists():
                config_content = (target_dir / config_file).read_text(errors="ignore")
                if "debug" in config_content.lower():
                    has_debug = True

        if has_debug:
            return CheckResult(
                name="Debug mode available",
                passed=True,
                message="Debug mode available via environment or config",
                severity=Severity.RECOMMENDED,
                level=2,
            )
        else:
            return CheckResult(
                name="Debug mode available",
                passed=False,
                message="No debug mode configuration found",
                severity=Severity.RECOMMENDED,
                level=2,
            )

    def _check_structured_logging_indicators(
        self, target_dir: Path, obs: dict
    ) -> CheckResult:
        """Check for structured logging indicators."""
        if obs["structured_logging"] or obs["metrics_libraries"]:
            return CheckResult(
                name="Structured logging indicators",
                passed=True,
                message="Structured logging library detected",
                severity=Severity.OPTIONAL,
                level=2,
            )

        # Check for JSON logging patterns
        for py_file in target_dir.rglob("*.py"):
            try:
                content = py_file.read_text(errors="ignore")
                if "json.dumps" in content and "logging" in content:
                    return CheckResult(
                        name="Structured logging indicators",
                        passed=True,
                        message="JSON structured logging detected",
                        severity=Severity.OPTIONAL,
                        level=2,
                    )
            except Exception:
                pass

        return CheckResult(
            name="Structured logging indicators",
            passed=False,
            message="No structured logging detected",
            severity=Severity.OPTIONAL,
            level=2,
        )

    # Level 3: Standardized

    def _check_health_check_endpoint(self, target_dir: Path, obs: dict) -> CheckResult:
        """Check if health check endpoint exists."""
        if obs["health_check_endpoint"]:
            return CheckResult(
                name="Health check endpoint",
                passed=True,
                message="Health check endpoint configured",
                severity=Severity.OPTIONAL,
                level=3,
            )

        # Also check for /health patterns in all Python files
        for py_file in target_dir.rglob("*.py"):
            try:
                content = py_file.read_text(errors="ignore")
                if (
                    '"/health"' in content
                    or "'/health'" in content
                    or "/healthz" in content
                ):
                    return CheckResult(
                        name="Health check endpoint",
                        passed=True,
                        message="Health check endpoint configured",
                        severity=Severity.OPTIONAL,
                        level=3,
                    )
            except Exception:
                pass

        return CheckResult(
            name="Health check endpoint",
            passed=False,
            message="No health check endpoint found",
            severity=Severity.OPTIONAL,
            level=3,
        )

    def _check_request_logging(self, target_dir: Path, obs: dict) -> CheckResult:
        """Check if request logging is configured."""
        request_logging_keywords = [
            "request logging",
            "http logging",
            "middleware",
            "access_log",
            "request_log",
        ]
        content = obs["readme_content"] + obs["agents_content"]

        if any(keyword in content for keyword in request_logging_keywords):
            return CheckResult(
                name="Request logging configured",
                passed=True,
                message="Request logging documented",
                severity=Severity.OPTIONAL,
                level=3,
            )

        # Check source files
        for py_file in target_dir.rglob("*.py"):
            try:
                file_content = py_file.read_text(errors="ignore")
                if "access_log" in file_content or "request_log" in file_content:
                    return CheckResult(
                        name="Request logging configured",
                        passed=True,
                        message="Request logging middleware detected",
                        severity=Severity.OPTIONAL,
                        level=3,
                    )
            except Exception:
                pass

        return CheckResult(
            name="Request logging configured",
            passed=False,
            message="No request logging middleware found",
            severity=Severity.OPTIONAL,
            level=3,
        )

    def _check_performance_metrics(self, target_dir: Path, obs: dict) -> CheckResult:
        """Check if performance metrics are configured."""
        metrics_keywords = [
            "timing",
            "latency",
            "duration",
            "performance",
            "benchmark",
            "metric",
        ]
        content = obs["readme_content"] + obs["agents_content"]

        if any(keyword in content for keyword in metrics_keywords):
            return CheckResult(
                name="Performance metrics configured",
                passed=True,
                message="Performance metrics documented",
                severity=Severity.OPTIONAL,
                level=3,
            )

        # Check for timing code
        for py_file in target_dir.rglob("*.py"):
            try:
                file_content = py_file.read_text(errors="ignore")
                if "time.time()" in file_content or "timeit" in file_content:
                    return CheckResult(
                        name="Performance metrics configured",
                        passed=True,
                        message="Performance metrics detected",
                        severity=Severity.OPTIONAL,
                        level=3,
                    )
            except Exception:
                pass

        return CheckResult(
            name="Performance metrics configured",
            passed=False,
            message="No performance metrics found",
            severity=Severity.OPTIONAL,
            level=3,
        )

    def _check_error_context_preserved(
        self, target_dir: Path, obs: dict
    ) -> CheckResult:
        """Check if error context is preserved."""
        for py_file in target_dir.rglob("*.py"):
            try:
                content = py_file.read_text(errors="ignore")
                # Look for exception chaining or wrapping
                if "raise" in content and "from" in content:
                    if re.search(r"raise.*from\s+\w+", content):
                        return CheckResult(
                            name="Error context preserved",
                            passed=True,
                            message="Error context preservation detected",
                            severity=Severity.OPTIONAL,
                            level=3,
                        )
            except Exception:
                pass

        return CheckResult(
            name="Error context preserved",
            passed=False,
            message="Error context may not be preserved",
            severity=Severity.OPTIONAL,
            level=3,
        )

    # Level 4: Optimized

    def _check_log_aggregation_config(self, target_dir: Path, obs: dict) -> CheckResult:
        """Check if log aggregation is configured."""
        if obs["monitoring_config"]:
            return CheckResult(
                name="Log aggregation configured",
                passed=True,
                message="Log aggregation configuration found",
                severity=Severity.OPTIONAL,
                level=4,
            )

        # Check for common log aggregation patterns
        aggregation_keywords = ["datadog", "elasticsearch", "logstash", "kibana"]
        content = obs["readme_content"] + obs["agents_content"]

        if any(keyword in content for keyword in aggregation_keywords):
            return CheckResult(
                name="Log aggregation configured",
                passed=True,
                message="Log aggregation service mentioned",
                severity=Severity.OPTIONAL,
                level=4,
            )

        return CheckResult(
            name="Log aggregation configured",
            passed=False,
            message="No log aggregation configuration found",
            severity=Severity.OPTIONAL,
            level=4,
        )

    def _check_distributed_tracing(self, target_dir: Path, obs: dict) -> CheckResult:
        """Check if distributed tracing is configured."""
        if obs["tracing_config"]:
            return CheckResult(
                name="Distributed tracing configured",
                passed=True,
                message="Distributed tracing configuration found",
                severity=Severity.OPTIONAL,
                level=4,
            )

        # Check for tracing libraries
        tracing_keywords = ["opentelemetry", "jaeger", "zipkin", "otel"]
        content = obs["readme_content"] + obs["agents_content"]

        if any(keyword in content for keyword in tracing_keywords):
            return CheckResult(
                name="Distributed tracing configured",
                passed=True,
                message="Distributed tracing mentioned",
                severity=Severity.OPTIONAL,
                level=4,
            )

        # Check pyproject.toml
        if (target_dir / "pyproject.toml").exists():
            content = (target_dir / "pyproject.toml").read_text(errors="ignore")
            if any(keyword in content for keyword in tracing_keywords):
                return CheckResult(
                    name="Distributed tracing configured",
                    passed=True,
                    message="Distributed tracing library found",
                    severity=Severity.OPTIONAL,
                    level=4,
                )

        return CheckResult(
            name="Distributed tracing configured",
            passed=False,
            message="No distributed tracing configured",
            severity=Severity.OPTIONAL,
            level=4,
        )

    def _check_custom_metrics(self, target_dir: Path, obs: dict) -> CheckResult:
        """Check if custom metrics are present."""
        if obs["metrics_libraries"]:
            return CheckResult(
                name="Custom metrics present",
                passed=True,
                message="Metrics library detected",
                severity=Severity.OPTIONAL,
                level=4,
            )

        # Look for metrics in code
        metrics_keywords = [
            "prometheus",
            "statsd",
            "metric",
            "gauge",
            "counter",
            "histogram",
        ]
        content = obs["readme_content"] + obs["agents_content"]

        if any(keyword in content for keyword in metrics_keywords):
            return CheckResult(
                name="Custom metrics present",
                passed=True,
                message="Custom metrics documented",
                severity=Severity.OPTIONAL,
                level=4,
            )

        # Check source code
        for py_file in target_dir.rglob("*.py"):
            try:
                file_content = py_file.read_text(errors="ignore")
                if any(keyword in file_content for keyword in metrics_keywords):
                    return CheckResult(
                        name="Custom metrics present",
                        passed=True,
                        message="Custom metrics detected",
                        severity=Severity.OPTIONAL,
                        level=4,
                    )
            except Exception:
                pass

        return CheckResult(
            name="Custom metrics present",
            passed=False,
            message="No custom metrics found",
            severity=Severity.OPTIONAL,
            level=4,
        )

    def _check_alert_configuration(self, target_dir: Path, obs: dict) -> CheckResult:
        """Check if alert configuration exists."""
        alert_files = ["prometheus_rules.yml", "alert_rules.yml", "alerts.yml"]

        for alert_file in alert_files:
            if (target_dir / alert_file).exists():
                return CheckResult(
                    name="Alert configuration present",
                    passed=True,
                    message="Alert configuration found",
                    severity=Severity.OPTIONAL,
                    level=4,
                )

        # Check for alert mentions
        alert_keywords = ["alert", "pagerduty", "datadog monitor", "alarm"]
        content = obs["readme_content"] + obs["agents_content"]

        if any(keyword in content for keyword in alert_keywords):
            return CheckResult(
                name="Alert configuration present",
                passed=True,
                message="Alert configuration mentioned",
                severity=Severity.OPTIONAL,
                level=4,
            )

        return CheckResult(
            name="Alert configuration present",
            passed=False,
            message="No alert configuration found",
            severity=Severity.OPTIONAL,
            level=4,
        )

    # Level 5: Autonomous

    def _check_profiling_tools_configured(
        self, target_dir: Path, obs: dict
    ) -> CheckResult:
        """Check if profiling tools are configured."""
        profiling_keywords = [
            "pprof",
            "py-spy",
            "cprofile",
            "flamegraph",
            "clinic.js",
            "autocannon",
        ]
        content = obs["readme_content"] + obs["agents_content"]

        if any(keyword in content for keyword in profiling_keywords):
            return CheckResult(
                name="Profiling tools configured",
                passed=True,
                message="Profiling tools documented",
                severity=Severity.OPTIONAL,
                level=5,
            )

        # Check Makefile or package.json
        if (target_dir / "Makefile").exists():
            make_content = (target_dir / "Makefile").read_text(errors="ignore")
            if any(keyword in make_content for keyword in profiling_keywords):
                return CheckResult(
                    name="Profiling tools configured",
                    passed=True,
                    message="Profiling target in Makefile",
                    severity=Severity.OPTIONAL,
                    level=5,
                )

        return CheckResult(
            name="Profiling tools configured",
            passed=False,
            message="No profiling tools configured",
            severity=Severity.OPTIONAL,
            level=5,
        )

    def _check_memory_cpu_monitoring(self, target_dir: Path, obs: dict) -> CheckResult:
        """Check if memory and CPU monitoring is configured."""
        monitoring_keywords = [
            "memory",
            "cpu",
            "heap",
            "gc monitoring",
            "resource utilization",
        ]
        content = obs["readme_content"] + obs["agents_content"]

        if any(keyword in content for keyword in monitoring_keywords):
            return CheckResult(
                name="Memory/CPU monitoring configured",
                passed=True,
                message="Memory and CPU monitoring documented",
                severity=Severity.OPTIONAL,
                level=5,
            )

        # Check source code
        for py_file in target_dir.rglob("*.py"):
            try:
                file_content = py_file.read_text(errors="ignore")
                if "psutil" in file_content or "resource" in file_content:
                    return CheckResult(
                        name="Memory/CPU monitoring configured",
                        passed=True,
                        message="Memory/CPU monitoring detected",
                        severity=Severity.OPTIONAL,
                        level=5,
                    )
            except Exception:
                pass

        return CheckResult(
            name="Memory/CPU monitoring configured",
            passed=False,
            message="No memory/CPU monitoring found",
            severity=Severity.OPTIONAL,
            level=5,
        )

    def _check_log_analysis(self, target_dir: Path, obs: dict) -> CheckResult:
        """Check if log analysis tools are configured."""
        analysis_keywords = [
            "elk",
            "splunk",
            "datadog",
            "log analysis",
            "dashboard",
            "kibana",
        ]
        content = obs["readme_content"] + obs["agents_content"]

        if any(keyword in content for keyword in analysis_keywords):
            return CheckResult(
                name="Log analysis tools configured",
                passed=True,
                message="Log analysis tools documented",
                severity=Severity.OPTIONAL,
                level=5,
            )

        return CheckResult(
            name="Log analysis tools configured",
            passed=False,
            message="No log analysis tools found",
            severity=Severity.OPTIONAL,
            level=5,
        )

    def _check_feedback_loops(self, target_dir: Path, obs: dict) -> CheckResult:
        """Check if observability feeds back into system."""
        feedback_keywords = [
            "autoscaling",
            "circuit breaker",
            "auto-scaling",
            "adaptive",
            "self-healing",
        ]
        content = obs["readme_content"] + obs["agents_content"]

        if any(keyword in content for keyword in feedback_keywords):
            return CheckResult(
                name="Observability feedback loops configured",
                passed=True,
                message="Observability feedback loops documented",
                severity=Severity.OPTIONAL,
                level=5,
            )

        # Check for autoscaling config files
        if (target_dir / ".keda" / "scaler.yaml").exists() or (
            target_dir / ".hpa" / "config.yaml"
        ).exists():
            return CheckResult(
                name="Observability feedback loops configured",
                passed=True,
                message="Auto-scaling configuration found",
                severity=Severity.OPTIONAL,
                level=5,
            )

        return CheckResult(
            name="Observability feedback loops configured",
            passed=False,
            message="No feedback loops from observability detected",
            severity=Severity.OPTIONAL,
            level=5,
        )
