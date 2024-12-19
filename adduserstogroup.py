# Import necessary modules
import argparse
import sys
from ldap3 import Server, Connection, ALL, NTLM, MODIFY_ADD, MODIFY_REPLACE, MODIFY_DELETE

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Add a user to an Active Directory group.')
parser.add_argument('-d','--domain', required=True, help='The domain name of the Active Directory server.')
parser.add_argument('-g','--group', required=True, help='The name of the group to add the user to.')
parser.add_argument('-a','--adduser', required=True, help='The username of the user to add.')
parser.add_argument('-u','--user', required=True, help='The username of an Active Directory user with AddMember privilege.')
parser.add_argument('-p','--password', required=True, help='The password of the Active Directory user.')
args = parser.parse_args()

# Extract values from command-line arguments
domain_name = args.domain
group_name = args.group
user_name = args.adduser
ad_username = args.user
ad_password = args.password

# Construct the search base from the domain name
search_base = 'dc=' + ',dc='.join(domain_name.split('.'))

# Create a connection to the Active Directory server
server = Server(domain_name, get_info=ALL)
conn = Connection(
    server,
    user=f'{domain_name}\\{ad_username}',
    password=ad_password,
    authentication=NTLM
)

# Bind to the server with the given credentials
if conn.bind():
    print('[+] Connected to Active Directory successfully.')
else:
    print('[-] Error: failed to bind to the Active Directory server.')
    sys.exit(1)

# Search for the group with the given name
conn.search(
    search_base=search_base,
    search_filter=f'(&(objectClass=group)(cn={group_name}))',
    attributes=['member']
)

# Check if the group was found
if conn.entries:
    print('[+] Group ' + group_name + ' found.')
else:
    print('[-] Error: group not found.')
    sys.exit(1)

# Extract the group's DN and member list
group_dn = conn.entries[0].entry_dn
members = conn.entries[0].member.values

# Search for the user with the given username
conn.search(
    search_base=search_base,
    search_filter=f'(&(objectClass=user)(sAMAccountName={user_name}))',
    attributes=['distinguishedName']
)

# Check if the user was found
if conn.entries:
    print('[+] User ' + user_name + ' found.')
else:
    print('[-] Error: user not found.')
    sys.exit(1)

# Extract the user's DN
user_dn = conn.entries[0].distinguishedName.value

# Check if the user is already a member of the group
if user_dn in members:
    print('[+] User is already a member of the group.')
else:
    # Add the user to the group
    if conn.modify(
        dn=group_dn,
        changes={'member': [(MODIFY_ADD, [user_dn])]}
    ):
        print('[+] User added to group successfully.')
    else:
        print('[-] There was an error trying to add the user to the group.')
