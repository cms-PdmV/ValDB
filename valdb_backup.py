import cx_Oracle
import sqlite3
import sys
from secrets import secrets


print('Backup name: %s' % (sys.argv[1]))


def create_release(row):
   return {'id': row[0],
           'category': row[1],
           'subcategory': row[2],
           'release_name': row[3],
           'version': row[4],
           'date': row[5].strftime('%s'),
           'status_kind': row[6]}


def create_status(row):
    return {'id': row[0],
            'validation_status': row[1],
            'comments': row[2],
            'links': row[3],
            'user_name': row[4],
            'messageID': row[5],
            'email_subject': row[6],
            'relmon_url': row[7]}


def create_user(row):
    return {'user_name': row[0],
            'email': row[1],
            'admin': row[2],
            'validator': row[3]}


def create_user_rights(row):
    return {'id': row[0],
            'user_name': row[1],
            'category': row[2],
            'subcategory': row[3],
            'status_kind': row[4]}


host_name = 'int2r-s.cern.ch'
port_number =  10121
service_name = 'int2r_lb.cern.ch'
username = secrets['PdmV/valdb']['connections']['dev']['writer']['user']
password = secrets['PdmV/valdb']['connections']['dev']['writer']['password']

dsn_tns = cx_Oracle.makedsn(host_name, port_number, service_name=service_name)
valdb_conn = cx_Oracle.connect(user=username, password=password, dsn=dsn_tns)
valdb_cursor = valdb_conn.cursor()

backup_name = sys.argv[1]
backup_conn = sqlite3.connect(backup_name)
backup_cursor = backup_conn.cursor()


backup_cursor.execute('''CREATE TABLE IF NOT EXISTS releases
                         (id integer PRIMARY KEY,
                          category text,
                          subcategory text,
                          release_name text,
                          version integer,
                          date integer,
                          status_kind text)''')

backup_cursor.execute('''CREATE TABLE IF NOT EXISTS releases_lv
                         (id integer PRIMARY KEY,
                          category text,
                          subcategory text,
                          release_name text,
                          version integer,
                          date integer,
                          status_kind text)''')

backup_cursor.execute('''CREATE TABLE IF NOT EXISTS status
                         (id integer,
                          validation_status text,
                          comments text,
                          links text,
                          user_name text,
                          messageID text,
                          email_subject text,
                          relmon_url text,
                          FOREIGN KEY(id) REFERENCES releases(id))''')

backup_cursor.execute('''CREATE TABLE IF NOT EXISTS status_lv
                         (id integer,
                          validation_status text,
                          comments text,
                          links text,
                          user_name text,
                          messageID text,
                          email_subject text,
                          relmon_url text,
                          FOREIGN KEY(id) REFERENCES releases(id))''')

backup_cursor.execute('''CREATE TABLE IF NOT EXISTS users
                         (user_name text,
                          email text,
                          admin short,
                          validator short)''')

backup_cursor.execute('''CREATE TABLE IF NOT EXISTS user_rights
                         (id integer PRIMARY KEY,
                          user_name text,
                          category text,
                          subcategory text,
                          status_kind text)''')

backup_conn.commit();
backup_cursor.execute('DELETE FROM releases;')
backup_cursor.execute('DELETE FROM releases_lv;')
backup_cursor.execute('DELETE FROM status;')
backup_cursor.execute('DELETE FROM status_lv;')
backup_cursor.execute('DELETE FROM users;')
backup_cursor.execute('DELETE FROM user_rights;')
backup_conn.commit();

print('Fetching releases')
for i, r in enumerate(valdb_cursor.execute('select * from CMS_PDMV_VAL.releases')):
    release = create_release(r)
    backup_cursor.execute('INSERT INTO releases VALUES (?, ?, ?, ?, ?, ?, ?)', [release['id'],
                                                                                release['category'],
                                                                                release['subcategory'],
                                                                                release['release_name'],
                                                                                release['version'],
                                                                                release['date'],
                                                                                release['status_kind']])
    if i and i % 1000 == 0:
        print('Commiting releases after %s insertions' % (i))
        backup_conn.commit()

backup_conn.commit()

print('Fetching releases_lv')
for i, r in enumerate(valdb_cursor.execute('select * from CMS_PDMV_VAL.releases_lv')):
    release = create_release(r)
    backup_cursor.execute('INSERT INTO releases_lv VALUES (?, ?, ?, ?, ?, ?, ?)', [release['id'],
                                                                                   release['category'],
                                                                                   release['subcategory'],
                                                                                   release['release_name'],
                                                                                   release['version'],
                                                                                   release['date'],
                                                                                   release['status_kind']])
    if i and i % 1000 == 0:
        print('Commiting releases_lv after %s insertions' % (i))
        backup_conn.commit()

backup_conn.commit()

print('Fetching status')
for i, r in enumerate(valdb_cursor.execute('select * from CMS_PDMV_VAL.status')):
    status = create_status(r)
    backup_cursor.execute('INSERT INTO status VALUES (?, ?, ?, ?, ?, ?, ?, ?)', [status['id'],
                                                                                 status['validation_status'],
                                                                                 status['comments'],
                                                                                 status['links'],
                                                                                 status['user_name'],
                                                                                 status['messageID'],
                                                                                 status['email_subject'],
                                                                                 status['relmon_url']])
    if i and i % 1000 == 0:
        print('Commiting status after %s insertions' % (i))
        backup_conn.commit()

backup_conn.commit()

print('Fetching status_lv')
for r in valdb_cursor.execute('select * from CMS_PDMV_VAL.status_lv'):
    status  = create_status(r)
    backup_cursor.execute('INSERT INTO status_lv VALUES (?, ?, ?, ?, ?, ?, ?, ?)', [status['id'],
                                                                                    status['validation_status'],
                                                                                    status['comments'],
                                                                                    status['links'],
                                                                                    status['user_name'],
                                                                                    status['messageID'],
                                                                                    status['email_subject'],
                                                                                    status['relmon_url']])
    if i and i % 1000 == 0:
        print('Commiting status_lv after %s insertions' % (i))
        backup_conn.commit()

backup_conn.commit()

print('Fetching users')
for r in valdb_cursor.execute('select * from CMS_PDMV_VAL.users'):
    user = create_user(r)
    backup_cursor.execute('INSERT INTO users VALUES (?, ?, ?, ?)', [user['user_name'],
                                                                    user['email'],
                                                                    user['admin'],
                                                                    user['validator']])
    if i and i % 1000 == 0:
        print('Commiting users after %s insertions' % (i))
        backup_conn.commit()

backup_conn.commit()

print('Fetching user rights')
for r in valdb_cursor.execute('select * from CMS_PDMV_VAL.user_rights'):
    user_right = create_user_rights(r)
    backup_cursor.execute('INSERT INTO user_rights VALUES (?, ?, ?, ?, ?)', [user_right['id'],
                                                                             user_right['user_name'],
                                                                             user_right['category'],
                                                                             user_right['subcategory'],
                                                                             user_right['status_kind']])
    if i and i % 1000 == 0:
        print('Commiting user_rights after %s insertions' % (i))
        backup_conn.commit()

backup_conn.commit()

valdb_conn.close()

backup_conn.close()
