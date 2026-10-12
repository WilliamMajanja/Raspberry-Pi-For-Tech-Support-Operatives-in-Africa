# Contributing

Contributions that improve accuracy, clarity, accessibility, and responsible use are welcome.

## Documentation changes

- Write in clear, direct English and explain unfamiliar terms on first use.
- Use the recipe structure: task, platform/prerequisites, command, explanation, verification, and safety/rollback notes.
- Prefer primary sources: official Kali or Debian documentation, upstream manuals, RFCs, standards, and the project’s own source.
- Date platform-specific checks and name the distribution release, architecture, and software version tested.
- Label commands as **read-only**, **changes local state**, or **sends network traffic** when the effect is not obvious.
- Use fictional names, synthetic data, loopback, and isolated lab examples. Never include secrets, live credentials, or personal data.
- Clearly distinguish project claims, source-code observations, and independently verified results.
- Preserve historical authorship and source citations. Do not copy cookbook text or third-party project documentation into this repository without permission and compatible licensing.

## Testing a contribution

This is a static Markdown guide and has no required build system. Check local links and navigation before submitting. If you add a Bash snippet, run `bash -n` on it and execute only harmless examples in a disposable directory. Do not test network or security examples outside an authorized lab.

Run the repository’s optional dependency-free checker with `python3 tools/check_docs.py`. It uses Python’s standard library and Bash syntax checking; it does not install packages or execute the examples.

For platform-specific commands, say exactly where they were tested. Do not describe a Debian test as a Kali test or imply that a linked third-party application was validated when it was not.

## Pull requests

Keep changes focused. Summarize the learning outcome, list pages changed, cite sources, and note the checks performed. For large proposed chapters, open an issue first so scope and source provenance can be discussed.
