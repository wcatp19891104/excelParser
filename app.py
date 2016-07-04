import excel_parser

import os
from flask import Flask, request, redirect, url_for, render_template, send_from_directory
import flask_mail
from werkzeug import secure_filename

UPLOAD_FOLDER = '/home/zaicheng/repo/'
ALLOWED_EXTENSIONS = set(['txt', 'csv'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
mail = flask_mail.Mail()
mail.init_app(app)

def send_mail(files, recipients):
    msg = flask_mail.Message("hello",
                             sender="zaicheng.wang@example.com",
                             recipients=[recipients])
    for file in files:
        with app.open_resource(file) as fp:
            msg.attach(file, 'text', fp.read())
    mail.send(msg)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def process(file, step_number, step_repeat, currency_ratio):
        excel_parser.retrieve_by_step(file, [(step_number, step_repeat, currency_ratio)])
        # send_mail([file], "wcatp19891104@gmail.com")

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        files = request.files.getlist("my_file[]")
        step_number = request.form.get("step_number")
        step_repeat = request.form.get("step_repeat")
        currency_ratio = request.form.get("currency_ratio")
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                process(os.path.join(app.config['UPLOAD_FOLDER'], filename), step_number, step_repeat, currency_ratio)
    file_path = os.listdir(app.config['UPLOAD_FOLDER'],)
    file_path = generate_links(file_path)
    return render_template('index.html', file_path=file_path)

def generate_links(file_names):
    results = list()
    for file_name in file_names:
        results.append(
            "/download/" + file_name
        )
    return results

@app.route("/download/<file>", methods=['GET', 'POST'])
def download(file):
    uploads = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
    a = send_from_directory(directory=uploads, filename=file)
    return a

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)

