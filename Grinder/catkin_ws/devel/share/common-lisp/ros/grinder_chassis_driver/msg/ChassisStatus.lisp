; Auto-generated. Do not edit!


(cl:in-package grinder_chassis_driver-msg)


;//! \htmlinclude ChassisStatus.msg.html

(cl:defclass <ChassisStatus> (roslisp-msg-protocol:ros-message)
  ((header
    :reader header
    :initarg :header
    :type std_msgs-msg:Header
    :initform (cl:make-instance 'std_msgs-msg:Header))
   (connected
    :reader connected
    :initarg :connected
    :type cl:boolean
    :initform cl:nil)
   (enabled
    :reader enabled
    :initarg :enabled
    :type cl:boolean
    :initform cl:nil)
   (work_mode
    :reader work_mode
    :initarg :work_mode
    :type cl:fixnum
    :initform 0)
   (disc_speed_target
    :reader disc_speed_target
    :initarg :disc_speed_target
    :type cl:fixnum
    :initform 0)
   (disc_speed_feedback
    :reader disc_speed_feedback
    :initarg :disc_speed_feedback
    :type cl:fixnum
    :initform 0)
   (disc_enabled
    :reader disc_enabled
    :initarg :disc_enabled
    :type cl:boolean
    :initform cl:nil)
   (disc_lift_state
    :reader disc_lift_state
    :initarg :disc_lift_state
    :type cl:fixnum
    :initform 0)
   (light_enabled
    :reader light_enabled
    :initarg :light_enabled
    :type cl:boolean
    :initform cl:nil)
   (consecutive_failures
    :reader consecutive_failures
    :initarg :consecutive_failures
    :type cl:integer
    :initform 0)
   (last_error
    :reader last_error
    :initarg :last_error
    :type cl:string
    :initform ""))
)

(cl:defclass ChassisStatus (<ChassisStatus>)
  ())

(cl:defmethod cl:initialize-instance :after ((m <ChassisStatus>) cl:&rest args)
  (cl:declare (cl:ignorable args))
  (cl:unless (cl:typep m 'ChassisStatus)
    (roslisp-msg-protocol:msg-deprecation-warning "using old message class name grinder_chassis_driver-msg:<ChassisStatus> is deprecated: use grinder_chassis_driver-msg:ChassisStatus instead.")))

(cl:ensure-generic-function 'header-val :lambda-list '(m))
(cl:defmethod header-val ((m <ChassisStatus>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader grinder_chassis_driver-msg:header-val is deprecated.  Use grinder_chassis_driver-msg:header instead.")
  (header m))

(cl:ensure-generic-function 'connected-val :lambda-list '(m))
(cl:defmethod connected-val ((m <ChassisStatus>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader grinder_chassis_driver-msg:connected-val is deprecated.  Use grinder_chassis_driver-msg:connected instead.")
  (connected m))

(cl:ensure-generic-function 'enabled-val :lambda-list '(m))
(cl:defmethod enabled-val ((m <ChassisStatus>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader grinder_chassis_driver-msg:enabled-val is deprecated.  Use grinder_chassis_driver-msg:enabled instead.")
  (enabled m))

(cl:ensure-generic-function 'work_mode-val :lambda-list '(m))
(cl:defmethod work_mode-val ((m <ChassisStatus>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader grinder_chassis_driver-msg:work_mode-val is deprecated.  Use grinder_chassis_driver-msg:work_mode instead.")
  (work_mode m))

(cl:ensure-generic-function 'disc_speed_target-val :lambda-list '(m))
(cl:defmethod disc_speed_target-val ((m <ChassisStatus>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader grinder_chassis_driver-msg:disc_speed_target-val is deprecated.  Use grinder_chassis_driver-msg:disc_speed_target instead.")
  (disc_speed_target m))

(cl:ensure-generic-function 'disc_speed_feedback-val :lambda-list '(m))
(cl:defmethod disc_speed_feedback-val ((m <ChassisStatus>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader grinder_chassis_driver-msg:disc_speed_feedback-val is deprecated.  Use grinder_chassis_driver-msg:disc_speed_feedback instead.")
  (disc_speed_feedback m))

(cl:ensure-generic-function 'disc_enabled-val :lambda-list '(m))
(cl:defmethod disc_enabled-val ((m <ChassisStatus>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader grinder_chassis_driver-msg:disc_enabled-val is deprecated.  Use grinder_chassis_driver-msg:disc_enabled instead.")
  (disc_enabled m))

(cl:ensure-generic-function 'disc_lift_state-val :lambda-list '(m))
(cl:defmethod disc_lift_state-val ((m <ChassisStatus>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader grinder_chassis_driver-msg:disc_lift_state-val is deprecated.  Use grinder_chassis_driver-msg:disc_lift_state instead.")
  (disc_lift_state m))

(cl:ensure-generic-function 'light_enabled-val :lambda-list '(m))
(cl:defmethod light_enabled-val ((m <ChassisStatus>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader grinder_chassis_driver-msg:light_enabled-val is deprecated.  Use grinder_chassis_driver-msg:light_enabled instead.")
  (light_enabled m))

(cl:ensure-generic-function 'consecutive_failures-val :lambda-list '(m))
(cl:defmethod consecutive_failures-val ((m <ChassisStatus>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader grinder_chassis_driver-msg:consecutive_failures-val is deprecated.  Use grinder_chassis_driver-msg:consecutive_failures instead.")
  (consecutive_failures m))

(cl:ensure-generic-function 'last_error-val :lambda-list '(m))
(cl:defmethod last_error-val ((m <ChassisStatus>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader grinder_chassis_driver-msg:last_error-val is deprecated.  Use grinder_chassis_driver-msg:last_error instead.")
  (last_error m))
(cl:defmethod roslisp-msg-protocol:serialize ((msg <ChassisStatus>) ostream)
  "Serializes a message object of type '<ChassisStatus>"
  (roslisp-msg-protocol:serialize (cl:slot-value msg 'header) ostream)
  (cl:write-byte (cl:ldb (cl:byte 8 0) (cl:if (cl:slot-value msg 'connected) 1 0)) ostream)
  (cl:write-byte (cl:ldb (cl:byte 8 0) (cl:if (cl:slot-value msg 'enabled) 1 0)) ostream)
  (cl:write-byte (cl:ldb (cl:byte 8 0) (cl:slot-value msg 'work_mode)) ostream)
  (cl:write-byte (cl:ldb (cl:byte 8 8) (cl:slot-value msg 'work_mode)) ostream)
  (cl:let* ((signed (cl:slot-value msg 'disc_speed_target)) (unsigned (cl:if (cl:< signed 0) (cl:+ signed 65536) signed)))
    (cl:write-byte (cl:ldb (cl:byte 8 0) unsigned) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) unsigned) ostream)
    )
  (cl:let* ((signed (cl:slot-value msg 'disc_speed_feedback)) (unsigned (cl:if (cl:< signed 0) (cl:+ signed 65536) signed)))
    (cl:write-byte (cl:ldb (cl:byte 8 0) unsigned) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) unsigned) ostream)
    )
  (cl:write-byte (cl:ldb (cl:byte 8 0) (cl:if (cl:slot-value msg 'disc_enabled) 1 0)) ostream)
  (cl:write-byte (cl:ldb (cl:byte 8 0) (cl:slot-value msg 'disc_lift_state)) ostream)
  (cl:write-byte (cl:ldb (cl:byte 8 8) (cl:slot-value msg 'disc_lift_state)) ostream)
  (cl:write-byte (cl:ldb (cl:byte 8 0) (cl:if (cl:slot-value msg 'light_enabled) 1 0)) ostream)
  (cl:write-byte (cl:ldb (cl:byte 8 0) (cl:slot-value msg 'consecutive_failures)) ostream)
  (cl:write-byte (cl:ldb (cl:byte 8 8) (cl:slot-value msg 'consecutive_failures)) ostream)
  (cl:write-byte (cl:ldb (cl:byte 8 16) (cl:slot-value msg 'consecutive_failures)) ostream)
  (cl:write-byte (cl:ldb (cl:byte 8 24) (cl:slot-value msg 'consecutive_failures)) ostream)
  (cl:let ((__ros_str_len (cl:length (cl:slot-value msg 'last_error))))
    (cl:write-byte (cl:ldb (cl:byte 8 0) __ros_str_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) __ros_str_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) __ros_str_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) __ros_str_len) ostream))
  (cl:map cl:nil #'(cl:lambda (c) (cl:write-byte (cl:char-code c) ostream)) (cl:slot-value msg 'last_error))
)
(cl:defmethod roslisp-msg-protocol:deserialize ((msg <ChassisStatus>) istream)
  "Deserializes a message object of type '<ChassisStatus>"
  (roslisp-msg-protocol:deserialize (cl:slot-value msg 'header) istream)
    (cl:setf (cl:slot-value msg 'connected) (cl:not (cl:zerop (cl:read-byte istream))))
    (cl:setf (cl:slot-value msg 'enabled) (cl:not (cl:zerop (cl:read-byte istream))))
    (cl:setf (cl:ldb (cl:byte 8 0) (cl:slot-value msg 'work_mode)) (cl:read-byte istream))
    (cl:setf (cl:ldb (cl:byte 8 8) (cl:slot-value msg 'work_mode)) (cl:read-byte istream))
    (cl:let ((unsigned 0))
      (cl:setf (cl:ldb (cl:byte 8 0) unsigned) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) unsigned) (cl:read-byte istream))
      (cl:setf (cl:slot-value msg 'disc_speed_target) (cl:if (cl:< unsigned 32768) unsigned (cl:- unsigned 65536))))
    (cl:let ((unsigned 0))
      (cl:setf (cl:ldb (cl:byte 8 0) unsigned) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) unsigned) (cl:read-byte istream))
      (cl:setf (cl:slot-value msg 'disc_speed_feedback) (cl:if (cl:< unsigned 32768) unsigned (cl:- unsigned 65536))))
    (cl:setf (cl:slot-value msg 'disc_enabled) (cl:not (cl:zerop (cl:read-byte istream))))
    (cl:setf (cl:ldb (cl:byte 8 0) (cl:slot-value msg 'disc_lift_state)) (cl:read-byte istream))
    (cl:setf (cl:ldb (cl:byte 8 8) (cl:slot-value msg 'disc_lift_state)) (cl:read-byte istream))
    (cl:setf (cl:slot-value msg 'light_enabled) (cl:not (cl:zerop (cl:read-byte istream))))
    (cl:setf (cl:ldb (cl:byte 8 0) (cl:slot-value msg 'consecutive_failures)) (cl:read-byte istream))
    (cl:setf (cl:ldb (cl:byte 8 8) (cl:slot-value msg 'consecutive_failures)) (cl:read-byte istream))
    (cl:setf (cl:ldb (cl:byte 8 16) (cl:slot-value msg 'consecutive_failures)) (cl:read-byte istream))
    (cl:setf (cl:ldb (cl:byte 8 24) (cl:slot-value msg 'consecutive_failures)) (cl:read-byte istream))
    (cl:let ((__ros_str_len 0))
      (cl:setf (cl:ldb (cl:byte 8 0) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 16) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 24) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:slot-value msg 'last_error) (cl:make-string __ros_str_len))
      (cl:dotimes (__ros_str_idx __ros_str_len msg)
        (cl:setf (cl:char (cl:slot-value msg 'last_error) __ros_str_idx) (cl:code-char (cl:read-byte istream)))))
  msg
)
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql '<ChassisStatus>)))
  "Returns string type for a message object of type '<ChassisStatus>"
  "grinder_chassis_driver/ChassisStatus")
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql 'ChassisStatus)))
  "Returns string type for a message object of type 'ChassisStatus"
  "grinder_chassis_driver/ChassisStatus")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql '<ChassisStatus>)))
  "Returns md5sum for a message object of type '<ChassisStatus>"
  "332527d3d7aab4589bcc1f2c43bb82d4")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql 'ChassisStatus)))
  "Returns md5sum for a message object of type 'ChassisStatus"
  "332527d3d7aab4589bcc1f2c43bb82d4")
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql '<ChassisStatus>)))
  "Returns full string definition for message of type '<ChassisStatus>"
  (cl:format cl:nil "std_msgs/Header header~%bool connected~%bool enabled~%uint16 work_mode~%int16 disc_speed_target~%int16 disc_speed_feedback~%bool disc_enabled~%uint16 disc_lift_state~%bool light_enabled~%uint32 consecutive_failures~%string last_error~%~%================================================================================~%MSG: std_msgs/Header~%# Standard metadata for higher-level stamped data types.~%# This is generally used to communicate timestamped data ~%# in a particular coordinate frame.~%# ~%# sequence ID: consecutively increasing ID ~%uint32 seq~%#Two-integer timestamp that is expressed as:~%# * stamp.sec: seconds (stamp_secs) since epoch (in Python the variable is called 'secs')~%# * stamp.nsec: nanoseconds since stamp_secs (in Python the variable is called 'nsecs')~%# time-handling sugar is provided by the client library~%time stamp~%#Frame this data is associated with~%string frame_id~%~%~%"))
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql 'ChassisStatus)))
  "Returns full string definition for message of type 'ChassisStatus"
  (cl:format cl:nil "std_msgs/Header header~%bool connected~%bool enabled~%uint16 work_mode~%int16 disc_speed_target~%int16 disc_speed_feedback~%bool disc_enabled~%uint16 disc_lift_state~%bool light_enabled~%uint32 consecutive_failures~%string last_error~%~%================================================================================~%MSG: std_msgs/Header~%# Standard metadata for higher-level stamped data types.~%# This is generally used to communicate timestamped data ~%# in a particular coordinate frame.~%# ~%# sequence ID: consecutively increasing ID ~%uint32 seq~%#Two-integer timestamp that is expressed as:~%# * stamp.sec: seconds (stamp_secs) since epoch (in Python the variable is called 'secs')~%# * stamp.nsec: nanoseconds since stamp_secs (in Python the variable is called 'nsecs')~%# time-handling sugar is provided by the client library~%time stamp~%#Frame this data is associated with~%string frame_id~%~%~%"))
(cl:defmethod roslisp-msg-protocol:serialization-length ((msg <ChassisStatus>))
  (cl:+ 0
     (roslisp-msg-protocol:serialization-length (cl:slot-value msg 'header))
     1
     1
     2
     2
     2
     1
     2
     1
     4
     4 (cl:length (cl:slot-value msg 'last_error))
))
(cl:defmethod roslisp-msg-protocol:ros-message-to-list ((msg <ChassisStatus>))
  "Converts a ROS message object to a list"
  (cl:list 'ChassisStatus
    (cl:cons ':header (header msg))
    (cl:cons ':connected (connected msg))
    (cl:cons ':enabled (enabled msg))
    (cl:cons ':work_mode (work_mode msg))
    (cl:cons ':disc_speed_target (disc_speed_target msg))
    (cl:cons ':disc_speed_feedback (disc_speed_feedback msg))
    (cl:cons ':disc_enabled (disc_enabled msg))
    (cl:cons ':disc_lift_state (disc_lift_state msg))
    (cl:cons ':light_enabled (light_enabled msg))
    (cl:cons ':consecutive_failures (consecutive_failures msg))
    (cl:cons ':last_error (last_error msg))
))
