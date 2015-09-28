import os
import cv2
import tempfile

from flask import Flask, request, redirect, url_for
from flask import jsonify
from werkzeug import secure_filename

UPLOAD_FOLDER = '/tmp/'
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png'])
FACE_CASCADE = cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_frontalface_alt2.xml')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route("/face_counter/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            f = tempfile.NamedTemporaryFile(delete=False)
            file.save(f.name)
            
            # Read the image
            image = cv2.imread(f.name)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Detect faces in the image
            faces = FACE_CASCADE.detectMultiScale(
               gray,
               scaleFactor=1.1,
               minNeighbors=5,
               minSize=(30, 30),
               flags = cv2.cv.CV_HAAR_SCALE_IMAGE
            )
            os.unlink(f.name)
            return jsonify({"faces": len(faces)})
        else:
            return jsonify({"error": 'extension not allowed'})
             

    return jsonify({"usage": "POST /face_counter/"})
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)

