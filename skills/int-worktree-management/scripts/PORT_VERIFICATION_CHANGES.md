# Port Verification System-Level Changes

## Summary
Added system-level port availability verification to worktree-management scripts. All scripts now check actual OS port usage in addition to registry allocations, implementing fail-fast behavior on conflicts.

## Changes Made

### 1. worktree_create.py
**Added:**
- `is_port_available(port, host)` - Socket-based system port check
- Updated `allocate_ports()` to verify ports are free on BOTH registry AND system
- Fail-fast error reporting when port conflicts detected

**Behavior:**
- Before allocating a port, checks if it's truly available via socket bind test
- Tracks conflicts (ports free in registry but occupied on system)
- Exits with detailed error message if conflicts found
- Error message suggests running `registry_validate.py --verify-ports`

**Example Error:**
```
WorktreeError: Port conflict detected in feature range 5000-5099.
Ports free in registry but occupied on system: 5001, 5002, 5003.
Run 'registry_validate.py --verify-ports' to detect and clean stale allocations.
```

### 2. registry_validate.py
**Added:**
- `is_port_available(port, host)` - Socket-based system port check
- `verify_system_ports(entries)` - Validates all allocated ports against system
- `--verify-ports` command-line flag - Enables system verification

**Behavior:**
- When `--verify-ports` flag is used, checks all registry-allocated ports
- Detects stale allocations (ports in registry but not actually in use)
- Reports stale ports as warnings with fixable status
- Can be combined with `--fix` to clean stale allocations

**Usage:**
```bash
# Detect conflicts
python registry_validate.py --verify-ports

# Detect and fix
python registry_validate.py --verify-ports --fix

# Verbose output
python registry_validate.py --verify-ports --verbose
```

### 3. port_allocate.py
**Already Had:**
- `is_port_in_use(port)` - System-level port checking (already present)
- `allocate_port()` - Already checked both registry and system
- `detect_conflicts()` - Already detected registry/system mismatches
- `cleanup_stale_allocations()` - Already cleaned stale entries

**No changes needed** - This script was already correctly implemented.

## Implementation Details

### Port Availability Check
```python
def is_port_available(port: int, host: str = '127.0.0.1') -> bool:
    """Check if port is actually available on system using socket bind test."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((host, port))
            return True  # Port is available
    except OSError as e:
        if e.errno in (48, 98):  # EADDRINUSE
            return False  # Port in use
        raise  # Unexpected error
```

### Fail-Fast Philosophy
- **No fallbacks or workarounds** - Port conflicts are fatal errors
- **Immediate exit** - No attempt to work around occupied ports
- **Clear diagnostics** - Error messages guide users to resolution
- **Prevention over cure** - Catch conflicts before worktree creation

## Testing Recommendations

### Test 1: Clean State
```bash
# Should succeed - no conflicts
cd /path/to/repo
python worktree_create.py --purpose feature --identifier test-001 --branch main --ports
```

### Test 2: Port Conflict Detection
```bash
# Occupy port 5000 manually
python -m http.server 5000 &

# Should fail with conflict error
python worktree_create.py --purpose feature --identifier test-002 --branch main --ports
```

### Test 3: Stale Allocation Detection
```bash
# Create worktree with port
python worktree_create.py --purpose feature --identifier test-003 --branch main --ports

# Kill the service using that port (simulate crash)
# ...

# Should detect stale allocation
python registry_validate.py --verify-ports

# Should clean stale allocation
python registry_validate.py --verify-ports --fix
```

### Test 4: Registry Validation
```bash
# Check registry consistency without system verification
python registry_validate.py --verbose

# Check WITH system verification
python registry_validate.py --verify-ports --verbose
```

## Exit Codes

### worktree_create.py
- `0` - Success
- `1` - Worktree creation failed (including port conflicts)
- `130` - User cancelled (SIGINT)

### registry_validate.py
- `0` - Valid (with or without warnings)
- `1` - Fixable errors (use --fix)
- `2` - Critical errors (manual intervention required)

## Integration Notes

1. **Concurrent Safety**: All scripts use registry locking to prevent race conditions
2. **Socket Binding**: Uses SO_REUSEADDR to avoid false positives from TIME_WAIT states
3. **Error Propagation**: Port conflicts always cause immediate exit (no silent failures)
4. **Cross-Platform**: errno checks handle both macOS (48) and Linux (98) for EADDRINUSE

## Future Enhancements

Potential improvements:
- Auto-cleanup of stale allocations before port allocation
- Port reservation system to prevent race conditions
- Health check endpoints for allocated ports
- Automatic retry with different port ranges
- Integration with systemd/launchd for service management
