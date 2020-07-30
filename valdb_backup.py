import cx_Oracle
import sqlite3
import sys


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


host_name = 'int2r-s.cern.ch'
port_number =  10121
service_name = 'int2r_lb.cern.ch'
username = 'CMS_PDMV_VAL_W'
password = 'SE9AFEFUTRAC4U93'

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
conn.close()

print('Fetched %s releases' % (len(releases)))
print('Fetched %s releases_lv' % (len(releases_lv)))
print('Fetched %s status' % (len(status)))
print('Fetched %s status_lv' % (len(status_lv)))

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

conn.commit();
cursor.execute('DELETE FROM releases;')
cursor.execute('DELETE FROM releases_lv;')
cursor.execute('DELETE FROM status;')
cursor.execute('DELETE FROM status_lv;')
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
conn.close()
