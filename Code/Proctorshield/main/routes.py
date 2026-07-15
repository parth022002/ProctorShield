from flask import render_template,redirect,Blueprint,url_for,Response,make_response,current_app,send_from_directory
from flask_login import current_user
import os

main = Blueprint("main",__name__,template_folder="templates",static_folder="static")

@main.route("/")
def welcome():
    if current_user.is_authenticated == False:
        return render_template("welcome.html",title = "Welcome")
    else:
        if current_user.student is not None:
            return redirect(url_for('student.home'))
        else:
            return redirect(url_for('teacher.home'))


@main.route('/sw.js')
def service_worker():
    response = make_response(current_app.send_static_file('sw.js'))
    response.headers['Content-Type'] = 'application/javascript'
    response.headers['Service-Worker-Allowed'] = '/'
    return response


@main.route('/assets/<path:filename>')
def serve_assets(filename):
    assets_dir = os.path.join(current_app.root_path, '..', 'assets')
    return send_from_directory(assets_dir, filename)
        








