; Auto-generated. Do not edit!


(cl:in-package grinder_chassis_driver-msg)


;//! \htmlinclude WheelSpeedState.msg.html

(cl:defclass <WheelSpeedState> (roslisp-msg-protocol:ros-message)
  ((header
    :reader header
    :initarg :header
    :type std_msgs-msg:Header
    :initform (cl:make-instance 'std_msgs-msg:Header))
   (target_left_wheel_speed
    :reader target_left_wheel_speed
    :initarg :target_left_wheel_speed
    :type cl:fixnum
    :initform 0)
   (target_right_wheel_speed
    :reader target_right_wheel_speed
    :initarg :target_right_wheel_speed
    :type cl:fixnum
    :initform 0)
   (feedback_left_wheel_speed
    :reader feedback_left_wheel_speed
    :initarg :feedback_left_wheel_speed
    :type cl:fixnum
    :initform 0)
   (feedback_right_wheel_speed
    :reader feedback_right_wheel_speed
    :initarg :feedback_right_wheel_speed
    :type cl:fixnum
    :initform 0)
   (feedback_valid
    :reader feedback_valid
    :initarg :feedback_valid
    :type cl:boolean
    :initform cl:nil))
)

(cl:defclass WheelSpeedState (<WheelSpeedState>)
  ())

(cl:defmethod cl:initialize-instance :after ((m <WheelSpeedState>) cl:&rest args)
  (cl:declare (cl:ignorable args))
  (cl:unless (cl:typep m 'WheelSpeedState)
    (roslisp-msg-protocol:msg-deprecation-warning "using old message class name grinder_chassis_driver-msg:<WheelSpeedState> is deprecated: use grinder_chassis_driver-msg:WheelSpeedState instead.")))

(cl:ensure-generic-function 'header-val :lambda-list '(m))
(cl:defmethod header-val ((m <WheelSpeedState>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader grinder_chassis_driver-msg:header-val is deprecated.  Use grinder_chassis_driver-msg:header instead.")
  (header m))

(cl:ensure-generic-function 'target_left_wheel_speed-val :lambda-list '(m))
(cl:defmethod target_left_wheel_speed-val ((m <WheelSpeedState>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader grinder_chassis_driver-msg:target_left_wheel_speed-val is deprecated.  Use grinder_chassis_driver-msg:target_left_wheel_speed instead.")
  (target_left_wheel_speed m))

(cl:ensure-generic-function 'target_right_wheel_speed-val :lambda-list '(m))
(cl:defmethod target_right_wheel_speed-val ((m <WheelSpeedState>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader grinder_chassis_driver-msg:target_right_wheel_speed-val is deprecated.  Use grinder_chassis_driver-msg:target_right_wheel_speed instead.")
  (target_right_wheel_speed m))

(cl:ensure-generic-function 'feedback_left_wheel_speed-val :lambda-list '(m))
(cl:defmethod feedback_left_wheel_speed-val ((m <WheelSpeedState>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader grinder_chassis_driver-msg:feedback_left_wheel_speed-val is deprecated.  Use grinder_chassis_driver-msg:feedback_left_wheel_speed instead.")
  (feedback_left_wheel_speed m))

(cl:ensure-generic-function 'feedback_right_wheel_speed-val :lambda-list '(m))
(cl:defmethod feedback_right_wheel_speed-val ((m <WheelSpeedState>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader grinder_chassis_driver-msg:feedback_right_wheel_speed-val is deprecated.  Use grinder_chassis_driver-msg:feedback_right_wheel_speed instead.")
  (feedback_right_wheel_speed m))

(cl:ensure-generic-function 'feedback_valid-val :lambda-list '(m))
(cl:defmethod feedback_valid-val ((m <WheelSpeedState>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader grinder_chassis_driver-msg:feedback_valid-val is deprecated.  Use grinder_chassis_driver-msg:feedback_valid instead.")
  (feedback_valid m))
(cl:defmethod roslisp-msg-protocol:serialize ((msg <WheelSpeedState>) ostream)
  "Serializes a message object of type '<WheelSpeedState>"
  (roslisp-msg-protocol:serialize (cl:slot-value msg 'header) ostream)
  (cl:let* ((signed (cl:slot-value msg 'target_left_wheel_speed)) (unsigned (cl:if (cl:< signed 0) (cl:+ signed 65536) signed)))
    (cl:write-byte (cl:ldb (cl:byte 8 0) unsigned) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) unsigned) ostream)
    )
  (cl:let* ((signed (cl:slot-value msg 'target_right_wheel_speed)) (unsigned (cl:if (cl:< signed 0) (cl:+ signed 65536) signed)))
    (cl:write-byte (cl:ldb (cl:byte 8 0) unsigned) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) unsigned) ostream)
    )
  (cl:let* ((signed (cl:slot-value msg 'feedback_left_wheel_speed)) (unsigned (cl:if (cl:< signed 0) (cl:+ signed 65536) signed)))
    (cl:write-byte (cl:ldb (cl:byte 8 0) unsigned) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) unsigned) ostream)
    )
  (cl:let* ((signed (cl:slot-value msg 'feedback_right_wheel_speed)) (unsigned (cl:if (cl:< signed 0) (cl:+ signed 65536) signed)))
    (cl:write-byte (cl:ldb (cl:byte 8 0) unsigned) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) unsigned) ostream)
    )
  (cl:write-byte (cl:ldb (cl:byte 8 0) (cl:if (cl:slot-value msg 'feedback_valid) 1 0)) ostream)
)
(cl:defmethod roslisp-msg-protocol:deserialize ((msg <WheelSpeedState>) istream)
  "Deserializes a message object of type '<WheelSpeedState>"
  (roslisp-msg-protocol:deserialize (cl:slot-value msg 'header) istream)
    (cl:let ((unsigned 0))
      (cl:setf (cl:ldb (cl:byte 8 0) unsigned) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) unsigned) (cl:read-byte istream))
      (cl:setf (cl:slot-value msg 'target_left_wheel_speed) (cl:if (cl:< unsigned 32768) unsigned (cl:- unsigned 65536))))
    (cl:let ((unsigned 0))
      (cl:setf (cl:ldb (cl:byte 8 0) unsigned) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) unsigned) (cl:read-byte istream))
      (cl:setf (cl:slot-value msg 'target_right_wheel_speed) (cl:if (cl:< unsigned 32768) unsigned (cl:- unsigned 65536))))
    (cl:let ((unsigned 0))
      (cl:setf (cl:ldb (cl:byte 8 0) unsigned) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) unsigned) (cl:read-byte istream))
      (cl:setf (cl:slot-value msg 'feedback_left_wheel_speed) (cl:if (cl:< unsigned 32768) unsigned (cl:- unsigned 65536))))
    (cl:let ((unsigned 0))
      (cl:setf (cl:ldb (cl:byte 8 0) unsigned) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) unsigned) (cl:read-byte istream))
      (cl:setf (cl:slot-value msg 'feedback_right_wheel_speed) (cl:if (cl:< unsigned 32768) unsigned (cl:- unsigned 65536))))
    (cl:setf (cl:slot-value msg 'feedback_valid) (cl:not (cl:zerop (cl:read-byte istream))))
  msg
)
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql '<WheelSpeedState>)))
  "Returns string type for a message object of type '<WheelSpeedState>"
  "grinder_chassis_driver/WheelSpeedState")
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql 'WheelSpeedState)))
  "Returns string type for a message object of type 'WheelSpeedState"
  "grinder_chassis_driver/WheelSpeedState")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql '<WheelSpeedState>)))
  "Returns md5sum for a message object of type '<WheelSpeedState>"
  "f50663abf771ecfd2d1486cfc892cbc3")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql 'WheelSpeedState)))
  "Returns md5sum for a message object of type 'WheelSpeedState"
  "f50663abf771ecfd2d1486cfc892cbc3")
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql '<WheelSpeedState>)))
  "Returns full string definition for message of type '<WheelSpeedState>"
  (cl:format cl:nil "std_msgs/Header header~%int16 target_left_wheel_speed~%int16 target_right_wheel_speed~%int16 feedback_left_wheel_speed~%int16 feedback_right_wheel_speed~%bool feedback_valid~%~%================================================================================~%MSG: std_msgs/Header~%# Standard metadata for higher-level stamped data types.~%# This is generally used to communicate timestamped data ~%# in a particular coordinate frame.~%# ~%# sequence ID: consecutively increasing ID ~%uint32 seq~%#Two-integer timestamp that is expressed as:~%# * stamp.sec: seconds (stamp_secs) since epoch (in Python the variable is called 'secs')~%# * stamp.nsec: nanoseconds since stamp_secs (in Python the variable is called 'nsecs')~%# time-handling sugar is provided by the client library~%time stamp~%#Frame this data is associated with~%string frame_id~%~%~%"))
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql 'WheelSpeedState)))
  "Returns full string definition for message of type 'WheelSpeedState"
  (cl:format cl:nil "std_msgs/Header header~%int16 target_left_wheel_speed~%int16 target_right_wheel_speed~%int16 feedback_left_wheel_speed~%int16 feedback_right_wheel_speed~%bool feedback_valid~%~%================================================================================~%MSG: std_msgs/Header~%# Standard metadata for higher-level stamped data types.~%# This is generally used to communicate timestamped data ~%# in a particular coordinate frame.~%# ~%# sequence ID: consecutively increasing ID ~%uint32 seq~%#Two-integer timestamp that is expressed as:~%# * stamp.sec: seconds (stamp_secs) since epoch (in Python the variable is called 'secs')~%# * stamp.nsec: nanoseconds since stamp_secs (in Python the variable is called 'nsecs')~%# time-handling sugar is provided by the client library~%time stamp~%#Frame this data is associated with~%string frame_id~%~%~%"))
(cl:defmethod roslisp-msg-protocol:serialization-length ((msg <WheelSpeedState>))
  (cl:+ 0
     (roslisp-msg-protocol:serialization-length (cl:slot-value msg 'header))
     2
     2
     2
     2
     1
))
(cl:defmethod roslisp-msg-protocol:ros-message-to-list ((msg <WheelSpeedState>))
  "Converts a ROS message object to a list"
  (cl:list 'WheelSpeedState
    (cl:cons ':header (header msg))
    (cl:cons ':target_left_wheel_speed (target_left_wheel_speed msg))
    (cl:cons ':target_right_wheel_speed (target_right_wheel_speed msg))
    (cl:cons ':feedback_left_wheel_speed (feedback_left_wheel_speed msg))
    (cl:cons ':feedback_right_wheel_speed (feedback_right_wheel_speed msg))
    (cl:cons ':feedback_valid (feedback_valid msg))
))
