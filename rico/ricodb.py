import sqlite3
from pathlib import Path



# ------------------------------------------------------------
#   RicoDB is a class to manage sqlite database in ChatBox and RicoBOT
# ------------------------------------------------------------

## user:
#  ID, first_name, nickname, gname
## chat:
#  ID, locale, jetlag
## permission:
#  (user.ID, chat.ID), level
# ally:
#   ID, chat.ID, name (example: accademia)
# userally:
#   (user.ID, ally.ID)
# event:
#   ID, chat.ID, when (utc timestamp), message
# eventdest:
#   (ally.ID, event.ID)

# https://forum.smallgiantgames.com/t/titan-rosters/25305
# titan:
#   ID, name, color, life,
# (la war viene memorizzata a parte, non nel DB ma viene notificata come evento) 
#   titan None is a titan died



class RicoDB:
    def __init__(self, xfile='ricobot.db'):
        self._conn = sqlite3.connect(xfile)
        self._conn.row_factory = sqlite3.Row
        self._cursor = self._conn.cursor()
        dbpath = Path(xfile)
        if not dbpath.exists():
            self._create_tables()
    
    def _create_tables(self):
        # riminders:
        # table titan flags: +1 suggested green potions, +2 is rare)
        # colors: 1=Red, 2=Green 3=Blue 4=Yellow 5=Purple
        self._cursor.execute("PRAGMA foreign_keys=ON")
        self._cursor.execute('''CREATE TABLE user
            (id integer PRIMARY KEY NOT NULL, first_name TEXT,
             nickname TEXT, gname TEXT)''')
        self._cursor.execute('''CREATE TABLE chat
            (id integer PRIMARY KEY NOT NULL, locale TEXT,
             jetlag INTEGER)''')
        self._cursor.execute('''CREATE TABLE permission
            (userid integer NOT NULL, chatid integer NOT NULL,
             level integer NOT NULL,
             FOREIGN KEY(userid) REFERENCES user(id),
             FOREIGN KEY(chatid) REFERENCES chat(id),
             PRIMARY KEY(userid, chatid))''')
        self._cursor.execute('''CREATE TABLE ally
            (id integer PRIMARY KEY AUTOINCREMENT, 
             chatid integer NOT NULL, name text NOT NULL,
             FOREIGN KEY(chatid) REFERENCES chat(id))''')
        self._cursor.execute('''CREATE TABLE userally
            (userid integer NOT NULL, allyid integer NOT NULL,
             FOREIGN KEY(userid) REFERENCES user(id),
             FOREIGN KEY(allyid) REFERENCES ally(id),
             PRIMARY KEY(userid, allyid))''')
        self._cursor.execute('''CREATE TABLE event
            (id integer PRIMARY KEY AUTOINCREMENT,
            time BLOB, chatid INTEGER NOT NULL,
            allyid INTEGER NOT NULL, message text,
            FOREIGN KEY(chatid) REFERENCES chat(id),
            FOREIGN KEY(allyid) REFERENCES ally(id))''')
    
    def commit(self):
        self._conn.commit()
    
    def _params_validation(self, table, params):
        expected_params = self._cursor.execute('''
            PRAGMA table_info({})'''.format(table))
        expected_params = [dict(x) for x in expected_params.fetchall()]
        expected_params = [x['name'] for x in expected_params]
        for x in params:
            if x not in expected_params:
                raise ValueError(
                    "'{}' is not a valid column for '{}' "
                    'table'.format(x, table))
    
    def _add_general(self, table, params):
        self._cursor.execute('''INSERT INTO {} VALUES
            ({})'''.format(table, ','.join('?' for x in params)),
            params)
    
    def _mod_general_whereid(self, table, params):
        if 'id' not in params:
            raise ValueError('params MUST contain an userid')
        self._params_validation(table, params)
        userid = params.pop('id')
        changes = ','.join(f'{key}=?' for key in params)
        values = list(params.values()) + [userid]
        self._cursor.execute('''
            UPDATE {} SET {} WHERE {}.id=?'''.format(table, changes, table),
            values)
    
    
    def add_user(self, userid, first_name, nickname, gname=None):
        self._add_general('user', (userid, first_name, nickname, gname))
    
    def mod_user(self, params):
        self._mod_general_whereid('user', params)
    
    def add_chat(self, chatid, locale, jetlag):
        self._add_general('chat', (chatid, locale, jetlag))
    
    def mod_chat(self, params):
        self._mod_general_whereid('chat', params)
    
    def get_permission(self, userid, chatid):
        permission = self._cursor.execute('''
            SELECT level FROM permission WHERE userid=? AND chatid=?''',
            (userid, chatid))
        try:
            permission = dict(permission.fetchone())
        except TypeError:
            # when fetchone() does not find any result, it is None so
            # using dict(fetchone()) with no result will generate a TypeError
            # exception. This case permission level is 'user' (level: 10)
            return 10
        return permission['level']
    
    def set_permission(self, userid, chatid, level):
        start_level = self.get_permission(userid, chatid)
        if level == start_level:
            return
        elif level == 10:
            self._cursor.execute('''
                DELETE FROM permission WHERE userid=? AND chatid=?''',
                (userid, chatid))
        else:
            self._cursor.execute('''
                INSERT OR REPLACE INTO permission VALUES(?,?,?)''',
                (userid, chatid, level))
    
    def add_ally(self, chatid, allyname):
        self._add_general('ally', (None, chatid, allyname))
    
    def del_ally(self, chatid, allyname):
        self._cursor.execute('''
            DELETE FROM ally WHERE name=? AND chatid=?''',
            (allyname, chatid))
    