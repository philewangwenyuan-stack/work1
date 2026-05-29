; Auto-generated. Do not edit!


(cl:in-package slamware_ros_sdk-srv)


;//! \htmlinclude SyncGetStcm-request.msg.html

(cl:defclass <SyncGetStcm-request> (roslisp-msg-protocol:ros-message)
  ((mapfile
    :reader mapfile
    :initarg :mapfile
    :type cl:string
    :initform ""))
)

(cl:defclass SyncGetStcm-request (<SyncGetStcm-request>)
  ())

(cl:defmethod cl:initialize-instance :after ((m <SyncGetStcm-request>) cl:&rest args)
  (cl:declare (cl:ignorable args))
  (cl:unless (cl:typep m 'SyncGetStcm-request)
    (roslisp-msg-protocol:msg-deprecation-warning "using old message class name slamware_ros_sdk-srv:<SyncGetStcm-request> is deprecated: use slamware_ros_sdk-srv:SyncGetStcm-request instead.")))

(cl:ensure-generic-function 'mapfile-val :lambda-list '(m))
(cl:defmethod mapfile-val ((m <SyncGetStcm-request>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader slamware_ros_sdk-srv:mapfile-val is deprecated.  Use slamware_ros_sdk-srv:mapfile instead.")
  (mapfile m))
(cl:defmethod roslisp-msg-protocol:serialize ((msg <SyncGetStcm-request>) ostream)
  "Serializes a message object of type '<SyncGetStcm-request>"
  (cl:let ((__ros_str_len (cl:length (cl:slot-value msg 'mapfile))))
    (cl:write-byte (cl:ldb (cl:byte 8 0) __ros_str_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) __ros_str_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) __ros_str_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) __ros_str_len) ostream))
  (cl:map cl:nil #'(cl:lambda (c) (cl:write-byte (cl:char-code c) ostream)) (cl:slot-value msg 'mapfile))
)
(cl:defmethod roslisp-msg-protocol:deserialize ((msg <SyncGetStcm-request>) istream)
  "Deserializes a message object of type '<SyncGetStcm-request>"
    (cl:let ((__ros_str_len 0))
      (cl:setf (cl:ldb (cl:byte 8 0) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 16) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 24) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:slot-value msg 'mapfile) (cl:make-string __ros_str_len))
      (cl:dotimes (__ros_str_idx __ros_str_len msg)
        (cl:setf (cl:char (cl:slot-value msg 'mapfile) __ros_str_idx) (cl:code-char (cl:read-byte istream)))))
  msg
)
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql '<SyncGetStcm-request>)))
  "Returns string type for a service object of type '<SyncGetStcm-request>"
  "slamware_ros_sdk/SyncGetStcmRequest")
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql 'SyncGetStcm-request)))
  "Returns string type for a service object of type 'SyncGetStcm-request"
  "slamware_ros_sdk/SyncGetStcmRequest")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql '<SyncGetStcm-request>)))
  "Returns md5sum for a message object of type '<SyncGetStcm-request>"
  "919cbda8c3832c78ab0496dedc3e5520")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql 'SyncGetStcm-request)))
  "Returns md5sum for a message object of type 'SyncGetStcm-request"
  "919cbda8c3832c78ab0496dedc3e5520")
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql '<SyncGetStcm-request>)))
  "Returns full string definition for message of type '<SyncGetStcm-request>"
  (cl:format cl:nil "# Request~%string mapfile~%~%~%~%"))
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql 'SyncGetStcm-request)))
  "Returns full string definition for message of type 'SyncGetStcm-request"
  (cl:format cl:nil "# Request~%string mapfile~%~%~%~%"))
(cl:defmethod roslisp-msg-protocol:serialization-length ((msg <SyncGetStcm-request>))
  (cl:+ 0
     4 (cl:length (cl:slot-value msg 'mapfile))
))
(cl:defmethod roslisp-msg-protocol:ros-message-to-list ((msg <SyncGetStcm-request>))
  "Converts a ROS message object to a list"
  (cl:list 'SyncGetStcm-request
    (cl:cons ':mapfile (mapfile msg))
))
;//! \htmlinclude SyncGetStcm-response.msg.html

(cl:defclass <SyncGetStcm-response> (roslisp-msg-protocol:ros-message)
  ((success
    :reader success
    :initarg :success
    :type cl:boolean
    :initform cl:nil)
   (message
    :reader message
    :initarg :message
    :type cl:string
    :initform ""))
)

(cl:defclass SyncGetStcm-response (<SyncGetStcm-response>)
  ())

(cl:defmethod cl:initialize-instance :after ((m <SyncGetStcm-response>) cl:&rest args)
  (cl:declare (cl:ignorable args))
  (cl:unless (cl:typep m 'SyncGetStcm-response)
    (roslisp-msg-protocol:msg-deprecation-warning "using old message class name slamware_ros_sdk-srv:<SyncGetStcm-response> is deprecated: use slamware_ros_sdk-srv:SyncGetStcm-response instead.")))

(cl:ensure-generic-function 'success-val :lambda-list '(m))
(cl:defmethod success-val ((m <SyncGetStcm-response>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader slamware_ros_sdk-srv:success-val is deprecated.  Use slamware_ros_sdk-srv:success instead.")
  (success m))

(cl:ensure-generic-function 'message-val :lambda-list '(m))
(cl:defmethod message-val ((m <SyncGetStcm-response>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader slamware_ros_sdk-srv:message-val is deprecated.  Use slamware_ros_sdk-srv:message instead.")
  (message m))
(cl:defmethod roslisp-msg-protocol:serialize ((msg <SyncGetStcm-response>) ostream)
  "Serializes a message object of type '<SyncGetStcm-response>"
  (cl:write-byte (cl:ldb (cl:byte 8 0) (cl:if (cl:slot-value msg 'success) 1 0)) ostream)
  (cl:let ((__ros_str_len (cl:length (cl:slot-value msg 'message))))
    (cl:write-byte (cl:ldb (cl:byte 8 0) __ros_str_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) __ros_str_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) __ros_str_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) __ros_str_len) ostream))
  (cl:map cl:nil #'(cl:lambda (c) (cl:write-byte (cl:char-code c) ostream)) (cl:slot-value msg 'message))
)
(cl:defmethod roslisp-msg-protocol:deserialize ((msg <SyncGetStcm-response>) istream)
  "Deserializes a message object of type '<SyncGetStcm-response>"
    (cl:setf (cl:slot-value msg 'success) (cl:not (cl:zerop (cl:read-byte istream))))
    (cl:let ((__ros_str_len 0))
      (cl:setf (cl:ldb (cl:byte 8 0) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 16) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 24) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:slot-value msg 'message) (cl:make-string __ros_str_len))
      (cl:dotimes (__ros_str_idx __ros_str_len msg)
        (cl:setf (cl:char (cl:slot-value msg 'message) __ros_str_idx) (cl:code-char (cl:read-byte istream)))))
  msg
)
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql '<SyncGetStcm-response>)))
  "Returns string type for a service object of type '<SyncGetStcm-response>"
  "slamware_ros_sdk/SyncGetStcmResponse")
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql 'SyncGetStcm-response)))
  "Returns string type for a service object of type 'SyncGetStcm-response"
  "slamware_ros_sdk/SyncGetStcmResponse")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql '<SyncGetStcm-response>)))
  "Returns md5sum for a message object of type '<SyncGetStcm-response>"
  "919cbda8c3832c78ab0496dedc3e5520")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql 'SyncGetStcm-response)))
  "Returns md5sum for a message object of type 'SyncGetStcm-response"
  "919cbda8c3832c78ab0496dedc3e5520")
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql '<SyncGetStcm-response>)))
  "Returns full string definition for message of type '<SyncGetStcm-response>"
  (cl:format cl:nil "~%# Response~%bool success~%string message~%~%~%~%"))
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql 'SyncGetStcm-response)))
  "Returns full string definition for message of type 'SyncGetStcm-response"
  (cl:format cl:nil "~%# Response~%bool success~%string message~%~%~%~%"))
(cl:defmethod roslisp-msg-protocol:serialization-length ((msg <SyncGetStcm-response>))
  (cl:+ 0
     1
     4 (cl:length (cl:slot-value msg 'message))
))
(cl:defmethod roslisp-msg-protocol:ros-message-to-list ((msg <SyncGetStcm-response>))
  "Converts a ROS message object to a list"
  (cl:list 'SyncGetStcm-response
    (cl:cons ':success (success msg))
    (cl:cons ':message (message msg))
))
(cl:defmethod roslisp-msg-protocol:service-request-type ((msg (cl:eql 'SyncGetStcm)))
  'SyncGetStcm-request)
(cl:defmethod roslisp-msg-protocol:service-response-type ((msg (cl:eql 'SyncGetStcm)))
  'SyncGetStcm-response)
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql 'SyncGetStcm)))
  "Returns string type for a service object of type '<SyncGetStcm>"
  "slamware_ros_sdk/SyncGetStcm")