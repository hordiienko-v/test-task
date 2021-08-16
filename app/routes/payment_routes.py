from app import app
from flask import request, render_template
from app.utils.utils import generate_sign
from app.utils.secret import secret_key, shop_id, payway

@app.route("/pay", methods=["POST"])
def pay():
    data = request.form.to_dict()
    data["amount"] = format(float(data["amount"]),".2f")

    sign = generate_sign(secret_key, amount=data["amount"], currency=data["currency"],
        shop_id=shop_id, shop_order_id="1111")

    return render_template("pay.html", amount=data["amount"], currency=data["currency"],
        shop_id=shop_id, shop_order_id="1111", sign=sign, description=data["description"])

@app.route("/bill", methods=["POST"])
def bill():
    pass

@app.route("/invoice", methods=["POST"])
def invoice():
    pass
