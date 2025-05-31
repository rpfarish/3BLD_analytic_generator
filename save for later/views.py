from flask import Blueprint

views = Blueprint(__name__, "views")

# @views.route("/")
# def home():
#     return render_template("index.html", name="Joe", age=42)
#
#
# @views.route("/profile")
# def profile():
#     args = request.args
#     name = args.get('name')
#     return render_template("index.html", name=name)
#
#
# @views.route("/json")
# def get_json():
#     return jsonify({"name": "tim", "coolness": 10})
#
#
# @views.route("/data", methods=["POST", "GET"])
# def get_data():
#     data = request.json
#     return jsonify({'status': 'success !'})
#
#
# @views.route('/form_example', methods=['POST', 'GET'])
# def handle_form():
#     print(request.form.get('name'))
#     print(request.form.get('age'))
#     return request.form
#
#
# @views.route('/json_example', methods=['POST', 'GET'])
# def handle_json():
#     data = request.json
#     print(data.get('name'))
#     print(data.get('age'))
#     return data
