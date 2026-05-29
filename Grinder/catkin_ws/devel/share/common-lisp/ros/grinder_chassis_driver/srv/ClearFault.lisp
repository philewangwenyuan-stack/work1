; Auto-generated. Do not edit!


(cl:in-package grinder_chassis_driver-srv)


;//! \htmlinclude ClearFault-request.msg.html

(cl:defclass <ClearFault-request> (roslisp-msg-protocol:ros-message)
  ()
)

(cl:defclass ClearFault-request (<ClearFault-request>)
  ())

(cl:defmethod cl:initialize-instance :after ((m <ClearFault-request>) cl:&rest args)
  (cl:declare (cl:ignorable args))
  (cl:unless (cl:typep m 'ClearFault-request)
    (roslisp-msg-protocol:msg-deprecation-warning "using old message class name grinder_chassis_driver-srv:<ClearFault-request> is deprecated: use grinder_chassis_driver-srv:ClearFault-request instead.")))
(cl:defmethod roslisp-msg-protocol:serialize ((msg <ClearFault-request>) ostream)
  "Serializes a message object of type '<ClearFault-request>"
)
(cl:defmethod roslisp-msg-protocol:deserialize ((msg <ClearFault-request>) istream)
  "Deserializes a message object of type '<ClearFault-request>"
  msg
)
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql '<ClearFault-request>)))
  "Returns string type for a service object of type '<ClearFault-request>"
  "grinder_chassis_driver/ClearFaultRequest")
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql 'ClearFault-request)))
  "Returns string type for a service object of type 'ClearFault-request"
  "grinder_chassis_driver/ClearFaultRequest")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql '<ClearFault-request>)))
  "Returns md5sum for a message object of type '<ClearFault-request>"
  "937c9679a518e3a18d831e57125ea522")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql 'ClearFault-request)))
  "Returns md5sum for a message object of type 'ClearFault-request"
  "937c9679a518e3a18d831e57125ea522")
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql '<ClearFault-request>)))
  "Returns full string definition for message of type '<ClearFault-request>"
  (cl:format cl:nil "~%~%"))
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql 'ClearFault-request)))
  "Returns full string definition for message of type 'ClearFault-request"
  (cl:format cl:nil "~%~%"))
(cl:defmethod roslisp-msg-protocol:serialization-length ((msg <ClearFault-request>))
  (cl:+ 0
))
(cl:defmethod roslisp-msg-protocol:ros-message-to-list ((msg <ClearFault-request>))
  "Converts a ROS message object to a list"
  (cl:list 'ClearFault-request
))
;//! \htmlinclude ClearFault-response.msg.html

(cl:defclass <ClearFault-response> (roslisp-msg-protocol:ros-message)
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

(cl:defclass ClearFault-response (<ClearFault-response>)
  ())

(cl:defmethod cl:initialize-instance :after ((m <ClearFault-response>) cl:&rest args)
  (cl:declare (cl:ignorable args))
  (cl:unless (cl:typep m 'ClearFault-response)
    (roslisp-msg-protocol:msg-deprecation-warning "using old message class name grinder_chassis_driver-srv:<ClearFault-response> is deprecated: use grinder_chassis_driver-srv:ClearFault-response instead.")))

(cl:ensure-generic-function 'success-val :lambda-list '(m))
(cl:defmethod success-val ((m <ClearFault-response>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader grinder_chassis_driver-srv:success-val is deprecated.  Use grinder_chassis_driver-srv:success instead.")
  (success m))

(cl:ensure-generic-function 'message-val :lambda-list '(m))
(cl:defmethod message-val ((m <ClearFault-response>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader grinder_chassis_driver-srv:message-val is deprecated.  Use grinder_chassis_driver-srv:message instead.")
  (message m))
(cl:defmethod roslisp-msg-protocol:serialize ((msg <ClearFault-response>) ostream)
  "Serializes a message object of type '<ClearFault-response>"
  (cl:write-byte (cl:ldb (cl:byte 8 0) (cl:if (cl:slot-value msg 'success) 1 0)) ostream)
  (cl:let ((__ros_str_len (cl:length (cl:slot-value msg 'message))))
    (cl:write-byte (cl:ldb (cl:byte 8 0) __ros_str_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) __ros_str_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) __ros_str_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) __ros_str_len) ostream))
  (cl:map cl:nil #'(cl:lambda (c) (cl:write-byte (cl:char-code c) ostream)) (cl:slot-value msg 'message))
)
(cl:defmethod roslisp-msg-protocol:deserialize ((msg <ClearFault-response>) istream)
  "Deserializes a message object of type '<ClearFault-response>"
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
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql '<ClearFault-response>)))
  "Returns string type for a service object of type '<ClearFault-response>"
  "grinder_chassis_driver/ClearFaultResponse")
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql 'ClearFault-response)))
  "Returns string type for a service object of type 'ClearFault-response"
  "grinder_chassis_driver/ClearFaultResponse")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql '<ClearFault-response>)))
  "Returns md5sum for a message object of type '<ClearFault-response>"
  "937c9679a518e3a18d831e57125ea522")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql 'ClearFault-response)))
  "Returns md5sum for a message object of type 'ClearFault-response"
  "937c9679a518e3a18d831e57125ea522")
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql '<ClearFault-response>)))
  "Returns full string definition for message of type '<ClearFault-response>"
  (cl:format cl:nil "bool success~%string message~%~%~%~%"))
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql 'ClearFault-response)))
  "Returns full string definition for message of type 'ClearFault-response"
  (cl:format cl:nil "bool success~%string message~%~%~%~%"))
(cl:defmethod roslisp-msg-protocol:serialization-length ((msg <ClearFault-response>))
  (cl:+ 0
     1
     4 (cl:length (cl:slot-value msg 'message))
))
(cl:defmethod roslisp-msg-protocol:ros-message-to-list ((msg <ClearFault-response>))
  "Converts a ROS message object to a list"
  (cl:list 'ClearFault-response
    (cl:cons ':success (success msg))
    (cl:cons ':message (message msg))
))
(cl:defmethod roslisp-msg-protocol:service-request-type ((msg (cl:eql 'ClearFault)))
  'ClearFault-request)
(cl:defmethod roslisp-msg-protocol:service-response-type ((msg (cl:eql 'ClearFault)))
  'ClearFault-response)
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql 'ClearFault)))
  "Returns string type for a service object of type '<ClearFault>"
  "grinder_chassis_driver/ClearFault")