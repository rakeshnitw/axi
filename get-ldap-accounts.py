#! /usr/bin/env python
"""
Queries a LDAP server for fetching a list of accounts and displaying them in a
specific format. Created and tested for Active Directory.
"""
"""
Copyright (c) since 2006, GECAD Technologies. All rights reserved.
For feedback and/or bugs in this script, please send an e-mail to:
  "AXIGEN Team" <team@axigen.com>
"""
_CVSID='$Id: get-ldap-accounts.py,v 1.3 2016/05/23 17:08:43 nini@qa1 Exp $'
if __name__=='__main__':
  import ldap, re, random, base64, sys, os

  # Read LDAP settings from environment variables or command-line arguments.
  # No static sample values are used; all connection details must be supplied
  # at runtime.
  ldapHost = os.environ.get('LDAP_HOST')
  ldapBindUser = os.environ.get('LDAP_BIND_USER')
  ldapBindPass = os.environ.get('LDAP_BIND_PASS')
  baseDN = os.environ.get('LDAP_BASE_DN')
  searchFilter = os.environ.get('LDAP_SEARCH_FILTER', '(objectClass=user)')
  accountAttributeName = os.environ.get('LDAP_ACCOUNT_ATTR', 'sAMAccountName')
  specialAccounts = []
  if os.environ.get('LDAP_SPECIAL_ACCOUNTS'):
    specialAccounts = [x.strip() for x in os.environ.get('LDAP_SPECIAL_ACCOUNTS').split(',') if x.strip()]
  specialAccountsMask = []
  if os.environ.get('LDAP_SPECIAL_ACCOUNTS_MASK'):
    specialAccountsMask = [x.strip() for x in os.environ.get('LDAP_SPECIAL_ACCOUNTS_MASK').split(',') if x.strip()]

  def printEntry(entry):
    print("# %s" % dn)
    for attr in entry:
      for k in range(len(entry[attr])):
        print(attr+':', repr(entry[attr][k]))
    print()
    print()

  domain=''
  generatePasswords=False
  if len(sys.argv)>1:
    for arg in sys.argv[1:]:
      if arg.lower().startswith('domain='):
        domain='@'+arg[7:]
      elif arg.lower()=='-p':
        generatePasswords=True
      elif arg.lower().startswith('host='):
        ldapHost=arg[5:]
      elif arg.lower().startswith('binduser='):
        ldapBindUser=arg[9:]
      elif arg.lower().startswith('bindpass='):
        ldapBindPass=arg[9:]
      elif arg.lower().startswith('basedn='):
        baseDN=arg[7:]
      elif arg.lower().startswith('filter='):
        searchFilter=arg[7:]
      elif arg.lower().startswith('attr='):
        accountAttributeName=arg[5:]
      elif arg.lower().startswith('exclude='):
        specialAccounts=[x.strip() for x in arg[8:].split(',') if x.strip()]
      elif arg.lower().startswith('excludemask='):
        specialAccountsMask=[x.strip() for x in arg[12:].split(',') if x.strip()]
      elif arg.lower() in ['-h', '/?', '--help']:
        print("AXIGEN LDAP Query Helper")
        print("Usage: %s [-h|--help|/?] [domain=<domain>] [-p] [host=<ldap host>] [binduser=<bind user>] [bindpass=<bind password>] [basedn=<base DN>] [filter=<search filter>] [attr=<account attribute>] [exclude=<comma-separated accounts>] [excludemask=<comma-separated regexes>]" % os.path.basename(sys.argv[0]))
        print("       -h | --help | /? -> print this help")
        print("       -p               -> print a tab delimited password field")
        print("                           (password is base64 encoded of a 16 character")
        print("                           random string)")
        print("       domain=<domain>  -> a @<domain> string will be appended to each")
        print("                           printed user")
        print("                           (useful for the import-accounts.py script)")
        print("       host=<ldap host> -> LDAP server host or IP")
        print("       binduser=<user>  -> LDAP bind user DN")
        print("       bindpass=<pass>  -> LDAP bind password")
        print("       basedn=<DN>      -> base DN for the search")
        print("       filter=<filter>  -> LDAP search filter (default: (objectClass=user))")
        print("       attr=<attr>      -> account attribute name (default: sAMAccountName)")
        print("       exclude=<list>   -> comma-separated list of accounts to exclude")
        print("       excludemask=<list> -> comma-separated list of regex masks to exclude")
        print("     Environment variables LDAP_HOST, LDAP_BIND_USER, LDAP_BIND_PASS,")
        print("     LDAP_BASE_DN, LDAP_SEARCH_FILTER, LDAP_ACCOUNT_ATTR,")
        print("     LDAP_SPECIAL_ACCOUNTS and LDAP_SPECIAL_ACCOUNTS_MASK are also supported.")
        sys.exit()

  if not ldapHost or not ldapBindUser or not ldapBindPass or not baseDN:
    print("ERROR: LDAP host, bind user, bind password and base DN are required.", file=sys.stderr)
    print("       Provide them as command-line arguments or environment variables.", file=sys.stderr)
    sys.exit(1)

  l=ldap.initialize('ldap://%s' % ldapHost)
  l.simple_bind(ldapBindUser, ldapBindPass)
  searchScope = ldap.SCOPE_SUBTREE
  retrieveAttributes = None 
  ldap_result_id = l.search(baseDN, searchScope, searchFilter, retrieveAttributes)
  result_set = []
  while 1:
    result_type, result_data = l.result(ldap_result_id, 0)
    if (result_data == []):
      break
    else:
      if result_type == ldap.RES_SEARCH_ENTRY:
        result_set.append(result_data)
  for i in result_set:
    for j in i:
      dn=j[0]
      dbentry=j[1]; # dictionary
      acctName=dbentry[accountAttributeName][0]
      if acctName in specialAccounts:
        continue
      matched=False
      for sme in specialAccountsMask:
        m=re.compile(sme)
        if m.match(acctName):
          matched=True
          break
      if matched:
        continue
      p=''
      if generatePasswords:
        for k in range(16):
          p+=chr(random.randint(1,254))
        p='\t'+base64.b64encode(p.encode('latin-1')).decode('ascii')
      print(acctName+domain+p)
