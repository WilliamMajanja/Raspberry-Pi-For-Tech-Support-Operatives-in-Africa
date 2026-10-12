# Bash Shell Programming

Bash is both an interactive shell and a scripting language. Learning shell fundamentals makes Linux administration more reproducible and helps readers understand the command examples elsewhere in this guide. The examples use Bash features and do not require extra packages beyond Bash and standard command-line utilities already present on many desktop installations.

## 1. Commands, arguments, and exit status

A simple command consists of a program name followed by arguments:

```bash
printf '%s\n' 'Hello, Linux'
```

The shell locates the command through `PATH`, expands syntax such as variables and globs, and then starts the program. The program returns an **exit status**: conventionally `0` means success and a non-zero value means some kind of failure. Capture the previous status with `$?` immediately after the command that produced it.

```bash
if test -r /etc/os-release; then
    printf '%s\n' 'Distribution metadata is readable.'
fi
```

Do not treat “the command printed output” as proof that it succeeded. Check exit status and inspect expected output.

## 2. Quoting and expansion

Quoting controls what the shell interprets:

- **Single quotes** preserve every character literally: `'two words $HOME'`.
- **Double quotes** preserve spaces and most special characters while allowing variable and command substitutions: `"$HOME"`.
- **Unquoted expansions** are subject to word splitting and pathname expansion; avoid them for data.

Prefer:

```bash
printf '%s\n' "$HOME"
```

Avoid relying on unquoted variables, especially when a value may contain spaces, wildcard characters, or be empty:

```bash
# Safer: one argument, even if the path contains spaces.
mkdir -- "$HOME/security notes"
```

The `--` convention marks the end of options for many utilities. It helps when a filename begins with `-`, but it is not supported by every command.

## 3. Variables and environment

Assign a shell variable without spaces around `=`:

```bash
project='sample-lab'
printf 'Project: %s\n' "$project"
```

An **environment variable** is exported to child processes:

```bash
export LANG=C
```

Environment values are configuration, not secure secret storage. Avoid placing passwords, private keys, or long-lived tokens directly in shell history, command arguments, shared logs, or public scripts.

## 4. Redirection and pipelines

File descriptors conventionally include standard input (`0`), standard output (`1`), and standard error (`2`).

```bash
command >output.txt 2>errors.txt
command >>output.txt
command 2>&1 | another-command
```

`>` truncates an existing destination. Check the path before using it; a typo can overwrite valuable data. A pipeline connects one process’s output to another process’s input:

```bash
printf '%s\n' alpha beta gamma | sort
```

By default, a pipeline’s status is generally the status of its last command. In scripts, `set -o pipefail` makes a pipeline fail if a command in it fails.

## 5. Globs, arrays, and loops

Globs are expanded by the shell, not by the command. An unmatched glob may remain a literal string in Bash unless `nullglob` is enabled.

```bash
shopt -s nullglob
files=(./*.md)
for file in "${files[@]}"; do
    printf 'Markdown file: %s\n' "$file"
done
```

Arrays preserve each item as a separate value. Quote `"${array[@]}"` when passing elements as arguments. This avoids turning a filename containing spaces into multiple arguments.

## 6. Conditions and functions

Use `[[ ... ]]` for Bash string tests and `(( ... ))` for arithmetic:

```bash
if [[ -n ${EDITOR:-} ]]; then
    printf 'Editor is set to %s\n' "$EDITOR"
fi

count=3
if (( count > 0 )); then
    printf 'There are items to review.\n'
fi
```

`${value:-fallback}` supplies a default without changing the variable. Define a function to give a repeated operation a name:

```bash
say_status() {
    printf '[%s] %s\n' "$(date '+%H:%M:%S')" "$1"
}

say_status 'Review started'
```

## 7. A small, safe script

This example only reads Markdown files in the current directory and reports how many it finds:

```bash
#!/usr/bin/env bash
set -Eeuo pipefail
shopt -s nullglob

files=(./*.md)
printf 'Found %d Markdown files in %s\n' "${#files[@]}" "$PWD"
for file in "${files[@]}"; do
    printf ' - %s\n' "$file"
done
```

`set -e` can behave unexpectedly in conditionals, pipelines, and functions; it is not a substitute for deliberate error handling. For scripts that modify data, validate arguments, quote every expansion, test on sample data, and make backups or use a disposable working directory.

Syntax-check a script without running it:

```bash
bash -n ./script.sh
```

Run a local script explicitly with Bash:

```bash
bash ./script.sh
```

## 8. Safe scripting practices

1. **Be explicit about paths.** Resolve input and output paths before destructive actions.
2. **Quote expansions.** Treat filenames and user input as data, not shell syntax.
3. **Avoid `eval`.** It turns text into executable shell code and is rarely necessary.
4. **Avoid broad deletion and privilege.** Do not run `rm -rf` on variables or use `sudo` as a debugging shortcut.
5. **Check prerequisites and errors.** A clear error is safer than continuing with incomplete state.
6. **Do not parse `ls` output.** Use globs or `find` with null-delimited output when appropriate.
7. **Keep secrets out of source.** Use a suitable secret store or a protected file with carefully limited permissions.
8. **Test in a disposable directory.** First test with harmless sample files and inspect the result.
9. **Know which shell is used.** Debian’s `/bin/sh` is commonly Dash; Bash-specific syntax requires Bash (`#!/usr/bin/env bash`).

## 9. Bash versus other shells

Shells share common concepts but do not share every feature. Bash arrays, `[[ ... ]]`, process substitution, and some expansions are not POSIX `sh` syntax. If portability is required, write to the POSIX shell subset and test with the intended `/bin/sh`. If a script uses Bash, declare Bash in its shebang and invoke it accordingly.

## 10. References

- [Practical command-line recipes in this guide](Command_Line_Recipes.md)
- [GNU Bash Reference Manual](https://www.gnu.org/software/bash/manual/)
- [BashFAQ](https://mywiki.wooledge.org/BashFAQ)
- [ShellCheck](https://www.shellcheck.net/) — optional static-analysis service/tool; not required to read or run the examples in this guide.
- [`bash(1)` manual](https://manpages.debian.org/bash/bash.1.en.html)
