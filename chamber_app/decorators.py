#  Copyright (c) 2025. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
#  Morbi non lorem porttitor neque feugiat blandit. Ut vitae ipsum eget quam lacinia accumsan.
#  Etiam sed turpis ac ipsum condimentum fringilla. Maecenas magna.
#  Proin dapibus sapien vel ante. Aliquam erat volutpat. Pellentesque sagittis ligula eget metus.
#  Vestibulum commodo. Ut rhoncus gravida arcu.

from functools import wraps
from flask import redirect, url_for, session, abort
from flask_login import current_user


def is_admin(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        # Check if the user is logged in and has the 'admin' role
        if not current_user.has_role('admin'):
            abort(404)  # Redirect to an error page
        return func(*args, **kwargs)

    return decorated_function
