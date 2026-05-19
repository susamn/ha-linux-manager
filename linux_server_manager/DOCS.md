# Linux Server Power Manager

This Add-on allows you to safely manage the power state of multiple remote Linux servers.

## Features
- **Remote Shutdown:** Connects via SSH and executes a shutdown command.
- **Smart Power Cut:** Monitors the server's reachability (Ping). Once unreachable, it waits for a safety buffer (10s) and then turns off the associated smart plug in Home Assistant.
- **Power On:** Simply turns on the smart plug to boot the machine (requires BIOS "Restore on AC Power Loss" to be enabled).
- **Multi-Server UI:** A clean dashboard to manage all your servers in one place.

## Configuration

Add your servers to the configuration like this:

```yaml
servers:
  - name: "My Ubuntu Server"
    host: "192.168.1.100"
    user: "your_username"
    password: "your_password"
    plug_entity: "switch.server_smart_plug"
```

## Important Notes
- **Sudo Permissions:** The SSH user must have `sudo` permissions without a password prompt for the `shutdown` command, OR the password provided in the config must match the sudo password (the add-on tries to pipe the password to `sudo -S`).
- **BIOS Settings:** To turn the server ON using the smart plug, you must enable the "Restore on AC Power Loss" (or similar) setting in the server's BIOS.
- **Security:** Passwords are stored in the HA Add-on configuration. Using SSH keys is generally more secure, but this add-on currently uses password-based authentication as requested.
