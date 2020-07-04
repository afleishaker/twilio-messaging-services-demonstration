from contact import Contact
from contact_method import ContactMethod
from flask import Flask, render_template, request, flash, jsonify
from pyngrok import ngrok
from flask_pyngrok import PyNgrok
import os
import yaml
import time


responses = dict()
contact = None


def init_app(app):
    app.config['FLASK_ENV'] = os.environ.get('FLASK_ENV')
    app.secret_key = os.urandom(24)
    app.jinja_options['extensions'].append('jinja2.ext.with_')
    if app.config.get('FLASK_ENV') == 'development':
        pyngrok = PyNgrok()
        pyngrok.init_app(app=app)
        app.config['BASE_URL'] = ngrok.get_tunnels()[0].public_url
    else:
        print("* ngrok not development environment, defaulting to given URL")
        app.config['BASE_URL'] = os.environ.get('BASE_URL')
    app.run(debug=True,
         port=5000,
         use_reloader=False)


config = yaml.load(open("config.yaml"), Loader=yaml.FullLoader)
app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    global contact
    if contact is None:
        contact = Contact(app)
    if request.method == 'POST':
        form = request.form
        contact_method = ContactMethod(form.get('contactMethod'))
        response, error = contact.send_message(form, contact_method)
        if error is None:
            flash(f"Your contact was successful! It should be received shortly.", category='info')
        else:
            flash(f"Your contact failed with the following errors: {error}", category='error')
    return render_template('index.html',
                           phone_number=contact.phone_number,
                           whatsapp_phone_number=contact.whatsapp_phone_number)


@app.route('/responses/<phone_number>', methods=['GET'])
def yield_responses(phone_number):
    result = responses.get(phone_number)
    if result is None:
        result = []
    else:
        responses[phone_number] = []
    return jsonify(result)


@app.route('/receive_text', methods=['POST'])
def receive_text():
    body = request.form.get('Body')
    to = request.form.get('To')
    timestamp = time.time()
    response = {
        'Body': body,
        'To': to,
        'Timestamp': timestamp,
    }
    if 'whatsapp:' in request.form.get('From'):
        response['ContactMethod'] = 'WhatsApp'
        response['From'] = request.form.get('From').replace('whatsapp:', '')
        to = to.replace('whatsapp:', '')
    else:
        if 'SmsStatus' in request.form:
            response['ContactMethod'] = 'SMS'
        else:
            response['ContactMethod'] = 'Voice'
        response['From'] = request.form.get('From')
    if to in responses:
        responses[to].append(response)
    else:
        responses[to] = [response]
    return jsonify(responses)


@app.route('/receive_call', methods=['POST'])
def receive_call():
    return receive_text()


init_app(app)
