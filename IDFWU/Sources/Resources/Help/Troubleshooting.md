# Troubleshooting

Common symptoms and how to fix them.

## Scan Finds Nothing

**Symptom:** You added a scan root but the sidebar is empty or missing projects you expected.

**Fix:**
- Check that the root's **max depth** is high enough. If your projects live at `~/Developer/work/acme/web`, a depth of `1` under `~/Developer` will miss them — set depth to `3` or add `~/Developer/work` as its own root.
- Verify the **markers** list includes something that matches your projects. A pure static-site folder with only `index.html` won't match `.git` or `Package.swift`. Add a custom marker if needed.
- Make sure the scan root is **enabled** (toggle in Preferences → Scan Roots).
- Try a manual **Rescan** from the project's context menu or **Sync All** (`Shift+Cmd+R`).

## GitHub Connector Fails

**Symptom:** Projects don't get enriched with remote metadata, or you see connector errors in the Event Stream.

**Fix:**
- Open **Preferences → Connectors** and verify the GitHub personal access token is set and not expired
- Confirm the token has at least `repo` and `read:user` scopes
- Check that your network can reach `api.github.com` (corporate VPNs sometimes block this)
- Re-enter the token and click **Test Connection**

## APM Connection Red

**Symptom:** The APM status indicator in the status bar is red or shows "disconnected".

**Fix:**
- Verify the APM server is running at the configured URL (default: `http://localhost:3032`)
- Check the port — IDFWU expects port **3032** unless you've overridden it in Preferences → APM
- Run `curl http://localhost:3032/health` from a terminal; if that fails, the server is down
- Restart the APM server and wait ~5 seconds for IDFWU to reconnect automatically

## App Won't Launch

**Symptom:** IDFWU crashes on launch, hangs on the splash, or immediately quits.

**Fix:**
- Open **Preferences → Advanced** and click **Reset Defaults**. This wipes local preferences but leaves your projects and scan roots alone.
- If you can't reach Preferences, quit IDFWU and run `defaults delete com.idfwu.IDFWU` from Terminal, then relaunch.
- As a last resort, check `~/Library/Logs/IDFWU/` for crash logs and file a bug with the most recent entry.
