from flask import Flask, request, jsonify
import ldap_master_sync
import simplejson as json
from loguru import logger
import master_api_config

ldap_server = master_api_config.ldap_server

app = Flask(__name__)


def get_ldap_users(username, password, operator, operation):
    print(username, password)
    ldap_connection = ldap_master_sync.connect_ldap(ldap_server, username, password)
    users = ldap_master_sync.get_all_users_of_specific_ou(ldap_connection, operator, operation)
    return users


@app.route("/sync", methods=["POST"])
def auth():
    try:
        data = request.json
        logger.info(f"{request.remote_addr}-{data['binddn']}")
        users = get_ldap_users(data['binddn'], data['password'], data['operator'], data['operation'])
        return json.dumps(users)
    except Exception as e:
        logger.error(e)


if __name__ == '__main__':
    logger.info(f"connecting to ldap server:{ldap_server}")
    app.run(host='0.0.0.0', port=8080)
