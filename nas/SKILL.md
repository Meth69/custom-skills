---
name: nas
description: Use when the user mentions NAS, TrueNAS, truenas, home server, Jellyfin,
  Navidrome, Sonarr, Radarr, Prowlarr, Bazarr, Jellyseerr, media library, storage
  pools, nvmepool, spinningpool, docker apps on NAS, midclt, app permissions, or asks
  to SSH into `nas`. Also triggers on /nas.
argument-hint: [task description]
allowed-tools: Bash
---

# NAS — TrueNAS Scale Interface

This skill loads full context about the home TrueNAS server and provides structured
workflows for common operations. All reference data (storage paths, ports, services,
API patterns) is in [knowledge.md](knowledge.md).

## When invoked

1. **Read [knowledge.md](knowledge.md)** to load the full NAS reference into context.

2. **Parse intent** from `$ARGUMENTS` or the conversation. Determine which sub-workflow applies:
   - Query / status → [App Query](#app-query)
   - Start / stop / redeploy → [App Management](#app-management)
   - Install new app → [App Installation](#app-installation)
   - Media permissions → [Fix Permissions](#fix-permissions)
   - Storage / find files → [Storage Operations](#storage-operations)
   - Async job → [Job Polling](#job-polling)
   - Unknown → read the API definition first (see knowledge.md §2)

3. **Execute** via `ssh nas "..."`. Show the raw output and summarise.

4. **If the method is unfamiliar**, read its API definition before calling:
   ```bash
   ssh nas "cat /usr/lib/python3/dist-packages/middlewared/api/v25_10_2/<method>.py"
   ```

---

## App Query

```bash
# All apps with state
ssh nas "midclt call app.query | jq -r '.[] | \"\(.name): \(.state)\"'"

# Running apps only
ssh nas "midclt call app.query | jq -r '.[] | select(.state==\"RUNNING\") | .name'"

# Detailed info (containers, ports, volumes, image)
ssh nas "midclt call app.get_instance <name> | jq ."

# Container IDs
ssh nas "midclt call app.container_ids <name>"

# All used ports
ssh nas "midclt call app.used_ports | jq ."

# System info
ssh nas "midclt call system.info | jq ."
```

---

## App Management

```bash
# Start / stop / redeploy (returns job ID — see Job Polling)
ssh nas "midclt call app.start <name>"
ssh nas "midclt call app.stop <name>"
ssh nas "midclt call app.redeploy <name>"

# Upgrade
ssh nas "midclt call app.upgrade_summary <name> '{}'"   # check available
ssh nas "midclt call -j app.upgrade <name>"

# Delete
ssh nas "midclt call app.delete <name>"
```

**App won't start checklist:**
1. Check state: `midclt call app.get_instance <name> | jq '.state'`
2. Check port conflicts: `midclt call app.used_ports`
3. Inspect logs (requires sudo): `sudo docker logs <container_id>`

---

## App Installation

### Catalog app
```bash
# Find which train an app is in
ssh nas "midclt call catalog.apps '{}' | jq '.community | keys[] | select(test(\"<name>\"))'"

# Install
ssh nas "midclt call -j app.create '{
  \"catalog_app\": \"<catalog_name>\",
  \"app_name\": \"<instance_name>\",
  \"train\": \"community\",
  \"version\": \"latest\",
  \"values\": {}
}'"
```

**GOTCHA**: `train` defaults to `stable`. Community apps MUST set `"train": "community"`.

### Custom docker-compose app
```bash
# Create
ssh nas "midclt call -j app.create '{
  \"custom_app\": true,
  \"app_name\": \"<name>\",
  \"custom_compose_config_string\": \"<yaml-with-\\n>\"
}'"

# Update compose
ssh nas "midclt call -j app.update \"<name>\" '{\"custom_compose_config_string\": \"<yaml>\"}'"
```

---

## Fix Permissions

**User/Group IDs**: `lysergic=3000`, `apps=568`

Use `filesystem.chown` + `filesystem.setperm` (NOT raw `chown/chmod`):

```bash
# Bulk — all subfolders of tvshows
ssh nas "for dir in /mnt/nvmepool/nvmeshare/medialibrary/tvshows/*/; do
  midclt call filesystem.chown \"{\\\"path\\\": \\\"\$dir\\\", \\\"uid\\\": 3000, \\\"gid\\\": 568}\" --job
  midclt call filesystem.setperm \"{\\\"path\\\": \\\"\$dir\\\", \\\"mode\\\": \\\"775\\\"}\" --job
done"

# Bulk — all subfolders of movies
ssh nas "for dir in /mnt/nvmepool/nvmeshare/medialibrary/movies/*/; do
  midclt call filesystem.chown \"{\\\"path\\\": \\\"\$dir\\\", \\\"uid\\\": 3000, \\\"gid\\\": 568}\" --job
  midclt call filesystem.setperm \"{\\\"path\\\": \\\"\$dir\\\", \\\"mode\\\": \\\"775\\\"}\" --job
done"

# Single folder
ssh nas 'midclt call filesystem.chown "{\"path\": \"/mnt/...\", \"uid\": 3000, \"gid\": 568}" --job'
ssh nas 'midclt call filesystem.setperm "{\"path\": \"/mnt/...\", \"mode\": \"775\"}" --job'
```

Result: `lysergic:apps` ownership, `775` permissions (owner+group can write).

---

## Storage Operations

```bash
# Pool usage
ssh nas "df -h /mnt/nvmepool /mnt/spinningpool"

# List media library (new/temp content)
ssh nas "ls /mnt/nvmepool/nvmeshare/medialibrary/movies/"
ssh nas "ls /mnt/nvmepool/nvmeshare/medialibrary/tvshows/"

# List long-term keepers
ssh nas "ls /mnt/spinningpool/movies/"
ssh nas "ls /mnt/spinningpool/tvshows/"

# Music library
ssh nas "ls /mnt/spinningpool/music/"
```

**Search order for media**: always check `nvmeshare/medialibrary/` first (new/temp), then `spinningpool/` (long-term keepers).

---

## Job Polling

Async midclt ops (`app.create`, `app.redeploy`, `app.upgrade`, etc.) return a job ID.

```bash
# Wait for job to complete (blocks until done)
ssh nas "midclt call core.job_wait <job_id>"

# Or watch progress live
ssh nas "watch -n2 'midclt call core.get_jobs | jq \".[] | select(.id==<job_id>) | {state,progress}\"'"

# Check a specific job
ssh nas "midclt call core.get_jobs | jq '.[] | select(.id==<job_id>)'"
```

---

## Safety Rules

- **Docker commands require sudo** — use `midclt` where possible; only `sudo docker` for log inspection or operations without a midclt equivalent
- **Unknown method?** Read the API definition before guessing parameters
- **NVMe pool target**: keep below 80% — ZFS performance degrades above this
- **CrowdSec warning**: do NOT add nftables `forward` hook — breaks Docker networking on TrueNAS
