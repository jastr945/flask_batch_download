import os
import io
import json
import base64
import requests
import zipfile
from . import config
from flask import Flask, Response
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_CONFIG['uri']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class report(db.Model):
    """Report model corresponding to the 'report' database table."""

    record_id = db.Column(db.String, primary_key=True)
    if_deleted = db.Column(db.String)
    record_author = db.Column(db.String)
    record_date = db.Column(db.String)

    def __init__(self, record_id, if_deleted, record_author, record_date):
        self.record_id = record_id
        self.if_deleted = if_deleted
        self.record_author = record_author
        self.record_date = record_date


@app.route("/", methods=['POST', 'GET'])
def download_documents():
    """Saving JSReport payload into a file.
    Adding the file to a Zipfile object."""

    template_id = config.JSREPORT_CONFIG['template']
    reports = report.query.filter_by(if_deleted="F").all()
    zip_io = io.BytesIO()
    with zipfile.ZipFile(zip_io, mode='w',
                         compression=zipfile.ZIP_DEFLATED) as backup_zip:
        for r in reports:
            record_id = r.record_id
            pdf = create_pdf(template_id, record_id)
            saved_filename = '{}_{}.pdf'.format(r.record_author, r.record_date)
            if saved_filename in backup_zip.namelist():
                saved_filename = '{}_{}[1].pdf'.format(r.record_author, r.record_date)  # handling same names
            with open(saved_filename, 'wb') as f:
                f.write(pdf)
            backup_zip.write(saved_filename)
            os.remove(saved_filename)
    backup_zip.close()
    response = Response(zip_io.getvalue(),
                        content_type='application/x-zip-compressed',
                        status=200,
                        headers={"Content-disposition": "attachment;\
                        filename={}".format(config.ZIP_CONFIG['name'])})
    return response


def create_pdf(template_id, record_id):
    """Sending data to JSReport server."""

    url = config.JSREPORT_CONFIG['uri']
    username = config.JSREPORT_CONFIG['username']
    password = config.JSREPORT_CONFIG['password']
    string_data = '{}:{}'.format(username, password)
    encoded = base64.b64encode(string_data.encode())
    js_headers = {"Content-Type": "application/json",
                  "Authorization":"Basic {}".format(encoded)}
    payload = {"template": {"shortid": template_id},
                            "data": {"id": record_id}}
    req = requests.request("POST", url, headers=js_headers,
                                        data=json.dumps(payload))
    return req.content
