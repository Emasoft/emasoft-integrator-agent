#!/usr/bin/env python3
"""
Plugin Validator - Validate integrator-agent plugin structure

This script validates:
1. Plugin manifest (plugin.json) structure
2. Agent definitions
3. Command definitions
4. Skill structure
5. Hook configuration
6. Script references
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List


class ValidationResult:
    """Validation result tracker."""

    def __init__(self) -> None:
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.passed: List[str] = []

    def error(self, msg: str) -> None:
        """Add error."""
        self.errors.append(f"❌ ERROR: {msg}")

    def warning(self, msg: str) -> None:
        """Add warning."""
        self.warnings.append(f"⚠️  WARNING: {msg}")

    def success(self, msg: str) -> None:
        """Add success."""
        self.passed.append(f"✓ {msg}")

    def print_results(self, verbose: bool = False) -> int:
        """Print validation results."""
        if verbose and self.passed:
            print("\n=== PASSED CHECKS ===")
            for msg in self.passed:
                print(msg)

        if self.warnings:
            print("\n=== WARNINGS ===")
            for msg in self.warnings:
                print(msg)

        if self.errors:
            print("\n=== ERRORS ===")
            for msg in self.errors:
                print(msg)

        # Summary
        print("\n=== SUMMARY ===")
        print(f"Passed: {len(self.passed)}")
        print(f"Warnings: {len(self.warnings)}")
        print(f"Errors: {len(self.errors)}")

        # Exit code
        if self.errors:
            return 1
        elif self.warnings:
            return 2
        return 0


def validate_plugin(plugin_dir: Path, _verbose: bool = False) -> ValidationResult:
    """Validate plugin structure."""
    del _verbose  # Parameter kept for API compatibility
    result = ValidationResult()

    # Check plugin directory exists
    if not plugin_dir.exists():
        result.error(f"Plugin directory not found: {plugin_dir}")
        return result

    result.success(f"Plugin directory exists: {plugin_dir}")

    # Check plugin.json
    plugin_json = plugin_dir / ".claude-plugin" / "plugin.json"
    if not plugin_json.exists():
        result.error("plugin.json not found in .claude-plugin/")
        return result

    result.success("plugin.json exists")

    # Parse plugin.json
    try:
        with open(plugin_json, encoding="utf-8") as f:
            manifest = json.load(f)
        result.success("plugin.json is valid JSON")
    except json.JSONDecodeError as e:
        result.error(f"plugin.json is invalid JSON: {e}")
        return result

    # Validate required fields
    required_fields = ["name", "version", "description"]
    for field in required_fields:
        if field not in manifest:
            result.error(f"plugin.json missing required field: {field}")
        else:
            result.success(f"plugin.json has {field}: {manifest[field]}")

    # Validate manifest schema — Claude Code rejects unknown keys
    known_manifest_fields = {
        "name", "version", "description", "author", "homepage",
        "repository", "license", "keywords", "commands", "agents",
        "skills", "hooks", "mcpServers", "outputStyles", "lspServers",
    }
    for key in manifest.keys():
        if key not in known_manifest_fields:
            result.error(
                f"Unrecognized manifest field '{key}' — Claude Code rejects "
                f"unknown keys and plugin installation will fail"
            )

    # Validate repository field type — must be string URL, not object
    if "repository" in manifest and not isinstance(manifest["repository"], str):
        result.error(
            "Field 'repository' must be a string URL, not an object. "
            "Use \"https://github.com/user/repo\" format."
        )

    # Validate agents listed in manifest exist
    if "agents" in manifest:
        for agent_path in manifest["agents"]:
            full_agent_path = plugin_dir / agent_path.lstrip("./")
            if not full_agent_path.exists():
                result.error(f"Agent file not found: {agent_path}")
            else:
                result.success(f"Agent file exists: {agent_path}")

    # Check directories
    dirs_to_check = ["agents", "commands", "skills", "scripts", "hooks"]
    for dir_name in dirs_to_check:
        dir_path = plugin_dir / dir_name
        if dir_path.exists():
            result.success(f"{dir_name}/ directory exists")
        else:
            result.warning(f"{dir_name}/ directory not found")

    # Check skills have SKILL.md files
    skills_dir = plugin_dir / "skills"
    if skills_dir.exists():
        for skill_dir in skills_dir.iterdir():
            if skill_dir.is_dir():
                skill_md = skill_dir / "SKILL.md"
                if not skill_md.exists():
                    result.error(f"SKILL.md not found in {skill_dir.name}/")
                else:
                    result.success(f"SKILL.md exists in {skill_dir.name}/")

    # Check hooks.json
    hooks_json = plugin_dir / "hooks" / "hooks.json"
    if hooks_json.exists():
        try:
            with open(hooks_json, encoding="utf-8") as f:
                hooks_data = json.load(f)
            result.success("hooks.json is valid JSON")

            # Check referenced scripts exist
            if "hooks" in hooks_data:
                for _, hook_configs in hooks_data["hooks"].items():
                    for hook_config in hook_configs:
                        if "hooks" in hook_config:
                            for hook in hook_config["hooks"]:
                                if hook.get("type") == "command":
                                    cmd = hook.get("command", "")
                                    # Extract script path from command
                                    if "${CLAUDE_PLUGIN_ROOT}" in cmd:
                                        # Replace variable and parse command
                                        cmd_expanded = cmd.replace("${CLAUDE_PLUGIN_ROOT}", str(plugin_dir))
                                        parts = cmd_expanded.split()
                                        # Skip interpreter (python3, bash, etc.)
                                        script_part = parts[1] if len(parts) > 1 and parts[0] in ("python3", "python", "bash", "sh") else parts[0]
                                        full_script_path = Path(script_part)
                                        if full_script_path.exists():
                                            result.success(f"Hook script exists: {full_script_path.name}")
                                        else:
                                            result.error(f"Hook script not found: {script_part}")
        except json.JSONDecodeError as e:
            result.error(f"hooks.json is invalid JSON: {e}")
    else:
        result.warning("hooks.json not found")

    # Check scripts exist
    scripts_dir = plugin_dir / "scripts"
    if scripts_dir.exists():
        scripts = list(scripts_dir.glob("*.py"))
        result.success(f"Found {len(scripts)} Python scripts")

        # Check scripts are executable
        for script in scripts:
            content = script.read_text(encoding="utf-8")
            if not content.startswith("#!/usr/bin/env python3"):
                result.warning(f"Script missing shebang: {script.name}")

    return result


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate integrator-agent plugin structure"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show all passed checks",
    )
    parser.add_argument(
        "--plugin-dir",
        type=Path,
        help="Path to plugin directory (default: current directory's parent)",
    )

    args = parser.parse_args()

    # Determine plugin directory
    if args.plugin_dir:
        plugin_dir = args.plugin_dir
    else:
        # Assume we're running from scripts/ directory
        plugin_dir = Path(__file__).parent.parent

    print(f"Validating plugin: {plugin_dir}")
    print("=" * 60)

    result = validate_plugin(plugin_dir, args.verbose)
    exit_code = result.print_results(args.verbose)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
