from flask import Flask, request, render_template, send_file
from PIL import Image
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def jpeg_to_pdf(image_folder, output_pdf):
    image_files = [f for f in os.listdir(image_folder) if f.lower().endswith('.jpg') or f.lower().endswith('.jpeg')]
    image_files.sort()
    images = []
    image_paths = []  

    for image_file in image_files:
        image_path = os.path.join(image_folder, image_file)
        img = Image.open(image_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        images.append(img)
        image_paths.append(image_path)

    if images:
        images[0].save(output_pdf, save_all=True, append_images=images[1:])
        return image_paths  
    return []

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        files = request.files.getlist('file')
        for file in files:
            if file and file.filename.lower().endswith(('.jpg', '.jpeg')):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        output_pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], 'output.pdf')
        image_paths = jpeg_to_pdf(app.config['UPLOAD_FOLDER'], output_pdf_path)

        # Delete the JPEG files after the PDF is created
        for image_path in image_paths:
            os.remove(image_path)

        if image_paths:
            return render_template('upload.html', download_link=output_pdf_path)
        else:
            return "No images were found to convert."

    return render_template('upload.html')

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
