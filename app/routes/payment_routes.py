from app import app
import requests, json
from flask import request, render_template, redirect, url_for
from app.utils.generate_sign import generate_sign
from app.utils.params import secret_key, shop_id, payway
from app.models.payment import Payment
from datetime import datetime
import logging
from logging import config

 # setting up the logger
logger = logging.getLogger("gunicorn.info")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s --- %(levelname)s --- %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

@app.route("/pay", methods=["POST"])
def pay():
    # retrieving data from a form
    amount = request.form.get("amount")
    description = request.form.get("description")
    currency = request.form.get("currency")
    # formatting an amount
    amount = format(float(amount),".2f")
    # sign generating
    sign = generate_sign(secret_key, amount=amount, currency=currency,
        shop_id=shop_id, shop_order_id="1")

    payment = Payment(currency, amount, datetime.now(), description)
    # trying to save a payment to db
    try:
        payment.save_to_db()
        logger.info("method=pay, REQUEST, id={}, amount={}, currency={}".format(payment.id, payment.amount, payment.currency))
        # returning a form with autosubmitting
        return render_template("pay.html", amount=amount, currency=currency,
            shop_id=shop_id, shop_order_id="1", sign=sign, description=description)
    except Exception as e:
        logger.error("method=pay, error={}".format(e))
        return redirect("/?error=Something+wrong")

@app.route("/bill", methods=["POST"])
def bill():
    # retrieving data from a form
    amount = request.form.get("amount")
    description = request.form.get("description")
    currency = request.form.get("currency")
    # formatting an amount
    amount = format(float(amount),".2f")
    # sign generating
    sign = generate_sign(secret_key, shop_amount=amount, shop_currency=currency,
        shop_id=shop_id, shop_order_id="1", payer_currency=currency)

    # creating headers and payload for future request
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
    logger.info("method=bill, REQUEST, data={}".format(payload))
    # sending a request and achieving a response
    session = requests.Session()
    response = session.post("https://core.piastrix.com/bill/create", headers=headers, data=json.dumps(payload))
    response_json = response.json()
    logger.info("method=bill, RESPONSE, data={}".format(response_json))
    # checking response state
    if response_json["result"] == True:
        payment = Payment(currency, amount, datetime.now(), description)
        # trying to save a payment to db
        try:
            payment.save_to_db()
        except Exception as e:
            logger.error("method=bill, error={}".format(e))
            return redirect("/?error=Something+wrong")
        json_data = response_json["data"]
        # if all is good, redirecting to the obtained url
        return redirect(json_data["url"])
    else:
        logger.error("method=bill, data={}".format(response_json))
        return redirect("/?error={}".format(response_json["message"]))

@app.route("/invoice", methods=["POST"])
def invoice():
    # retrieving data from a form
    amount = request.form.get("amount")
    description = request.form.get("description")
    currency = request.form.get("currency")
    # formatting an amount
    amount = format(float(amount),".2f")
    # sign generating
    sign = generate_sign(secret_key, amount=amount, currency=currency,
        shop_id=shop_id, shop_order_id="1", payway=payway)
    # creating headers and payload for future request
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
    logger.info("method=invoice, REQUEST, data={}".format(payload))
    # sending a request and achieving a response
    session = requests.Session()
    response = session.post("https://core.piastrix.com/invoice/create", headers=headers, data=json.dumps(payload))
    response_json = response.json()
    logger.info("method=bill, RESPONSE, data={}".format(response_json))
    # checking response state
    if response_json["result"] == True:
        payment = Payment(currency, amount, datetime.now(), description)
        # trying to save a payment to db
        try:
            payment.save_to_db()
        except Exception as e:
            logger.error("method=invoice, error={}".format(e))
            return redirect("/?error=Something+wrong")
        json_data = response_json["data"]
        inner_data = json_data["data"]
        # returning a form with autosubmitting 
        return render_template("invoice.html", url=json_data["url"], method=json_data["method"], params=inner_data)
    else:
        logger.error("method=invoice, data={}".format(response_json))
        return redirect("/?error={}".format(response_json["message"]))
