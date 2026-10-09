import os

from flask import Flask, g, redirect, render_template, url_for


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-change-me"),
        DATABASE=os.path.join(app.instance_path, "reparacampus.sqlite"),
    )

    if test_config:
        app.config.update(test_config)

    os.makedirs(app.instance_path, exist_ok=True)

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import incidents
    app.register_blueprint(incidents.bp)

    from . import reporting
    app.register_blueprint(reporting.bp)

    @app.route("/")
    def index():
        if g.user is None:
            return redirect(url_for("auth.login"))
        if g.user["role"] == "SOLICITANTE":
            return redirect(url_for("incidents.index"))
        if g.user["role"] == "COORDINADOR":
            return redirect(url_for("incidents.manage"))
        if g.user["role"] == "TECNICO":
            return redirect(url_for("incidents.assigned"))
        return render_template("home.html")

    return app
