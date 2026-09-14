# Custom Node Commands

Some backends expose **custom node commands** — low-level debug tools for inspecting node internals or nudging stuck funds. They are backend-specific.

Only use these tools when the human **explicitly asks** to use them.

**DO NOT EXECUTE CUSTOM NODE COMMANDS ON YOU OWN WITHOUT HUMAN APPROVAL: THEY MAY HAVE UNEXPECTED SIDE-EFFECTS.**

Discover what the active backend supports with `list-custom-node-commands`, then run one with `execute-custom-node-command`.

## Commands

```bash
# List the custom node commands the active backend supports (with their arguments)
npx -y @getalby/hub-cli@0.6.0 list-custom-node-commands

# Execute a command. Pass the whole command line — name plus any flags — as a
# single quoted string. The output is backend-defined JSON.
npx -y @getalby/hub-cli@0.6.0 execute-custom-node-command "debug"

# A command that takes arguments (flags use --name value)
npx -y @getalby/hub-cli@0.6.0 execute-custom-node-command "pay_bolt12_offer --offer lno... --amount 1000"
```

`list-custom-node-commands` returns a `commands` array; each entry has a `name`, a `description`, and an `args` array (each arg has a `name` and `description`). Always run it first rather than assuming a command exists — the set depends on the backend.

## Notes

- Pass the entire command (name and flags) as one quoted string; the hub parses it server-side. Flags are `--name value`; omit any you don't need.
- These are debug tools. Some (e.g. cashu `reset`) are destructive — confirm with the user before running anything that resets or moves funds.
- The `debug` output for bark is the typical answer to "why didn't my receive credit?" — it surfaces VTXOs, the claimable lightning receive balance, and Ark server info. Pair it with `claimlightningreceives` or `runmaintenance` to recover stuck funds. See [Bark](./bark.md).
