"""MCP (Model Context Protocol) server for agent-readiness-score.

Exposes scanning functionality as MCP tools for integration with Claude Code,
Cursor, and other AI assistants.
"""

import asyncio
import json
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.types import Tool, TextContent, Resource

from agent_readiness.cli import get_all_pillars, get_pillar_by_name
from agent_readiness.scanner import Scanner

# Create MCP server instance
server = Server("agent-readiness-score")


class Tools:
    """MCP Tools implementation for agent-readiness-score."""

    @staticmethod
    def scan_repository(path: str, pillars: list[str] | None = None) -> str:
        """Scan a repository for agent readiness."""
        if not path:
            return json.dumps({"error": "path is required"})

        try:
            target_path = Path(path).resolve()
            if not target_path.exists() or not target_path.is_dir():
                return json.dumps(
                    {"error": f"{path} is not a valid directory"}
                )

            # Initialize scanner
            scanner = Scanner()

            # Register pillars
            if pillars:
                for pillar_name in pillars:
                    try:
                        pillar = get_pillar_by_name(pillar_name)
                        scanner.register_pillar(pillar)
                    except ValueError:
                        return json.dumps(
                            {"error": f"Unknown pillar '{pillar_name}'"}
                        )
            else:
                scanner.register_pillars(get_all_pillars())

            # Run scan
            result = scanner.scan(target_path)
            return json.dumps(result.to_dict(), indent=2)

        except Exception as e:
            return json.dumps({"error": f"Error scanning repository: {str(e)}"})

    @staticmethod
    def scan_pillar(path: str, pillar: str) -> str:
        """Scan a specific pillar."""
        if not path or not pillar:
            return json.dumps({"error": "path and pillar are required"})

        try:
            target_path = Path(path).resolve()
            if not target_path.exists() or not target_path.is_dir():
                return json.dumps(
                    {"error": f"{path} is not a valid directory"}
                )

            # Get specific pillar
            try:
                selected_pillar = get_pillar_by_name(pillar)
            except ValueError:
                return json.dumps(
                    {"error": f"Unknown pillar '{pillar}'"}
                )

            # Initialize and run scanner
            scanner = Scanner()
            scanner.register_pillar(selected_pillar)
            result = scanner.scan(target_path)

            return json.dumps(result.to_dict(), indent=2)

        except Exception as e:
            return json.dumps({"error": f"Error scanning pillar: {str(e)}"})

    @staticmethod
    def get_recommendations(path: str, max_items: int = 5) -> str:
        """Get recommendations for improving readiness."""
        if not path:
            return json.dumps({"error": "path is required"})

        try:
            target_path = Path(path).resolve()
            if not target_path.exists() or not target_path.is_dir():
                return json.dumps(
                    {"error": f"{path} is not a valid directory"}
                )

            # Scan repository
            scanner = Scanner()
            scanner.register_pillars(get_all_pillars())
            result = scanner.scan(target_path)

            # Generate recommendations
            recommendations = []
            for pillar in result.pillars:
                failed_checks = [c for c in pillar.checks if not c.passed]
                if failed_checks:
                    # Group by severity and level
                    critical = [
                        c for c in failed_checks if c.severity.value == "critical"
                    ]
                    required = [
                        c
                        for c in failed_checks
                        if c.severity.value in ("required", "error")
                    ]
                    level_1 = [c for c in failed_checks if c.level == 1]

                    if critical:
                        recommendations.append(
                            {
                                "pillar": pillar.name,
                                "priority": "CRITICAL",
                                "title": f"Address {len(critical)} critical issues",
                                "checks": [c.name for c in critical[:3]],
                            }
                        )
                    elif required:
                        recommendations.append(
                            {
                                "pillar": pillar.name,
                                "priority": "HIGH",
                                "title": f"Implement {len(required)} required checks",
                                "checks": [c.name for c in required[:3]],
                            }
                        )
                    elif level_1:
                        recommendations.append(
                            {
                                "pillar": pillar.name,
                                "priority": "MEDIUM",
                                "title": f"Complete {len(level_1)} foundational checks",
                                "checks": [c.name for c in level_1[:3]],
                            }
                        )

            # Sort by priority and limit
            priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
            recommendations.sort(
                key=lambda x: priority_order.get(x["priority"], 4)
            )
            recommendations = recommendations[:max_items]

            return json.dumps(
                {
                    "recommendations": recommendations,
                    "total_count": len(recommendations),
                }
            )

        except Exception as e:
            return json.dumps(
                {"error": f"Error getting recommendations: {str(e)}"}
            )

    @staticmethod
    def check_file(path: str, file_path: str, pillar: str) -> str:
        """Check a specific file against criteria."""
        if not all([path, file_path, pillar]):
            return json.dumps(
                {
                    "error": "path, file_path, and pillar are required"
                }
            )

        try:
            repo_path = Path(path).resolve()
            file_full_path = (repo_path / file_path).resolve()

            if not file_full_path.exists():
                return json.dumps(
                    {"error": f"File not found: {file_path}"}
                )

            # Get pillar
            try:
                selected_pillar = get_pillar_by_name(pillar)
            except ValueError:
                return json.dumps(
                    {"error": f"Unknown pillar '{pillar}'"}
                )

            # Read file content
            try:
                content = file_full_path.read_text()
            except Exception as e:
                return json.dumps({"error": f"Error reading file: {str(e)}"})

            # Basic analysis
            analysis = {
                "file_path": str(file_full_path.relative_to(repo_path)),
                "pillar": pillar,
                "file_size": len(content),
                "lines": len(content.splitlines()),
                "patterns_detected": [],
            }

            # Check for common patterns
            if "test" in file_path.lower():
                analysis["patterns_detected"].append("test_file")
            if "security" in content.lower():
                analysis["patterns_detected"].append("security_related")
            if "error" in content.lower() and "handling" in content.lower():
                analysis["patterns_detected"].append("error_handling")
            if "pytest" in content or "unittest" in content:
                analysis["patterns_detected"].append("testing_framework")
            if "import" in content:
                analysis["patterns_detected"].append("has_imports")

            return json.dumps(analysis, indent=2)

        except Exception as e:
            return json.dumps({"error": f"Error checking file: {str(e)}"})


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available MCP tools."""
    return [
        Tool(
            name="scan_repository",
            description="Scan a repository for agent readiness. Returns comprehensive score and pillar results.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the repository to scan",
                    },
                    "pillars": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional list of specific pillars to scan (e.g., ['Security', 'Testing']). If not provided, scans all pillars.",
                    },
                },
                "required": ["path"],
            },
        ),
        Tool(
            name="scan_pillar",
            description="Scan a specific pillar to get detailed results for that area.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the repository to scan",
                    },
                    "pillar": {
                        "type": "string",
                        "description": "Name of the pillar to scan (e.g., 'Security', 'Testing', 'Style & Validation')",
                    },
                },
                "required": ["path", "pillar"],
            },
        ),
        Tool(
            name="get_recommendations",
            description="Get actionable recommendations to improve agent readiness score.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the repository to analyze",
                    },
                    "max_items": {
                        "type": "integer",
                        "description": "Maximum number of recommendations to return (default: 5)",
                        "default": 5,
                    },
                },
                "required": ["path"],
            },
        ),
        Tool(
            name="check_file",
            description="Check a specific file against readiness criteria.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the repository",
                    },
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to check (relative to repository root)",
                    },
                    "pillar": {
                        "type": "string",
                        "description": "Pillar to check against",
                    },
                },
                "required": ["path", "file_path", "pillar"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls from the MCP client."""
    try:
        if name == "scan_repository":
            result = Tools.scan_repository(
                arguments.get("path"),
                arguments.get("pillars"),
            )
        elif name == "scan_pillar":
            result = Tools.scan_pillar(
                arguments.get("path"),
                arguments.get("pillar"),
            )
        elif name == "get_recommendations":
            result = Tools.get_recommendations(
                arguments.get("path"),
                arguments.get("max_items", 5),
            )
        elif name == "check_file":
            result = Tools.check_file(
                arguments.get("path"),
                arguments.get("file_path"),
                arguments.get("pillar"),
            )
        else:
            result = json.dumps({"error": f"Unknown tool: {name}"})

        return [TextContent(type="text", text=result)]

    except Exception as e:
        error_result = json.dumps({"error": str(e)})
        return [TextContent(type="text", text=error_result)]


async def start_mcp_server() -> None:
    """Start the MCP server using stdio transport."""
    async with server:
        # The server runs and processes requests from the client
        # Keep it alive
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            pass


def start_mcp_server_sync() -> None:
    """Start the MCP server synchronously (for CLI integration)."""
    asyncio.run(start_mcp_server())
