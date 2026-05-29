;; Auto-generated. Do not edit!


(when (boundp 'slamware_ros_sdk::SyncGetStcm)
  (if (not (find-package "SLAMWARE_ROS_SDK"))
    (make-package "SLAMWARE_ROS_SDK"))
  (shadow 'SyncGetStcm (find-package "SLAMWARE_ROS_SDK")))
(unless (find-package "SLAMWARE_ROS_SDK::SYNCGETSTCM")
  (make-package "SLAMWARE_ROS_SDK::SYNCGETSTCM"))
(unless (find-package "SLAMWARE_ROS_SDK::SYNCGETSTCMREQUEST")
  (make-package "SLAMWARE_ROS_SDK::SYNCGETSTCMREQUEST"))
(unless (find-package "SLAMWARE_ROS_SDK::SYNCGETSTCMRESPONSE")
  (make-package "SLAMWARE_ROS_SDK::SYNCGETSTCMRESPONSE"))

(in-package "ROS")





(defclass slamware_ros_sdk::SyncGetStcmRequest
  :super ros::object
  :slots (_mapfile ))

(defmethod slamware_ros_sdk::SyncGetStcmRequest
  (:init
   (&key
    ((:mapfile __mapfile) "")
    )
   (send-super :init)
   (setq _mapfile (string __mapfile))
   self)
  (:mapfile
   (&optional __mapfile)
   (if __mapfile (setq _mapfile __mapfile)) _mapfile)
  (:serialization-length
   ()
   (+
    ;; string _mapfile
    4 (length _mapfile)
    ))
  (:serialize
   (&optional strm)
   (let ((s (if strm strm
              (make-string-output-stream (send self :serialization-length)))))
     ;; string _mapfile
       (write-long (length _mapfile) s) (princ _mapfile s)
     ;;
     (if (null strm) (get-output-stream-string s))))
  (:deserialize
   (buf &optional (ptr- 0))
   ;; string _mapfile
     (let (n) (setq n (sys::peek buf ptr- :integer)) (incf ptr- 4) (setq _mapfile (subseq buf ptr- (+ ptr- n))) (incf ptr- n))
   ;;
   self)
  )

(defclass slamware_ros_sdk::SyncGetStcmResponse
  :super ros::object
  :slots (_success _message ))

(defmethod slamware_ros_sdk::SyncGetStcmResponse
  (:init
   (&key
    ((:success __success) nil)
    ((:message __message) "")
    )
   (send-super :init)
   (setq _success __success)
   (setq _message (string __message))
   self)
  (:success
   (&optional (__success :null))
   (if (not (eq __success :null)) (setq _success __success)) _success)
  (:message
   (&optional __message)
   (if __message (setq _message __message)) _message)
  (:serialization-length
   ()
   (+
    ;; bool _success
    1
    ;; string _message
    4 (length _message)
    ))
  (:serialize
   (&optional strm)
   (let ((s (if strm strm
              (make-string-output-stream (send self :serialization-length)))))
     ;; bool _success
       (if _success (write-byte -1 s) (write-byte 0 s))
     ;; string _message
       (write-long (length _message) s) (princ _message s)
     ;;
     (if (null strm) (get-output-stream-string s))))
  (:deserialize
   (buf &optional (ptr- 0))
   ;; bool _success
     (setq _success (not (= 0 (sys::peek buf ptr- :char)))) (incf ptr- 1)
   ;; string _message
     (let (n) (setq n (sys::peek buf ptr- :integer)) (incf ptr- 4) (setq _message (subseq buf ptr- (+ ptr- n))) (incf ptr- n))
   ;;
   self)
  )

(defclass slamware_ros_sdk::SyncGetStcm
  :super ros::object
  :slots ())

(setf (get slamware_ros_sdk::SyncGetStcm :md5sum-) "919cbda8c3832c78ab0496dedc3e5520")
(setf (get slamware_ros_sdk::SyncGetStcm :datatype-) "slamware_ros_sdk/SyncGetStcm")
(setf (get slamware_ros_sdk::SyncGetStcm :request) slamware_ros_sdk::SyncGetStcmRequest)
(setf (get slamware_ros_sdk::SyncGetStcm :response) slamware_ros_sdk::SyncGetStcmResponse)

(defmethod slamware_ros_sdk::SyncGetStcmRequest
  (:response () (instance slamware_ros_sdk::SyncGetStcmResponse :init)))

(setf (get slamware_ros_sdk::SyncGetStcmRequest :md5sum-) "919cbda8c3832c78ab0496dedc3e5520")
(setf (get slamware_ros_sdk::SyncGetStcmRequest :datatype-) "slamware_ros_sdk/SyncGetStcmRequest")
(setf (get slamware_ros_sdk::SyncGetStcmRequest :definition-)
      "# Request
string mapfile

---

# Response
bool success
string message

")

(setf (get slamware_ros_sdk::SyncGetStcmResponse :md5sum-) "919cbda8c3832c78ab0496dedc3e5520")
(setf (get slamware_ros_sdk::SyncGetStcmResponse :datatype-) "slamware_ros_sdk/SyncGetStcmResponse")
(setf (get slamware_ros_sdk::SyncGetStcmResponse :definition-)
      "# Request
string mapfile

---

# Response
bool success
string message

")



(provide :slamware_ros_sdk/SyncGetStcm "919cbda8c3832c78ab0496dedc3e5520")


