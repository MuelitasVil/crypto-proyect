from ldap3 import Server, Connection, SUBTREE, ALL
from hashlib import sha256


class User:
    def __init__(self, username, password, name, lastname, email):
        self.username = username
        self.password = password
        self.name = name
        self.lastname = lastname
        self.email = email


class LdapAdministrator:
    ldap_server = Server('host.docker.internal', port=389, get_info=ALL)
    ldap_user = 'cn=admin,dc=dned,dc=unal,dc=edu,dc=co'
    ldap_password = 'admin'

    # Conexion a la base de datos

    def get_conection_admin(self):
        try:
            ldap_connection = Connection(
                self.ldap_server,
                user=self.ldap_user,
                password=self.ldap_password,
                auto_bind=True,

            )
            print("Conexión exitosa al servidor LDAP")
            return ldap_connection
        except Exception as e:
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
            print("Conexión exitosa al servidor LDAP")
            return ldap_connection
        except Exception as e:
            print(f"No se pudo conectar al servidor LDAP: {e}")
            return None

    # Creacion de usuario

    def create_user(self, user: User):
        conn = self.get_conection_admin()

        if not conn:
            return {
                'respuesta': False,
                'Detail': "La conexion ha fracasado"
            }

        new_user_dn = (
            f'cn={user.username},cn=users,dc=dned,dc=unal,dc=edu,dc=co'
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
            response = conn.add(new_user_dn, attributes=new_user_attributes)
            if response:
                return {
                    'respuesta': True,
                    'Detail': "Usuario creado"
                }
            else:
                return {
                    'respuesta': False,
                    'Detail': "Usuario NO creado"
                }
        except Exception as e:
            return {
                'respuesta': False,
                'Detail': e
            }

    # Verificar si el usuario existe

    def check_user_existence(self, username, conn=False):
        if not conn:
            conn = self.get_conection_admin()

        user_dn = f'cn={username},cn=users,dc=dned,dc=unal,dc=edu,dc=co'

        try:
            conn.search(search_base=user_dn,
                        search_filter='(objectClass=inetOrgPerson)',
                        search_scope=SUBTREE)
            if conn.entries:
                print("El usuario existe en el servidor LDAP")
                return True
            else:
                print("El usuario no existe en el servidor LDAP")
                return False
        except Exception as e:
            print(f"No se pudo verificar la existencia del usuario: {e}")
            return True

    # Verificar la existencia del usuario

    def check_user_credentials(self, username, password):

        conn = self.get_conection_admin()

        if not conn:
            return {
                'respuesta': False,
                'Detail': "La conexion ha fracasado"
            }

        user_dn = f'cn={username},cn=users,dc=dned,dc=unal,dc=edu,dc=co'
        conn = self.get_conection_user(user_dn, self.get_hash_pass(password))

        if not conn:
            return {
                'respuesta': False,
                'Detail': "Usuario o Contraseña incorrecto"
            }

        return {
            'respuesta': True,
            'Detail': "Credenciales"
        }

    def delete_user(self, username):
        try:
            conn = self.get_conection_admin()
            user_dn = f'cn={username},cn=users,dc=dned,dc=unal,dc=edu,dc=co'
            response = conn.delete(user_dn)
            if response:
                print("Usuario eliminado exitosamente")
            else:
                print("Usuario No ha sido eliminado exitosamente")
        except Exception as e:
            print(f"No se pudo eliminar el usuario: {e}")

    def get_hash_pass(self, password):
        return sha256(password.encode('utf-8')).hexdigest()
