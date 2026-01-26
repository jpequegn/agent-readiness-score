"""Tests for Debugging & Observability pillar."""

from pathlib import Path

from agent_readiness.pillars.debugging_observability import DebuggingObservabilityPillar
from agent_readiness.models import Severity


def test_debugging_observability_pillar_name() -> None:
    """Test pillar has correct name."""
    pillar = DebuggingObservabilityPillar()
    assert pillar.name == "Debugging & Observability"


def test_debugging_observability_pillar_weight() -> None:
    """Test pillar has default weight."""
    pillar = DebuggingObservabilityPillar()
    assert pillar.weight == 1.0


def test_discover_observability_setup_complete(tmp_path: Path) -> None:
    """Test discovering all observability assets."""
    (tmp_path / "logging.conf").touch()
    (tmp_path / "prometheus.yml").touch()
    (tmp_path / "otel-config.yaml").touch()
    (tmp_path / "README.md").write_text("# Project\n\n## Logging\n\nWe use logging here.")

    pillar = DebuggingObservabilityPillar()
    obs = pillar._discover_observability_setup(tmp_path)

    assert obs["logger_config_files"]
    assert obs["monitoring_config"]
    assert obs["tracing_config"] is not None
    assert "logging" in obs["readme_content"]


def test_discover_observability_setup_none_found(tmp_path: Path) -> None:
    """Test discovering observability when none exists."""
    pillar = DebuggingObservabilityPillar()
    obs = pillar._discover_observability_setup(tmp_path)

    assert len(obs["logger_config_files"]) == 0
    assert len(obs["logging_library_found"]) == 0
    assert len(obs["monitoring_config"]) == 0


def test_check_logging_configuration_exists_found(tmp_path: Path) -> None:
    """Test logging config check when found."""
    (tmp_path / "logging.conf").touch()

    pillar = DebuggingObservabilityPillar()
    obs = pillar._discover_observability_setup(tmp_path)
    result = pillar._check_logging_configuration_exists(tmp_path, obs)

    assert result.passed
    assert result.severity == Severity.REQUIRED
    assert result.level == 1


def test_check_logging_configuration_exists_not_found(tmp_path: Path) -> None:
    """Test logging config check when not found."""
    pillar = DebuggingObservabilityPillar()
    obs = pillar._discover_observability_setup(tmp_path)
    result = pillar._check_logging_configuration_exists(tmp_path, obs)

    assert not result.passed


def test_check_error_handling_present_found(tmp_path: Path) -> None:
    """Test error handling check when present."""
    (tmp_path / "app.py").write_text(
        "try:\n"
        "    value = process()\n"
        "except Exception as e:\n"
        "    logger.error(f'Error: {e}')\n"
        "try:\n"
        "    another()\n"
        "except:\n"
        "    pass\n"
    )

    pillar = DebuggingObservabilityPillar()
    obs = pillar._discover_observability_setup(tmp_path)
    result = pillar._check_error_handling_present(tmp_path, obs)

    assert result.passed
    assert result.level == 1


def test_check_error_handling_present_not_found(tmp_path: Path) -> None:
    """Test error handling check when not present."""
    (tmp_path / "app.py").write_text("def func():\n    return 42\n")

    pillar = DebuggingObservabilityPillar()
    obs = pillar._discover_observability_setup(tmp_path)
    result = pillar._check_error_handling_present(tmp_path, obs)

    assert not result.passed


def test_check_logging_documented_found(tmp_path: Path) -> None:
    """Test logging documented check when found."""
    (tmp_path / "README.md").write_text(
        "# Project\n\n## Logging Configuration\n\n"
        "The application uses logging throughout with debug mode enabled via DEBUG=true."
    )

    pillar = DebuggingObservabilityPillar()
    obs = pillar._discover_observability_setup(tmp_path)
    result = pillar._check_logging_documented(tmp_path, obs)

    assert result.passed
    assert result.level == 2


