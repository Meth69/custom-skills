# NAS Knowledge Base — TrueNAS Scale

## 1. System & Access

| Property | Value |
|----------|-------|
| OS | TrueNAS Scale Goldeye 25.10.2.1 |
| Container runtime | Docker (k3s/kubernetes removed in Fangtooth) |
| IP | 192.168.178.100 |
| Hostname | `truenas` |
| SSH | `ssh nas` |
| Web UI | `https://192.168.178.100:444` (HTTPS redirect enabled) |

---

## 2. midclt Reference

### Usage Rules
1. **Unfamiliar method?** Read the API definition first — do NOT guess parameter formats:
   ```bash
   ssh nas "cat /usr/lib/python3/dist-packages/middlewared/api/v25_10_2/<method>.py"
   ```
2. **Parameter error?** Check the API definition immediately.
3. **Use `-j` flag** for async jobs (tracks job progress): `midclt call -j app.create ...`
4. **No sudo needed** for `midclt` — works directly as `admin` user over SSH.

### App Management Methods
| Method | Description |
|--------|-------------|
| `app.query` | List all apps with state |
| `app.get_instance <name>` | Get detailed app info (containers, ports, volumes, images) |
| `app.start <name>` | Start an app (returns job ID) |
| `app.stop <name>` | Stop an app (returns job ID) |
| `app.redeploy <name>` | Redeploy an app (returns job ID) |
| `app.upgrade <name>` | Upgrade an app |
| `app.upgrade_summary <name> '{}'` | Check if upgrade available (returns `upgrade_version`) |
| `app.create` | Install a new app from catalog |
| `app.delete <name>` | Remove an app |
| `app.update <name>` | Update app configuration |
| `app.container_ids <name>` | Get container IDs |
| `app.used_ports` | List all used ports |
| `app.image.query` | List docker images |
| `catalog.apps` | List all available catalog apps |
| `catalog.trains` | List available trains (stable, community, etc.) |

### Filesystem Methods
| Method | Description |
|--------|-------------|
| `filesystem.chown` | Set ownership (`uid`, `gid`, `path`) — preferred over `chown` |
| `filesystem.setperm` | Set permissions (`path`, `mode`) — preferred over `chmod` |

### Job Methods
| Method | Description |
|--------|-------------|
| `core.get_jobs` | List all jobs |
| `core.job_wait <id>` | Block until job completes |

### Quick Reference Commands
```bash
# List all apps with state
ssh nas "midclt call app.query | jq -r '.[] | \"\(.name): \(.state)\"'"

# Running apps only
ssh nas "midclt call app.query | jq '.[] | select(.state==\"RUNNING\") | .name'"

# Detailed app info
ssh nas "midclt call app.get_instance jellyfin | jq ."

# List all available app methods
ssh nas "midclt call core.get_methods | jq -r 'keys[] | select(startswith(\"app.\"))'"

# System info
ssh nas "midclt call system.info | jq ."

# Docker (requires sudo — prefer midclt where possible)
ssh nas "sudo docker ps"
```

---

## 3. Installing Apps

### Catalog Apps
```bash
# List catalog apps by train
ssh nas "midclt call catalog.apps '{}'" | jq '.stable | keys[]'
ssh nas "midclt call catalog.apps '{}'" | jq '.community | keys[]'

# Check which train an app is in
ssh nas "midclt call catalog.apps '{}'" | jq '.community.navidrome'

# Install
ssh nas "midclt call -j app.create '{
  \"catalog_app\": \"<app_name>\",
  \"app_name\": \"<instance_name>\",
  \"train\": \"<train_name>\",
  \"version\": \"<chart_version>\",
  \"values\": {}
}'"
```

### `app.create` Parameters
| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `catalog_app` | Yes | — | App name in catalog (e.g., `"navidrome"`) |
| `app_name` | Yes | — | Instance name (alphanumeric + hyphens, must start with letter) |
| `train` | No | `stable` | **Must be `"community"` for community apps** |
| `version` | No | `latest` | Chart version |
| `values` | No | `{}` | Configuration overrides |

**GOTCHA**: `train` defaults to `stable`. Community-only apps FAIL silently with the wrong train.

### Example: Install Navidrome
```bash
ssh nas "midclt call -j app.create '{\"catalog_app\": \"navidrome\", \"app_name\": \"navidrome\", \"train\": \"community\", \"values\": {}}'"
```

### Custom docker-compose Apps
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

## 4. Storage Layout

### Pools
| Pool | Type | Size | Target usage |
|------|------|------|-------------|
| `nvmepool` | NVMe SSD (Samsung 980 1TB) | ~896 GB | Primary/fast — **keep below 80%** |
| `spinningpool` | HDD mirror (2× Seagate Exos 8TB) | ~7.3 TB | Bulk/archive |

