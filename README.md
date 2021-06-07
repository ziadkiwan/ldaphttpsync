### Ldap Http Sync

syncs master openldap server users with any slave openldap server over http, , usefull if you are behind an http proxy and want to achieve centralized authentication.


#### Installation and Configuration:

`ldap_master_api.py` is a flask api server which receives a bind_dn and password request over the `/sync` end-point
authenticate with master ldap, once authenticated it will return all the users, this script should be somewhere
reachable by the master openldap server,
`ldap_master_api_config.py` contains configurations, `ldap_server = 'ldap://ipaddress'` is the master server that the
api server needs to query and authentication to get the users.

`ldap_client_sync.py` send a request to the api to get user and then syncs the users with the local ldap server this
script should be deployed on the client ldap server behind the http proxy.`ldap_client_sync_config.py` contains the
following configuration:

```python
API_ENDPOINT = "http://master_api_ip/sync"  # API server IP

master_bind_dn = 'cn=ldapadm,dc=example,dc=com'  # Master Server Bind DN
master_bind_pwd = 'admin'  # Master Server Bind PW
operator = '1111'  # Operator Name
operation = 'test'  # Operation Name

local_ldap_server = 'ldap://local_ldap_ip'  # Slave (local) Ldap Server
local_ldap_bind_dn = 'cn=admin,dc=example,dc=com'  # Slave (local) Server Bind DN
local_ldap_bind_pwd = 'admin'  # Slave (local) Server Bind DN
```

**Note:** we use operator and operation to filter out our operations, so we don't return all the users that we have on
our ldap server. if you want to change the filter you need to edit

```python 
filter = f"(&(objectClass=posixAccount)(operator={operator})(operation={operation}))"
```

insde the `ldap_master_sync.py` script, and change the api request body to match your requirements.

`ldap_master_sync.py` is the interface to the ldap server we use it to apply all the logic there, it needs to be on the
Master Api server and on the slave in the same directory.

#### Required Dependencies:

```shell
pip install simplejson
pip install loguru
pip install python-ldap
pip install flask
pip install requests
```

#### Adding Operator and Operation Attributes to openldap:

create an `attributes.ldif` file with the following content:

```shell
dn: cn=operations,cn=schema,cn=config
objectClass: olcSchemaConfig
cn: operations
olcAttributeTypes: ( 1.2.840.113556.1.4.221
    NAME 'operator'
    EQUALITY caseIgnoreMatch
    SYNTAX '1.3.6.1.4.1.1466.115.121.1.15' )
olcAttributeTypes: ( 1.2.840.113556.1.4.222
    NAME 'operation'
    EQUALITY caseIgnoreMatch
    SYNTAX '1.3.6.1.4.1.1466.115.121.1.15' )
olcObjectClasses: ( 1.3.6.1.4.1.4203.666.100.1
    NAME 'operations'
    SUP posixAccount
    AUXILIARY
    DESC 'Our operations at the operator side'
    MAY (operator $ operation))
```

apply the LDIF file using:

```shell
 ldapadd -vvv -Y EXTERNAL -H ldapi:/// -f attributes.ldif 
```

each account you want to use should have `operations` as object class or else it won't have the custom attributes.
