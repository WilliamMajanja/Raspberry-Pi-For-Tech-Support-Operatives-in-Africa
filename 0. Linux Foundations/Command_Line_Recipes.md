# Practical Command-Line Recipes

This chapter uses a cookbook format: each recipe starts with a practical task, gives a short command, then explains what it does, how to check the result, and what to watch out for. Commands are original examples for this guide, not copied from a third-party book. The default examples favor inspection and reversible work over destructive actions.

**Compatibility key**

- **Debian/Kali:** expected to work on current Debian-derived systems; check optional command availability.
- **Bash:** requires Bash syntax; Debian’s `/bin/sh` may be Dash.
- **Optional:** requires the named package or service, which may not be installed by default.

## Quick recipe index

| Topic | Recipes |
| --- | --- |
| Identify the device and safely reuse shell history | [1](#1-identify-the-distribution-architecture-and-kernel), [2](#2-recall-a-shell-command-without-blindly-rerunning-it) |
| Format, count, and process local text | [3](#3-format-tab-separated-output-as-a-table), [4](#4-count-repeated-lines), [5](#5-read-a-file-one-line-at-a-time-in-bash) |
| Inspect storage, sockets, services, and routes | [6](#6-inspect-disk-usage), [7](#7-check-local-listening-sockets), [8](#8-read-service-status-and-logs), [9](#9-inspect-network-configuration-without-scanning) |
| Check packages, update Kali, and compare remote files | [10](#10-check-a-package-before-installing-it), [11](#11-update-kali-deliberately), [12](#12-compare-a-local-file-with-an-authorized-remote-copy) |
| Verify, preview, serve, or record local files | [13](#13-verify-a-downloaded-file-against-its-publishers-checksum), [14](#14-preview-an-archive-before-extracting-it), [15](#15-serve-a-local-directory-only-to-this-computer), [16](#16-capture-a-terminal-session-carefully) |
| Everyday habits | [17](#17-useful-command-line-habits) |

## 1. Identify the distribution, architecture, and kernel

**Use when:** a command or package depends on which Linux system is running.

```bash
grep -E '^(PRETTY_NAME|VERSION_CODENAME)=' /etc/os-release
uname -m
uname -r
```

**How it works:** `/etc/os-release` reports distribution identity; `uname -m` reports machine architecture; `uname -r` reports the currently running kernel. These are distinct facts: the installed packages, CPU architecture, and active kernel release are not interchangeable.

**Verify:** compare the distribution and release with the official documentation for the command you plan to use.

**Platform note:** on Debian/Kali, `dpkg --print-architecture` gives the package architecture (for example, `arm64`), which may differ in spelling from `uname -m` (often `aarch64`).

## 2. Recall a shell command without blindly rerunning it

**Use when:** you want to reuse a long command from the current shell session.

Press **Ctrl-R**, type a distinctive fragment, inspect the recalled command, edit it, and press Enter only after checking every argument and target.

**Why this safer pattern:** Bash history expansion offers shortcuts such as `!!`, `!$`, and `!prefix`, but they can repeat a destructive command or substitute an unexpected argument. In particular, avoid blindly prefixing a recalled command with `sudo`. Read the complete command first and add elevation deliberately.

**Privacy note:** command history may contain paths, hostnames, tokens, or other sensitive data. Clearing the visible history is not a secure erasure guarantee; commands may also be present in terminal logs, audit records, backups, or process accounting.

## 3. Format tab-separated output as a table

**Use when:** you have a small tab-separated report that is hard to scan.

```bash
printf 'name\tstate\nrouter\tseen\nserver\tunknown\n' | column -t -s $'\t'
```

**How it works:** `printf` emits predictable tab-separated input. `column` aligns fields using a tab as the delimiter.

**Verify:** compare the output rows with the input. Do not use this presentation-oriented output as a machine-readable data format.

**Platform note:** `$'…'` is Bash syntax. Some minimal systems may not include `column`; it is commonly provided by `util-linux` on Debian-derived systems.

## 4. Count repeated lines

**Use when:** summarizing identical lines from a local, authorized log or report.

```bash
printf '%s\n' warning info warning error warning | sort | uniq -c | sort -nr
```

**How it works:** `uniq` counts adjacent duplicates, so sort first. The final numeric reverse sort puts the most common values first.

**Caution:** raw logs may contain personal data, internal addresses, session identifiers, or secrets. Redact before sharing output.

## 5. Read a file one line at a time in Bash

**Use when:** writing a small Bash script that must preserve spaces and backslashes in each line.

```bash
while IFS= read -r line || [[ -n $line ]]; do
    printf 'Line: %s\n' "$line"
done < ./sample.txt
```

**How it works:** `IFS=` prevents trimming; `-r` prevents backslash interpretation; the final condition handles a last line without a newline. Redirecting the file into the loop avoids the common pipeline subshell issue.

**Verify:** test with a disposable file containing spaces, a backslash, an empty line, and a final line without a newline. Use only files you are authorized to read.

## 6. Inspect disk usage

**Use when:** checking which mounted filesystems are nearing capacity.

```bash
df -hT
```

**How it works:** `df` reports filesystem-level use; `-h` selects human-readable units and `-T` includes the filesystem type.

For a user-owned directory, a limited-depth summary can help find large subdirectories:

```bash
du -h --max-depth=1 "$HOME" 2>/dev/null | sort -h
```

`du` may take time on large trees. Start with your own home directory; do not recursively scan private or production data without permission.

## 7. Check local listening sockets

**Use when:** confirming whether a service is listening on this machine.

```bash
ss -lntup
```

**How it works:** `ss` displays listening TCP and UDP sockets; `-n` keeps numeric addresses/ports, `-t` selects TCP, `-u` UDP, `-l` listeners, and `-p` process information where available.

**Verify:** check the local address as well as the port. `127.0.0.1` is loopback; `0.0.0.0` and `::` generally indicate listening on all IPv4 or IPv6 interfaces. Process details for other users’ services may require elevated privileges; do not use `sudo` unless you need it and are authorized.

## 8. Read service status and logs

**Use when:** diagnosing a systemd service on Debian or Kali.

```bash
systemctl status --no-pager --full NetworkManager
journalctl -u NetworkManager --since today --no-pager
```

Replace `NetworkManager` with a service you recognize. `status` shows current state and recent messages; `journalctl` queries the journal.

**Caution:** logs can contain usernames, network names, addresses, and service data. Sanitize them before posting publicly. These commands inspect state; `start`, `stop`, `enable`, and `disable` change it.

## 9. Inspect network configuration without scanning

**Use when:** checking local interfaces and the current route.

```bash
ip -brief address
ip route
```

These commands inspect local configuration. They do not test whether another person’s system is vulnerable or authorized for assessment. If DNS resolution is needed, use an approved hostname and understand that the lookup contacts the configured resolver.

## 10. Check a package before installing it

**Use when:** verifying which version a distribution repository offers.

```bash
apt-cache policy PACKAGE_NAME
```

Replace `PACKAGE_NAME` with an actual package name. `apt-cache policy` is an inspection step; it does not install the package.

**Kali-specific reminder:** follow [Kali’s repository guidance](https://www.kali.org/docs/general-use/kali-apt-sources/) on a Kali installation. On Debian, use Debian repositories. Do not add Kali repositories to Debian or mix Debian and Kali repositories on one installation.

## 11. Update Kali deliberately

**Use when:** maintaining a Kali installation between authorized engagements.

Kali is rolling-release. First review Kali’s current [update guidance](https://www.kali.org/docs/general-use/updating-kali/) and confirm the configured repository. On a Kali installation, the documented upgrade flow is:

```bash
sudo apt update
sudo apt full-upgrade
```

Review proposed removals and changes before confirming. Back up important data, make sure you have recovery access, and avoid changing a known-good assessment environment during an engagement. These commands are for Kali, **not** a Debian host. Debian has its own release and upgrade procedures.

## 12. Compare a local file with an authorized remote copy

**Use when:** checking whether a local file differs from the same file on a host you administer.

```bash
diff -u ./local.conf <(ssh admin@example.test 'cat -- /etc/example.conf')
```

**How it works:** Bash process substitution makes the SSH command’s output available to `diff`. Replace the account, host, and path with values you are authorized to access. Review the SSH host-key prompt; do not bypass host-key verification.

**Caution:** configuration output may contain secrets. Avoid writing it to public logs or tickets.

## 13. Verify a downloaded file against its publisher’s checksum

**Use when:** a trusted publisher provides a checksum for the exact release artifact.

```bash
sha256sum ./downloaded-file
```

Compare the full digest with the value obtained independently from the publisher’s authenticated release channel. Computing a hash alone does not establish authenticity; if the download and checksum come from the same compromised source, both may be wrong.

## 14. Preview an archive before extracting it

**Use when:** examining a downloaded archive before use.

```bash
file ./archive.tar.gz
tar -tzf ./archive.tar.gz | less
```

Review member names and sizes before extraction. Archives from untrusted sources can contain misleading paths, symlinks, or unexpected content. Extract only in a new, disposable directory and inspect the result before opening files or running programs.

## 15. Serve a local directory only to this computer

**Use when:** previewing static files in a browser without installing a web server.

From the directory you intend to share:

```bash
python3 -m http.server --bind 127.0.0.1 8000
```

Open `http://127.0.0.1:8000/` on the same machine, then stop the server with `Ctrl-C`.

**Why bind matters:** Python’s simple HTTP server can otherwise listen on network interfaces. Do not use this command to serve confidential files or expose a directory to a network. It is a convenience server, not an authenticated production server.

## 16. Capture a terminal session carefully

**Use when:** keeping a transcript of a reproducible local test.

```bash
umask 077
script --quiet --return "$HOME/session.typescript"
```

Run the test, then type `exit` to finish the recording. The transcript may capture commands and visible output, including secrets. Review and sanitize it before sharing; `umask 077` limits access to the created file on systems that honor the standard umask behavior.

## 17. Useful command-line habits

- Use `man COMMAND`, `COMMAND --help`, and the distribution’s official documentation before copying unfamiliar options.
- Use shell tab completion and `Ctrl-R` history search, then review a recalled command before running it.
- Use `printf` rather than relying on implementation-specific `echo` escape handling.
- Prefer `ss` over older `netstat` examples on current systems.
- Prefer structured output or null-delimited filenames over parsing human-formatted `ls` output.
- Never assume a command is harmless because it is one line. Check target paths, privileges, network scope, and whether it writes or deletes data.
- Never feed unreviewed data into `eval`, a shell pipeline that executes it, or a privileged command.

## Command Index

| Command | Recipes |
| --- | --- |
| `apt-cache` | [10](#10-check-a-package-before-installing-it) |
| `bash` | [2](#2-recall-a-shell-command-without-blindly-rerunning-it), [5](#5-read-a-file-one-line-at-a-time-in-bash), [17](#17-useful-command-line-habits) |
| `column` | [3](#3-format-tab-separated-output-as-a-table) |
| `df`, `du`, `sort` | [6](#6-inspect-disk-usage), [4](#4-count-repeated-lines) |
| `diff`, `ssh` | [12](#12-compare-a-local-file-with-an-authorized-remote-copy) |
| `file`, `less`, `tar` | [14](#14-preview-an-archive-before-extracting-it) |
| `getent`, `ip` | [9](#9-inspect-network-configuration-without-scanning) |
| `grep`, `uname` | [1](#1-identify-the-distribution-architecture-and-kernel) |
| `journalctl`, `systemctl` | [8](#8-read-service-status-and-logs) |
| `python3` | [15](#15-serve-a-local-directory-only-to-this-computer) |
| `script` | [16](#16-capture-a-terminal-session-carefully) |
| `sha256sum` | [13](#13-verify-a-downloaded-file-against-its-publishers-checksum) |
| `ss` | [7](#7-check-local-listening-sockets) |

The catalog is a navigation aid; use each utility’s manual page for its complete current behavior.

## Source and editorial note

The recipe presentation—task first, concise command, explanation, and example—was informed by **Jason Cannon, _Command Line Kung Fu: Bash Scripting Tricks, Linux Shell Programming Tips, and Bash One-liners_ (2014, ISBN 978-1-4992-2203-6)**, a book available in the author’s local bookshelf. This chapter is newly written for Raspberry Pi OS, Debian, and Kali support contexts; it does not reproduce that book’s text or command examples. Older one-liners need review for current utilities, safe defaults, and changed distribution behavior.

For Raspberry Pi-specific tasks, consult Raspberry Pi’s official documentation. For Kali tasks, consult the [official Kali documentation](https://www.kali.org/docs/) first. Corey P. Schultz’s [*Kali Linux Cookbook*, Third Edition (2025)](https://www.packtpub.com/en-au/product/kali-linux-cookbook-9781835889817) and its [publisher sample-code repository](https://github.com/PacktPublishing/Kali-Linux-Cookbook-Third-Edition) are further reading; the book and code have separate licensing terms. Do not copy book text or examples into this guide without permission.
