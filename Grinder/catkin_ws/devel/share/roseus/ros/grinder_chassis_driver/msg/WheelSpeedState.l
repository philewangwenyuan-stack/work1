;; Auto-generated. Do not edit!


(when (boundp 'grinder_chassis_driver::WheelSpeedState)
  (if (not (find-package "GRINDER_CHASSIS_DRIVER"))
    (make-package "GRINDER_CHASSIS_DRIVER"))
  (shadow 'WheelSpeedState (find-package "GRINDER_CHASSIS_DRIVER")))
(unless (find-package "GRINDER_CHASSIS_DRIVER::WHEELSPEEDSTATE")
  (make-package "GRINDER_CHASSIS_DRIVER::WHEELSPEEDSTATE"))

(in-package "ROS")
;;//! \htmlinclude WheelSpeedState.msg.html
(if (not (find-package "STD_MSGS"))
  (ros::roseus-add-msgs "std_msgs"))


(defclass grinder_chassis_driver::WheelSpeedState
  :super ros::object
  :slots (_header _target_left_wheel_speed _target_right_wheel_speed _feedback_left_wheel_speed _feedback_right_wheel_speed _feedback_valid ))

(defmethod grinder_chassis_driver::WheelSpeedState
  (:init
   (&key
    ((:header __header) (instance std_msgs::Header :init))
    ((:target_left_wheel_speed __target_left_wheel_speed) 0)
    ((:target_right_wheel_speed __target_right_wheel_speed) 0)
    ((:feedback_left_wheel_speed __feedback_left_wheel_speed) 0)
    ((:feedback_right_wheel_speed __feedback_right_wheel_speed) 0)
    ((:feedback_valid __feedback_valid) nil)
    )
   (send-super :init)
   (setq _header __header)
   (setq _target_left_wheel_speed (round __target_left_wheel_speed))
   (setq _target_right_wheel_speed (round __target_right_wheel_speed))
   (setq _feedback_left_wheel_speed (round __feedback_left_wheel_speed))
   (setq _feedback_right_wheel_speed (round __feedback_right_wheel_speed))
   (setq _feedback_valid __feedback_valid)
   self)
  (:header
   (&rest __header)
   (if (keywordp (car __header))
       (send* _header __header)
     (progn
       (if __header (setq _header (car __header)))
       _header)))
  (:target_left_wheel_speed
   (&optional __target_left_wheel_speed)
   (if __target_left_wheel_speed (setq _target_left_wheel_speed __target_left_wheel_speed)) _target_left_wheel_speed)
  (:target_right_wheel_speed
   (&optional __target_right_wheel_speed)
   (if __target_right_wheel_speed (setq _target_right_wheel_speed __target_right_wheel_speed)) _target_right_wheel_speed)
  (:feedback_left_wheel_speed
   (&optional __feedback_left_wheel_speed)
   (if __feedback_left_wheel_speed (setq _feedback_left_wheel_speed __feedback_left_wheel_speed)) _feedback_left_wheel_speed)
  (:feedback_right_wheel_speed
   (&optional __feedback_right_wheel_speed)
   (if __feedback_right_wheel_speed (setq _feedback_right_wheel_speed __feedback_right_wheel_speed)) _feedback_right_wheel_speed)
  (:feedback_valid
   (&optional (__feedback_valid :null))
   (if (not (eq __feedback_valid :null)) (setq _feedback_valid __feedback_valid)) _feedback_valid)
  (:serialization-length
   ()
   (+
    ;; std_msgs/Header _header
    (send _header :serialization-length)
    ;; int16 _target_left_wheel_speed
    2
    ;; int16 _target_right_wheel_speed
    2
    ;; int16 _feedback_left_wheel_speed
    2
    ;; int16 _feedback_right_wheel_speed
    2
    ;; bool _feedback_valid
    1
    ))
  (:serialize
   (&optional strm)
   (let ((s (if strm strm
              (make-string-output-stream (send self :serialization-length)))))
     ;; std_msgs/Header _header
       (send _header :serialize s)
     ;; int16 _target_left_wheel_speed
       (write-word _target_left_wheel_speed s)
     ;; int16 _target_right_wheel_speed
       (write-word _target_right_wheel_speed s)
     ;; int16 _feedback_left_wheel_speed
       (write-word _feedback_left_wheel_speed s)
     ;; int16 _feedback_right_wheel_speed
       (write-word _feedback_right_wheel_speed s)
     ;; bool _feedback_valid
       (if _feedback_valid (write-byte -1 s) (write-byte 0 s))
     ;;
     (if (null strm) (get-output-stream-string s))))
  (:deserialize
   (buf &optional (ptr- 0))
   ;; std_msgs/Header _header
     (send _header :deserialize buf ptr-) (incf ptr- (send _header :serialization-length))
   ;; int16 _target_left_wheel_speed
     (setq _target_left_wheel_speed (sys::peek buf ptr- :short)) (incf ptr- 2)
   ;; int16 _target_right_wheel_speed
     (setq _target_right_wheel_speed (sys::peek buf ptr- :short)) (incf ptr- 2)
   ;; int16 _feedback_left_wheel_speed
     (setq _feedback_left_wheel_speed (sys::peek buf ptr- :short)) (incf ptr- 2)
   ;; int16 _feedback_right_wheel_speed
     (setq _feedback_right_wheel_speed (sys::peek buf ptr- :short)) (incf ptr- 2)
   ;; bool _feedback_valid
     (setq _feedback_valid (not (= 0 (sys::peek buf ptr- :char)))) (incf ptr- 1)
   ;;
   self)
  )

(setf (get grinder_chassis_driver::WheelSpeedState :md5sum-) "f50663abf771ecfd2d1486cfc892cbc3")
(setf (get grinder_chassis_driver::WheelSpeedState :datatype-) "grinder_chassis_driver/WheelSpeedState")
(setf (get grinder_chassis_driver::WheelSpeedState :definition-)
      "std_msgs/Header header
int16 target_left_wheel_speed
int16 target_right_wheel_speed
int16 feedback_left_wheel_speed
int16 feedback_right_wheel_speed
bool feedback_valid

================================================================================
MSG: std_msgs/Header
# Standard metadata for higher-level stamped data types.
# This is generally used to communicate timestamped data 
# in a particular coordinate frame.
# 
# sequence ID: consecutively increasing ID 
uint32 seq
#Two-integer timestamp that is expressed as:
# * stamp.sec: seconds (stamp_secs) since epoch (in Python the variable is called 'secs')
# * stamp.nsec: nanoseconds since stamp_secs (in Python the variable is called 'nsecs')
# time-handling sugar is provided by the client library
time stamp
#Frame this data is associated with
string frame_id

")



(provide :grinder_chassis_driver/WheelSpeedState "f50663abf771ecfd2d1486cfc892cbc3")


