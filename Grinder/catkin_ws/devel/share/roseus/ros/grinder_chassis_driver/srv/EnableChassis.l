;; Auto-generated. Do not edit!


(when (boundp 'grinder_chassis_driver::EnableChassis)
  (if (not (find-package "GRINDER_CHASSIS_DRIVER"))
    (make-package "GRINDER_CHASSIS_DRIVER"))
  (shadow 'EnableChassis (find-package "GRINDER_CHASSIS_DRIVER")))
(unless (find-package "GRINDER_CHASSIS_DRIVER::ENABLECHASSIS")
  (make-package "GRINDER_CHASSIS_DRIVER::ENABLECHASSIS"))
(unless (find-package "GRINDER_CHASSIS_DRIVER::ENABLECHASSISREQUEST")
  (make-package "GRINDER_CHASSIS_DRIVER::ENABLECHASSISREQUEST"))
(unless (find-package "GRINDER_CHASSIS_DRIVER::ENABLECHASSISRESPONSE")
  (make-package "GRINDER_CHASSIS_DRIVER::ENABLECHASSISRESPONSE"))

(in-package "ROS")





(defclass grinder_chassis_driver::EnableChassisRequest
  :super ros::object
  :slots (_enable ))

(defmethod grinder_chassis_driver::EnableChassisRequest
  (:init
   (&key
    ((:enable __enable) nil)
    )
   (send-super :init)
   (setq _enable __enable)
   self)
  (:enable
   (&optional (__enable :null))
   (if (not (eq __enable :null)) (setq _enable __enable)) _enable)
  (:serialization-length
   ()
   (+
    ;; bool _enable
    1
    ))
  (:serialize
   (&optional strm)
   (let ((s (if strm strm
              (make-string-output-stream (send self :serialization-length)))))
     ;; bool _enable
       (if _enable (write-byte -1 s) (write-byte 0 s))
     ;;
     (if (null strm) (get-output-stream-string s))))
  (:deserialize
   (buf &optional (ptr- 0))
   ;; bool _enable
     (setq _enable (not (= 0 (sys::peek buf ptr- :char)))) (incf ptr- 1)
   ;;
   self)
  )

(defclass grinder_chassis_driver::EnableChassisResponse
  :super ros::object
  :slots (_success _message ))

(defmethod grinder_chassis_driver::EnableChassisResponse
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

(defclass grinder_chassis_driver::EnableChassis
  :super ros::object
  :slots ())

(setf (get grinder_chassis_driver::EnableChassis :md5sum-) "66bc8d9da0bd59298d38df02f3ee7f7f")
(setf (get grinder_chassis_driver::EnableChassis :datatype-) "grinder_chassis_driver/EnableChassis")
(setf (get grinder_chassis_driver::EnableChassis :request) grinder_chassis_driver::EnableChassisRequest)
(setf (get grinder_chassis_driver::EnableChassis :response) grinder_chassis_driver::EnableChassisResponse)

(defmethod grinder_chassis_driver::EnableChassisRequest
  (:response () (instance grinder_chassis_driver::EnableChassisResponse :init)))

(setf (get grinder_chassis_driver::EnableChassisRequest :md5sum-) "66bc8d9da0bd59298d38df02f3ee7f7f")
(setf (get grinder_chassis_driver::EnableChassisRequest :datatype-) "grinder_chassis_driver/EnableChassisRequest")
(setf (get grinder_chassis_driver::EnableChassisRequest :definition-)
      "bool enable
---
bool success
string message

")

(setf (get grinder_chassis_driver::EnableChassisResponse :md5sum-) "66bc8d9da0bd59298d38df02f3ee7f7f")
(setf (get grinder_chassis_driver::EnableChassisResponse :datatype-) "grinder_chassis_driver/EnableChassisResponse")
(setf (get grinder_chassis_driver::EnableChassisResponse :definition-)
      "bool enable
---
bool success
string message

")



(provide :grinder_chassis_driver/EnableChassis "66bc8d9da0bd59298d38df02f3ee7f7f")


