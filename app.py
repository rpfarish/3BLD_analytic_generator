from flask import Flask
from flask import render_template, request, redirect

from Cube.drill import Drill
from views import views

app = Flask(__name__)
app.register_blueprint(views, url_prefix="/")


@app.route("/", methods=['POST', 'GET'])
def scramble(edgebuffer="UF"):
    print("edge buffer", edgebuffer)
    if request.method == "GET":

        return redirect(f"drilledgebuffer/{edgebuffer}")
        # return render_template("index.html", edgebuffer=edgebuffer)
    else:
        return render_template("index.html", scrambles="Scramble")


@app.route("/drilledgebuffer/<edgebuffer>", methods=['POST', 'GET'])
def drilledgebuffer(edgebuffer):
    print("edge buffer here", edgebuffer)
    args = request.args
    eb = args.get("edgebuffer")
    if eb is not None:
        edgebuffer = eb

    print(eb)
    if request.method == "GET":
        scrambles = Drill().drill_edge_buffer(edge_buffer=edgebuffer, return_list=True)
        return render_template("index.html", scrambles=scrambles, edgebuffer=edgebuffer)
    scrambles = Drill().drill_edge_buffer(edge_buffer=edgebuffer, return_list=True)
    return render_template("index.html", scrambles=scrambles, edgebuffer=edgebuffer)
    # else:
    #     return render_template("index.html", scrambles="Scramble")

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
