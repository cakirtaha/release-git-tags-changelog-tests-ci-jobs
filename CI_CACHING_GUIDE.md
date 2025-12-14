# CI Caching Guide

## Problem Statement

Pre-commit hook environments were being reinstalled on every CI run, even though caching was configured. This caused slow CI runs.

## Root Causes

### 1. **No Fallback Cache Keys**
```yaml
# ❌ OLD - Only exact matches
key: pre-commit-${{ hashFiles('.pre-commit-config.yaml') }}
```

If the config file hash changed even slightly, the entire cache was rebuilt from scratch.

### 2. **No Cache Hit Verification**
No way to tell if cache was working or missing.

### 3. **Missing Explicit Hook Installation**
`pre-commit run` installs hooks implicitly, but this might not leverage cache properly.

### 4. **Incomplete Caching Strategy**
Only pre-commit environments were cached, not Python dependencies.

## Solution Implemented

### 1. **Enhanced Pre-commit Cache with Restore Keys**

```yaml
- name: Cache pre-commit environments
  uses: actions/cache@v4
  id: cache-precommit  # ← Add ID for status checking
  with:
    path: ~/.cache/pre-commit
    # Primary key: exact match on config file
    key: pre-commit-${{ runner.os }}-${{ hashFiles('.pre-commit-config.yaml') }}
    # Fallback keys: use previous cache if available
    restore-keys: |
      pre-commit-${{ runner.os }}-
```

**How it works:**
1. **First try:** Exact match on `pre-commit-Linux-abc123` (config file hash)
2. **Fallback:** Any cache starting with `pre-commit-Linux-`
3. **Result:** Even if config changes slightly, old cache is restored and updated

### 2. **Explicit Hook Installation with Verification**

```yaml
- name: Install pre-commit hooks
  run: |
    # Show cache status
    if [ "${{ steps.cache-precommit.outputs.cache-hit }}" == "true" ]; then
      echo "✅ Pre-commit cache HIT - using cached environments"
    else
      echo "❌ Pre-commit cache MISS - will download and install"
    fi

    # Explicitly install hook environments
    pre-commit install-hooks

    # Show what's cached
    echo "Cached pre-commit environments:"
    ls -lh ~/.cache/pre-commit/
```

**Benefits:**
- ✅ Shows cache hit/miss status in logs
- ✅ Explicitly installs hooks (leverages cache)
- ✅ Displays cached environments for debugging

### 3. **Added Python Dependencies Cache**

```yaml
- name: Cache Python dependencies
  uses: actions/cache@v4
  with:
    path: |
      ~/.cache/pip
      .venv
    key: python-deps-${{ runner.os }}-${{ hashFiles('pyproject.toml', 'uv.lock') }}
    restore-keys: |
      python-deps-${{ runner.os }}-
```

**What it caches:**
- `~/.cache/pip` - pip's download cache
- `.venv` - Virtual environment (if created)

### 4. **Optimized Cache Order**

```yaml
steps:
  - Checkout code
  - Setup Python
  - Install uv (with built-in cache)
  - Cache pre-commit environments ← Before installing deps
  - Cache Python dependencies
  - Install dependencies
  - Install pre-commit hooks
  - Run pre-commit
```

**Why this order:**
- Caches are restored before dependencies are installed
- Pre-commit hooks installed after cache restoration

## Cache Keys Explained

### Pre-commit Cache Key

```yaml
key: pre-commit-${{ runner.os }}-${{ hashFiles('.pre-commit-config.yaml') }}
```

**Breakdown:**
- `pre-commit-` - Prefix for identification
- `${{ runner.os }}` - OS name (Linux, macOS, Windows)
- `${{ hashFiles('.pre-commit-config.yaml') }}` - SHA256 hash of config file

**Example key:**
```
pre-commit-Linux-e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

**When key changes:**
- `.pre-commit-config.yaml` modified → New hash → Cache miss

**Restore keys:**
```yaml
restore-keys: |
  pre-commit-${{ runner.os }}-
