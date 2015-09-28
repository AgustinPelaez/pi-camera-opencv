from flask import Flask, request
from flask import jsonify

import os
import cv2
import tempfile
import requests


UPLOAD_FOLDER = '/tmp/'
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png'])
API_URL_UBIDOTS = 'http://things.ubidots.com/api/v1.6'
FACE_CASCADE = cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_frontalface_alt2.xml')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route("/images/face_counter/<string:variable>/<string:token>", methods=['GET', 'POST'])
def index(variable, token):
    if request.method == 'POST':
        rsp = requests.get(
            '{api_url}/variables/{variable}'.format(api_url=API_URL_UBIDOTS, variable=variable),
            headers={'x-auth-token': token}
        )

        # if the token not authorized or the variable does not exist
        if rsp.status_code != 200:
            response = jsonify({"error": rsp.json()})
            response.status_code = rsp.status_code
            return response

        file_req = request.files['file']
        if file_req and allowed_file(file_req.filename):
            f = tempfile.NamedTemporaryFile(delete=False)
            file_req.save(f.name)

            # Read the image
            image = cv2.imread(f.name)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Detect faces in the image
            faces = FACE_CASCADE.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30),
                flags=cv2.cv.CV_HAAR_SCALE_IMAGE
            )

            os.unlink(f.name)
            rsp = requests.post(
                '{api_url}/variables/{variable}/values'.format(api_url=API_URL_UBIDOTS, variable=variable),
                data={'value': len(faces)},
                headers={'x-auth-token': token}
            )

            response = jsonify({"faces": len(faces), "api": rsp.json()})
            response.status_code = rsp.status_code
        else:
            response = jsonify({"error": 'extension not allowed'})
            response.status_code = 403
        return response

    return jsonify({"usage": "POST /face_counter/"})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
