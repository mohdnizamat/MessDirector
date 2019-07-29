

from .manager_views import manager_blueprint

def register_blueprints_manager(app):
    app.register_blueprint(manager_blueprint)
