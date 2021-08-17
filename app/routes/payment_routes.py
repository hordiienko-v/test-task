from app import app
import requests, json
from flask import request, render_template, redirect, url_for
from app.utils.generate_sign import generate_sign
from app.utils.params import secret_key, shop_id, payway
from app.models.payment import Payment
from datetime import datetime

@app.route("/pay", methods=["POST"])
def pay():
    amount = request.form.get("amount")
    description = request.form.get("description")
    currency = request.form.get("currency")

    amount = format(float(amount),".2f")
    sign = generate_sign(secret_key, amount=amount, currency=currency,
        shop_id=shop_id, shop_order_id="1")

    payment = Payment(currency, amount, datetime.now(), description)
    payment.save_to_db()

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
    response_json = response.json()

    if response_json["result"] == True:
        payment = Payment(currency, amount, datetime.now(), description)
        payment.save_to_db()
        json_data = response_json["data"]
        return redirect(json_data["url"])
    else:
        return redirect("/?error={}".format(response_json["message"]))

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
    response_json = response.json()
    # print(response_json)

    if response_json["result"] == True:
        payment = Payment(currency, amount, datetime.now(), description)
        payment.save_to_db()
        json_data = response_json["data"]
        inner_data = json_data["data"]
        return render_template("invoice.html", url=json_data["url"], method=json_data["method"], params=inner_data)
    else:
        return redirect("/?error={}".format(response_json["message"]))
