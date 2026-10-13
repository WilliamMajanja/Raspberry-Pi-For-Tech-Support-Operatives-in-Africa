# Third-Party Component Notices

The book's original prose, FieldKit source, Coffee Pot Snake artwork, and puzzle content are CC0-scoped as described in `LICENSING.md`.

Standalone executables bundle the Python interpreter and PyInstaller's bootloader/runtime. Each app bundle includes this notice, the Python runtime notice when available, PyInstaller's `COPYING.txt`, and the CC0 scope/license texts. The bundled runtime/build components retain their upstream terms, including the [Python license](https://docs.python.org/3/license.html) and the [PyInstaller license and bootloader exception](https://github.com/pyinstaller/pyinstaller/blob/develop/COPYING.txt). If packaging adds other runtime components, add their exact versions and license notices to the bundle before release.

The CPIP Book Portal separately runs CPIP and its declared dependencies; these retain their own licenses and are not CC0-scoped by this repository. The FieldKit standalone client does not bundle the CPIP server or its Python dependencies.

`cryptography` is used for Ed25519 edition-manifest signing and verification. It is distributed under Apache-2.0 OR BSD-3-Clause; standalone app ZIPs include the installed version's component notice.

No generated standalone binary may be uploaded as an official reader download until its component notices, target OS/architecture, and SHA-256 manifest are included in the CPIP portal release record.
