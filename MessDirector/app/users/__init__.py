# __init__.py is a special Python file that allows a directory to become
# a Python package so it can be accessed using the 'import' statement.

from .user_views import user_blueprint

def register_blueprints_user(app):
    app.register_blueprint(user_blueprint)
