from app import app
import requests, json
from flask import request, render_template, redirect
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
    data = request.form.to_dict()
    data["amount"] = format(float(data["amount"]),".2f")

    sign = generate_sign(secret_key, shop_id=shop_id, shop_amount=data["amount"],
        shop_currency=data["currency"], shop_order_id="1111", payer_currency=data["currency"])

    headers = {"Content-Type": "application/json"}
    payload = {
        "shop_id": shop_id,
        "shop_amount": data["amount"],
        "shop_currency": data["currency"],
        "payer_currency": data["currency"],
        "sign": sign,
        "shop_order_id": "1111",
        "description": data["description"],
        "payer_account": "201494711279"
    }
    session = requests.Session()
    response = session.post("https://core.piastrix.com/bill/create", headers=headers, data=json.dumps(payload))
    json_data = response.json()["data"]

    return redirect(json_data["url"])

@app.route("/invoice", methods=["POST"])
def invoice():
    data = request.form.to_dict()
    data["amount"] = format(float(data["amount"]),".2f")

    params = data.copy()

    sign = generate_sign(secret_key, shop_id=shop_id, amount=data["amount"],
        currency=data["currency"], shop_order_id="1", payway=payway)

    params["sign"] = sign
    params["payway"] = payway
    params["shop_id"] = shop_id
    params["shop_order_id"] = "1"

    headers = {"Content-Type": "application/json"}
    # payload = {
    #     "currency": data["currency"],
    #     "payway": payway,
    #     "amount": data["amount"],
    #     "shop_id": shop_id,
    #     "shop_order_id": "1",
    #     "description": data["description"],
    #     "sign": sign
    # }
    session = requests.Session()
    response = session.post("https://core.piastrix.com/invoice/create", headers=headers, data=json.dumps(params))
    print(response.json())
    json_data = response.json()["data"]
    inner_data = json_data["data"]
    # return render_template("invoice.html", url=json_data["url"], ac_account_email=inner_data["ac_account_email"],
    #     ac_amount=inner_data["ac_amount"], ac_currency=inner_data["ac_currency"], ac_order_id=inner_data["ac_order_id"],
    #     ac_sci_name=inner_data["ac_sci_name"])
    return render_template("invoice.html", url=json_data["url"], method=json_data["method"], params=inner_data)
