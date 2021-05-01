from flask import Flask, render_template, request, flash, logging, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from werkzeug.security import generate_password_hash, check_password_hash 
from functools import wraps
from datetime import datetime
from pyzbar import pyzbar
from werkzeug.utils import secure_filename
import os
import cv2
import fitz
import pandas as pd

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ey.db'
app.secret_key = "151FAHUI216892GAOP"
db = SQLAlchemy(app)

class Data(db.Model):
    __tablename__ = 'data'
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(80), nullable=False)
    has_qr_code = db.Column(db.Boolean, nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) 
    
db.create_all()

@app.route("/")
def home(): 
    return render_template('index.html')

@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
      files = request.files.getlist('file')
      for f in files:
        data = Data()
        data.file_name = f.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename))
        f.save(file_path)
        doc = fitz.open(file_path)
        image_list = doc.getPageImageList(0)
        for image in image_list:
            xref = image[0]
            pix = fitz.Pixmap(doc, xref)
            if pix.n < 5:
                pix.writeImage(f'{xref}.png')
                image = cv2.imread(f'{xref}.png')
                barcodes = pyzbar.decode(image)
                if len(barcodes) > 0:
                    for barcode in barcodes:
                        df = pd.DataFrame({'qrcode': [barcode.data.decode('utf-8')], 'file_name': [f.filename]})
                        df.to_csv('result.csv')
                        data.has_qr_code = True
                        db.session.add(data)
                        db.session.commit()
                else:
                    print("No barcode")
        data.has_qr_code = False
        db.session.add(data)
        db.session.commit()
      return 'file uploaded successfully'

if __name__ == '__main__':
    app.run(debug=True)