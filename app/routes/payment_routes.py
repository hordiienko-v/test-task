from app import app
import requests, json
from flask import request, render_template, redirect
from app.utils.utils import generate_sign
from app.utils.secret import secret_key, shop_id, payway

@app.route("/pay", methods=["POST"])
def pay():
    amount = request.form.get("amount")
    description = request.form.get("description")
    currency = request.form.get("currency")

    amount = format(float(amount),".2f")
    sign = generate_sign(secret_key, amount=amount, currency=currency,
        shop_id=shop_id, shop_order_id="1")

    return render_template("pay.html", amount=amount, currency=currency,
        shop_id=shop_id, shop_order_id="1", sign=sign, description=description)

@app.route("/bill", methods=["POST"])
def bill():
    amount = request.form.get("amount")
    description = request.form.get("description")
    currency = request.form.get("currency")

    amount = format(float(amount),".2f")

    sign = generate_sign(secret_key, shop_amount=amount, shop_currency=currency,
        shop_id=shop_id, shop_order_id="1", payer_currency=currency)

    headers = {"Content-Type": "application/json"}
    payload = {
        "shop_id": shop_id,
        "shop_amount": amount,
        "shop_currency": currency,
        "payer_currency": currency,
        "sign": sign,
        "shop_order_id": "1",
        "description": description,
        "payer_account": "201494711279"
    }
    session = requests.Session()
    response = session.post("https://core.piastrix.com/bill/create", headers=headers, data=json.dumps(payload))

    if response.json()["message"] == "Ok":
        json_data = response.json()["data"]
        return redirect(json_data["url"])
    else:
        pass

@app.route("/invoice", methods=["POST"])
def invoice():
    amount = request.form.get("amount")
    description = request.form.get("description")
    currency = request.form.get("currency")

    amount = format(float(amount),".2f")
    sign = generate_sign(secret_key, amount=amount, currency=currency,
        shop_id=shop_id, shop_order_id="1", payway=payway)

    headers = {"Content-Type": "application/json"}
    payload = {
        "shop_id": shop_id,
        "amount": amount,
        "currency": currency,
        "sign": sign,
        "shop_order_id": "1",
        "description": description,
        "payway": payway
    }

    session = requests.Session()
    response = session.post("https://core.piastrix.com/invoice/create", headers=headers, data=json.dumps(payload))

    print(response.json())
    if response.json()["message"] == "Ok":
        json_data = response.json()["data"]
        inner_data = json_data["data"]

        return render_template("invoice.html", url=json_data["url"], method=json_data["method"], params=inner_data)
    else:
        pass
