; Auto-generated. Do not edit!


(cl:in-package grinder_scheduler-msg)


;//! \htmlinclude SchedulerStatus.msg.html

(cl:defclass <SchedulerStatus> (roslisp-msg-protocol:ros-message)
  ((header
    :reader header
    :initarg :header
    :type std_msgs-msg:Header
    :initform (cl:make-instance 'std_msgs-msg:Header))
   (task_id
    :reader task_id
    :initarg :task_id
    :type cl:string
    :initform "")
   (state
    :reader state
    :initarg :state
    :type cl:string
    :initform "")
   (progress
    :reader progress
    :initarg :progress
    :type cl:float
    :initform 0.0)
   (map_version
    :reader map_version
    :initarg :map_version
    :type cl:integer
    :initform 0)
   (map_available
    :reader map_available
    :initarg :map_available
    :type cl:boolean
    :initform cl:nil)
   (stream_online
    :reader stream_online
    :initarg :stream_online
    :type cl:boolean
    :initform cl:nil)
   (replan_requested
    :reader replan_requested
    :initarg :replan_requested
    :type cl:boolean
    :initform cl:nil)
   (last_error
    :reader last_error
    :initarg :last_error
    :type cl:string
    :initform "")
   (pose
    :reader pose
    :initarg :pose
    :type geometry_msgs-msg:Pose2D
    :initform (cl:make-instance 'geometry_msgs-msg:Pose2D))
   (path_point_count
    :reader path_point_count
    :initarg :path_point_count
    :type cl:integer
    :initform 0))
)

(cl:defclass SchedulerStatus (<SchedulerStatus>)
  ())

(cl:defmethod cl:initialize-instance :after ((m <SchedulerStatus>) cl:&rest args)
  (cl:declare (cl:ignorable args))
  (cl:unless (cl:typep m 'SchedulerStatus)
    (roslisp-msg-protocol:msg-deprecation-warning "using old message class name grinder_scheduler-msg:<SchedulerStatus> is deprecated: use grinder_scheduler-msg:SchedulerStatus instead.")))

(cl:ensure-generic-function 'header-val :lambda-list '(m))
(cl:defmethod header-val ((m <SchedulerStatus>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader grinder_scheduler-msg:header-val is deprecated.  Use grinder_scheduler-msg:header instead.")
  (header m))

(cl:ensure-generic-function 'task_id-val :lambda-list '(m))
(cl:defmethod task_id-val ((m <SchedulerStatus>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader grinder_scheduler-msg:task_id-val is deprecated.  Use grinder_scheduler-msg:task_id instead.")
  (task_id m))

(cl:ensure-generic-function 'state-val :lambda-list '(m))
(cl:defmethod state-val ((m <SchedulerStatus>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader grinder_scheduler-msg:state-val is deprecated.  Use grinder_scheduler-msg:state instead.")
  (state m))

(cl:ensure-generic-function 'progress-val :lambda-list '(m))
(cl:defmethod progress-val ((m <SchedulerStatus>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader grinder_scheduler-msg:progress-val is deprecated.  Use grinder_scheduler-msg:progress instead.")
  (progress m))

(cl:ensure-generic-function 'map_version-val :lambda-list '(m))
(cl:defmethod map_version-val ((m <SchedulerStatus>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader grinder_scheduler-msg:map_version-val is deprecated.  Use grinder_scheduler-msg:map_version instead.")
  (map_version m))

(cl:ensure-generic-function 'map_available-val :lambda-list '(m))
(cl:defmethod map_available-val ((m <SchedulerStatus>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader grinder_scheduler-msg:map_available-val is deprecated.  Use grinder_scheduler-msg:map_available instead.")
  (map_available m))

(cl:ensure-generic-function 'stream_online-val :lambda-list '(m))
(cl:defmethod stream_online-val ((m <SchedulerStatus>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader grinder_scheduler-msg:stream_online-val is deprecated.  Use grinder_scheduler-msg:stream_online instead.")
  (stream_online m))

(cl:ensure-generic-function 'replan_requested-val :lambda-list '(m))
(cl:defmethod replan_requested-val ((m <SchedulerStatus>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader grinder_scheduler-msg:replan_requested-val is deprecated.  Use grinder_scheduler-msg:replan_requested instead.")
  (replan_requested m))

(cl:ensure-generic-function 'last_error-val :lambda-list '(m))
(cl:defmethod last_error-val ((m <SchedulerStatus>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader grinder_scheduler-msg:last_error-val is deprecated.  Use grinder_scheduler-msg:last_error instead.")
  (last_error m))

(cl:ensure-generic-function 'pose-val :lambda-list '(m))
(cl:defmethod pose-val ((m <SchedulerStatus>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader grinder_scheduler-msg:pose-val is deprecated.  Use grinder_scheduler-msg:pose instead.")
  (pose m))

(cl:ensure-generic-function 'path_point_count-val :lambda-list '(m))
(cl:defmethod path_point_count-val ((m <SchedulerStatus>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader grinder_scheduler-msg:path_point_count-val is deprecated.  Use grinder_scheduler-msg:path_point_count instead.")
  (path_point_count m))
(cl:defmethod roslisp-msg-protocol:serialize ((msg <SchedulerStatus>) ostream)
  "Serializes a message object of type '<SchedulerStatus>"
  (roslisp-msg-protocol:serialize (cl:slot-value msg 'header) ostream)
  (cl:let ((__ros_str_len (cl:length (cl:slot-value msg 'task_id))))
    (cl:write-byte (cl:ldb (cl:byte 8 0) __ros_str_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) __ros_str_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) __ros_str_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) __ros_str_len) ostream))
  (cl:map cl:nil #'(cl:lambda (c) (cl:write-byte (cl:char-code c) ostream)) (cl:slot-value msg 'task_id))
  (cl:let ((__ros_str_len (cl:length (cl:slot-value msg 'state))))
    (cl:write-byte (cl:ldb (cl:byte 8 0) __ros_str_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) __ros_str_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) __ros_str_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) __ros_str_len) ostream))
  (cl:map cl:nil #'(cl:lambda (c) (cl:write-byte (cl:char-code c) ostream)) (cl:slot-value msg 'state))
  (cl:let ((bits (roslisp-utils:encode-single-float-bits (cl:slot-value msg 'progress))))
    (cl:write-byte (cl:ldb (cl:byte 8 0) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) bits) ostream))
  (cl:write-byte (cl:ldb (cl:byte 8 0) (cl:slot-value msg 'map_version)) ostream)
  (cl:write-byte (cl:ldb (cl:byte 8 8) (cl:slot-value msg 'map_version)) ostream)
  (cl:write-byte (cl:ldb (cl:byte 8 16) (cl:slot-value msg 'map_version)) ostream)
  (cl:write-byte (cl:ldb (cl:byte 8 24) (cl:slot-value msg 'map_version)) ostream)
  (cl:write-byte (cl:ldb (cl:byte 8 0) (cl:if (cl:slot-value msg 'map_available) 1 0)) ostream)
  (cl:write-byte (cl:ldb (cl:byte 8 0) (cl:if (cl:slot-value msg 'stream_online) 1 0)) ostream)
  (cl:write-byte (cl:ldb (cl:byte 8 0) (cl:if (cl:slot-value msg 'replan_requested) 1 0)) ostream)
  (cl:let ((__ros_str_len (cl:length (cl:slot-value msg 'last_error))))
    (cl:write-byte (cl:ldb (cl:byte 8 0) __ros_str_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) __ros_str_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) __ros_str_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) __ros_str_len) ostream))
  (cl:map cl:nil #'(cl:lambda (c) (cl:write-byte (cl:char-code c) ostream)) (cl:slot-value msg 'last_error))
  (roslisp-msg-protocol:serialize (cl:slot-value msg 'pose) ostream)
  (cl:write-byte (cl:ldb (cl:byte 8 0) (cl:slot-value msg 'path_point_count)) ostream)
  (cl:write-byte (cl:ldb (cl:byte 8 8) (cl:slot-value msg 'path_point_count)) ostream)
  (cl:write-byte (cl:ldb (cl:byte 8 16) (cl:slot-value msg 'path_point_count)) ostream)
  (cl:write-byte (cl:ldb (cl:byte 8 24) (cl:slot-value msg 'path_point_count)) ostream)
)
(cl:defmethod roslisp-msg-protocol:deserialize ((msg <SchedulerStatus>) istream)
  "Deserializes a message object of type '<SchedulerStatus>"
  (roslisp-msg-protocol:deserialize (cl:slot-value msg 'header) istream)
    (cl:let ((__ros_str_len 0))
      (cl:setf (cl:ldb (cl:byte 8 0) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 16) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 24) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:slot-value msg 'task_id) (cl:make-string __ros_str_len))
      (cl:dotimes (__ros_str_idx __ros_str_len msg)
        (cl:setf (cl:char (cl:slot-value msg 'task_id) __ros_str_idx) (cl:code-char (cl:read-byte istream)))))
    (cl:let ((__ros_str_len 0))
      (cl:setf (cl:ldb (cl:byte 8 0) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 16) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 24) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:slot-value msg 'state) (cl:make-string __ros_str_len))
      (cl:dotimes (__ros_str_idx __ros_str_len msg)
        (cl:setf (cl:char (cl:slot-value msg 'state) __ros_str_idx) (cl:code-char (cl:read-byte istream)))))
    (cl:let ((bits 0))
      (cl:setf (cl:ldb (cl:byte 8 0) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 16) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 24) bits) (cl:read-byte istream))
    (cl:setf (cl:slot-value msg 'progress) (roslisp-utils:decode-single-float-bits bits)))
    (cl:setf (cl:ldb (cl:byte 8 0) (cl:slot-value msg 'map_version)) (cl:read-byte istream))
    (cl:setf (cl:ldb (cl:byte 8 8) (cl:slot-value msg 'map_version)) (cl:read-byte istream))
    (cl:setf (cl:ldb (cl:byte 8 16) (cl:slot-value msg 'map_version)) (cl:read-byte istream))
    (cl:setf (cl:ldb (cl:byte 8 24) (cl:slot-value msg 'map_version)) (cl:read-byte istream))
    (cl:setf (cl:slot-value msg 'map_available) (cl:not (cl:zerop (cl:read-byte istream))))
    (cl:setf (cl:slot-value msg 'stream_online) (cl:not (cl:zerop (cl:read-byte istream))))
    (cl:setf (cl:slot-value msg 'replan_requested) (cl:not (cl:zerop (cl:read-byte istream))))
    (cl:let ((__ros_str_len 0))
      (cl:setf (cl:ldb (cl:byte 8 0) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 16) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 24) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:slot-value msg 'last_error) (cl:make-string __ros_str_len))
      (cl:dotimes (__ros_str_idx __ros_str_len msg)
        (cl:setf (cl:char (cl:slot-value msg 'last_error) __ros_str_idx) (cl:code-char (cl:read-byte istream)))))
  (roslisp-msg-protocol:deserialize (cl:slot-value msg 'pose) istream)
    (cl:setf (cl:ldb (cl:byte 8 0) (cl:slot-value msg 'path_point_count)) (cl:read-byte istream))
    (cl:setf (cl:ldb (cl:byte 8 8) (cl:slot-value msg 'path_point_count)) (cl:read-byte istream))
    (cl:setf (cl:ldb (cl:byte 8 16) (cl:slot-value msg 'path_point_count)) (cl:read-byte istream))
    (cl:setf (cl:ldb (cl:byte 8 24) (cl:slot-value msg 'path_point_count)) (cl:read-byte istream))
  msg
)
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql '<SchedulerStatus>)))
  "Returns string type for a message object of type '<SchedulerStatus>"
  "grinder_scheduler/SchedulerStatus")
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql 'SchedulerStatus)))
  "Returns string type for a message object of type 'SchedulerStatus"
  "grinder_scheduler/SchedulerStatus")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql '<SchedulerStatus>)))
  "Returns md5sum for a message object of type '<SchedulerStatus>"
  "5f4e9266173ca1d3c3829a5e19868d37")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql 'SchedulerStatus)))
  "Returns md5sum for a message object of type 'SchedulerStatus"
  "5f4e9266173ca1d3c3829a5e19868d37")
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql '<SchedulerStatus>)))
  "Returns full string definition for message of type '<SchedulerStatus>"
  (cl:format cl:nil "std_msgs/Header header~%string task_id~%string state~%float32 progress~%uint32 map_version~%bool map_available~%bool stream_online~%bool replan_requested~%string last_error~%geometry_msgs/Pose2D pose~%uint32 path_point_count~%~%================================================================================~%MSG: std_msgs/Header~%# Standard metadata for higher-level stamped data types.~%# This is generally used to communicate timestamped data ~%# in a particular coordinate frame.~%# ~%# sequence ID: consecutively increasing ID ~%uint32 seq~%#Two-integer timestamp that is expressed as:~%# * stamp.sec: seconds (stamp_secs) since epoch (in Python the variable is called 'secs')~%# * stamp.nsec: nanoseconds since stamp_secs (in Python the variable is called 'nsecs')~%# time-handling sugar is provided by the client library~%time stamp~%#Frame this data is associated with~%string frame_id~%~%================================================================================~%MSG: geometry_msgs/Pose2D~%# Deprecated~%# Please use the full 3D pose.~%~%# In general our recommendation is to use a full 3D representation of everything and for 2D specific applications make the appropriate projections into the plane for their calculations but optimally will preserve the 3D information during processing.~%~%# If we have parallel copies of 2D datatypes every UI and other pipeline will end up needing to have dual interfaces to plot everything. And you will end up with not being able to use 3D tools for 2D use cases even if they're completely valid, as you'd have to reimplement it with different inputs and outputs. It's not particularly hard to plot the 2D pose or compute the yaw error for the Pose message and there are already tools and libraries that can do this for you.~%~%~%# This expresses a position and orientation on a 2D manifold.~%~%float64 x~%float64 y~%float64 theta~%~%~%"))
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql 'SchedulerStatus)))
  "Returns full string definition for message of type 'SchedulerStatus"
  (cl:format cl:nil "std_msgs/Header header~%string task_id~%string state~%float32 progress~%uint32 map_version~%bool map_available~%bool stream_online~%bool replan_requested~%string last_error~%geometry_msgs/Pose2D pose~%uint32 path_point_count~%~%================================================================================~%MSG: std_msgs/Header~%# Standard metadata for higher-level stamped data types.~%# This is generally used to communicate timestamped data ~%# in a particular coordinate frame.~%# ~%# sequence ID: consecutively increasing ID ~%uint32 seq~%#Two-integer timestamp that is expressed as:~%# * stamp.sec: seconds (stamp_secs) since epoch (in Python the variable is called 'secs')~%# * stamp.nsec: nanoseconds since stamp_secs (in Python the variable is called 'nsecs')~%# time-handling sugar is provided by the client library~%time stamp~%#Frame this data is associated with~%string frame_id~%~%================================================================================~%MSG: geometry_msgs/Pose2D~%# Deprecated~%# Please use the full 3D pose.~%~%# In general our recommendation is to use a full 3D representation of everything and for 2D specific applications make the appropriate projections into the plane for their calculations but optimally will preserve the 3D information during processing.~%~%# If we have parallel copies of 2D datatypes every UI and other pipeline will end up needing to have dual interfaces to plot everything. And you will end up with not being able to use 3D tools for 2D use cases even if they're completely valid, as you'd have to reimplement it with different inputs and outputs. It's not particularly hard to plot the 2D pose or compute the yaw error for the Pose message and there are already tools and libraries that can do this for you.~%~%~%# This expresses a position and orientation on a 2D manifold.~%~%float64 x~%float64 y~%float64 theta~%~%~%"))
(cl:defmethod roslisp-msg-protocol:serialization-length ((msg <SchedulerStatus>))
  (cl:+ 0
     (roslisp-msg-protocol:serialization-length (cl:slot-value msg 'header))
     4 (cl:length (cl:slot-value msg 'task_id))
     4 (cl:length (cl:slot-value msg 'state))
     4
     4
     1
     1
     1
     4 (cl:length (cl:slot-value msg 'last_error))
     (roslisp-msg-protocol:serialization-length (cl:slot-value msg 'pose))
     4
))
(cl:defmethod roslisp-msg-protocol:ros-message-to-list ((msg <SchedulerStatus>))
  "Converts a ROS message object to a list"
  (cl:list 'SchedulerStatus
    (cl:cons ':header (header msg))
    (cl:cons ':task_id (task_id msg))
    (cl:cons ':state (state msg))
    (cl:cons ':progress (progress msg))
    (cl:cons ':map_version (map_version msg))
    (cl:cons ':map_available (map_available msg))
    (cl:cons ':stream_online (stream_online msg))
    (cl:cons ':replan_requested (replan_requested msg))
    (cl:cons ':last_error (last_error msg))
    (cl:cons ':pose (pose msg))
    (cl:cons ':path_point_count (path_point_count msg))
))
