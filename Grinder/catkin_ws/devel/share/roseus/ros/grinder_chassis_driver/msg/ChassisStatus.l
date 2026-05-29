;; Auto-generated. Do not edit!


(when (boundp 'grinder_chassis_driver::ChassisStatus)
  (if (not (find-package "GRINDER_CHASSIS_DRIVER"))
    (make-package "GRINDER_CHASSIS_DRIVER"))
  (shadow 'ChassisStatus (find-package "GRINDER_CHASSIS_DRIVER")))
(unless (find-package "GRINDER_CHASSIS_DRIVER::CHASSISSTATUS")
  (make-package "GRINDER_CHASSIS_DRIVER::CHASSISSTATUS"))

(in-package "ROS")
;;//! \htmlinclude ChassisStatus.msg.html
(if (not (find-package "STD_MSGS"))
  (ros::roseus-add-msgs "std_msgs"))


(defclass grinder_chassis_driver::ChassisStatus
  :super ros::object
  :slots (_header _connected _enabled _work_mode _disc_speed_target _disc_speed_feedback _disc_enabled _disc_lift_state _light_enabled _consecutive_failures _last_error ))

(defmethod grinder_chassis_driver::ChassisStatus
  (:init
   (&key
    ((:header __header) (instance std_msgs::Header :init))
    ((:connected __connected) nil)
    ((:enabled __enabled) nil)
    ((:work_mode __work_mode) 0)
    ((:disc_speed_target __disc_speed_target) 0)
    ((:disc_speed_feedback __disc_speed_feedback) 0)
    ((:disc_enabled __disc_enabled) nil)
    ((:disc_lift_state __disc_lift_state) 0)
    ((:light_enabled __light_enabled) nil)
    ((:consecutive_failures __consecutive_failures) 0)
    ((:last_error __last_error) "")
    )
   (send-super :init)
   (setq _header __header)
   (setq _connected __connected)
   (setq _enabled __enabled)
   (setq _work_mode (round __work_mode))
   (setq _disc_speed_target (round __disc_speed_target))
   (setq _disc_speed_feedback (round __disc_speed_feedback))
   (setq _disc_enabled __disc_enabled)
   (setq _disc_lift_state (round __disc_lift_state))
   (setq _light_enabled __light_enabled)
   (setq _consecutive_failures (round __consecutive_failures))
   (setq _last_error (string __last_error))
   self)
  (:header
   (&rest __header)
   (if (keywordp (car __header))
       (send* _header __header)
     (progn
       (if __header (setq _header (car __header)))
       _header)))
  (:connected
   (&optional (__connected :null))
   (if (not (eq __connected :null)) (setq _connected __connected)) _connected)
  (:enabled
   (&optional (__enabled :null))
   (if (not (eq __enabled :null)) (setq _enabled __enabled)) _enabled)
  (:work_mode
   (&optional __work_mode)
   (if __work_mode (setq _work_mode __work_mode)) _work_mode)
  (:disc_speed_target
   (&optional __disc_speed_target)
   (if __disc_speed_target (setq _disc_speed_target __disc_speed_target)) _disc_speed_target)
  (:disc_speed_feedback
   (&optional __disc_speed_feedback)
   (if __disc_speed_feedback (setq _disc_speed_feedback __disc_speed_feedback)) _disc_speed_feedback)
  (:disc_enabled
   (&optional (__disc_enabled :null))
   (if (not (eq __disc_enabled :null)) (setq _disc_enabled __disc_enabled)) _disc_enabled)
  (:disc_lift_state
   (&optional __disc_lift_state)
   (if __disc_lift_state (setq _disc_lift_state __disc_lift_state)) _disc_lift_state)
  (:light_enabled
   (&optional (__light_enabled :null))
   (if (not (eq __light_enabled :null)) (setq _light_enabled __light_enabled)) _light_enabled)
  (:consecutive_failures
   (&optional __consecutive_failures)
   (if __consecutive_failures (setq _consecutive_failures __consecutive_failures)) _consecutive_failures)
  (:last_error
   (&optional __last_error)
   (if __last_error (setq _last_error __last_error)) _last_error)
  (:serialization-length
   ()
   (+
    ;; std_msgs/Header _header
    (send _header :serialization-length)
    ;; bool _connected
    1
    ;; bool _enabled
    1
    ;; uint16 _work_mode
    2
    ;; int16 _disc_speed_target
    2
    ;; int16 _disc_speed_feedback
    2
    ;; bool _disc_enabled
    1
    ;; uint16 _disc_lift_state
    2
    ;; bool _light_enabled
    1
    ;; uint32 _consecutive_failures
    4
    ;; string _last_error
    4 (length _last_error)
    ))
  (:serialize
   (&optional strm)
   (let ((s (if strm strm
              (make-string-output-stream (send self :serialization-length)))))
     ;; std_msgs/Header _header
       (send _header :serialize s)
     ;; bool _connected
       (if _connected (write-byte -1 s) (write-byte 0 s))
     ;; bool _enabled
       (if _enabled (write-byte -1 s) (write-byte 0 s))
     ;; uint16 _work_mode
       (write-word _work_mode s)
     ;; int16 _disc_speed_target
       (write-word _disc_speed_target s)
     ;; int16 _disc_speed_feedback
       (write-word _disc_speed_feedback s)
     ;; bool _disc_enabled
       (if _disc_enabled (write-byte -1 s) (write-byte 0 s))
     ;; uint16 _disc_lift_state
       (write-word _disc_lift_state s)
     ;; bool _light_enabled
       (if _light_enabled (write-byte -1 s) (write-byte 0 s))
     ;; uint32 _consecutive_failures
       (write-long _consecutive_failures s)
     ;; string _last_error
       (write-long (length _last_error) s) (princ _last_error s)
     ;;
     (if (null strm) (get-output-stream-string s))))
  (:deserialize
   (buf &optional (ptr- 0))
   ;; std_msgs/Header _header
     (send _header :deserialize buf ptr-) (incf ptr- (send _header :serialization-length))
   ;; bool _connected
     (setq _connected (not (= 0 (sys::peek buf ptr- :char)))) (incf ptr- 1)
   ;; bool _enabled
     (setq _enabled (not (= 0 (sys::peek buf ptr- :char)))) (incf ptr- 1)
   ;; uint16 _work_mode
     (setq _work_mode (sys::peek buf ptr- :short)) (incf ptr- 2)
   ;; int16 _disc_speed_target
     (setq _disc_speed_target (sys::peek buf ptr- :short)) (incf ptr- 2)
   ;; int16 _disc_speed_feedback
     (setq _disc_speed_feedback (sys::peek buf ptr- :short)) (incf ptr- 2)
   ;; bool _disc_enabled
     (setq _disc_enabled (not (= 0 (sys::peek buf ptr- :char)))) (incf ptr- 1)
   ;; uint16 _disc_lift_state
     (setq _disc_lift_state (sys::peek buf ptr- :short)) (incf ptr- 2)
   ;; bool _light_enabled
     (setq _light_enabled (not (= 0 (sys::peek buf ptr- :char)))) (incf ptr- 1)
   ;; uint32 _consecutive_failures
     (setq _consecutive_failures (sys::peek buf ptr- :integer)) (incf ptr- 4)
   ;; string _last_error
     (let (n) (setq n (sys::peek buf ptr- :integer)) (incf ptr- 4) (setq _last_error (subseq buf ptr- (+ ptr- n))) (incf ptr- n))
   ;;
   self)
  )

(setf (get grinder_chassis_driver::ChassisStatus :md5sum-) "332527d3d7aab4589bcc1f2c43bb82d4")
(setf (get grinder_chassis_driver::ChassisStatus :datatype-) "grinder_chassis_driver/ChassisStatus")
(setf (get grinder_chassis_driver::ChassisStatus :definition-)
      "std_msgs/Header header
bool connected
bool enabled
uint16 work_mode
int16 disc_speed_target
int16 disc_speed_feedback
bool disc_enabled
uint16 disc_lift_state
bool light_enabled
uint32 consecutive_failures
string last_error

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



(provide :grinder_chassis_driver/ChassisStatus "332527d3d7aab4589bcc1f2c43bb82d4")


