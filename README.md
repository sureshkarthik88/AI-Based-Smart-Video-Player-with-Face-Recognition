# AI-Based-Smart-Video-Player-with-Face-Recognition
Developed a smart video player with face recognition-based user authentication. Implemented automatic play and pause functionality using real-time face detection. Enabled secure access control for authorized users only. Integrated camera monitoring for continuous user presence detection.

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
