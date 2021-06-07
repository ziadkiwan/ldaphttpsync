import ldap
import ldap.modlist as modlist
import json
from loguru import logger


def connect_ldap(ldap_ip, binddn, bindpassword):
    logger.info(f"Connecting to ldap:{ldap_ip} with bind_dn={binddn}")
    try:
        connect = ldap.initialize(ldap_ip)
        connect.set_option(ldap.OPT_REFERRALS, 0)
        connect.simple_bind_s(binddn, bindpassword)
        return connect
    except Exception as e:
        logger.error(e)


def get_all_users_of_specific_ou(ldap_connection, operator=None, operation=None):
    logger.info(f"Getting all users operator:{operator} operation:{operation}")
    try:
        filter = f"(&(objectClass=posixAccount)(operator={operator})(operation={operation}))"
        result = ldap_connection.search_s('dc=montyldap,dc=com',
                                          ldap.SCOPE_SUBTREE, filter)
        logger.debug(result)
        logger.info(f"users Count: {len(result)}")
        return result
    except Exception as e:
        logger.error(e)


def create_ou(ldap_connection, ou_dn, ou_name):
    try:
        ou_name = ou_name.encode('utf-8')
        attr = {'objectClass': ['organizationalUnit'.encode('utf-8'), 'top'.encode('utf-8')], 'ou': ou_name}
        ldif = modlist.addModlist(attr)
        ldap_connection.add_s(ou_dn, ldif)
        logger.info(ou_dn + "-Added")
    except Exception as e:
        logger.error(e)


def delete_user(ldap_connection, user_dn):
    try:
        ldap_connection.delete_s(user_dn)
        logger.info(user_dn + "-deleted")
    except Exception as e:
        logger.error(e)


def add_user(ldap_connection, user):
    try:
        ldif = modlist.addModlist(user[1])
        ldap_connection.add_s(user[0], ldif)
        logger.info(user[0] + "-added")
    except ldap.ALREADY_EXISTS as e:
        logger.info(user[0] + "-ALREADY_EXISTS")
        delete_user(ldap_connection, user[0])
        add_user(ldap_connection, user)
    except ldap.NO_SUCH_OBJECT as e:
        logger.info(user[0] + "-CREATING_OU")
        dn_split = user[0].split(',')[1:]
        create_ou(ldap_connection, ",".join(dn_split), dn_split[0].split('=')[1])
        add_user(ldap_connection, user)
    except Exception as e:
        logger.error(e)


def comapre_sync_ldap(ldap_connection, master_ldap_users, local_ldap_users, operator, operation):
    logger.info("~~~~~Syncing USERS~~~~~")
    for i in range(len(master_ldap_users)):
        master_ldap_users[i][1] = {key: [v.encode("utf-8") if type(v) == str else v for v in values] for key, values in
                                   master_ldap_users[i][1].items()}
        master_ldap_users[i] = tuple(master_ldap_users[i])

    for master_user in master_ldap_users:
        if master_user not in local_ldap_users:
            add_user(ldap_connection, master_user)

    local_ldap_users = get_all_users_of_specific_ou(ldap_connection, operator, operation)
    for local_user in local_ldap_users:
        if local_user not in master_ldap_users:
            delete_user(ldap_connection, local_user[0])
    logger.info("~~~~~Done Sync USERS~~~~~")

### TESTING ONLY 
# ldap_connection = connect_ldap(ldap_server, ldap_bind_dn, ldap_bind_pwd)
# master_users = get_all_users_of_specific_ou(ldap_connection)
# print("~~~~~MASTER USERS~~~~~")
# for dn, _ in master_users:
#     print(dn)
#
# ldap_connection_2 = connect_ldap(ldap_server_2, ldap_bind_dn_2, ldap_bind_pwd_2)
# local_users = get_all_users_of_specific_ou(ldap_connection_2)
# print("~~~~~LOCAL USERS~~~~~")
# for dn, _ in local_users:
#     print(dn)
#
# comapre_sync_ldap(ldap_connection_2, master_users, local_users)
