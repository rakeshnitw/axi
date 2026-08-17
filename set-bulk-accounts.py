#! /usr/bin/env python
"""
Script that uses the CLI module to set a number of attributes for a bulk
account list.
"""

"""
Copyright (c) since 2007, GECAD Technologies. All rights reserved.
For feedback and/or bugs in this script, please send an e-mail to:
  "AXIGEN Team" <team@axigen.com>
"""
_CVSID = "$Id: set-bulk-accounts.py,v 1.5 2016/05/23 16:06:33 nini@qa1 Exp $"
if __name__ == "__main__":
    import sys

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

    def show_help():
        print(
            """
Basic usage:
  %s file=<accounts file> [host=<cli host>] \\
    [port=<cli port>] [debug=<debug level>] \\
    [pass=<admin password>] [[context]:setting=value]...

  Where, each parameter is:
  file - the filename containing each account per line, including @domain
  host - CLI host to connect to; default: localhost
  port - CLI port to connect ro; default: 7000
  debug - if set to 1 will display all the protocol communication over CLI
  pass - if specified, will use this password, otherwise will ask for one
  context:setting=value - for each account, you may specify one or multiple
        settings with this format.
  
  Context may be one of: webmaildata, quotas, limits, etc (anything that starts
  with "CONFIG" in the account context's HELP command), also you may specify an
  empty context to set attributes directly in the account

  Examples of usage
  - set the totalMessageSize quota setting to 100MB:
    %s file=myaccounts.txt host=<host> port=<port> quotas:totalMessageSize=102400

  - set the language to "de":
    %s file=myaccounts.txt host=<host> port=<port> webmaildata:language=de

  - reset the password:
    %s file=myaccounts.txt :passwd=<password>
  """
            % (sys.argv[0], sys.argv[0], sys.argv[0], sys.argv[0]),
            file=sys.stderr,
        )

    # defaults
    acctFile = None
    cliHost = None
    cliPort = None
    cliPass = None
    cliDebug = None

    sets = []
    for param in sys.argv[1:]:
        if param.startswith("file="):
            acctFile = param[5:]
            continue
        if param.startswith("host="):
            cliHost = param[5:]
            continue
        if param.startswith("port="):
            cliPort = param[5:]
            continue
        if param.startswith("pass="):
            cliPass = param[5:]
            continue
        if param.startswith("debug="):
            cliDebug = param[6:]
            continue
        if ":" not in param or "=" not in param:
            continue
        sets.append(param)
    if not len(sets):
        print("Nothing to set! Exiting...", file=sys.stderr)
        show_help()
        sys.exit(1)
    if cliHost == None:
        cliHost = "127.0.0.1"
    if cliPort == None:
        cliPort = "7000"
    if not cliPort.isdigit():
        print("Port must be a number", file=sys.stderr)
        sys.exit(1)
    cliPort = int(cliPort)
    try:
        fd = open(acctFile, "r")
    except:
        print(
            "Could not open accounts file (%s), or none specified" % acctFile,
            file=sys.stderr,
        )
        show_help()
        sys.exit(1)
    c = cli2.CLI(cliHost, cliPort)
    if not cliPass:
        import getpass

        while not cliPass:
            cliPass = getpass.getpass("Enter CLI Admin password: ")
            if not cliPass:
                print("Empty passwords are not allowed!", file=sys.stderr)
    sets.sort()
    if cliDebug == "1":
        cli2.CLI.debug = 1
    c.auth(cliPass, "admin")
    prevDomain = None
    lineNo = 0
    for line in fd:
        lineNo += 1
        acc_dom = line.strip().split("@")
        if len(acc_dom) != 2:
            print("Ignored line %d: %s" % (lineNo, line.strip()), file=sys.stderr)
            continue
        myAccount = acc_dom[0]
        myDomain = acc_dom[1]
        if myDomain != prevDomain:
            if prevDomain != None:
                c.commit()
            c.update_domain(myDomain)
            prevDomain = myDomain
        c.update_account(myAccount)
        prevContext = None
        for set in sets:
            eq_split = set.split("=")
            dc_split = eq_split[0].split(":")
            myContext = dc_split[0]
            mySetting = dc_split[1]
            myValue = eq_split[1]
            if myContext != prevContext:
                if prevContext != None and myContext != "":
                    c.done()
                if myContext != "":
                    c.config(myContext)
                prevContext = myContext
            c.set_data({mySetting: myValue})
            print(
                "Ok: %s->%s->%s->%s: %s"
                % (myDomain, myAccount, myContext, mySetting, myValue)
            )
        if myContext != "":
            c.done()
        c.commit()
    fd.close()
