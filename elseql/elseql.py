#!/usr/bin/env python
# Copyright (c) 2012 Raffaele Sena https://github.com/raff
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, dis-
# tribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the fol-
# lowing conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABIL-
# ITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
# SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, 
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS

#
# A SQL-like command line tool to query ElasticSearch
#

if __name__ == '__main__':
    import sys
    if '--cmd2' in sys.argv:
        _CMD2_REQUIRED = True
        sys.argv.remove('--cmd2')
    else:
        _CMD2_REQUIRED = False

try:
    import cmd2 as cmd
except ImportError:
    if _CMD2_REQUIRED:
        print ""
        print "cmd2 is not installed: please install and try again"
        print ""
        raise
    else:
        import cmd

import shlex
import pprint
import traceback

from parser import ElseParser, ElseParserException
from search import ElseSearch, DEFAULT_PORT

class DebugPrinter:
    def write(self, s):
        print s

class ElseShell(cmd.Cmd):

    prompt = "elseql> "

    def __init__(self, port, debug):
        cmd.Cmd.__init__(self)
        self.search = ElseSearch(port, debug)

    def getargs(self, line):
        return shlex.split(str(line.decode('string-escape')))

    def do_keywords(self, line):
        print self.search.get_keywords()

    def do_select(self, line):
        self.search.search('select ' + line)

    def do_explain(self, line):
        self.search.search(line, explain=True)

    def do_EOF(self, line):
        "Exit shell"
        return True

    def do_shell(self, line):
        "Shell"
        os.system(line)

    #
    # override cmd
    #

    def emptyline(self):
        pass

    def onecmd(self, s):
        try:
            return cmd.Cmd.onecmd(self, s)
        except:
            traceback.print_exc()
            return False

    def default(self, line):
        line = line.strip()
        if line and line[0] in ['#', ';']:
            return False
        else:
            return cmd.Cmd.default(self, line)

    def completedefault(self, test, line, beginidx, endidx):
        list = []

        for k in self.search.get_keywords():
            if k.startswith(test):
                list.append(k)

        return list

    def postloop(self):
        print "Goodbye!"

def run_command():
    import sys

    args = sys.argv
    progname = args.pop(0)
    debug = False

    port = DEFAULT_PORT

    while args:
        if args[0][0] == '-':
            arg = args.pop(0)

            if arg.startswith('--port=') or arg.startswith('--host='):
                port = arg[7:]

            elif arg == '--debug':
                debug = True

            elif arg == '--':
                break

            else:
                print "invalid argument ", arg
                return 1
        else:
            break

    ElseShell(port, debug).cmdloop()

if __name__ == "__main__":
    run_command()
