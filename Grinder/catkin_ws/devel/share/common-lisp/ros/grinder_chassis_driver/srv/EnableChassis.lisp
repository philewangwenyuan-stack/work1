; Auto-generated. Do not edit!


(cl:in-package grinder_chassis_driver-srv)


;//! \htmlinclude EnableChassis-request.msg.html

(cl:defclass <EnableChassis-request> (roslisp-msg-protocol:ros-message)
  ((enable
    :reader enable
    :initarg :enable
    :type cl:boolean
    :initform cl:nil))
)

(cl:defclass EnableChassis-request (<EnableChassis-request>)
  ())

(cl:defmethod cl:initialize-instance :after ((m <EnableChassis-request>) cl:&rest args)
  (cl:declare (cl:ignorable args))
  (cl:unless (cl:typep m 'EnableChassis-request)
    (roslisp-msg-protocol:msg-deprecation-warning "using old message class name grinder_chassis_driver-srv:<EnableChassis-request> is deprecated: use grinder_chassis_driver-srv:EnableChassis-request instead.")))

(cl:ensure-generic-function 'enable-val :lambda-list '(m))
(cl:defmethod enable-val ((m <EnableChassis-request>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader grinder_chassis_driver-srv:enable-val is deprecated.  Use grinder_chassis_driver-srv:enable instead.")
  (enable m))
(cl:defmethod roslisp-msg-protocol:serialize ((msg <EnableChassis-request>) ostream)
  "Serializes a message object of type '<EnableChassis-request>"
  (cl:write-byte (cl:ldb (cl:byte 8 0) (cl:if (cl:slot-value msg 'enable) 1 0)) ostream)
)
(cl:defmethod roslisp-msg-protocol:deserialize ((msg <EnableChassis-request>) istream)
  "Deserializes a message object of type '<EnableChassis-request>"
    (cl:setf (cl:slot-value msg 'enable) (cl:not (cl:zerop (cl:read-byte istream))))
  msg
)
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql '<EnableChassis-request>)))
  "Returns string type for a service object of type '<EnableChassis-request>"
  "grinder_chassis_driver/EnableChassisRequest")
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql 'EnableChassis-request)))
  "Returns string type for a service object of type 'EnableChassis-request"
  "grinder_chassis_driver/EnableChassisRequest")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql '<EnableChassis-request>)))
  "Returns md5sum for a message object of type '<EnableChassis-request>"
  "66bc8d9da0bd59298d38df02f3ee7f7f")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql 'EnableChassis-request)))
  "Returns md5sum for a message object of type 'EnableChassis-request"
  "66bc8d9da0bd59298d38df02f3ee7f7f")
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql '<EnableChassis-request>)))
  "Returns full string definition for message of type '<EnableChassis-request>"
  (cl:format cl:nil "bool enable~%~%~%"))
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql 'EnableChassis-request)))
  "Returns full string definition for message of type 'EnableChassis-request"
  (cl:format cl:nil "bool enable~%~%~%"))
(cl:defmethod roslisp-msg-protocol:serialization-length ((msg <EnableChassis-request>))
  (cl:+ 0
     1
))
(cl:defmethod roslisp-msg-protocol:ros-message-to-list ((msg <EnableChassis-request>))
  "Converts a ROS message object to a list"
  (cl:list 'EnableChassis-request
    (cl:cons ':enable (enable msg))
))
;//! \htmlinclude EnableChassis-response.msg.html

(cl:defclass <EnableChassis-response> (roslisp-msg-protocol:ros-message)
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

(cl:defclass EnableChassis-response (<EnableChassis-response>)
  ())

(cl:defmethod cl:initialize-instance :after ((m <EnableChassis-response>) cl:&rest args)
  (cl:declare (cl:ignorable args))
  (cl:unless (cl:typep m 'EnableChassis-response)
    (roslisp-msg-protocol:msg-deprecation-warning "using old message class name grinder_chassis_driver-srv:<EnableChassis-response> is deprecated: use grinder_chassis_driver-srv:EnableChassis-response instead.")))

(cl:ensure-generic-function 'success-val :lambda-list '(m))
(cl:defmethod success-val ((m <EnableChassis-response>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader grinder_chassis_driver-srv:success-val is deprecated.  Use grinder_chassis_driver-srv:success instead.")
  (success m))

(cl:ensure-generic-function 'message-val :lambda-list '(m))
(cl:defmethod message-val ((m <EnableChassis-response>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader grinder_chassis_driver-srv:message-val is deprecated.  Use grinder_chassis_driver-srv:message instead.")
  (message m))
(cl:defmethod roslisp-msg-protocol:serialize ((msg <EnableChassis-response>) ostream)
  "Serializes a message object of type '<EnableChassis-response>"
  (cl:write-byte (cl:ldb (cl:byte 8 0) (cl:if (cl:slot-value msg 'success) 1 0)) ostream)
  (cl:let ((__ros_str_len (cl:length (cl:slot-value msg 'message))))
    (cl:write-byte (cl:ldb (cl:byte 8 0) __ros_str_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) __ros_str_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) __ros_str_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) __ros_str_len) ostream))
  (cl:map cl:nil #'(cl:lambda (c) (cl:write-byte (cl:char-code c) ostream)) (cl:slot-value msg 'message))
)
(cl:defmethod roslisp-msg-protocol:deserialize ((msg <EnableChassis-response>) istream)
  "Deserializes a message object of type '<EnableChassis-response>"
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
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql '<EnableChassis-response>)))
  "Returns string type for a service object of type '<EnableChassis-response>"
  "grinder_chassis_driver/EnableChassisResponse")
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql 'EnableChassis-response)))
  "Returns string type for a service object of type 'EnableChassis-response"
  "grinder_chassis_driver/EnableChassisResponse")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql '<EnableChassis-response>)))
  "Returns md5sum for a message object of type '<EnableChassis-response>"
  "66bc8d9da0bd59298d38df02f3ee7f7f")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql 'EnableChassis-response)))
  "Returns md5sum for a message object of type 'EnableChassis-response"
  "66bc8d9da0bd59298d38df02f3ee7f7f")
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql '<EnableChassis-response>)))
  "Returns full string definition for message of type '<EnableChassis-response>"
  (cl:format cl:nil "bool success~%string message~%~%~%~%"))
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql 'EnableChassis-response)))
  "Returns full string definition for message of type 'EnableChassis-response"
  (cl:format cl:nil "bool success~%string message~%~%~%~%"))
(cl:defmethod roslisp-msg-protocol:serialization-length ((msg <EnableChassis-response>))
  (cl:+ 0
     1
     4 (cl:length (cl:slot-value msg 'message))
))
(cl:defmethod roslisp-msg-protocol:ros-message-to-list ((msg <EnableChassis-response>))
  "Converts a ROS message object to a list"
  (cl:list 'EnableChassis-response
    (cl:cons ':success (success msg))
    (cl:cons ':message (message msg))
))
(cl:defmethod roslisp-msg-protocol:service-request-type ((msg (cl:eql 'EnableChassis)))
  'EnableChassis-request)
(cl:defmethod roslisp-msg-protocol:service-response-type ((msg (cl:eql 'EnableChassis)))
  'EnableChassis-response)
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql 'EnableChassis)))
  "Returns string type for a service object of type '<EnableChassis>"
  "grinder_chassis_driver/EnableChassis")