### `/mnt/nvmepool/nvmeshare/` — Application Data (PRIMARY)
| Directory | Purpose |
|-----------|---------|
| `medialibrary/movies/` | NEW movies — default Jellyseer download, **temporary/deletable** |
| `medialibrary/tvshows/` | NEW TV shows — default Jellyseer download, **temporary/deletable** |
| `downloads/movies/` | Active torrent downloads for movies |
| `downloads/tvshows/` | Active torrent downloads for TV shows |
| `jellyfin/` | Media server config, metadata, plugins |
| `qbittorrent/` | Torrent client data |
| `kavita/` | Manga/comic reader data |
| `jellyseer/` | Media request management |
| `paperless/` | Document management (custom compose app) |
| `mealie/` | Recipe manager |
| `linkding/` | Bookmark manager |
| `syncthing/` | File sync config |
| `homarr/`, `homepage/` | Dashboard apps |
| `factorio/` | Game server data |
| `actualbudget/` | Budgeting app |
| `wger/` | Fitness app |
| `secondbrain/` | Notes/knowledge base |
| `recyclarr/` | Sonarr/Radarr config sync |
| `composefiles/` | Docker compose files |
| `nginx-proxy-manager/` | Reverse proxy configs |
| `scripts/` | Custom maintenance scripts (ntfy alert forwarder, auto-update) |
| `crowdsec/` | CrowdSec engine + bouncer config |

### `/mnt/spinningpool/` — Archive/Bulk Storage
| Directory | Purpose |
|-----------|---------|
| `music/` | Music library for Navidrome |
| `movies/` | **LONG-TERM** movie keepers (62+ titles, includes 4K/HDR) |
| `tvshows/` | **LONG-TERM** TV keepers (AoT, GoT, Better Call Saul, etc.) |
| `aks/` | Photo archive (194 folders, personal/family by event/date) |
| `books/` | E-books (Health, Islam, Medicina Estetica, Novels, Self-Improvement, Trading) |
| `courses/` | Online courses (Affinity Photo, Procreate, iPhone Photography) |
| `generalstorage/` | General files (Audio, Backup, Documenti, ECM, Games Backup, University, Videos) |
| `immich/` | Immich photo management data |
| `backup/` | App backups (linkding, mealie, paperless, secondbrain) |
| `syncthing/` | Syncthing sync folder |
| `piwigo/` | Piwigo gallery data |

---

## 5. Media Workflow

- **NVMe is the default** — user prefers NVMe as much as possible
- Jellyseerr downloads go to NVMe by default
- `nvmeshare/medialibrary/` = NEW/TEMPORARY — can be deleted, check here first
- `spinningpool/movies/` and `spinningpool/tvshows/` = LONG-TERM keepers only

**Search order for media:**
1. `/mnt/nvmepool/nvmeshare/medialibrary/` (new/temp)
2. `/mnt/spinningpool/` (archived/long-term)

---

## 6. Permissions

**User/Group IDs**: `lysergic=3000`, `apps=568`

