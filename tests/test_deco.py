import pytest
import rico.ricodb as rdb
import rico.ricodeco as deco


# ----------------------------------------
#  Part 1: decorated fake functions
# ----------------------------------------



def std_function(one, two, three):
    return '{}, {}, {}'.format(one, two, three)



@deco.ricocmd(private=True, err_msg='error2')
def std_function_private(one, two, three):
    return '{}, {}, {}'.format(one, two, three)



@deco.ricocmd(wip=True)
def std_function_wip(one, two, three):
    return '{}, {}, {}'.format(one, two, three)



@deco.ricocmd(rank=15, err_msg='error2')
def std_function_rank(one, two, three):
    return '{}, {}, {}'.format(one, two, three)



@deco.ricocmd(wip=True, rank=15)
def std_rank_wip(one, two, three):
    return '{}, {}, {}'.format(one, two, three)



@deco.ricocmd(wip=True, private=True)
def std_private_wip(one, two, three):
    return '{}, {}, {}'.format(one, two, three)



# -----------------------------------
#  Part 2: Test fixture and make deco args
# -----------------------------------



@pytest.fixture
def db_instance():
    db = rdb.RicoDB(':memory:')
    db.add_user(1, 'alfa', 'beta', 'gamma')
    db.add_chat(1, 'it', 1)
    return db



# make deco args (standard function)
def mk_dargs(db, *, userid=1, chatid=1, owner=1, room=1):
    security = {'owner': owner, 'room': room}
    return (db, userid, chatid, security)


# -----------------------------------
#  Part 3: Actual tests
# -----------------------------------



def test_deco_private(db_instance):
    db = db_instance
    deco_args = mk_dargs(db)
    fn = deco._deco_private(deco_args, 'error')(std_function)
    assert std_function(1, 2, 3) == '1, 2, 3'
    assert fn(4, 5, 6) == '4, 5, 6'
    assert std_function_private(1, 2, 3, deco_args=deco_args) == '1, 2, 3'
    deco_args = mk_dargs(db, owner=2)
    fn = deco._deco_private(deco_args, 'error')(std_function)
    assert fn(7, 8, 9) == 'error'
    assert std_function_private(1, 2, 3) == '1, 2, 3'
    assert std_function_private(1, 2, 3, deco_args=deco_args) == 'error2'



def test_deco_wip(db_instance):
    db = db_instance
    deco_args = mk_dargs(db)
    fn = deco._deco_wip(deco_args)(std_function)
    assert fn(4, 5, 6) == '4, 5, 6'
    assert std_function_wip(1, 2, 3, deco_args=deco_args) == '1, 2, 3'
    deco_args = mk_dargs(db, room=2)
    fn = deco._deco_wip(deco_args)(std_function)
    assert fn(7, 8, 9) == 'Operation not yet available (under development)'
    assert std_function_wip(1, 2, 3) == '1, 2, 3'
    assert (std_function_wip(1, 2, 3, deco_args=deco_args) ==
        'Operation not yet available (under development)')



def test_deco_rank(db_instance):
    db = db_instance
    deco_args = mk_dargs(db, owner=2)
    fn = deco._deco_rank(deco_args, 15, 'error')(std_function)
    assert fn(1, 2, 3) == 'error'
    assert std_function_rank(1, 2, 3, deco_args=deco_args) == 'error2'
    assert std_function_rank(1, 2, 3) == '1, 2, 3'
    db.set_permission(1,1, 15)
    assert fn(1, 2, 3) == '1, 2, 3'
    assert std_function_rank(1, 2, 3, deco_args=deco_args) == '1, 2, 3'
    db.set_permission(1,1, 155)
    assert fn(1, 2, 3) == '1, 2, 3'
    assert std_function_rank(1, 2, 3, deco_args=deco_args) == '1, 2, 3'
    db.set_permission(1,1, 14)
    assert fn(1, 2, 3) == 'error'
    assert std_function_rank(1, 2, 3, deco_args=deco_args) == 'error2'
    # --- FROM NOW OWN I SET OWNER to 1 (wich is the active userid)
    # So all the operation will be allowed regardless of rank level
    # The owner will be allowed to do anything in any situation
    deco_args = mk_dargs(db)
    fn = deco._deco_rank(deco_args, 15, 'error')(std_function)
    db.set_permission(1,1, 10)
    assert fn(1, 2, 3) == '1, 2, 3'
    assert std_function_rank(1, 2, 3, deco_args=deco_args) == '1, 2, 3'
    db.set_permission(1,1, 100)
    assert fn(1, 2, 3) == '1, 2, 3'
    assert std_function_rank(1, 2, 3, deco_args=deco_args) == '1, 2, 3'
    


def test_rank_with_wip(db_instance):
    db = db_instance
    # 1: rank OK, room OK
    db.set_permission(1,1, 20)
    deco_args = mk_dargs(db, owner=2)
    assert std_rank_wip(1, 2, 3, deco_args=deco_args) == '1, 2, 3'
    # 2: rank OK, OUTSIDE ROOM
    deco_args = mk_dargs(db, owner=2, room=2)
    assert (std_rank_wip(1, 2, 3, deco_args=deco_args) ==
        'Operation not yet available (under development)')
    # 3: rank LOW, OUTSIDE ROOM
    db.set_permission(1,1, 10)
    assert (std_rank_wip(1, 2, 3, deco_args=deco_args) == 
        'Operation not yet available (under development)')
    # 4: rank LOW, room OK
    deco_args = mk_dargs(db, owner=2)
    assert (std_rank_wip(1, 2, 3, deco_args=deco_args) ==
        'Operation not allowed')



def test_private_with_wip(db_instance):
    db = db_instance
    # 1: owner OK, room OK
    deco_args = mk_dargs(db)
    assert std_private_wip(1, 2, 3, deco_args=deco_args) == '1, 2, 3'
    # 2: owner OK, OUTSIDE ROOM
    deco_args = mk_dargs(db, room=2)
    assert (std_private_wip(1, 2, 3, deco_args=deco_args) == 
        'Operation not yet available (under development)')
    # 3: NOT owner, OUTSIDE ROOM
    deco_args = mk_dargs(db, owner=2, room=2)
    assert (std_private_wip(1, 2, 3, deco_args=deco_args) == 
        'Operation not yet available (under development)')
    # 4: NOT owner, room OK
    deco_args = mk_dargs(db, owner=2)
    assert (std_private_wip(1, 2, 3, deco_args=deco_args) == 
        'Operation not allowed (reserved to maintainer)')



def test_ricocmd_registration():
    deco.rico_commands.clear()
    
    @deco.ricocmd()
    def f1():
        return '1'
    
    @deco.ricocmd()
    def f2():
        return '2'
    
    @deco.ricocmd()
    def f3():
        return '3'
    
    assert sorted(deco.rico_commands) == sorted(['f1', 'f2', 'f3'])
    for i in range(1,4):
        fn = deco.rico_commands['f{}'.format(i)]
        assert fn() == '{}'.format(i)
    