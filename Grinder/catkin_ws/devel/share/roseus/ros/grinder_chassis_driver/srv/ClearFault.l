;; Auto-generated. Do not edit!


(when (boundp 'grinder_chassis_driver::ClearFault)
  (if (not (find-package "GRINDER_CHASSIS_DRIVER"))
    (make-package "GRINDER_CHASSIS_DRIVER"))
  (shadow 'ClearFault (find-package "GRINDER_CHASSIS_DRIVER")))
(unless (find-package "GRINDER_CHASSIS_DRIVER::CLEARFAULT")
  (make-package "GRINDER_CHASSIS_DRIVER::CLEARFAULT"))
(unless (find-package "GRINDER_CHASSIS_DRIVER::CLEARFAULTREQUEST")
  (make-package "GRINDER_CHASSIS_DRIVER::CLEARFAULTREQUEST"))
(unless (find-package "GRINDER_CHASSIS_DRIVER::CLEARFAULTRESPONSE")
  (make-package "GRINDER_CHASSIS_DRIVER::CLEARFAULTRESPONSE"))

(in-package "ROS")





(defclass grinder_chassis_driver::ClearFaultRequest
  :super ros::object
  :slots ())

(defmethod grinder_chassis_driver::ClearFaultRequest
  (:init
   (&key
    )
   (send-super :init)
   self)
  (:serialization-length
   ()
   (+
    0
    ))
  (:serialize
   (&optional strm)
   (let ((s (if strm strm
              (make-string-output-stream (send self :serialization-length)))))
     ;;
     (if (null strm) (get-output-stream-string s))))
  (:deserialize
   (buf &optional (ptr- 0))
   ;;
   self)
  )

(defclass grinder_chassis_driver::ClearFaultResponse
  :super ros::object
  :slots (_success _message ))

(defmethod grinder_chassis_driver::ClearFaultResponse
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

(defclass grinder_chassis_driver::ClearFault
  :super ros::object
  :slots ())

(setf (get grinder_chassis_driver::ClearFault :md5sum-) "937c9679a518e3a18d831e57125ea522")
(setf (get grinder_chassis_driver::ClearFault :datatype-) "grinder_chassis_driver/ClearFault")
(setf (get grinder_chassis_driver::ClearFault :request) grinder_chassis_driver::ClearFaultRequest)
(setf (get grinder_chassis_driver::ClearFault :response) grinder_chassis_driver::ClearFaultResponse)

(defmethod grinder_chassis_driver::ClearFaultRequest
  (:response () (instance grinder_chassis_driver::ClearFaultResponse :init)))

(setf (get grinder_chassis_driver::ClearFaultRequest :md5sum-) "937c9679a518e3a18d831e57125ea522")
(setf (get grinder_chassis_driver::ClearFaultRequest :datatype-) "grinder_chassis_driver/ClearFaultRequest")
(setf (get grinder_chassis_driver::ClearFaultRequest :definition-)
      "---
bool success
string message

")

(setf (get grinder_chassis_driver::ClearFaultResponse :md5sum-) "937c9679a518e3a18d831e57125ea522")
(setf (get grinder_chassis_driver::ClearFaultResponse :datatype-) "grinder_chassis_driver/ClearFaultResponse")
(setf (get grinder_chassis_driver::ClearFaultResponse :definition-)
      "---
bool success
string message

")



(provide :grinder_chassis_driver/ClearFault "937c9679a518e3a18d831e57125ea522")


