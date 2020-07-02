from flask import Flask, render_template, request, flash
from ContactMethod import *
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.jinja_options['extensions'].append('jinja2.ext.with_')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        form = request.form
        contactMethod = form.get('contactMethod')
        response, error = ContactMethod(contactMethod).send_message(form)
        if error is None:
            flash(f"Your contact was successful! It should be received shortly.", category="info")
        else:
            flash(f"Your contact failed with the following errors: {error}", category="error")
    return render_template('index.html')

if __name__ == '__main__':
    app.run()
