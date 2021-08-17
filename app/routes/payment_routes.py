from app import app
import requests, json
from flask import request, render_template, redirect, url_for
from app.utils.generate_sign import generate_sign
from app.utils.params import secret_key, shop_id, payway
from app.models.payment import Payment
from datetime import datetime
import logging
from logging import config

logger = logging.getLogger("payments_log")
logger.setLevel(logging.INFO)
handler = logging.FileHandler("payments.log")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

@app.route("/pay", methods=["POST"])
def pay():
    amount = request.form.get("amount")
    description = request.form.get("description")
    currency = request.form.get("currency")

    amount = format(float(amount),".2f")
    sign = generate_sign(secret_key, amount=amount, currency=currency,
        shop_id=shop_id, shop_order_id="1")

    payment = Payment(currency, amount, datetime.now(), description)
    try:
        payment.save_to_db()
        logger.info("method=pay | id={} | amount={} | currency={}".format(payment.id, payment.amount, payment.currency))
        return render_template("pay.html", amount=amount, currency=currency,
            shop_id=shop_id, shop_order_id="1", sign=sign, description=description)
    except Exception as e:
        logger.error("method=pay | error={}".format(e))
        return redirect("/?error=Something+wrong")

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
        try:
            payment.save_to_db()
            logger.info("method=bill | id={} | amount={} | currency={}".format(payment.id, payment.amount, payment.currency))
        except Exception as e:
            logger.error("method=bill | error={}".format(e))
            return redirect("/?error=Something+wrong")
        json_data = response_json["data"]
        return redirect(json_data["url"])
    else:
        logger.error("method=bill | error={}".format(response_json["message"]))
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

    if response_json["result"] == True:
        payment = Payment(currency, amount, datetime.now(), description)
        try:
            payment.save_to_db()
            logger.info("method=invoice | id={} | amount={} | currency={}".format(payment.id, payment.amount, payment.currency))
        except Exception as e:
            logger.error("method=invoice | error={}".format(e))
            return redirect("/?error=Something+wrong")
        json_data = response_json["data"]
        inner_data = json_data["data"]
        return render_template("invoice.html", url=json_data["url"], method=json_data["method"], params=inner_data)
    else:
        logger.error("method=invoice | error={}".format(response_json["message"]))
        return redirect("/?error={}".format(response_json["message"]))