def test_check_logging_documented_not_found(tmp_path: Path) -> None:
    """Test logging documented check when not found."""
    (tmp_path / "README.md").write_text("# Project")

    pillar = DebuggingObservabilityPillar()
    obs = pillar._discover_observability_setup(tmp_path)
    result = pillar._check_logging_documented(tmp_path, obs)

    assert not result.passed


def test_check_error_messages_descriptive_found(tmp_path: Path) -> None:
    """Test error messages check when descriptive."""
    (tmp_path / "app.py").write_text(
        "raise ValueError(f'Invalid value: {value}, expected {expected}')\n"
        "raise RuntimeError(f'Failed to connect to {host}:{port}')\n"
    )

    pillar = DebuggingObservabilityPillar()
    obs = pillar._discover_observability_setup(tmp_path)
    result = pillar._check_error_messages_descriptive(tmp_path, obs)

    assert result.passed
    assert result.level == 2


def test_check_error_messages_descriptive_not_found(tmp_path: Path) -> None:
    """Test error messages check when not descriptive."""
    (tmp_path / "app.py").write_text(
        "raise ValueError('Error')\n"
        "raise RuntimeError('Failed')\n"
    )

    pillar = DebuggingObservabilityPillar()
    obs = pillar._discover_observability_setup(tmp_path)
    result = pillar._check_error_messages_descriptive(tmp_path, obs)

    assert not result.passed


def test_check_debug_mode_available_env(tmp_path: Path) -> None:
    """Test debug mode check with environment variable."""
    (tmp_path / ".env.example").write_text("DEBUG=false\nLOGLEVEL=info\n")

    pillar = DebuggingObservabilityPillar()
    obs = pillar._discover_observability_setup(tmp_path)
    result = pillar._check_debug_mode_available(tmp_path, obs)

    assert result.passed
    assert result.level == 2


def test_check_debug_mode_available_readme(tmp_path: Path) -> None:
    """Test debug mode check with README mention."""
    (tmp_path / "README.md").write_text("# Project\n\nEnable debug mode with DEBUG=true")

    pillar = DebuggingObservabilityPillar()
    obs = pillar._discover_observability_setup(tmp_path)
    result = pillar._check_debug_mode_available(tmp_path, obs)

    assert result.passed


def test_check_debug_mode_available_not_found(tmp_path: Path) -> None:
    """Test debug mode check when not found."""
    (tmp_path / "README.md").write_text("# Project")

    pillar = DebuggingObservabilityPillar()
    obs = pillar._discover_observability_setup(tmp_path)
    result = pillar._check_debug_mode_available(tmp_path, obs)

    assert not result.passed


def test_check_structured_logging_indicators_found(tmp_path: Path) -> None:
    """Test structured logging check when found."""
    (tmp_path / "app.py").write_text(
        "import json\n"
        "import logging\n"
        "logger = logging.getLogger(__name__)\n"
        "logger.info(json.dumps({'event': 'started'}))\n"
    )

    pillar = DebuggingObservabilityPillar()
    obs = pillar._discover_observability_setup(tmp_path)
    result = pillar._check_structured_logging_indicators(tmp_path, obs)

    assert result.passed
    assert result.level == 2


def test_check_structured_logging_indicators_not_found(tmp_path: Path) -> None:
    """Test structured logging check when not found."""
    (tmp_path / "app.py").write_text("print('hello')\n")

    pillar = DebuggingObservabilityPillar()
    obs = pillar._discover_observability_setup(tmp_path)
    result = pillar._check_structured_logging_indicators(tmp_path, obs)

    assert not result.passed


def test_check_health_check_endpoint_found(tmp_path: Path) -> None:
    """Test health check endpoint when found."""
    (tmp_path / "app.py").write_text(
        "def health_check():\n"
        "    return {'status': 'healthy'}\n"
        "app.route('/health')(health_check)\n"
    )

    pillar = DebuggingObservabilityPillar()
    obs = pillar._discover_observability_setup(tmp_path)
    result = pillar._check_health_check_endpoint(tmp_path, obs)

    assert result.passed
    assert result.level == 3


