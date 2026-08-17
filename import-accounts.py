#! /usr/bin/env python
"""
Imports accounts from a specified file, one account per line.
"""

"""
Copyright (c) since 2006, GECAD Technologies. All rights reserved.
For feedback and/or bugs in this script, please send an e-mail to:
  "AXIGEN Team" <team@axigen.com>
"""
_CVSID = "$Id: import-accounts.py,v 1.7 2016/05/23 16:38:17 nini@qa1 Exp $"
if __name__ == "__main__":
    import sys, os

    sys.path.append(os.path.join(sys.path[0], "lib"))
    sys.path.append("lib")
    sys.path.append("/opt/axigen/scripts/lib")
    try:
        import cli2
    except ImportError:
        print("ERROR: AXIGEN CLI Module could not be imported.", file=sys.stderr)
        print(
            "Please place cli.py in one of the following directories:", file=sys.stderr
        )
        for x in sys.path:
            print("-", x, file=sys.stderr)
        sys.exit(1)

    # defaults
    CLIHOST = "127.0.0.1"
    CLIPORT = 7000
    CLIUSER = "admin"
    CLIPASS = ""

    PARAMS = ["accounts-file"]
    PARAMSV = {"accounts-file": None}

    if len(sys.argv) < len(PARAMS) + 1:
        sys.stderr.write("Usage: %s " % sys.argv[0])
        for p in PARAMS:
            sys.stderr.write("<%s> " % p)
        sys.stderr.write("[admin-passwd [cli-host[:port]]]")
        print(file=sys.stderr)
        sys.exit(255)
    for i in range(1, len(PARAMS) + 1):
        PARAMSV[PARAMS[i - 1]] = sys.argv[i]
    if len(sys.argv) >= len(PARAMS) + 2:
        CLIPASS = sys.argv[len(PARAMS) + 1]
    if len(sys.argv) >= len(PARAMS) + 3:
        CLIHOST = sys.argv[len(PARAMS) + 2]
    if ":" in CLIHOST:
        try:
            CLIPORT = int(CLIHOST.split(":")[1])
        except ValueError:
            print("Error: Non-numeric CLI port passed as parameter", file=sys.stderr)
            sys.exit(1)
        CLIHOST = CLIHOST.split(":")[0]
    if not CLIPASS:
        import getpass

        while not CLIPASS:
            CLIPASS = getpass.getpass("Enter CLI Admin password:")
            if not CLIPASS:
                print("Empty passwords are not allowed!", file=sys.stderr)

    if "CLIDEBUG" in os.environ:
        if len(os.environ["CLIDEBUG"]) > 0:
            cli2.CLI.debug = 1

    accounts = []
    f = open(PARAMSV["accounts-file"], "r")
    lines = f.readlines()
    f.close()
    for l in lines:
        l = l.strip()
        if len(l) == 0:
            continue
        lpair = l.split("\t")
        if len(lpair) < 2:
            print(
                "!! No password field found. Please TAB-delimit the password field on the same line as the account address",
                file=sys.stderr,
            )
            continue
        laddr = lpair[0]
        lpass = lpair[1]
        if laddr.count("@") != 1:
            print("!! Invalid address format:", l, file=sys.stderr)
            continue
        accounts.append([laddr, lpass])
    c = cli2.CLI(CLIHOST, CLIPORT, CLIUSER, CLIPASS)
    for accpas in accounts:
        acct = accpas[0]
        passwd = accpas[1]
        name = acct.split("@")[0].lower()
        dom = acct.split("@")[1].lower()
        if not c.hasDomain(dom):
            print("!! Domain does not exist for:", acct, file=sys.stderr)
            continue
        if name in c.getAccountsList(dom):
            print("!! Account already exists:", acct, file=sys.stderr)
            continue
        try:
            c.addAccount(dom, name, passwd)
        except:
            print("!! Failed to add account:", acct, file=sys.stderr)
            continue
        print("Account added:", acct)
