# Installation

How to get Alby Hub running. Once it's up, use the CLI to manage it — see [Initial Setup](./initial-setup.md) for the first-time setup flow.

## Recommended: systemd service (Linux)

On a Linux server, **the default and recommended way to install Alby Hub is the systemd install script** ([x86_64](#linux-x86_64) / [aarch64](#linux-aarch64-arm64-servers)). It installs the hub as a service that starts automatically on boot and is restarted on failure.

**This is the default for every backend**. A backend that needs extra environment variables does not change this; set those on the systemd unit rather than dropping to a manual binary install (see [Configuring env vars for a systemd install](#configuring-env-vars-for-a-systemd-install)).

### Linux x86_64

Installs as a systemd service that starts automatically on boot.

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/getAlby/hub/master/scripts/linux-x86_64/install.sh)" -- -y --skip-verify -s
```

Flags: `-y` non-interactive, `--skip-verify` skip PGP signature verification, `-s` install as systemd service.

After the script completes, verify with `systemctl status albyhub`. If the script fails, diagnose and fix the specific error then re-run it — do **not** fall back to a manual binary install or create your own systemd service.

Default port: `http://localhost:8029`

To update later: run `./update.sh` in the install directory. Backup data lives in `[install path]/data`.

### Linux aarch64 (ARM64 Servers)

Installs as a systemd service that starts automatically on boot. Same approach as x86_64, different script:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/getAlby/hub/master/scripts/linux-aarch64/install.sh)" -- -y --skip-verify -s
```

Flags: `-y` non-interactive, `--skip-verify` skip PGP signature verification, `-s` install as systemd service.

After the script completes, verify with `systemctl status albyhub`. If the script fails, diagnose and fix the specific error then re-run it — do **not** fall back to a manual binary install or create your own systemd service.

### Configuring env vars for a systemd install

**This is not needed by default. Only add env vars if the user explicitly specifies them.**

The systemd install runs the hub from a fixed working directory, so a `.env` file is **not** read. Any backend or configuration that needs extra environment variables (e.g. LND credential paths, a custom `MEMPOOL_API` or `LDK_ESPLORA_SERVER`) must have those vars set on the systemd unit, **before** running `setup`.

Add a drop-in override and restart:

```bash
sudo systemctl edit albyhub
```

In the editor, add (one `Environment=` line per var):

```ini
[Service]
Environment="KEY=value"
```

Then apply and restart:

```bash
sudo systemctl restart albyhub
```

Data (database, keys, logs) stays in `[install dir]/data` — the persistent location the install script configures — so there is no need for `WORK_DIR=.`. See [Backends](./backends.md) for which vars each backend needs.

## Other installation options

Manual binary, Docker, Raspberry Pi, desktop app, and Umbrel/Start9 — see [Other installation options](./other-installation-options.md).

## System Requirements

| Backend                  | RAM                          | Disk    |
| ------------------------ | ---------------------------- | ------- |
| LDK (default)            | 2 GB (or 512 MB + 2 GB swap) | 1 GB+   |
| Others                   | 256 MB                       | Minimal |

lightning port 9735 should be open and reachable for optimal channel connectivity.