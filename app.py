from flask import Flask
from flask import render_template, request, url_for, redirect

from Cube.drill import Drill
from get_scrambles import get_scramble
from views import views

app = Flask(__name__)
app.register_blueprint(views, url_prefix="/")


@app.route("/", methods=['POST', 'GET'])
def scramble():
    if request.method == "POST":
        scram = get_scramble()
        return redirect(url_for("scramble", scramble=get_scramble()))
    else:
        return render_template("index.html", scramble=get_scramble())


@app.route("/drilledgebuffer/<edgebuffer>", methods=['POST', 'GET'])
def drilledgebuffer(edge_buffer):
    drill = Drill()

    if request.method == "GET":
        scram = get_scramble()
        return redirect(url_for("scramble", scramble=get_scramble()))
    else:
        return render_template("index.html", scramble=get_scramble())


#
# @app.route("/login", methods=['POST', 'GET'])
# def login():
#     if request.method == "POST":
#         usr = request.form["nm"]
#         return redirect(url_for("usr", usr=usr))
#     else:
#         return render_template("index.html")
#
#
# @app.route("/<usr>", methods=['POST', 'GET'])
# def usr(usr):
#     if request.method == "POST":
#         usr = request.form["nm"]
#         return redirect(url_for("usr", usr=usr))
#     else:
#         return render_template("index.html", usr=usr)


if __name__ == "__main__":
    app.run(debug=True, port=8000)
