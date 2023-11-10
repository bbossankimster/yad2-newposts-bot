from settings import ALLOWED_USERS
from functools import wraps


def restricted(func):
    @wraps(func)
    def wrapped(update, *args, **kwargs):
        user_id = update.effective_user.id
        ## print("Access to bot with user_id", user_id)
        if user_id not in ALLOWED_USERS:
            print("Unauthorized access denied for {}.".format(user_id))
            return
        return func(update, *args, **kwargs)
    return wrapped
