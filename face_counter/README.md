# Use with python request

```pyhon
import requests

url = "http://localhost:5001/face_counter/"

files = {'file': open('image_persons.jpg', 'rb')}

r = requests.post(url, files=files)

print r.json()


```


using curl

```bash
curl -X POST -F "file=@image_persons.jpg" http://localhost:5001/face_counter/ 

```