def test_check_health_check_endpoint_not_found(tmp_path: Path) -> None:
    """Test health check endpoint when not found."""
    (tmp_path / "app.py").write_text("def main():\n    pass\n")

    pillar = DebuggingObservabilityPillar()
    obs = pillar._discover_observability_setup(tmp_path)
    result = pillar._check_health_check_endpoint(tmp_path, obs)

    assert not result.passed


def test_check_request_logging_found(tmp_path: Path) -> None:
    """Test request logging check when found."""
    (tmp_path / "README.md").write_text(
        "# Project\n\n## Request Logging\n\nAll HTTP requests are logged with timing."
    )

    pillar = DebuggingObservabilityPillar()
    obs = pillar._discover_observability_setup(tmp_path)
    result = pillar._check_request_logging(tmp_path, obs)

    assert result.passed
    assert result.level == 3


def test_check_request_logging_not_found(tmp_path: Path) -> None:
    """Test request logging check when not found."""
    (tmp_path / "README.md").write_text("# Project")

    pillar = DebuggingObservabilityPillar()
    obs = pillar._discover_observability_setup(tmp_path)
    result = pillar._check_request_logging(tmp_path, obs)

    assert not result.passed


def test_check_performance_metrics_found(tmp_path: Path) -> None:
    """Test performance metrics check when found."""
    (tmp_path / "app.py").write_text(
        "import time\n"
        "start = time.time()\n"
        "process()\n"
        "duration = time.time() - start\n"
        "print(f'Duration: {duration:.3f}s')\n"
    )

    pillar = DebuggingObservabilityPillar()
    obs = pillar._discover_observability_setup(tmp_path)
    result = pillar._check_performance_metrics(tmp_path, obs)

    assert result.passed
    assert result.level == 3


def test_check_performance_metrics_not_found(tmp_path: Path) -> None:
    """Test performance metrics check when not found."""
    (tmp_path / "app.py").write_text("def func():\n    return 42\n")

    pillar = DebuggingObservabilityPillar()
    obs = pillar._discover_observability_setup(tmp_path)
    result = pillar._check_performance_metrics(tmp_path, obs)

    assert not result.passed


def test_check_error_context_preserved_found(tmp_path: Path) -> None:
    """Test error context preservation when found."""
    (tmp_path / "app.py").write_text(
        "try:\n"
        "    risky_operation()\n"
        "except ValueError as e:\n"
        "    raise RuntimeError('Operation failed') from e\n"
    )

    pillar = DebuggingObservabilityPillar()
    obs = pillar._discover_observability_setup(tmp_path)
    result = pillar._check_error_context_preserved(tmp_path, obs)

    assert result.passed
    assert result.level == 3


def test_check_error_context_preserved_not_found(tmp_path: Path) -> None:
    """Test error context preservation when not found."""
    (tmp_path / "app.py").write_text(
        "try:\n"
        "    risky_operation()\n"
        "except:\n"
        "    raise\n"
    )

    pillar = DebuggingObservabilityPillar()
    obs = pillar._discover_observability_setup(tmp_path)
    result = pillar._check_error_context_preserved(tmp_path, obs)

    assert not result.passed


def test_check_log_aggregation_config_found(tmp_path: Path) -> None:
    """Test log aggregation config check when found."""
    (tmp_path / "prometheus.yml").touch()

    pillar = DebuggingObservabilityPillar()
    obs = pillar._discover_observability_setup(tmp_path)
    result = pillar._check_log_aggregation_config(tmp_path, obs)

    assert result.passed
    assert result.level == 4


def test_check_log_aggregation_config_not_found(tmp_path: Path) -> None:
    """Test log aggregation config check when not found."""
    pillar = DebuggingObservabilityPillar()
    obs = pillar._discover_observability_setup(tmp_path)
    result = pillar._check_log_aggregation_config(tmp_path, obs)

    assert not result.passed


