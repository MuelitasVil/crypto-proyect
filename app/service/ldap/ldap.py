from ldap3 import Server, Connection, SUBTREE, ALL
from hashlib import sha256
from app.utils.app_logger import AppLogger

logger = AppLogger(__file__, "ldap.log")


class User:
    def __init__(self, username, password, name, lastname, email):
        self.username = username
        self.password = password
        self.name = name
        self.lastname = lastname
        self.email = email


class LdapAdministrator:
    ldap_server = Server('localhost', port=389, get_info=ALL)
    ldap_user = 'cn=admin,dc=dned,dc=unal,dc=edu,dc=co'
    ldap_password = 'admin'

    # Conexion a la base de datos

    def get_conection_admin(self):
        try:
            logger.info("Attempting to connect to LDAP server as admin")
            ldap_connection = Connection(
                self.ldap_server,
                user=self.ldap_user,
                password=self.ldap_password,
                auto_bind=True,

            )
            print("Conexión exitosa al servidor LDAP")
            return ldap_connection
        except Exception as e:
            logger.error(f"Failed to connect to LDAP server as admin: {e}")
            print(f"No se pudo conectar al servidor LDAP: {e}")
            return None

    def get_conection_user(self, user_dn, password):
        try:
            ldap_connection = Connection(
                self.ldap_server,
                user=user_dn,
                password=password,
                auto_bind=True,

            )
            logger.info(
                f"User {user_dn} connected successfully to LDAP server"
            )
            return ldap_connection
        except Exception as e:
            logger.error(
                f"Failed to connect to LDAP server as user {user_dn}: {e}"
            )
            return None

    # Creacion de usuario

    def create_user(self, user: User):
        logger.info(f"Creating LDAP user with username: {user.username}")
        conn = self.get_conection_admin()

        if not conn:
            return {
                'respuesta': False,
                'Detail': "La conexion ha fracasado"
            }

        new_user_dn = (
            f'cn={user.username},cn=,dc=dned,dc=unal,dc=edu,dc=co'
        )

        if self.check_user_existence(user.username, conn):
            return {
                'respuesta': False,
                'Detail': "Usuario ya ha sido creado"
            }

        new_user_attributes = {
            'objectClass': ['inetOrgPerson', 'top'],
            'uid': user.username,
            'userPassword': self.get_hash_pass(user.password),
            'givenName': user.name,
            'sn': user.lastname,
            'mail': user.email
        }

        try:
            logger.info(f"Adding new LDAP user: {user.username}")
            response = conn.add(new_user_dn, attributes=new_user_attributes)
            if response:
                logger.info(f"LDAP user {user.username} created successfully")
                return {
                    'respuesta': True,
                    'Detail': "Usuario creado"
                }
            else:
                logger.error(f"Failed to create LDAP user: {user.username}")
                return {
                    'respuesta': False,
                    'Detail': "Usuario NO creado"
                }
        except Exception as e:
            logger.error(
                f"Exception occurred while creating LDAP user"
                f"{user.username}: {e}"
            )
            return {
                'respuesta': False,
                'Detail': e
            }

    # Verificar si el usuario existe

    def check_user_existence(self, username, conn=False):
        logger.info(f"Checking existence of LDAP user: {username}")
        if not conn:
            conn = self.get_conection_admin()

        user_dn = f'cn={username},cn=users,dc=dned,dc=unal,dc=edu,dc=co'

        try:
            logger.info(f"Searching for LDAP user: {username}")
            conn.search(search_base=user_dn,
                        search_filter='(objectClass=inetOrgPerson)',
                        search_scope=SUBTREE)
            if conn.entries:
                logger.info(
                    f"LDAP user {username} exists in the server"
                )
                return True
            else:
                logger.info(
                    f"LDAP user {username} does not exist in the server"
                )
                return False
        except Exception as e:
            logger.error(f"Failed to verify existence of LDAP user"
                         f" {username}: {e}")
            return True

    # Verificar la existencia del usuario

    def check_user_credentials(self, username, password):
        logger.info(f"Verifying credentials for LDAP user: {username}")
        conn = self.get_conection_admin()

        if not conn:
            logger.error("Admin connection to LDAP server failed")
            return {
                'respuesta': False,
                'Detail': "La conexion ha fracasado"
            }

        user_dn = f'cn={username},cn=users,dc=dned,dc=unal,dc=edu,dc=co'
        conn = self.get_conection_user(user_dn, self.get_hash_pass(password))

        if not conn:
            logger.error(f"Failed to authenticate LDAP user: {username}")
            return {
                'respuesta': False,
                'Detail': "Usuario o Contraseña incorrecto"
            }

        logger.info(f"LDAP user {username} authenticated successfully")
        return {
            'respuesta': True,
            'Detail': "Credenciales"
        }

    def delete_user(self, username):
        try:
            logger.info(f"Deleting LDAP user: {username}")
            conn = self.get_conection_admin()
            user_dn = f'cn={username},cn=users,dc=dned,dc=unal,dc=edu,dc=co'
            response = conn.delete(user_dn)
            if response:
                logger.info(f"LDAP user {username} deleted successfully")
            else:
                logger.info(
                    f"LDAP user {username} was not deleted successfully"
                )
        except Exception as e:
            logger.error(f"Failed to delete LDAP user {username}: {e}")

    def get_hash_pass(self, password):
        return sha256(password.encode('utf-8')).hexdigest()
