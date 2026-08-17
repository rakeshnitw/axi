#! /usr/bin/env python
"""
Script that searches for patterns in each account personal data. Search is
being done in the attribute names. For example, searching for businessAddress
will return all the accounts, because all of them contain this keyword as
attribute.

Copyright (c) since 2007, GECAD Technologies. All rights reserved.
For feedback and/or bugs in this script, please send an e-mail to:
  "AXIGEN Team" <team@axigen.com>
"""
_CVSID='$Id: search-details.py,v 1.3 2016/05/23 16:54:29 nini@qa1 Exp $'
if __name__=='__main__':
  import sys
  sys.path.append(os.path.join(sys.path[0],'lib'))
  sys.path.append('/opt/axigen/scripts/lib')
  try:
    import cli2
  except ImportError:
    print('ERROR: AXIGEN CLI Module could not be imported.', file=sys.stderr)
    print('Please place cli2.py in one of the following directories:', file=sys.stderr)
    for x in sys.path:
      print('-',x, file=sys.stderr)
    sys.exit(1)

  def show_help():
    print("""
Basic usage:
  %s pattern=<pattern-to-search-for> \\
    [host=<cli host>] [port=<cli port>] [pass=<admin password>] \\
    [debug=<debug level>]

  Where, each parameter is:
  pattern - the pattern to search for
  host    - CLI host to connect to; default: localhost
  port    - CLI port to connect to; default: 7000
  pass    - if specified, will use this password, otherwise will ask for one
  debug   - if set to 1 will display all the protocol communication over CLI
  """ % (sys.argv[0]), file=sys.stderr)

  #defaults
  pattern=None
  cliHost=None
  cliPort=None
  cliPass=None
  cliDebug=None

  for param in sys.argv[1:]:
    if param.startswith('pattern='):
      pattern=param[8:]
      continue
    if param.startswith('host='):
      cliHost=param[5:]
      continue
    if param.startswith('port='):
      cliPort=param[5:]
      continue
    if param.startswith('pass='):
      cliPass=param[5:]
      continue
    if param.startswith('debug='):
      cliDebug=param[6:]
      continue
  if not pattern:
    print("ERROR: Missing pattern", file=sys.stderr)
    show_help()
    sys.exit(1)
  if cliHost==None:
    cliHost="127.0.0.1"
  if cliPort==None:
    cliPort="7000"
  if not cliPort.isdigit():
    print("Port must be a number", file=sys.stderr)
    sys.exit(1)
  cliPort=int(cliPort)
  c=cli2.CLI(cliHost, cliPort)
  if not cliPass:
    import getpass
    while not cliPass:
      cliPass=getpass.getpass('Enter CLI Admin password: ')
      if not cliPass:
        print('Empty passwords are not allowed!', file=sys.stderr)
  if cliDebug=="1":
    cli2.CLI.debug=1
  c.auth(cliPass, "admin")
  domains=c.get_domains()
  for domain in domains:
    try:
      c.update_domain(domain)
    except:
      print("ERROR: Could not enter context for domain `%s`" % domain, file=sys.stderr)
      continue
    accounts=c.get_accounts()
    for account in accounts:
      try:
        c.update_account(account)
      except:
        print("ERROR: Could not enter account context for: `%s@%s`" % (account, domain), file=sys.stderr)
        continue
      cinfo=c.show_contactinfo()
      matches=[]
      for line in cinfo.split(cli2.CRLF)[2:-3]:
        if pattern.lower() in line.lower():
          matches.append(line)
      if len(matches)>0:
        for match in matches:
          print("%s@%s: %s" % (account, domain, match))
      c.back()
    c.back()