def test_check_distributed_tracing_found(tmp_path: Path) -> None:
    """Test distributed tracing check when found."""
    (tmp_path / "otel-config.yaml").touch()

    pillar = DebuggingObservabilityPillar()
    obs = pillar._discover_observability_setup(tmp_path)
    result = pillar._check_distributed_tracing(tmp_path, obs)

    assert result.passed
    assert result.level == 4


def test_check_distributed_tracing_pyproject(tmp_path: Path) -> None:
    """Test distributed tracing check with pyproject.toml."""
    (tmp_path / "pyproject.toml").write_text(
        "[project]\n"
        "dependencies = ['opentelemetry-api']\n"
    )

    pillar = DebuggingObservabilityPillar()
    obs = pillar._discover_observability_setup(tmp_path)
    result = pillar._check_distributed_tracing(tmp_path, obs)

    assert result.passed


def test_check_distributed_tracing_not_found(tmp_path: Path) -> None:
    """Test distributed tracing check when not found."""
    pillar = DebuggingObservabilityPillar()
    obs = pillar._discover_observability_setup(tmp_path)
    result = pillar._check_distributed_tracing(tmp_path, obs)

    assert not result.passed


def test_check_custom_metrics_found(tmp_path: Path) -> None:
    """Test custom metrics check when found."""
    (tmp_path / "app.py").write_text(
        "from prometheus_client import Counter\n"
        "request_count = Counter('requests', 'Request counter')\n"
    )

    pillar = DebuggingObservabilityPillar()
    obs = pillar._discover_observability_setup(tmp_path)
    result = pillar._check_custom_metrics(tmp_path, obs)

    assert result.passed
    assert result.level == 4


def test_check_custom_metrics_not_found(tmp_path: Path) -> None:
    """Test custom metrics check when not found."""
    (tmp_path / "app.py").write_text("def main():\n    pass\n")

    pillar = DebuggingObservabilityPillar()
    obs = pillar._discover_observability_setup(tmp_path)
    result = pillar._check_custom_metrics(tmp_path, obs)

    assert not result.passed


def test_check_alert_configuration_found(tmp_path: Path) -> None:
    """Test alert configuration check when found."""
    (tmp_path / "prometheus_rules.yml").touch()

    pillar = DebuggingObservabilityPillar()
    obs = pillar._discover_observability_setup(tmp_path)
    result = pillar._check_alert_configuration(tmp_path, obs)

    assert result.passed
    assert result.level == 4


def test_check_alert_configuration_not_found(tmp_path: Path) -> None:
    """Test alert configuration check when not found."""
    pillar = DebuggingObservabilityPillar()
    obs = pillar._discover_observability_setup(tmp_path)
    result = pillar._check_alert_configuration(tmp_path, obs)

    assert not result.passed


def test_check_profiling_tools_configured_found(tmp_path: Path) -> None:
    """Test profiling tools check when found."""
    (tmp_path / "README.md").write_text(
        "# Project\n\n## Profiling\n\n"
        "Use py-spy for CPU profiling: py-spy record -o profile.svg python app.py"
    )

    pillar = DebuggingObservabilityPillar()
    obs = pillar._discover_observability_setup(tmp_path)
    result = pillar._check_profiling_tools_configured(tmp_path, obs)

    assert result.passed
    assert result.level == 5


def test_check_profiling_tools_configured_not_found(tmp_path: Path) -> None:
    """Test profiling tools check when not found."""
    (tmp_path / "README.md").write_text("# Project")

    pillar = DebuggingObservabilityPillar()
    obs = pillar._discover_observability_setup(tmp_path)
    result = pillar._check_profiling_tools_configured(tmp_path, obs)

    assert not result.passed


