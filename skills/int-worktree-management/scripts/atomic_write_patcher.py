#!/usr/bin/env python3
"""
Patch all registry scripts to use atomic write operations.
Adds atomic_write_registry() function and replaces all direct writes.
"""

import re
from pathlib import Path

SCRIPTS_TO_PATCH = [
    "port_allocate.py",
    "worktree_create.py",
    "worktree_remove.py",
    "registry_validate.py",
]

ATOMIC_WRITE_FUNCTION = '''

# Registry schema version for future migrations
REGISTRY_SCHEMA_VERSION = "1.0"


def atomic_write_registry(registry: dict, registry_path: Path) -> None:
    """Write registry atomically using temp file + rename pattern.

    This prevents corruption if process crashes during write.
    The rename operation is atomic on POSIX systems.

    Args:
        registry: Registry data to write
        registry_path: Path to registry file

    Raises:
        OSError: If write fails
        json.JSONDecodeError: If registry is not JSON-serializable
    """
    # Ensure parent directory exists
    registry_path.parent.mkdir(parents=True, exist_ok=True)

    # Write to temp file in same directory (required for atomic rename)
    with tempfile.NamedTemporaryFile(
        mode='w',
        dir=registry_path.parent,
        suffix='.tmp',
        delete=False
    ) as tmp:
        json.dump(registry, tmp, indent=2, sort_keys=True)
        tmp.flush()
        os.fsync(tmp.fileno())  # Ensure data hits disk
        tmp_path = Path(tmp.name)

    # Atomic rename
    shutil.move(str(tmp_path), str(registry_path))


def ensure_registry_schema(registry: dict) -> dict:
    """Ensure registry has schema version, migrate if needed."""
    if "schema_version" not in registry:
        registry["schema_version"] = REGISTRY_SCHEMA_VERSION
    return registry
'''


def add_imports(content: str) -> str:
    """Add tempfile and shutil imports if missing."""
    lines = content.split("\n")

    # Find import section
    import_end = 0
    has_tempfile = False
    has_shutil = False

    for i, line in enumerate(lines):
        if line.startswith("import ") or line.startswith("from "):
            import_end = i
            if "tempfile" in line:
                has_tempfile = True
            if "shutil" in line:
                has_shutil = True

    # Add missing imports after last import
    new_imports = []
    if not has_tempfile:
        new_imports.append("import tempfile")
    if not has_shutil:
        new_imports.append("import shutil")

    if new_imports:
        lines.insert(import_end + 1, "\n".join(new_imports))

    return "\n".join(lines)


def add_atomic_functions(content: str) -> str:
    """Add atomic write functions after imports."""
    # Find first non-import, non-comment, non-docstring code
    lines = content.split("\n")

    in_docstring = False
    insert_pos = 0

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Track docstrings
        if stripped.startswith('"""') or stripped.startswith("'''"):
            in_docstring = not in_docstring
            continue

        if in_docstring:
            continue

        # Skip imports and comments
        if (
            stripped.startswith("import ")
            or stripped.startswith("from ")
            or stripped.startswith("#")
            or not stripped
        ):
            insert_pos = i + 1
            continue

        # Found first real code
        break

    # Check if atomic functions already exist
    if "def atomic_write_registry" in content:
        return content

    lines.insert(insert_pos, ATOMIC_WRITE_FUNCTION)
    return "\n".join(lines)


