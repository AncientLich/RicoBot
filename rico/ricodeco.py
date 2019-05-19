import gettext
from functools import wraps

_ = gettext.gettext


def _deco_rank(deco_args, level, err=None):
    def decorator(fn):
        @wraps(fn)
        def decorated(*args, 
                      deco_args=deco_args, err=err, level=level, 
                      **kwargs):
            if err is None:
                err = _ ('Operation not allowed')
            db, userid, chatid, security = deco_args
            if (db.get_permission(userid, chatid) < level
                     and userid != security['owner']):
                return err
            else:
                return fn(*args, **kwargs)
        return decorated
    return decorator 



def _deco_private(deco_args, err=None):
    def decorator(fn):
        @wraps(fn)
        def decorated(*args, deco_args=deco_args, err=err, **kwargs):
            if err is None:
                err = _ ('Operation not allowed (reserved to maintainer)')
            db, userid, chatid, security = deco_args
            if userid != security['owner']:
                return err
            else:
                return fn(*args, **kwargs)
        return decorated
    return decorator



def _deco_wip(deco_args):
    def decorator(fn):
        @wraps(fn)
        def decorated(*args, deco_args=deco_args, **kwargs):
            db, userid, chatid, security = deco_args
            if chatid != security['room']:
                err =  _ ('Operation not yet available (under development)')
                return err
            else:
                return fn(*args, **kwargs)
        return decorated
    return decorator



# -------------------------------
#   This is the only decorator wich will be used outside ricodeco
#   The other decorators will be applied by ricocmd itself
# ------------------------------



rico_commands = {}



def ricocmd(*, rank=None, private=False, wip=False, err_msg=None):
    def decorator(fn):
        rico_commands[fn.__name__] = fn
        @wraps(fn)
        def decorated(*args, **kwargs):
            deco_args = kwargs.pop('deco_args', None)
            # ---------------
            #   Error checks
            # ---------------
            if rank is not None and not isinstance(rank, int):
                raise ValueError('ricocmd rank must be an integer')
            elif private and isinstance(rank, int):
                raise ValueError('ricocmd "private" and "rank" must not be'
                    'used together')
            elif deco_args is None:
                # if no deco_args found, than no decoration applied
                return fn(*args, **kwargs)
            # -------------------------------
            #  Actual decoration starts here
            # -------------------------------
            new_fn = fn
            if private:
                new_fn = _deco_private(deco_args, err_msg)(new_fn)
            elif isinstance(rank, int):
                # private and rank are self-exclusive each other
                new_fn = _deco_rank(deco_args, rank, err_msg)(new_fn)
            # -------
            #  private/rank can be paired with wip/room
            # -------
            if wip:
                new_fn = _deco_wip(deco_args)(new_fn)
            return new_fn(*args, **kwargs)
        return decorated
    return decorator


