; Auto-generated. Do not edit!


(cl:in-package slamware_ros_sdk-msg)


;//! \htmlinclude RelocalizationStatus.msg.html

(cl:defclass <RelocalizationStatus> (roslisp-msg-protocol:ros-message)
  ((timestamp_ns
    :reader timestamp_ns
    :initarg :timestamp_ns
    :type cl:integer
    :initform 0)
   (status
    :reader status
    :initarg :status
    :type cl:string
    :initform ""))
)

(cl:defclass RelocalizationStatus (<RelocalizationStatus>)
  ())

(cl:defmethod cl:initialize-instance :after ((m <RelocalizationStatus>) cl:&rest args)
  (cl:declare (cl:ignorable args))
  (cl:unless (cl:typep m 'RelocalizationStatus)
    (roslisp-msg-protocol:msg-deprecation-warning "using old message class name slamware_ros_sdk-msg:<RelocalizationStatus> is deprecated: use slamware_ros_sdk-msg:RelocalizationStatus instead.")))

(cl:ensure-generic-function 'timestamp_ns-val :lambda-list '(m))
(cl:defmethod timestamp_ns-val ((m <RelocalizationStatus>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader slamware_ros_sdk-msg:timestamp_ns-val is deprecated.  Use slamware_ros_sdk-msg:timestamp_ns instead.")
  (timestamp_ns m))

(cl:ensure-generic-function 'status-val :lambda-list '(m))
(cl:defmethod status-val ((m <RelocalizationStatus>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader slamware_ros_sdk-msg:status-val is deprecated.  Use slamware_ros_sdk-msg:status instead.")
  (status m))
(cl:defmethod roslisp-msg-protocol:serialize ((msg <RelocalizationStatus>) ostream)
  "Serializes a message object of type '<RelocalizationStatus>"
  (cl:write-byte (cl:ldb (cl:byte 8 0) (cl:slot-value msg 'timestamp_ns)) ostream)
  (cl:write-byte (cl:ldb (cl:byte 8 8) (cl:slot-value msg 'timestamp_ns)) ostream)
  (cl:write-byte (cl:ldb (cl:byte 8 16) (cl:slot-value msg 'timestamp_ns)) ostream)
  (cl:write-byte (cl:ldb (cl:byte 8 24) (cl:slot-value msg 'timestamp_ns)) ostream)
  (cl:write-byte (cl:ldb (cl:byte 8 32) (cl:slot-value msg 'timestamp_ns)) ostream)
  (cl:write-byte (cl:ldb (cl:byte 8 40) (cl:slot-value msg 'timestamp_ns)) ostream)
  (cl:write-byte (cl:ldb (cl:byte 8 48) (cl:slot-value msg 'timestamp_ns)) ostream)
  (cl:write-byte (cl:ldb (cl:byte 8 56) (cl:slot-value msg 'timestamp_ns)) ostream)
  (cl:let ((__ros_str_len (cl:length (cl:slot-value msg 'status))))
    (cl:write-byte (cl:ldb (cl:byte 8 0) __ros_str_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) __ros_str_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) __ros_str_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) __ros_str_len) ostream))
  (cl:map cl:nil #'(cl:lambda (c) (cl:write-byte (cl:char-code c) ostream)) (cl:slot-value msg 'status))
)
(cl:defmethod roslisp-msg-protocol:deserialize ((msg <RelocalizationStatus>) istream)
  "Deserializes a message object of type '<RelocalizationStatus>"
    (cl:setf (cl:ldb (cl:byte 8 0) (cl:slot-value msg 'timestamp_ns)) (cl:read-byte istream))
    (cl:setf (cl:ldb (cl:byte 8 8) (cl:slot-value msg 'timestamp_ns)) (cl:read-byte istream))
    (cl:setf (cl:ldb (cl:byte 8 16) (cl:slot-value msg 'timestamp_ns)) (cl:read-byte istream))
    (cl:setf (cl:ldb (cl:byte 8 24) (cl:slot-value msg 'timestamp_ns)) (cl:read-byte istream))
    (cl:setf (cl:ldb (cl:byte 8 32) (cl:slot-value msg 'timestamp_ns)) (cl:read-byte istream))
    (cl:setf (cl:ldb (cl:byte 8 40) (cl:slot-value msg 'timestamp_ns)) (cl:read-byte istream))
    (cl:setf (cl:ldb (cl:byte 8 48) (cl:slot-value msg 'timestamp_ns)) (cl:read-byte istream))
    (cl:setf (cl:ldb (cl:byte 8 56) (cl:slot-value msg 'timestamp_ns)) (cl:read-byte istream))
    (cl:let ((__ros_str_len 0))
      (cl:setf (cl:ldb (cl:byte 8 0) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 16) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 24) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:slot-value msg 'status) (cl:make-string __ros_str_len))
      (cl:dotimes (__ros_str_idx __ros_str_len msg)
        (cl:setf (cl:char (cl:slot-value msg 'status) __ros_str_idx) (cl:code-char (cl:read-byte istream)))))
  msg
)
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql '<RelocalizationStatus>)))
  "Returns string type for a message object of type '<RelocalizationStatus>"
  "slamware_ros_sdk/RelocalizationStatus")
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql 'RelocalizationStatus)))
  "Returns string type for a message object of type 'RelocalizationStatus"
  "slamware_ros_sdk/RelocalizationStatus")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql '<RelocalizationStatus>)))
  "Returns md5sum for a message object of type '<RelocalizationStatus>"
  "ccc1e4824af73d0a8de6d07224862f42")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql 'RelocalizationStatus)))
  "Returns md5sum for a message object of type 'RelocalizationStatus"
  "ccc1e4824af73d0a8de6d07224862f42")
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql '<RelocalizationStatus>)))
  "Returns full string definition for message of type '<RelocalizationStatus>"
  (cl:format cl:nil "~%uint64 timestamp_ns~%string status~%~%~%"))
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql 'RelocalizationStatus)))
  "Returns full string definition for message of type 'RelocalizationStatus"
  (cl:format cl:nil "~%uint64 timestamp_ns~%string status~%~%~%"))
(cl:defmethod roslisp-msg-protocol:serialization-length ((msg <RelocalizationStatus>))
  (cl:+ 0
     8
     4 (cl:length (cl:slot-value msg 'status))
))
(cl:defmethod roslisp-msg-protocol:ros-message-to-list ((msg <RelocalizationStatus>))
  "Converts a ROS message object to a list"
  (cl:list 'RelocalizationStatus
    (cl:cons ':timestamp_ns (timestamp_ns msg))
    (cl:cons ':status (status msg))
))
