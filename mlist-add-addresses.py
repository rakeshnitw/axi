#! /usr/bin/env python
"""
Adds addresses from a a file (each line containing "email@address full name")
to a specific mailing list
"""

"""
Copyright (c) since 2006, GECAD Technologies. All rights reserved.
For feedback and/or bugs in this script, please send an e-mail to:
  "AXIGEN Team" <team@axigen.com>
"""
_CVSID = "$Id: mlist-add-addresses.py,v 1.2 2016/05/23 17:00:47 nini@qa1 Exp $"
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

    PARAMS = ["file", "domain", "mail-list"]
    PARAMSV = {"file": None, "domain": None, "mail-list": None}

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
    f = open(PARAMSV["file"], "r")
    c.goto_root_context()
    c.update_domain(PARAMSV["domain"])
    c.update_list(PARAMSV["mail-list"])
    for l in f:
        ls = l.strip()
        if len(ls) < 1:
            continue
        ls = ls.split()
        email = ls[0]
        if len(ls) > 1:
            name = " ".join(ls[1:])
        else:
            name = email
            print(
                'WARNING: address "%s" contains no name. Using the address as the display name.'
                % email,
                file=sys.stderr,
            )
        try:
            c.mlist_add_user(email, name)
        except:
            print(
                'WARNING: Failed to add address "%s" to mailing list' % email,
                file=sys.stderr,
            )
            continue
        c.done()
    c.commit()