Always use `filesystem.chown` + `filesystem.setperm` (NOT raw `chown/chmod`):

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
ssh nas 'midclt call filesystem.chown "{\"path\": \"/mnt/nvmepool/nvmeshare/medialibrary/tvshows/FOLDER\", \"uid\": 3000, \"gid\": 568}" --job'
ssh nas 'midclt call filesystem.setperm "{\"path\": \"/mnt/nvmepool/nvmeshare/medialibrary/tvshows/FOLDER\", \"mode\": \"775\"}" --job'
```

Result: `lysergic:apps` ownership, `775` (owner+group can write).

---

## 7. Running Services

### Active Apps
| App | Port(s) |
|-----|---------|
| jellyfin | 8096 |
| jellyseerr | 5055 |
| radarr | 7878 |
| sonarr | 8989 |
| bazarr | 6767 |
| prowlarr | 9696 |
| qbittorrent | 10189 (web), 51413 (torrent) |
| flaresolverr | 8191 |
| recyclarr | — |
| kavita | 2030 |
| linkding | 9090 |
| syncthing | 8384 (web), 22000 (sync) |
| immich | 2283 |
| piwigo | 8080 |
| open-webui | 3000 |
| navidrome | 30043 |
| nginx-proxy-manager | 80, 443, 81 (admin) |
| paperless-ngx | 8000 |

### Stopped Apps
`wger`, `factorio`, `wg-easy`, `dockge`, `homepage`, `actual-budget`, `kosync`, `dnstt`

### Custom docker-compose Apps
| App | Port | Containers |
|-----|------|------------|
| paperless-ngx | 8000 | paperless-ngx + postgres:17 + redis:7 |

---

## 8. Domain Routing (Nginx Proxy Manager)

NPM configs at `/mnt/nvmepool/nvmeshare/nginx-proxy-manager/`

| Domain | Target |
|--------|--------|
| `jelly.alcared.it` | Jellyfin (public) |
| `kavita.alcared.it` | Kavita (public) |
| `ding.alcared.it` | Navidrome (public) |
| `seer.alcared.it` | Jellyseerr (public, multi-user) |
| `fit.alcared.it` | wger (STOPPED — broken proxy, remove or update) |

---

## 9. Monitoring

| System | Details |
|--------|---------|
| **ntfy.sh alerts** | Topic: `lysacidnasalerts6-9` |
| TrueNAS alerts | Cron every 5 min — `truenas-ntfy-alerts.sh` (WARNING/CRITICAL/EMERGENCY) |
| NVMe usage alert | Cron every 30 min — `nvme-disk-alert.sh` (fires once at >90%, resets when resolved) |
| Weekly auto-update | Cron ID 7, Sat 3AM — `app-auto-update.sh` (upgrades all RUNNING apps, notifies ntfy) |
| SMART tests | Weekly SHORT (all disks, Sun 2AM), monthly LONG (HDDs, 1st 3AM) |
| ZFS snapshots | nvmeshare every 4h, 7-day retention, recursive |
| ZFS scrubs | Both pools weekly (Sunday) |

Scripts at: `/mnt/nvmepool/nvmeshare/scripts/`
Auto-update log: `/mnt/nvmepool/nvmeshare/scripts/app-update.log`

---

## 10. Security

### Applied Hardening
- SSH: weak ciphers disabled (NONE, AES128-CBC removed), key-only auth
- NFS: all 16 exports restricted to `192.168.178.0/24`
- HTTPS redirect enabled for TrueNAS Web UI
- Audit log retention: 30 days (max)
- **CrowdSec** (custom app): parses NPM logs, bans malicious IPs via iptables DOCKER-USER + INPUT chains, notifies ntfy on ban
  - Engine: `crowdsecurity/crowdsec:latest`, API on `127.0.0.1:8085`
  - Bouncer: `ghcr.io/shgew/cs-firewall-bouncer-docker`, iptables mode
  - Collection: `crowdsecurity/nginx-proxy-manager`
  - **WARNING: Do NOT add nftables `forward` hook** — breaks Docker networking on TrueNAS (iptables-nft conflict)

### Still Needs Web UI Configuration
- Enable 2FA/TOTP for admin account (Credentials > Users > admin)
- Enable authentication on Radarr, Sonarr, Prowlarr, Bazarr (Settings > General > Authentication)
- Replace broad `nvmeshare` SMB share with purpose-specific shares
- Regenerate SSL certificate with proper SANs (`192.168.178.100`, `truenas`)

---

## 11. Recyclarr / Quality Profiles

- Config: `/mnt/nvmepool/nvmeshare/recyclarr/configs/recyclarr.yml`
- Sync: `ssh nas "sudo docker exec ix-recyclarr-recyclarr-1 recyclarr sync"`

### 5 Profiles (synced to both Radarr and Sonarr)
| Profile | Priority |
|---------|----------|
| `HD 1080p [ITA/ENG]` / `1080p [ITA/ENG]` | Bluray > WEB, Italian+MULTi scored +1500 |
| `4K [ITA/ENG]` | UHD/WEB-2160p, Italian+MULTi scored +1500 |
| `HD 1080p [ENG]` / `1080p [ENG]` | English only |
| `4K [ENG]` | English only 4K |
| `HD 1080p [CHN]` / `1080p [CHN]` | Chinese+MULTi scored +1500 |

- **Italian/MULTi scores** (+1500): managed via API, protected by `reset_unmatched_scores.except`. If re-syncing after profile deletion, re-apply scores via Radarr/Sonarr API.
- **Minimum seeders**: 5 on all indexers
- **Jellyseerr**: quality profiles appear in "Advanced" tab when requesting media

---

## 12. Notes & Gotchas

### SSH User Permissions
`admin` (uid 950) is in groups: `admin`, `builtin_administrators`, `apps` (568), `lysergic` (3000).
Can write to any `775` lysergic-group dirs on nvmeshare.

### ZFS Dataset ACL Inheritance
New datasets inherit NFSv4 ACL from pool. If a child dataset has NFSv4 but parent has POSIX, SMB will alert.
Fix: `pool.dataset.update "<dataset>" '{"acltype": "POSIX", "aclmode": "DISCARD"}'`

### Paperless-ngx
Custom compose app (postgres:17 + redis:7). Data at `/mnt/nvmepool/nvmeshare/paperless/` (single dataset, no child datasets). Documents backed up to `spinningpool/backup/paperless`.

### ZFS Replication
`secondbrain`, `linkding`, `paperless` all replicate to `spinningpool/backup/` using the main nvmeshare snapshot task.

### Job Polling (Async Operations)
```bash
# Block until complete
ssh nas "midclt call core.job_wait <job_id>"

# Watch progress live
ssh nas "watch -n2 'midclt call core.get_jobs | jq \".[] | select(.id==<job_id>) | {state,progress}\"'"
```
