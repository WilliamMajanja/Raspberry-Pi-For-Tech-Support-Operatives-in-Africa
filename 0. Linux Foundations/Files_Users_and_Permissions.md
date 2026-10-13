# Files, Users, and Permissions

This chapter explains where Linux stores files, how users and groups control access, and how to inspect permissions without changing a device. These fundamentals help prevent accidental data exposure during routine support.

## A filesystem path is a location, not a command

Linux names files and directories in a single tree beginning at `/`. A relative path is interpreted from the current working directory; an absolute path begins with `/`.

| Path | Common purpose | Support note |
| --- | --- | --- |
| `/etc` | System configuration | Read before editing; preserve a backup and change record. |
| `/home/NAME` | A user's working files | May contain private data; access only with authorization. |
| `/var/log` | System and service logs | Logs may include identifiers, network details, or secrets. |
| `/tmp` | Temporary working files | Often cleared automatically; never treat it as durable storage. |
| `/proc` and `/sys` | Kernel and device interfaces | Some entries are writable controls, not ordinary files. |

Begin with non-destructive inspection:

```bash
pwd
ls -ld -- . "$HOME"
stat -- "$HOME"
```

`pwd` identifies the current directory. `ls -ld` reports the directory itself rather than its contents. `stat` shows ownership, permissions, and timestamps. Avoid publishing raw command output without checking it for usernames, paths, and sensitive details.

## Users, groups, and access

Linux processes run with user and group identities. A file has an owner, a group, and permission bits for the owner, group, and everyone else. The common permission letters are:

- `r` — read a file, or list a directory's names;
- `w` — change a file, or create/remove entries in a directory;
- `x` — execute a file, or traverse a directory.

Inspect the current account and group memberships with:

```bash
id
```

Do not assume two accounts with similar names are the same identity. Shared administrator accounts make audits and handovers harder; use individual accounts and an approved privilege process where practical.

## A safe permissions exercise

Use a temporary directory you own. The commands create only local sample files, set private permissions on them, and then inspect the result:

```bash
work=$(mktemp -d)
umask 077
printf '%s\n' 'synthetic support note' > "$work/note.txt"
chmod 600 "$work/note.txt"
stat -- "$work/note.txt"
```

`umask 077` makes new files private to the current user on systems that follow normal Unix permission semantics. `chmod 600` gives the owner read/write access and removes access for group and other accounts. Do not run permission changes on production data until you understand the impact and have approval.

When finished, inspect before removing anything. The safer first cleanup step is to print the exact temporary path and remove only that known file in a disposable exercise. Avoid broad recursive deletion commands.

## Permission troubleshooting recipe

1. Record the exact path and the account that receives the error.
2. Run `id` and `stat -- PATH` without `sudo`.
3. Check each parent directory: a user needs execute/traverse permission on each directory in the path.
4. Confirm the file's owner, group, and permission bits with the service or data owner.
5. Make a change only with authorization, a rollback plan, and a clear reason; verify access as the intended account.

Do not use `chmod 777` as a generic fix. It grants broad access, obscures the actual ownership issue, and can expose confidential information.

## When an operation needs elevation

Administrative privilege can change ownership, read private data, install packages, or alter system configuration. Before using `sudo`:

- identify the exact operation and target path;
- confirm that the account and task are authorized;
- inspect the command and arguments;
- prefer the narrowest operation possible;
- record the change and test the intended user's access afterward.

## Known limits

Access control can also involve ACLs, capabilities, containers, network filesystems, service accounts, and mandatory access-control systems. These vary by distribution and configuration. This chapter covers ordinary Unix permission bits; consult the target system's documentation before diagnosing advanced policy behavior.
