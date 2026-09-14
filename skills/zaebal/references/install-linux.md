# Linux hook setup

Read this only for an installation/update/removal request targeting a Linux
agent process, including WSL when the agent runs inside that distribution.
Do not install PowerShell or Windows launchers, or write the Windows user's config.

Use a full `howdeploy/Z.A.E.B.A.L` checkout matching the skill revision. A download
of only `skills/zaebal` does not contain `core/` or the registration helper. If no
revision is recorded, obtain one fresh checkout for both skill and runtime.
Use an existing Python 3.10+; the runtime and helper need only its standard library.

## Codex

From that checkout:

```sh
python3 scripts/install_codex_hook.py --platform linux
```

The helper registers only Codex, honoring `CODEX_HOME`, and stores the selected
absolute interpreter/runtime command. `--config` and `--dest` select explicit
paths for isolated checks. It preserves unrelated hooks, user settings and
incident history, and prints a unique config backup. Reinstall replaces its own
entry. No Windows adapter or dependency is installed.

Close editors changing `hooks.json` during setup. Concurrent runs of this helper
are serialized; outside edits detected before replacement abort the update, but
uncoordinated external editors do not share its lock.

Run the short platform smoke:

```sh
python3 -m unittest discover -s tests -p test_cross_platform.py
```

This uses temporary configuration/state and no paid external auditor. For live
activation, review/trust the hook through Codex `/hooks` where required, start a
fresh session and verify that a controlled complaint delivers the protocol and
ordinary input stays silent. Report command smoke and host activation separately.

Update by repeating setup from the matching new checkout. Unregister only this
hook with the same path options and `--remove`; runtime and user data remain.

## Other Linux hosts

The existing adapters in `adapters/claude-code`, `adapters/kimi-cli` and
`adapters/opencode` and the shared runtime remain the Linux integration path.
Read only the chosen host adapter and relevant `install.sh` section; install its
entry while preserving unrelated configuration. The legacy `./install.sh`
auto-detects and installs **all** available hosts, so run it only if the user asked
for all of them. Existing `./uninstall.sh` removes all integrations and data;
do not use it to unregister just one host.