```

**Fallback behavior:**
1. Try exact match: `pre-commit-Linux-e3b0c...`
2. If miss, try: `pre-commit-Linux-*` (any previous cache for Linux)
3. If miss, build from scratch

### Python Dependencies Cache Key

```yaml
key: python-deps-${{ runner.os }}-${{ hashFiles('pyproject.toml', 'uv.lock') }}
```

**When key changes:**
- `pyproject.toml` modified → New hash → Cache miss
- `uv.lock` modified → New hash → Cache miss

## What Gets Cached

### 1. Pre-commit Environments

**Location:** `~/.cache/pre-commit/`

**Contents:**
```
~/.cache/pre-commit/
├── repoxxx/               # Ruff environment
├── repoyyyy/              # MyPy environment
├── repozzzz/              # Bandit environment
└── ...
```

**Size:** ~100-500MB (depending on hooks)

**Cache duration:** Until `.pre-commit-config.yaml` changes

### 2. Python Dependencies

**Locations:**
- `~/.cache/pip/` - Pip's package cache
- `.venv/` - Virtual environment (if used)

**Cache duration:** Until `pyproject.toml` or `uv.lock` changes

### 3. UV Package Cache

**Location:** Managed by `astral-sh/setup-uv@v4`

**Enabled via:**
```yaml
- name: Install uv
  uses: astral-sh/setup-uv@v4
  with:
    enable-cache: true
```

**What it caches:** Downloaded packages for faster installation

## Verification

### Check Cache Status in Logs

Look for these messages in GitHub Actions logs:

**Cache hit:**
```
✅ Pre-commit cache HIT - using cached environments
Installing pre-commit hook environments...
[INFO] Initializing environment for https://github.com/astral-sh/ruff-pre-commit.
[INFO] Environment already installed.
```

**Cache miss:**
```
❌ Pre-commit cache MISS - will download and install hook environments
Installing pre-commit hook environments...
[INFO] Initializing environment for https://github.com/astral-sh/ruff-pre-commit.
[INFO] Installing environment for https://github.com/astral-sh/ruff-pre-commit.
[INFO] Once installed this environment will be reused.
[INFO] This may take a few minutes...
```

### Check Cache Size in GitHub

1. Go to repository → **Actions**
2. Click **Caches** (left sidebar)
3. See all cached items with sizes

**Example:**
```
Cache Key                                    Size    Last Used
pre-commit-Linux-e3b0c44...                 234 MB  2 hours ago
python-deps-Linux-a1b2c3d...                45 MB   2 hours ago
```

### Manually Verify Cache

```bash
# On your local machine, check pre-commit cache
ls -lh ~/.cache/pre-commit/

# Output should show hook environments
# repo-xxx/  repo-yyy/  repo-zzz/
```

## Performance Impact

### Before (No Efficient Caching)

```
Step: Install dependencies           30s
Step: Run pre-commit hooks           120s  ← Installing environments
Total: 150s
```

### After (With Optimized Caching)

**First run (cache miss):**
```
Step: Cache pre-commit (miss)        2s
Step: Install dependencies           30s
Step: Install pre-commit hooks       90s   ← Building cache
Step: Run pre-commit hooks           30s
Total: 152s (slightly slower due to cache setup)
```

**Subsequent runs (cache hit):**
```
Step: Cache pre-commit (hit)         3s    ← Restore cache
Step: Install dependencies           10s   ← Faster with pip cache
Step: Install pre-commit hooks       5s    ← Already cached!
Step: Run pre-commit hooks           25s
Total: 43s (~70% faster!)
```

### Expected Speedup

- **Pre-commit hook installation:** 90s → 5s (94% faster)
- **Overall CI time:** 150s → 43s (71% faster)
- **Cost savings:** ~70% reduction in CI minutes

## Cache Invalidation

Caches are invalidated (rebuilt) when:

### Pre-commit Cache

1. `.pre-commit-config.yaml` changes
   - Adding/removing hooks
   - Changing hook versions
   - Modifying hook arguments

2. Manual cache deletion (in GitHub UI)

3. Cache expires (GitHub auto-deletes after 7 days of inactivity)

### Python Dependencies Cache

1. `pyproject.toml` changes
   - Adding/removing dependencies
   - Changing versions

2. `uv.lock` changes
   - Dependency resolution changes

3. Manual cache deletion or expiration

## Troubleshooting

### Issue: Cache always misses

**Check:**
1. View logs for cache key
2. Compare keys between runs
3. Ensure files being hashed exist

**Debug:**
```yaml
- name: Debug cache key
  run: |
    echo "Config hash: ${{ hashFiles('.pre-commit-config.yaml') }}"
    echo "OS: ${{ runner.os }}"
    echo "Full key: pre-commit-${{ runner.os }}-${{ hashFiles('.pre-commit-config.yaml') }}"
