#!/usr/bin/env python3
"""
Port Allocation Manager for Worktree Services

Manages port allocation across worktrees to prevent conflicts.
Supports allocation by service type, release, availability checks, and listing.

Port Ranges:
- web: 8080-8099 (20 ports)
- database: 5432-5439 (8 ports)
- testing: 9000-9099 (100 ports)
- debug: 5555-5564 (10 ports)

Registry Location:
- Default: ~/.atlas-orchestrator/port-registry.json
- Environment variable: ATLAS_PORT_REGISTRY

Usage Examples:
    # Allocate port for web service in worktree wt-001
    python port_allocate.py --allocate --service web --worktree wt-001

    # Check if port 8080 is available
    python port_allocate.py --check 8080

    # Release port 8080
    python port_allocate.py --release 8080

    # List all available web ports
    python port_allocate.py --available --service web

    # Show current allocations
    python port_allocate.py --list
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Add shared module to path
SKILLS_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(SKILLS_DIR / "shared"))
from cross_platform import (  # type: ignore[import-not-found]  # noqa: E402
    atomic_write_json,
    file_lock,
    get_atlas_dir,
    is_port_available,
)
from thresholds import WorktreeThresholds  # type: ignore[import-not-found]  # noqa: E402

# Get thresholds instance
THRESHOLDS = WorktreeThresholds()

# Port range definitions by service type (from shared thresholds)
PORT_RANGES = THRESHOLDS.PORT_RANGES


def get_registry_path() -> Path:
    """
    Get the path to the port registry file.

    Returns:
        Path object pointing to the registry file
    """
    # Check for environment variable override
    env_path = os.environ.get("ATLAS_PORT_REGISTRY")
    if env_path:
        return Path(env_path)

    # Default location - cast result from get_atlas_dir which returns Any
    atlas_dir: Path = Path(get_atlas_dir())
    return atlas_dir / "port-registry.json"


def load_registry() -> dict[str, Any]:
    """
    Load the port allocation registry from disk.

    Returns:
        Dictionary containing port allocations
    """
    registry_path = get_registry_path()

    with file_lock(registry_path):
        if not registry_path.exists():
            return {
                "allocations": {},
                "metadata": {"created": datetime.now().isoformat(), "version": "1.0"},
            }

        try:
            with open(registry_path, "r") as f:
                result: dict[str, Any] = json.load(f)
                return result
        except (json.JSONDecodeError, IOError) as e:
            print(f"ERROR: Failed to load registry: {e}", file=sys.stderr)
            sys.exit(1)


def save_registry(registry: dict[str, Any]) -> None:
    """
    Save the port allocation registry to disk using atomic writes.

    Args:
        registry: Dictionary containing port allocations
    """
    registry_path = get_registry_path()

    with file_lock(registry_path):
        registry["metadata"]["last_modified"] = datetime.now().isoformat()
        atomic_write_json(registry, registry_path)


def is_port_in_use(port: int) -> bool:
    """
    Check if a port is currently in use by attempting to bind to it.

    Args:
        port: Port number to check

    Returns:
        True if port is in use, False if available
    """
    return not is_port_available(port)


def get_service_range(service: str) -> tuple[int, int]:
    """
    Get the port range for a service type.

    Args:
        service: Service type (web, database, testing, debug)

    Returns:
        Tuple of (start_port, end_port)

    Raises:
        ValueError: If service type is invalid
    """
    if service not in PORT_RANGES:
        valid = ", ".join(PORT_RANGES.keys())
        raise ValueError(f"Invalid service type '{service}'. Valid types: {valid}")

    result: tuple[int, int] = PORT_RANGES[service]
    return result


def allocate_port(service: str, worktree_id: str) -> int | None:
    """
    Allocate an available port for a service in a worktree.

    Args:
        service: Service type (web, database, testing, debug)
        worktree_id: Worktree identifier

    Returns:
        Allocated port number, or None if no ports available
    """
    registry = load_registry()
    allocations = registry["allocations"]

    start_port, end_port = get_service_range(service)

    # Find first available port in range
    for port in range(start_port, end_port + 1):
        port_str = str(port)

        # Check if port is already allocated in registry
        if port_str in allocations:
            continue

        # Check if port is actually in use on the system
        if is_port_in_use(port):
            continue

        # Allocate the port
        allocations[port_str] = {
            "service": service,
            "worktree": worktree_id,
            "allocated_at": datetime.now().isoformat(),
        }

        save_registry(registry)
        return port

    return None


def release_port(port: int) -> bool:
    """
    Release a previously allocated port.

    Args:
        port: Port number to release

    Returns:
        True if port was released, False if not allocated
    """
    registry = load_registry()
    allocations = registry["allocations"]
    port_str = str(port)

    if port_str not in allocations:
        return False

    del allocations[port_str]
    save_registry(registry)
    return True


def check_port(port: int) -> dict[str, Any]:
    """
    Check the status and availability of a port.

    Args:
        port: Port number to check

    Returns:
        Dictionary with port status information
    """
    registry = load_registry()
    allocations = registry["allocations"]
    port_str = str(port)

    # Check if port is in a valid range
    in_valid_range = False
    service_type: str | None = None
    for svc, (start, end) in PORT_RANGES.items():
        if start <= port <= end:
            in_valid_range = True
            service_type = svc
            break

    # Check registry allocation
    is_allocated = port_str in allocations
    allocation_info = allocations.get(port_str, {})

    # Check actual system usage
    in_use = is_port_in_use(port)

    return {
        "port": port,
        "in_valid_range": in_valid_range,
        "service_type": service_type,
        "is_allocated": is_allocated,
        "allocation_info": allocation_info,
        "in_use": in_use,
        "available": not is_allocated and not in_use and in_valid_range,
    }


def list_available_ports(service: str) -> list[int]:
    """
    List all available ports for a service type.

    Args:
        service: Service type (web, database, testing, debug)

    Returns:
        List of available port numbers
    """
    registry = load_registry()
    allocations = registry["allocations"]

    start_port, end_port = get_service_range(service)
    available: list[int] = []

    for port in range(start_port, end_port + 1):
        port_str = str(port)

        # Skip if allocated in registry
        if port_str in allocations:
            continue

        # Skip if in use on system
        if is_port_in_use(port):
            continue

        available.append(port)

    return available


def list_all_allocations() -> dict[str, Any]:
    """
    List all current port allocations.

    Returns:
        Dictionary of all allocations
    """
    registry = load_registry()
    result: dict[str, Any] = registry["allocations"]
    return result


def detect_conflicts() -> list[dict[str, Any]]:
    """
    Detect conflicts between registry and actual port usage.

    Returns:
        List of conflict reports
    """
    registry = load_registry()
    allocations = registry["allocations"]
    conflicts: list[dict[str, Any]] = []

    # Check for ports in use but not in registry
    for service, (start_port, end_port) in PORT_RANGES.items():
        for port in range(start_port, end_port + 1):
            port_str = str(port)
            in_use = is_port_in_use(port)
            is_allocated = port_str in allocations

            if in_use and not is_allocated:
                conflicts.append(
                    {
                        "type": "unregistered_usage",
                        "port": port,
                        "service": service,
                        "message": f"Port {port} is in use but not registered",
                    }
                )
            elif is_allocated and not in_use:
                conflicts.append(
                    {
                        "type": "stale_allocation",
                        "port": port,
                        "service": service,
                        "allocation": allocations[port_str],
                        "message": f"Port {port} is registered but not in use (stale)",
                    }
                )

    return conflicts


def cleanup_stale_allocations() -> int:
    """
    Remove stale allocations (registered but not in use).

    Returns:
        Number of stale allocations removed
    """
    registry = load_registry()
    allocations = registry["allocations"]
    removed = 0

    ports_to_remove = []
    for port_str, allocation in allocations.items():
        port = int(port_str)
        if not is_port_in_use(port):
            ports_to_remove.append(port_str)

    for port_str in ports_to_remove:
        del allocations[port_str]
        removed += 1

    if removed > 0:
        save_registry(registry)

    return removed


def main() -> None:
    """Main entry point for the port allocation manager."""
    parser = argparse.ArgumentParser(
        description="Port Allocation Manager for Worktree Services",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    # Main operations (mutually exclusive)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--allocate",
        action="store_true",
        help="Allocate port for service (requires --service and --worktree)",
    )
    group.add_argument(
        "--release", type=int, metavar="PORT", help="Release allocated port"
    )
    group.add_argument(
        "--check", type=int, metavar="PORT", help="Check port availability and status"
    )
    group.add_argument(
        "--available",
        action="store_true",
        help="List available ports (requires --service)",
    )
    group.add_argument(
        "--list", action="store_true", help="List all current allocations"
    )
    group.add_argument(
        "--conflicts",
        action="store_true",
        help="Detect conflicts between registry and actual usage",
    )
    group.add_argument(
        "--cleanup",
        action="store_true",
        help="Remove stale allocations (registered but not in use)",
    )

    # Additional arguments
    parser.add_argument(
        "--service",
        choices=list(PORT_RANGES.keys()),
        help="Service type (required for --allocate and --available)",
    )
    parser.add_argument(
        "--worktree", metavar="ID", help="Worktree identifier (required for --allocate)"
    )
    parser.add_argument(
        "--json", action="store_true", help="Output results in JSON format"
    )

    args = parser.parse_args()

    try:
        # Handle each operation
        if args.allocate:
            if not args.service:
                parser.error("--allocate requires --service")
            if not args.worktree:
                parser.error("--allocate requires --worktree")

            port = allocate_port(args.service, args.worktree)
            if port:
                if args.json:
                    print(
                        json.dumps(
                            {
                                "port": port,
                                "service": args.service,
                                "worktree": args.worktree,
                            }
                        )
                    )
                else:
                    print(
                        f"Allocated port {port} for {args.service} service in worktree {args.worktree}"
                    )
            else:
                print(
                    f"ERROR: No available ports for {args.service} service",
                    file=sys.stderr,
                )
                sys.exit(1)

        elif args.release:
            if release_port(args.release):
                if args.json:
                    print(json.dumps({"released": args.release}))
                else:
                    print(f"Released port {args.release}")
            else:
                print(f"ERROR: Port {args.release} was not allocated", file=sys.stderr)
                sys.exit(1)

        elif args.check:
            status = check_port(args.check)
            if args.json:
                print(json.dumps(status, indent=2))
            else:
                print(f"Port {args.check} status:")
                print(f"  In valid range: {status['in_valid_range']}")
                if status["service_type"]:
                    print(f"  Service type: {status['service_type']}")
                print(f"  Is allocated: {status['is_allocated']}")
                if status["allocation_info"]:
                    print(f"  Allocated to: {status['allocation_info']['worktree']}")
                    print(f"  Service: {status['allocation_info']['service']}")
                print(f"  In use: {status['in_use']}")
                print(f"  Available: {status['available']}")

        elif args.available:
            if not args.service:
                parser.error("--available requires --service")

            ports = list_available_ports(args.service)
            if args.json:
                print(
                    json.dumps(
                        {
                            "service": args.service,
                            "available_ports": ports,
                            "count": len(ports),
                        }
                    )
                )
            else:
                print(f"Available {args.service} ports ({len(ports)}):")
                if ports:
                    for port in ports:
                        print(f"  {port}")
                else:
                    print("  None")

        elif args.list:
            allocations = list_all_allocations()
            if args.json:
                print(json.dumps(allocations, indent=2))
            else:
                if not allocations:
                    print("No ports currently allocated")
                else:
                    print(f"Current port allocations ({len(allocations)}):")
                    for port_key, info in sorted(
                        allocations.items(), key=lambda x: int(x[0])
                    ):
                        print(
                            f"  Port {port_key}: {info['service']} service in worktree {info['worktree']}"
                        )
                        print(f"    Allocated: {info['allocated_at']}")

        elif args.conflicts:
            conflicts = detect_conflicts()
            if args.json:
                print(
                    json.dumps(
                        {"conflicts": conflicts, "count": len(conflicts)}, indent=2
                    )
                )
            else:
                if not conflicts:
                    print("No conflicts detected")
                else:
                    print(f"Detected {len(conflicts)} conflict(s):")
                    for conflict in conflicts:
                        print(f"  {conflict['message']}")
                        if conflict["type"] == "stale_allocation":
                            print(f"    Worktree: {conflict['allocation']['worktree']}")

        elif args.cleanup:
            removed = cleanup_stale_allocations()
            if args.json:
                print(json.dumps({"removed": removed}))
            else:
                print(f"Removed {removed} stale allocation(s)")

    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