def test_check_memory_cpu_monitoring_found(tmp_path: Path) -> None:
    """Test memory/CPU monitoring check when found."""
    (tmp_path / "app.py").write_text(
        "import psutil\n"
        "process = psutil.Process()\n"
        "memory_info = process.memory_info()\n"
    )

    pillar = DebuggingObservabilityPillar()
    obs = pillar._discover_observability_setup(tmp_path)
    result = pillar._check_memory_cpu_monitoring(tmp_path, obs)

    assert result.passed
    assert result.level == 5


def test_check_memory_cpu_monitoring_not_found(tmp_path: Path) -> None:
    """Test memory/CPU monitoring check when not found."""
    (tmp_path / "app.py").write_text("def main():\n    pass\n")

    pillar = DebuggingObservabilityPillar()
    obs = pillar._discover_observability_setup(tmp_path)
    result = pillar._check_memory_cpu_monitoring(tmp_path, obs)

    assert not result.passed


def test_check_log_analysis_found(tmp_path: Path) -> None:
    """Test log analysis check when found."""
    (tmp_path / "README.md").write_text(
        "# Project\n\n## Monitoring\n\nLogs are analyzed with ELK stack"
    )

    pillar = DebuggingObservabilityPillar()
    obs = pillar._discover_observability_setup(tmp_path)
    result = pillar._check_log_analysis(tmp_path, obs)

    assert result.passed
    assert result.level == 5


def test_check_log_analysis_not_found(tmp_path: Path) -> None:
    """Test log analysis check when not found."""
    (tmp_path / "README.md").write_text("# Project")

    pillar = DebuggingObservabilityPillar()
    obs = pillar._discover_observability_setup(tmp_path)
    result = pillar._check_log_analysis(tmp_path, obs)

    assert not result.passed


def test_check_feedback_loops_found(tmp_path: Path) -> None:
    """Test feedback loops check when found."""
    (tmp_path / "README.md").write_text(
        "# Project\n\n## Auto-scaling\n\nThe system uses autoscaling"
    )

    pillar = DebuggingObservabilityPillar()
    obs = pillar._discover_observability_setup(tmp_path)
    result = pillar._check_feedback_loops(tmp_path, obs)

    assert result.passed
    assert result.level == 5


def test_check_feedback_loops_not_found(tmp_path: Path) -> None:
    """Test feedback loops check when not found."""
    (tmp_path / "README.md").write_text("# Project")

    pillar = DebuggingObservabilityPillar()
    obs = pillar._discover_observability_setup(tmp_path)
    result = pillar._check_feedback_loops(tmp_path, obs)

    assert not result.passed


def test_evaluate_full_pillar(tmp_path: Path) -> None:
    """Test full pillar evaluation."""
    # Create project with good observability
    (tmp_path / "logging.conf").touch()
    (tmp_path / "app.py").write_text(
        "import logging\n"
        "try:\n"
        "    x = 1\n"
        "except Exception as e:\n"
        "    raise RuntimeError(f'Error: {e}') from e\n"
    )
    (tmp_path / "README.md").write_text(
        "# Project\n\n## Logging\n\nWe use logging with DEBUG=true"
    )
    (tmp_path / ".env.example").write_text("DEBUG=false\n")

    pillar = DebuggingObservabilityPillar()
    results = pillar.evaluate(tmp_path)

    # Should have multiple checks
    assert len(results) >= 15
    assert any(r.name == "Logging configuration exists" for r in results)
    assert any(r.name == "Error handling present" for r in results)

    # Some checks should pass
    passed = sum(1 for r in results if r.passed)
    assert passed > 0

    # All results should have a level between 1-5
    for result in results:
        assert 1 <= result.level <= 5


def test_debugging_observability_pillar_importable() -> None:
    """Test pillar can be imported from pillars package."""
    from agent_readiness.pillars import DebuggingObservabilityPillar

    pillar = DebuggingObservabilityPillar()
    assert pillar.name == "Debugging & Observability"