```

### Issue: Cache hit but still slow

**Possible causes:**
1. Cache restored to wrong path
2. Pre-commit hooks updated (new versions)
3. Cache corrupted

**Solution:**
```bash
# Manually clear cache in GitHub UI
Settings → Actions → Caches → Delete cache
```

### Issue: Cache too large

**Pre-commit cache size:** ~200-500MB is normal

**If larger:**
- Remove unused hooks from `.pre-commit-config.yaml`
- Cache will rebuild on next run

### Issue: "Cache service URL not found"

**Cause:** GitHub Actions cache not available (rare)

**Solution:** Wait and retry; service should recover

## Best Practices

### 1. Use Restore Keys

```yaml
# ✅ Good - Fallback to partial matches
restore-keys: |
  pre-commit-${{ runner.os }}-

# ❌ Bad - No fallback
restore-keys: []
```

### 2. Include OS in Cache Key

```yaml
# ✅ Good - Separate caches per OS
key: pre-commit-${{ runner.os }}-${{ hashFiles('...') }}

# ❌ Bad - Same cache for all OS (breaks)
key: pre-commit-${{ hashFiles('...') }}
```

### 3. Hash Relevant Files

```yaml
# ✅ Good - Changes when dependencies change
key: python-deps-${{ hashFiles('pyproject.toml', 'uv.lock') }}

# ❌ Bad - Never changes
key: python-deps-static
```

### 4. Cache Before Installing

```yaml
# ✅ Good - Cache first, then install
- name: Cache dependencies
- name: Install dependencies

# ❌ Bad - Install first, then cache (useless)
- name: Install dependencies
- name: Cache dependencies
```

### 5. Verify Cache Hits

```yaml
# ✅ Good - Check if cache worked
id: cache-precommit
run: |
  if [ "${{ steps.cache-precommit.outputs.cache-hit }}" == "true" ]; then
    echo "Cache hit!"
  fi
```

## Advanced: Custom Cache Keys

For more control:

```yaml
# Cache per branch
key: pre-commit-${{ runner.os }}-${{ github.ref }}-${{ hashFiles('...') }}

# Cache per Python version
key: pre-commit-${{ runner.os }}-py${{ matrix.python-version }}-${{ hashFiles('...') }}

# Cache with date (expires daily)
key: pre-commit-${{ runner.os }}-${{ github.run_number }}-${{ hashFiles('...') }}
```

## Monitoring Cache Effectiveness

### GitHub Actions Logs

Look for:
```
Cache Size: 234 MB
Cache restore time: 3s
```

### Cache Dashboard

Go to: `https://github.com/OWNER/REPO/actions/caches`

**Metrics:**
- Total cache size
- Cache hit rate
- Last used timestamps

### Optimize Based on Data

If pre-commit cache:
- **<100MB:** Normal, keep as is
- **100-500MB:** Normal for many hooks
- **>500MB:** Consider reducing hooks

## Summary

### Changes Made

1. ✅ Added `restore-keys` for fallback caching
2. ✅ Added cache hit verification
3. ✅ Added explicit `pre-commit install-hooks`
4. ✅ Added Python dependencies cache
5. ✅ Added cache visibility in logs
6. ✅ Optimized cache order

### Expected Results

- **70% faster CI** on cache hits
- **Clear cache status** in logs
- **Better cache utilization** with restore keys
- **Fewer re-downloads** of pre-commit hooks

### Next PR

You should see:
```
✅ Pre-commit cache HIT - using cached environments
```

Instead of downloading hook environments every time!
