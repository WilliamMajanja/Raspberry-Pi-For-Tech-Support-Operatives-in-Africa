# Linux Kernel and System Model

This chapter introduces the Linux kernel as the privileged core of the operating system. It focuses on understanding and safely inspecting a running system; kernel replacement, module loading, and tuning are advanced administration tasks and should be practiced in a disposable virtual machine.

## 1. What the kernel does

The **kernel** mediates access to hardware and provides services to programs. It manages processes, memory, devices, filesystems, networking, permissions, and system calls. A Linux distribution combines a Linux kernel with user-space programs, libraries, an installer, a package repository, and project-specific defaults.

The kernel is not the same thing as a distribution, desktop, shell, or collection of security tools:

| Component | Responsibility | Example |
| --- | --- | --- |
| Kernel | Hardware and core operating-system services | Linux kernel, device drivers |
| User space | Programs and libraries that use kernel services | `systemd`, OpenSSH, Python |
| Distribution | Integrated system, packages, repositories, defaults | Debian, Kali Linux |
| Desktop environment | Graphical session and desktop applications | KDE Plasma |
| Shell | Command interpreter and scripting language | Bash, Dash, Zsh |

Programs request kernel services through **system calls**. For example, opening a file in a program ultimately asks the kernel to resolve a path, check permissions, and interact with the filesystem. Ordinary applications run in user space; kernel code runs with elevated privilege. A kernel vulnerability can therefore affect the whole machine, while a user-space program is generally constrained by its account and permissions.

## 2. Boot and login at a high level

A typical Linux boot sequence is:

1. Firmware initializes hardware and selects a boot device.
2. A bootloader selects a kernel and initial RAM filesystem (initramfs).
3. The kernel initializes memory, drivers, and devices, then starts the first user-space process.
4. The init system starts system services.
5. A display manager may start a graphical session such as KDE Plasma.
6. A login manager or terminal starts the user’s applications and shell.

Exact details vary by hardware and distribution. On ARM single-board computers, firmware and boot partitions can differ from a conventional UEFI PC. A Wayland session is a user-space graphical session; Wayland does not replace the Linux kernel.

## 3. Identify the running system

These inspection commands do not change system configuration:

```bash
uname -r                 # running kernel release
uname -m                 # machine architecture, e.g. aarch64 or x86_64
cat /etc/os-release      # distribution identity and release
ps -p 1 -o comm=         # name of the first user-space process
```

`uname -r` reports the **currently running** kernel. Installing a newer kernel package does not make it active until the system has booted into it. `/etc/os-release` identifies the distribution; it does not identify every repository or package source configured on a system.

On this guide’s authoring machine, `dpkg --print-architecture` reports `arm64`, `/etc/os-release` reports Debian 13 (Trixie), and the graphical session is Wayland with KDE Plasma. These values are a test baseline, not a claim about every reader’s machine.

## 4. Processes, memory, devices, and virtual filesystems

The kernel tracks processes and their resources. Each process has an identity, credentials, open files, memory mappings, and scheduling state. Linux exposes selected runtime information through virtual filesystems:

- `/proc` exposes process and kernel runtime information.
- `/sys` exposes device and kernel-object attributes.
- `/dev` contains device nodes used to access devices through defined interfaces.

These are not ordinary directories containing conventional files on disk. Some entries are writable controls. Treat unfamiliar `/proc` and `/sys` paths as interfaces, not as harmless text files; prefer reading official documentation before changing a value.

Useful read-only inspection examples:

```bash
cat /proc/cmdline        # kernel command-line options for this boot
cat /proc/meminfo        # memory counters
ls /sys/class            # device-class names exposed by sysfs
lsmod                    # currently loaded modules
```

`lsmod` lists kernel modules; it does not prove that a module is safe or needed. `modinfo NAME` displays metadata where available. Do not load or unload modules on a production system as an experiment.

## 5. Drivers and modules

Many drivers are built into the kernel; others are loadable **kernel modules**. Modules can add support for hardware or kernel features. Because a module executes with kernel privilege, module provenance and compatibility matter. Secure Boot policies, signing requirements, kernel configuration, and distribution packaging can restrict which modules load.

For inventory and diagnostics, use the distribution’s documentation and package database. Do not download a random `.ko` file or copy one from a different kernel release. Modules are tightly coupled to kernel versions, configuration, and architecture.

## 6. Kernel updates and distribution differences

Use the package manager and repositories for the distribution actually installed:

- **Debian:** follow Debian’s documentation and configured Debian repositories.
- **Kali:** follow Kali’s documentation and Kali’s supported update process.

Never mix Kali and Debian repositories on one installation as a shortcut. That can replace foundational packages and leave the system in an unsupported state. Before a kernel update, make a backup, read the relevant distribution advisory, ensure there is a recovery route, and schedule a reboot when appropriate.

Kernel headers are development files used by some out-of-tree modules and build systems. They are not the running kernel, and installing headers alone does not update or activate a kernel.

## 7. Kernel configuration and tuning

Kernel configuration includes boot parameters, module settings, sysctl values, and distribution defaults. Some settings affect networking, memory, security boundaries, or device behavior. The fact that a value is writable does not mean it should be changed.

For a safe workflow:

1. Record the current OS, architecture, kernel release, and the setting’s current value.
2. Find the distribution or upstream kernel documentation for that exact setting.
3. Test in a disposable VM or non-production device with a recovery path.
4. Change one item at a time and verify the expected behavior.
5. Record how to revert the change and whether it persists across reboot.

Avoid copying “kernel hardening” snippets without understanding their scope. A setting may be obsolete, unavailable in a particular kernel, or harmful to a desktop or hardware driver.

## 8. Building a kernel: when and where

Building a custom kernel involves selecting a source version, validating its origin, configuring options, compiling for the correct architecture, signing where required, packaging, installing, and maintaining a recovery kernel. A custom kernel is not automatically faster or more secure. It can lose vendor patches, hardware support, security updates, or bootability.

This guide does not instruct readers to replace the kernel on their daily workstation. If kernel development is a learning goal, use a disposable virtual machine or spare device, follow the distribution’s maintained packaging instructions, preserve a known-good kernel, and verify checksums and signatures from trusted release channels.

## 9. Security concepts

- **Least privilege:** run ordinary programs as an unprivileged user; elevate only a specific administrative action.
- **Namespaces and cgroups:** kernel primitives used by containers to isolate views and limit resources. A container still shares the host kernel.
- **Capabilities:** divide some root privileges into narrower permissions; they are not a substitute for understanding the program being granted them.
- **Kernel attack surface:** includes system calls, drivers, modules, and exposed device interfaces. Keeping the supported system updated and removing unneeded access are more reliable than blindly applying tuning snippets.
- **Logs and evidence:** kernel messages can help diagnose drivers and boot problems. Preserve timestamps and original logs during incident response.

## 10. References

- [The Linux Kernel documentation](https://docs.kernel.org/)
- [Debian documentation](https://www.debian.org/doc/)
- [Kali Linux documentation](https://www.kali.org/docs/)
- [Linux man-pages project](https://www.kernel.org/doc/man-pages/)

**Scope:** foundational education. Commands above are read-only examples; kernel modification procedures should be validated separately on the target distribution and hardware.
