<p align="center">
  <img alt="picklevislogo" src=".github/logo.png">
</p>

# Picklevis

[![Python 2.7/3.5/3.10](https://github.com/Inokinoki/picklevis/actions/workflows/test-python.yml/badge.svg)](https://github.com/Inokinoki/picklevis/actions/workflows/test-python.yml)

A tool to visualize Python pickle file.

## Usage

```bash
python3 picklevis_core.py <pickle-file>
```

This default mode is execution-free: it parses opcodes via `pickletools` and does not execute pickle payload semantics.

To run full unpickling behavior (unsafe for untrusted files), use:

```bash
python3 picklevis_core.py <pickle-file> --execute
```

Optional flags:

- `--verbose`: print opcode/offset details
- `-o/--output <path>`: choose the output HTML file path
