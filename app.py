from flask import Flask, render_template, request, flash, logging, redirect, session, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from pyzbar import pyzbar
from werkzeug.utils import secure_filename
import os
import cv2
import fitz
import pandas as pd

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['TEMPLATES_AUTO_RELOAD'] = True
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

# ROUTES

@app.route("/", methods = ['GET', 'POST'])
def home(): 
    total_docs = Data.query.count()
    with_qr_code = Data.query.filter_by(has_qr_code = True).count()
    without_qr_code = total_docs - with_qr_code
    context = {'total_docs': total_docs, 'with_qr_code': with_qr_code, 'without_qr_code': without_qr_code}
    return render_template('index.html', context=context)

@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'POST':

      files = request.files.getlist('files[]')

    #   print(files)

      for f in files:
        has_qr_code = False
        file_path = save_file(f)
        doc = fitz.open(file_path)
        image_list = doc.getPageImageList(0)
        for image in image_list:
            image = save_extracted_image(doc, image[0])
            barcodes = pyzbar.decode(image)
            if len(barcodes) > 0:
                for barcode in barcodes:
                    generate_excel_file(barcode.data.decode('utf-8'), f.filename)
                    has_qr_code = True
        
        save_to_db(f.filename, has_qr_code)

      return jsonify(status=200)


# UTLIS FUNCTIONS

def save_file(file):

    file_path = os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(file.filename))

    file.save(file_path)

    return file_path

def generate_excel_file(data, filename):

    df = pd.DataFrame({'qrcode': [data], 'file_name': [filename]})

    df.to_excel('output.xlsx')

def save_to_db(filename, has_qr_code):

    data = Data(file_name=filename, has_qr_code=has_qr_code)

    db.session.add(data)

    db.session.commit()

def save_extracted_image(doc, xref):

    pix = fitz.Pixmap(doc, xref)

    if pix.n < 5:
        pix.writeImage(os.path.join(app.config['UPLOAD_FOLDER'], 'images', f'{xref}.png'))
    
    image = cv2.imread(os.path.join(app.config['UPLOAD_FOLDER'], 'images', f'{xref}.png'))    
    
    return image

if __name__ == '__main__':
    app.run(debug=True)