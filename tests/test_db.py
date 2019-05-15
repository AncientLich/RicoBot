import pytest
import rico.ricodb as rdb



@pytest.fixture
def init_db():
    return rdb.RicoDB(':memory:')



def test_db_create_tables(init_db):
    db = init_db
    # ------
    # Obtaining list of tables
    # ------
    ts = db._cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table'")
    ts = ts.fetchall()
    tables = set()
    for t in ts:
        t = dict(t)
        t = t['name']
        if 'sqlite' not in t:
            tables.add(t)
    assert tables == {'user', 'chat', 'permission', 'ally',
                      'userally', 'event'}



def test_params_validation(init_db):
    db = init_db
    db.add_user(1, 'alfa', 'alfa', 'alfa')
    with pytest.raises(ValueError):
        db.mod_user({'id': 1, 'unvalid_param': 'param'})



def test_db_add_user(init_db):
    db = init_db
    db.add_user(1, 'alfa', 'alfan1', 'alfan2')
    db.add_user(2, 'beta', 'betan1', 'betan2')
    db.add_user(3, 'gamma', 'gamman1', 'gamman2')
    value = db._cursor.execute('''SELECT * FROM user''')
    value = value.fetchall()
    value = [dict(x) for x in value]
    assert value == [
        {'id': 1, 'first_name': 'alfa',
         'nickname': 'alfan1', 'gname': 'alfan2'},
        {'id': 2, 'first_name': 'beta',
         'nickname': 'betan1', 'gname': 'betan2'},
        {'id': 3, 'first_name': 'gamma',
         'nickname': 'gamman1', 'gname': 'gamman2'},
    ]



def test_db_mod_user(init_db):
    db = init_db
    db.add_user(1, 'alfa', 'alfan1', 'alfan2')
    db.add_user(2, 'beta', 'betan1', 'betan2')
    db.add_user(3, 'gamma', 'gamman1', 'gamman2')
    db.mod_user({'id': 2, 'nickname': 'new_nick', 'first_name': 'rico'})
    value = db._cursor.execute('''SELECT * FROM user''')
    value = value.fetchall()
    value = [dict(x) for x in value]
    assert value == [
        {'id': 1, 'first_name': 'alfa',
         'nickname': 'alfan1', 'gname': 'alfan2'},
        {'id': 2, 'first_name': 'rico',
         'nickname': 'new_nick', 'gname': 'betan2'},
        {'id': 3, 'first_name': 'gamma',
         'nickname': 'gamman1', 'gname': 'gamman2'},
    ]


def test_db_add_chat(init_db):
    db = init_db
    db.add_chat(1, 'it', 1)
    value = db._cursor.execute('''SELECT * FROM chat''')
    value = dict(value.fetchone())
    assert value == {
        'id': 1, 'locale': 'it', 'jetlag': 1}



def test_db_mod_chat(init_db):
    db = init_db
    db.add_chat(1, 'it', 1)
    db.mod_chat({'id': 1, 'locale': 'en'})
    value = db._cursor.execute('''SELECT * FROM chat''')
    value = dict(value.fetchone())
    assert value == {
        'id': 1, 'locale': 'en', 'jetlag': 1}



def test_db_get_permission(init_db):
    db = init_db
    db.add_user(1, 'alfa', 'alfan1', 'alfan2')
    db.add_chat(1, 'it', 1)
    assert db.get_permission(1,1) == 10



def test_db_add_permission(init_db):
    db = init_db
    db.add_user(1, 'alfa', 'alfan1', 'alfan2')
    db.add_chat(1, 'it', 1)
    db.set_permission(1,1,10)
    value = db._cursor.execute('''SELECT * FROM permission''')
    value = value.fetchone()
    assert value is None
    db.set_permission(1,1,15)
    value = db.get_permission(1,1)
    value2 = db._cursor.execute('''SELECT * FROM permission''')
    value2 = [dict(x) for x in value2]
    assert len(value2) == 1
    assert value2[0] == {'userid': 1, 'chatid': 1, 'level': 15}
    assert value == 15
    db.set_permission(1,1,20)
    value = db.get_permission(1,1)
    assert value == 20
    db.set_permission(1,1,10)
    value = db.get_permission(1,1)
    value2 = db._cursor.execute('''SELECT * FROM permission''')
    value2 = value2.fetchone()
    assert value == 10
    assert value2 is None



def test_db_add_ally(init_db):
    db = init_db
    db.add_chat(1, 'it', 1)
    db.add_ally(1, 'accademia')
    value = db._cursor.execute('''SELECT * FROM ally''')
    value = dict(value.fetchone())
    assert value == {'id': 1, 'chatid': 1, 'name': 'accademia'}



def test_db_del_ally(init_db):
    db = init_db
    db.add_chat(1, 'it', 1)
    db.add_ally(1, 'accademia')
    db.del_ally(1, 'accademia')
    value = db._cursor.execute('''SELECT * FROM ally''')
    value = value.fetchone()
    assert value is None
    db.del_ally(1, 'cuccureddu')

