# Other Installation Options

Non-systemd ways to run Alby Hub. The recommended install is the [systemd service](./installation.md#recommended-systemd-service-linux) — only use the options below if the user explicitly asks for them.

## Linux x86_64 / aarch64 — HTTP Server Binary (Manual - not recommended)

> **Only use this if the user explicitly asks for a manual / no-systemd / throwaway test setup.** For any normal install, on any backend, use the [systemd service](./installation.md#recommended-systemd-service-linux) instead. Do not pick this path just because a backend needs env vars; configure those on the systemd unit (see [Configuring env vars for a systemd install](./installation.md#configuring-env-vars-for-a-systemd-install)).

For testing or running in a specific folder without systemd. The binary starts an HTTP server you manage yourself.

**Download the latest release:**

```bash
# Asset filenames follow this pattern — use the one matching your architecture:
#   albyhub-Server-Linux-x86_64.tar.bz2   (x86_64)
#   albyhub-Server-Linux-aarch64.tar.bz2  (ARM64)
curl -L --no-progress-meter -o albyhub.tar.bz2 \
  https://github.com/getAlby/hub/releases/latest/download/albyhub-Server-Linux-x86_64.tar.bz2
tar -xjf albyhub.tar.bz2
```

The binary is at `bin/albyhub`.

**Configuration via `.env` file:**

Hub reads a `.env` file in the working directory automatically — do not pass env vars inline and do not `source` the file manually. Create `.env` before starting.

**Ask the user** whether they want to use the default data directory (`~/.local/share/albyhub`) or keep data in the current folder. If they want data in the current folder, set `WORK_DIR=.` in the `.env`:

```
WORK_DIR=.
# Add any other vars here, e.g. NETWORK, MEMPOOL_API, LDK_ESPLORA_SERVER
```

Setting `WORK_DIR=.` keeps all hub data (database, logs, keys) in the current folder.

**Running the hub:**

Run in the background — the hub manages its own logging:

```bash
./bin/albyhub &
```

Do **not** redirect stdout (e.g. `> albyhub.log`). Logs are written to `{WORK_DIR}/log/nwc.log`.

Default port: `http://localhost:8080`

## Raspberry Pi 4/5 (Experimental)

```bash
/bin/bash -c "$(curl -fsSL https://getalby.com/install/hub/pi-aarch64-install.sh)"
```

Installs to `/opt/albyhub`. Update via `./update.sh`. Official support is limited for this platform.

## Docker

```bash
docker run -v ~/.local/share/albyhub:/data \
  -e WORK_DIR='/data' \
  -p 8080:8080 \
  ghcr.io/getalby/hub:latest
```

Docker Compose file: https://raw.githubusercontent.com/getAlby/hub/master/docker-compose.yml

Default port: `http://localhost:8080`

## Desktop App (Mac / Windows / Linux)

> **Warning:** Do not suggest the desktop app to users working with an agent. Agents cannot control or interact with the desktop GUI. Use one of the server/binary options above instead.

Download the latest release for your platform from https://github.com/getAlby/hub/releases/latest.

Platforms: Mac (arm64), Windows (amd64), Linux (amd64). Designed to run 24/7 on an always-online machine.

## Node Distributions (Umbrel / Start9)

- **Umbrel**: https://github.com/getAlby/umbrel-community-app-store
- **Start9**: https://github.com/horologger/nostr-wallet-connect-startos

Install via your node OS app store.
