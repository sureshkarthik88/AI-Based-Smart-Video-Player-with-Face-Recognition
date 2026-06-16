AI Based Smart Video Player With Face Recognition

Files:
- main.py
- camera.py
- camera2.py
- camera3.py
- templates/
- static/

Database:
- Import schema.sql
- Create MySQL database age_wise_video

Notes:
- Put OpenCV model files in the project root:
  - opencv_face_detector.pbtxt
  - opencv_face_detector_uint8.pb
  - age_deploy.prototxt
  - age_net.caffemodel
  - gender_deploy.prototxt
  - gender_net.caffemodel
- Put uploaded videos inside static/upload/
- Put played videos inside static/video/
