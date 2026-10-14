from flask import Blueprint, render_template

flask_views = Blueprint("views", __name__, template_folder="templates")

@flask_views.route("/audio-studio")
def audio_studio_page():
    # Renders your frontend dashboard layout
    return render_template("studio.html")
