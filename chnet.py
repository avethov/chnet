import winreg
import re
import pymssql
import _mssql
import sys
import getopt
import decimal
import uuid


HKCU_NETINTERFACE = r'Software\ELVEES\Orwell 2K'
HKLM_NETINTERFACE = r'SOFTWARE\ELVEES\Orwell'
DB_INIT_STRING = r'SOFTWARE\ELVEES\Common'

def get_old_server_ip():
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                             HKLM_NETINTERFACE,
                             0,
                             (winreg.KEY_READ + winreg.KEY_WOW64_64KEY))
        try:
            (old_server_ip_hklm, ktype) = winreg.QueryValueEx(key,
                                                              'NetInterface')
            if ktype is not winreg.REG_SZ:
                raise ValueError
        finally:
            key.Close()
    except OSError as error:
        print(error)

    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             HKCU_NETINTERFACE,
                             0,
                             (winreg.KEY_ALL_ACCESS + winreg.KEY_WOW64_64KEY))
        try:
            (old_server_ip_hkcu, ktype) = winreg.QueryValueEx(key,
                                                              'NetInterface')
            if ktype is not winreg.REG_SZ:
                raise ValueError
        finally:
            key.Close()
    except OSError as error:
        print(error)

    if old_server_ip_hklm == old_server_ip_hkcu:
        return old_server_ip_hklm
    else:
        raise ("Values of NetInterface are different")


def change_registry_netinterface(new_server_ip):
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                             HKLM_NETINTERFACE,
                             0,
                             (winreg.KEY_ALL_ACCESS + winreg.KEY_WOW64_64KEY))
        winreg.SetValueEx(key,
                          'NetInterface',
                          0,
                          winreg.REG_SZ,
                          new_server_ip)
        print(r'HKLM\SOFTWARE\ELVEES\Orwell\NetInterface was changed')
    except OSError as error:
        print(error)

    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             HKCU_NETINTERFACE,
                             0,
                             (winreg.KEY_ALL_ACCESS + winreg.KEY_WOW64_64KEY))
        winreg.SetValueEx(key,
                          'NetInterface',
                          0,
                          winreg.REG_SZ,
                          new_server_ip)
        print(r'HKCU\Software\ELVEES\Orwell 2K\NetInterface was changed')
    except OSError as error:
        print(error)


def get_db_connection_settings():
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                             DB_INIT_STRING,
                             0,
                             winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
        try:
            (init_string, ktype) = winreg.QueryValueEx(key,
                                                         'DBInitString')
            if ktype is not winreg.REG_SZ:
                raise ValueError
        finally:
            key.Close()
    except OSError as error:
        print(error)

    catalog = re.search(r'(?<=Initial Catalog=)([a-zA-Z0-9_]+)',
                        init_string)
    source = re.search(r'(?<=Data Source=)([a-zA-Z0-9\.()\\]+)',
                       init_string)

    return source.group(1), catalog.group(1)


def connect_db(server,
               catalog):
    host = server
    user = r'OrwellSAdmin'
    password = r't*e_AVafrEzUtaTha2rEmUJE@ew#xaze'
    database = catalog

    try:
        conn = pymssql.connect(host,
                               user,
                               password,
                               database)
    except _mssql.MssqlDatabaseException as error:
        raise

    return conn


def update_server_ip(sql_handle,
                     old_server_ip,
                     new_server_ip):
    cursor = sql_handle.cursor()
    cursor.execute('UPDATE Servers SET ServerIP=%s WHERE ServerIP=%s',
                   (new_server_ip, old_server_ip))

    sql_handle.commit()
    print(r'ServerIP in database was changed')

    cursor.execute('SELECT * FROM Servers')

    sql_handle.close()


def usage():
    usage = """
-h, --help      Show options
-i, --interface	New server ip address.
    """
    print(usage)


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hi:", ["help", "interface="])
    except getopt.GetoptError as err:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-i", "--interface"):
            new_server_ip = arg
        else:
            assert False, "Unsupported option"

    old_server_ip = get_old_server_ip()

    change_registry_netinterface(new_server_ip)

    (server, catalog) = get_db_connection_settings()

    sql_handle = connect_db(server,
                            catalog)

    update_server_ip(sql_handle,
                     old_server_ip,
                     new_server_ip)


if __name__ == '__main__':
    main(sys.argv[1:])






