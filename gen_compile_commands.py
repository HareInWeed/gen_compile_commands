import json
import argparse
import sys
import re
import shlex
import subprocess
from subprocess import Popen
from pathlib import Path
from textwrap import dedent
from enum import Enum
from enum import auto as enumAuto

gnuParser = argparse.ArgumentParser(
    description='parse gnu toolkits commands')
gnuParser.add_argument('sources', nargs='*')


class LOG_LEVEL(Enum):
    INFO = enumAuto()
    WARNING = enumAuto()
    ERROR = enumAuto()


def log(msg, level=LOG_LEVEL.INFO):
    dist = {
        LOG_LEVEL.ERROR: sys.stderr,
    }.get(level, sys.stdout)

    print(msg, file=dist)


def echo(obj):
    """ for debugging """
    print(obj)
    return obj


invalidFilenameChars = re.compile('[<>:"/?*\\|]')


def is_valid_filename(filename):
    return invalidFilenameChars.search(filename) == None


if __name__ == "__main__":
    argsParser = argparse.ArgumentParser(
        description='generate compile_commands.json.')
    argsParser.add_argument('-f', '--makefile', default=None,
                            help="specify makefile, leave it empty to parse the makefile under current folder")
    argsParser.add_argument('-c', '--compilers', nargs='*',
                            default=['gcc', 'g++', 'clang', 'clang++'],
                            help="specify the compiler executable names")

    args = argsParser.parse_args()

    compilers = args.compilers

    currentDir = Path().resolve()
    makefile = Path(
        args.makefile if args.makefile is not None else './makefile')

    targets = set()

    with makefile.open('r') as mf:
        for line in mf:
            result = re.search(r'^\s*(\w+)\s*:.*$', line)
            if result is not None:
                # print(result.group(1))
                targets.add(result.group(1))

    compileCmds = {}

    for target in targets:
        makeCmd = ['make', target, '--just-print', 'GEN_COMPILE_COMMANDS=true']
        if args.makefile is not None:
            makeCmd = [*makeCmd, '-f', args.makefile]
        output = Popen(makeCmd, stdout=subprocess.PIPE).communicate()[
            0].decode("utf-8").split('\n')
        for command in output:
            # fix utf-8 bom issue in windows shell
            command = re.sub('^\ufeff', '', command)
            command = re.sub(r'^\s+|\s+$', '', command)
            commandSeg = shlex.split(command)
            if len(commandSeg) == 0:
                continue
            if commandSeg[0] in compilers:
                info, _ = gnuParser.parse_known_args(commandSeg[1:])
                for source in info.sources:
                    if not is_valid_filename(source):
                        log(dedent(f'''\
                            filename "{source}" in command
                                {command}
                            is not a valid filename.
                            skip this command.

                            '''), LOG_LEVEL.ERROR)
                        continue
                    if source not in compileCmds:
                        try:
                            compileCmds[source] = {
                                "directory": str(currentDir.resolve()),
                                "command": command,
                                "file": str((currentDir / source).resolve())
                            }
                        except OSError as err:
                            log(dedent(f'''\
                            during parsing of command
                                {command}
                            an error ocurred:
                                {err}
                            skip this command.

                            '''), LOG_LEVEL.ERROR)

    with Path('./compile_commands.json').open('w+') as resultFile:
        print(json.dumps([*compileCmds.values()], indent=4), file=resultFile)
