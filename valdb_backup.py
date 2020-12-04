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
conn = cx_Oracle.connect(user=username, password=password, dsn=dsn_tns)

cursor = conn.cursor()
print('Fetching releases')
releases = [create_release(r) for r in cursor.execute('select * from CMS_PDMV_VAL.releases')]
print('Fetching releases_lv')
releases_lv = [create_release(r) for r in cursor.execute('select * from CMS_PDMV_VAL.releases_lv')]
print('Fetching status')
status = [create_status(r) for r in cursor.execute('select * from CMS_PDMV_VAL.status')]
print('Fetching status_lv')
status_lv = [create_status(r) for r in cursor.execute('select * from CMS_PDMV_VAL.status_lv')]
print('Fetching users')
users = [create_user(r) for r in cursor.execute('select * from CMS_PDMV_VAL.users')]
print('Fetching user rights')
user_rights = [create_user_rights(r) for r in cursor.execute('select * from CMS_PDMV_VAL.user_rights')]

conn.close()

print('Fetched %s releases' % (len(releases)))
print('Fetched %s releases_lv' % (len(releases_lv)))
print('Fetched %s status' % (len(status)))
print('Fetched %s status_lv' % (len(status_lv)))
print('Fetched %s users' % (len(users)))
print('Fetched %s user_rights' % (len(user_rights)))

backup_name = sys.argv[1]
conn = sqlite3.connect(backup_name)
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS releases
                  (id integer PRIMARY KEY,
                   category text,
                   subcategory text,
                   release_name text,
                   version integer,
                   date integer,
                   status_kind text)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS releases_lv
                  (id integer PRIMARY KEY,
                   category text,
                   subcategory text,
                   release_name text,
                   version integer,
                   date integer,
                   status_kind text)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS status
                  (id integer,
                   validation_status text,
                   comments text,
                   links text,
                   user_name text,
                   messageID text,
                   email_subject text,
                   relmon_url text,
                   FOREIGN KEY(id) REFERENCES releases(id))''')

cursor.execute('''CREATE TABLE IF NOT EXISTS status_lv
                  (id integer,
                   validation_status text,
                   comments text,
                   links text,
                   user_name text,
                   messageID text,
                   email_subject text,
                   relmon_url text,
                   FOREIGN KEY(id) REFERENCES releases(id))''')

cursor.execute('''CREATE TABLE IF NOT EXISTS users
                  (user_name text,
                   email text,
                   admin short,
                   validator short)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS user_rights
                  (id integer PRIMARY KEY,
                   user_name text,
                   category text,
                   subcategory text,
                   status_kind text)''')

conn.commit();
cursor.execute('DELETE FROM releases;')
cursor.execute('DELETE FROM releases_lv;')
cursor.execute('DELETE FROM status;')
cursor.execute('DELETE FROM status_lv;')
cursor.execute('DELETE FROM users;')
cursor.execute('DELETE FROM user_rights;')
conn.commit();

for i, release in enumerate(releases):
    cursor.execute('INSERT INTO releases VALUES (?, ?, ?, ?, ?, ?, ?)', [release['id'],
                                                                         release['category'],
                                                                         release['subcategory'],
                                                                         release['release_name'],
                                                                         release['version'],
                                                                         release['date'],
                                                                         release['status_kind']])
    if i % 1000 == 0:
        print('Commit releases after %s insertions' % (i))
        conn.commit()

conn.commit()

for i, release in enumerate(releases_lv):
    cursor.execute('INSERT INTO releases_lv VALUES (?, ?, ?, ?, ?, ?, ?)', [release['id'],
                                                                            release['category'],
                                                                            release['subcategory'],
                                                                            release['release_name'],
                                                                            release['version'],
                                                                            release['date'],
                                                                            release['status_kind']])
    if i % 1000 == 0:
        print('Commit releases_lv after %s insertions' % (i))
        conn.commit()

conn.commit()

for i, stat in enumerate(status):
    cursor.execute('INSERT INTO status VALUES (?, ?, ?, ?, ?, ?, ?, ?)', [stat['id'],
                                                                          stat['validation_status'],
                                                                          stat['comments'],
                                                                          stat['links'],
                                                                          stat['user_name'],
                                                                          stat['messageID'],
                                                                          stat['email_subject'],
                                                                          stat['relmon_url']])
    if i % 1000 == 0:
        print('Commit status after %s insertions' % (i))
        conn.commit()

conn.commit()

for i, stat in enumerate(status_lv):
    cursor.execute('INSERT INTO status_lv VALUES (?, ?, ?, ?, ?, ?, ?, ?)', [stat['id'],
                                                                             stat['validation_status'],
                                                                             stat['comments'],
                                                                             stat['links'],
                                                                             stat['user_name'],
                                                                             stat['messageID'],
                                                                             stat['email_subject'],
                                                                             stat['relmon_url']])
    if i % 1000 == 0:
        print('Commit status_lv after %s insertions' % (i))
        conn.commit()

conn.commit()

for i, user in enumerate(users):
    cursor.execute('INSERT INTO users VALUES (?, ?, ?, ?)', [user['user_name'],
                                                             user['email'],
                                                             user['admin'],
                                                             user['validator']])
    if i % 1000 == 0:
        print('Commit users after %s insertions' % (i))
        conn.commit()

conn.commit()

for i, user_right in enumerate(user_rights):
    cursor.execute('INSERT INTO user_rights VALUES (?, ?, ?, ?, ?)', [user_right['id'],
                                                                      user_right['user_name'],
                                                                      user_right['category'],
                                                                      user_right['subcategory'],
                                                                      user_right['status_kind']])
    if i % 1000 == 0:
        print('Commit user_rights after %s insertions' % (i))
        conn.commit()

conn.commit()
conn.close()
