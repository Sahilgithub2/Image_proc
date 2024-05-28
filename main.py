from flask import Flask, render_template, request, flash, redirect, url_for,send_from_directory
from markupsafe import Markup
import os
import cv2
import numpy as np
from PIL import Image
from werkzeug.utils import secure_filename
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'webp', 'jpg', 'jpeg', 'gif','svg'}
app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['STATIC_FOLDER'] = 'static'


@app.route("/", methods=["POST"])
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Image Processing

def ProcessImage(filename,operation):
    print(f"The operation is {operation} and filename is {filename}")
    img = cv2.imread(f"uploads/{filename}")
    match operation:
        case "cgray":
           imgProcessed = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
           newFilename = f"static/{filename}"
           cv2.imwrite(newFilename, imgProcessed)   
           return newFilename
        case "cwebp":
           newFilename = f"static/{filename.split('.')[0]}.webp"
           cv2.imwrite(newFilename, img)   
           return newFilename
        case "cpng":
           newFilename = f"static/{filename.split('.')[0]}.png"
           cv2.imwrite(newFilename, img)   
           return newFilename
        case "cjpg":
           newFilename = f"static/{filename.split('.')[0]}.jpg" 
           cv2.imwrite(newFilename, img)   
           return newFilename
    pass  

@app.route("/Home")
def home():
    return render_template("index.html")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == 'POST':
        operation = request.form.get("operation")
        if 'file' not in request.files:
            flash('No file part')
            return "Error"        
        return redirect("/")
    return render_template("index.html")

@app.route("/edit",methods=["GET","POST"])
def edit():
    if request.method == 'POST':
        operation= request.form.get("operation")
        if 'file' not in request.files:
            flash('No file part')
            return "Error"
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return "Error No File Is Selected"
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new= ProcessImage(filename, operation)
            flash(Markup(f"Your Image Has been Processed and available <a href='/{new}' target='_blank'>here</a>"))   
        else:
            flash("File Not Allowed Please Upload a valid image")
            return render_template("index.html")
    return render_template("index.html")


#Image resizing
def resize_image(input_image, output_image, width, height):
    img = Image.open(input_image)
    resized_img = img.resize((width, height), Image.NEAREST)
    resized_img.save(output_image)
@app.route("/download/<filename>", methods=["GET"])
def download(filename):
    return send_from_directory(app.config['STATIC_FOLDER'], filename, as_attachment=True)
@app.route("/resize", methods=["POST"])
def resize():
    if request.method == 'POST':
        if 'input-image' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)

        input_file = request.files['input-image']
        width = int(request.form.get('width'))
        height = int(request.form.get('height'))

        if input_file.filename == '' or not allowed_file(input_file.filename):
            flash('Invalid file format', 'error')
            return redirect(request.url)

        input_filename = secure_filename(input_file.filename)
        input_filepath = os.path.join(app.config['UPLOAD_FOLDER'], input_filename)
        input_file.save(input_filepath)

        resized_filename = f"resized_{input_filename}"
        resized_filepath = os.path.join(app.config['STATIC_FOLDER'], resized_filename)
        resize_image(input_filepath, resized_filepath, width, height)
        flash('Image resized and saved successfully!', 'success')
        return render_template('index.html', resized_image=resized_filename,download_link=resized_filename)

    return render_template('index.html', resized_image=None)


# Reloading
@app.route('/reload', methods=['GET'])
def reload_page():
    return redirect(url_for('index'))
if __name__ == "__main__":       
    app.run(debug=True,port=5500)

    