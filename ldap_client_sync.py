import ldap_master_sync
import requests
import simplejson as json
from loguru import logger
import ldap_client_sync_config

API_ENDPOINT = ldap_client_sync_config.API_ENDPOINT

master_bind_dn = ldap_client_sync_config.master_bind_dn
master_bind_pwd = ldap_client_sync_config.master_bind_pwd
operator = ldap_client_sync_config.operator
operation = ldap_client_sync_config.operation

ldap_server_2 = ldap_client_sync_config.local_ldap_server
ldap_bind_dn_2 = ldap_client_sync_config.local_ldap_bind_dn
ldap_bind_pwd_2 = ldap_client_sync_config.local_ldap_bind_pwd

data = {'binddn': master_bind_dn,
        'password': master_bind_pwd,
        'operator': operator,
        'operation': operation}

logger.info(f"Sending Request to {API_ENDPOINT}, with bind_dn={master_bind_dn}")
r = requests.post(url=API_ENDPOINT, json=data)
master_users = json.loads(r.text)
logger.debug(master_users)
logger.info(f"Received Request from {API_ENDPOINT}, users count:{len(master_users)}")

ldap_connection = ldap_master_sync.connect_ldap(ldap_server_2, ldap_bind_dn_2, ldap_bind_pwd_2)
local_users = ldap_master_sync.get_all_users_of_specific_ou(ldap_connection, operator, operation)

ldap_master_sync.comapre_sync_ldap(ldap_connection, master_users, local_users, operator, operation)