def replace_save_registry_calls(content: str) -> str:
    """Replace save_registry() implementations with atomic version."""

    # Pattern 1: port_allocate.py style (with open + json.dump)
    pattern1 = r'''def save_registry\(registry: Dict\) -> None:
    """
    Save the port allocation registry to disk\.

    Args:
        registry: Dictionary containing port allocations
    """
    registry_path = get_registry_path\(\)
    registry\["metadata"\]\["last_modified"\] = datetime\.now\(\)\.isoformat\(\)

    try:
        with open\(registry_path, "w"\) as f:
            json\.dump\(registry, f, indent=2\)
    except IOError as e:
        print\(f"ERROR: Failed to save registry: \{e\}", file=sys\.stderr\)
        sys\.exit\(1\)'''

    replacement1 = '''def save_registry(registry: Dict) -> None:
    """
    Save the port allocation registry to disk using atomic writes.

    Args:
        registry: Dictionary containing port allocations
    """
    registry_path = get_registry_path()
    registry["metadata"]["last_modified"] = datetime.now().isoformat()
    registry = ensure_registry_schema(registry)
    atomic_write_registry(registry, registry_path)'''

    content = re.sub(pattern1, replacement1, content, flags=re.MULTILINE)

    # Pattern 2: worktree_create.py style (Path.write_text)
    pattern2 = r'''def save_registry\(registry: Dict\) -> None:
    """
    Save worktree registry to JSON file\.

    Args:
        registry: Registry dictionary to save

    Raises:
        WorktreeError: If unable to save registry
    """
    try:
        REGISTRY_PATH\.parent\.mkdir\(parents=True, exist_ok=True\)
        registry\["last_updated"\] = datetime\.now\(\)\.isoformat\(\)
        REGISTRY_PATH\.write_text\(json\.dumps\(registry, indent=2\)\)
    except \(OSError, IOError\) as e:
        raise WorktreeError\(f"Failed to save registry to \{REGISTRY_PATH\}: \{e\}"\) from e'''

    replacement2 = '''def save_registry(registry: Dict) -> None:
    """
    Save worktree registry to JSON file using atomic writes.

    Args:
        registry: Registry dictionary to save

    Raises:
        WorktreeError: If unable to save registry
    """
    try:
        registry["last_updated"] = datetime.now().isoformat()
        registry = ensure_registry_schema(registry)
        atomic_write_registry(registry, REGISTRY_PATH)
    except OSError as e:
        raise WorktreeError(f"Failed to save registry to {REGISTRY_PATH}: {e}") from e'''

    content = re.sub(pattern2, replacement2, content, flags=re.MULTILINE)

    # Pattern 3: worktree_remove.py style (_save_registry with backup)
    pattern3 = r'''    def _save_registry\(self\) -> None:
        """Save registry to disk with backup\."""
        # Create backup
        if self\.registry_path\.exists\(\):
            backup_path = self\.registry_path\.with_suffix\("\.json\.backup"\)
            self\.registry_path\.rename\(backup_path\)

        # Write new registry
        with open\(self\.registry_path, "w"\) as f:
            json\.dump\(self\.registry, f, indent=2\)'''

    replacement3 = '''    def _save_registry(self) -> None:
        """Save registry to disk with backup using atomic writes."""
        # Create backup
        if self.registry_path.exists():
            backup_path = self.registry_path.with_suffix(".json.backup")
            shutil.copy2(self.registry_path, backup_path)

        # Write new registry atomically
        self.registry = ensure_registry_schema(self.registry)
        atomic_write_registry(self.registry, self.registry_path)'''

    content = re.sub(pattern3, replacement3, content, flags=re.MULTILINE)

    # Pattern 4: registry_validate.py style (save_registry with backup)
    pattern4 = r'''    def save_registry\(self, registry: Dict\) -> bool:
        """Save registry to disk"""
        if not self\.fix:
            return False

        try:
            # Create backup
            backup_path = self\.registry_path\.with_suffix\('\.json\.backup'\)
            if self\.registry_path\.exists\(\):
                import shutil
                shutil\.copy2\(self\.registry_path, backup_path\)
                self\.log\(f"Created backup: \{backup_path\}", "info"\)

            # Write registry
            with open\(self\.registry_path, 'w'\) as f:
                json\.dump\(registry, f, indent=2\)

            self\.log\("Registry saved successfully", "success"\)
            return True

        except Exception as e:
            self\.add_error\("critical", "filesystem",
                         f"Failed to save registry: \{e\}"\)
            return False'''

    replacement4 = '''    def save_registry(self, registry: Dict) -> bool:
        """Save registry to disk using atomic writes"""
        if not self.fix:
            return False

        try:
            # Create backup
            backup_path = self.registry_path.with_suffix('.json.backup')
            if self.registry_path.exists():
                shutil.copy2(self.registry_path, backup_path)
                self.log(f"Created backup: {backup_path}", "info")

            # Write registry atomically
            registry = ensure_registry_schema(registry)
            atomic_write_registry(registry, self.registry_path)

            self.log("Registry saved successfully", "success")
            return True

        except Exception as e:
            self.add_error("critical", "filesystem",
                         f"Failed to save registry: {e}")
            return False'''

    content = re.sub(pattern4, replacement4, content, flags=re.MULTILINE)

    return content


def patch_file(filepath: Path) -> bool:
    """Patch a single file with atomic write operations."""
    print(f"Patching {filepath.name}...")

    try:
        # Read current content
        content = filepath.read_text()
        original_content = content

        # Apply transformations
        content = add_imports(content)
        content = add_atomic_functions(content)
        content = replace_save_registry_calls(content)

        # Only write if changed
        if content != original_content:
            filepath.write_text(content)
            print(f"  ✓ Patched {filepath.name}")
            return True
        else:
            print(f"  - No changes needed for {filepath.name}")
            return False

    except Exception as e:
        print(f"  ✗ Failed to patch {filepath.name}: {e}")
        return False


def main() -> None:
    """Patch all registry scripts."""
    scripts_dir = Path(__file__).parent

    print("Adding atomic write operations to registry scripts...")
    print()

    patched_count = 0
    for script_name in SCRIPTS_TO_PATCH:
        script_path = scripts_dir / script_name

        if not script_path.exists():
            print(f"⚠ Skipping {script_name} (not found)")
            continue

        if patch_file(script_path):
            patched_count += 1

    print()
    print(f"[DONE] Patched {patched_count}/{len(SCRIPTS_TO_PATCH)} scripts")


if __name__ == "__main__":
    main()
