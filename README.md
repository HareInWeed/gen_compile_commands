# `compile_commands.json` generator

generate `compile_commands.json` from makefile for clangd

Basically, it iterates makefile to find every target, run `make target --print-all GEN_COMPILE_COMMANDS=true` for each one, parse outputs to collect all the compile commands, and write each command into `compile_commands.json` with the format required by clangd

## Usage

```plaintext
usage: gen_compile_commands.py [-h] [-f MAKEFILE] [-c [COMPILERS [COMPILERS ...]]]

generate compile_commands.json.

optional arguments:
  -h, --help            show this help message and exit
  -f MAKEFILE, --makefile MAKEFILE
                        specify makefile, leave it empty to parse the makefile under current folder
  -c [COMPILERS [COMPILERS ...]], --compilers [COMPILERS [COMPILERS ...]]
                        specify the compiler executable names
```