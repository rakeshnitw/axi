#! /usr/bin/env python
"""
Adds a local account to a specified mailing list from the same local domain
"""

"""
Copyright (c) since 2006, GECAD Technologies. All rights reserved.
For feedback and/or bugs in this script, please send an e-mail to:
  "AXIGEN Team" <team@axigen.com>
"""
_CVSID = "$Id: mlist-add-user.py,v 1.3 2016/05/23 16:55:38 nini@qa1 Exp $"
if __name__ == "__main__":
    import sys, os

    sys.path.append(os.path.join(sys.path[0], "lib"))
    sys.path.append("/opt/axigen/scripts/lib")
    try:
        import cli2
    except ImportError:
        print("ERROR: AXIGEN CLI Module could not be imported.", file=sys.stderr)
        print(
            "Please place cli2.py in one of the following directories:", file=sys.stderr
        )
        for x in sys.path:
            print("-", x, file=sys.stderr)
        sys.exit(1)

    # defaults
    CLIHOST = "127.0.0.1"
    CLIPORT = 7000
    CLIUSER = "admin"
    CLIPASS = ""

    PARAMS = ["account", "domain", "full-name", "mail-list"]
    PARAMSV = {"account": None, "domain": None, "full-name": None, "mail-list": None}

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
    if "CLIDEBUG" in os.environ:
        if len(os.environ["CLIDEBUG"]) > 0:
            cli2.CLI.debug = 1

    if not CLIPASS:
        import getpass

        while not CLIPASS:
            CLIPASS = getpass.getpass("Enter CLI Admin password:")
            if not CLIPASS:
                print("Empty passwords are not allowed!", file=sys.stderr)
    c = cli2.CLI(CLIHOST, CLIPORT, CLIUSER, CLIPASS)
    if not c.hasDomain(PARAMSV["domain"]):
        print("ERROR: Domain does not exist in AXIGEN", file=sys.stderr)
        sys.exit(1)
    if not PARAMSV["account"] in c.getAccountsList(PARAMSV["domain"]):
        print(
            "WARNING: Account %s does not exist in domain %s"
            % (PARAMSV["account"], PARAMSV["domain"]),
            file=sys.stderr,
        )
    try:
        c.mListAddUser(
            PARAMSV["mail-list"],
            PARAMSV["domain"],
            PARAMSV["account"] + "@" + PARAMSV["domain"],
            PARAMSV["full-name"],
        )
    except:
        print("ERROR: Failed to add user to mailing list", file=sys.stderr)
        sys.exit(2)
