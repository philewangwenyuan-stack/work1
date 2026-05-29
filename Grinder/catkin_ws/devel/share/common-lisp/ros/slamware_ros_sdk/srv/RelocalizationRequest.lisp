; Auto-generated. Do not edit!


(cl:in-package slamware_ros_sdk-srv)


;//! \htmlinclude RelocalizationRequest-request.msg.html

(cl:defclass <RelocalizationRequest-request> (roslisp-msg-protocol:ros-message)
  ()
)

(cl:defclass RelocalizationRequest-request (<RelocalizationRequest-request>)
  ())

(cl:defmethod cl:initialize-instance :after ((m <RelocalizationRequest-request>) cl:&rest args)
  (cl:declare (cl:ignorable args))
  (cl:unless (cl:typep m 'RelocalizationRequest-request)
    (roslisp-msg-protocol:msg-deprecation-warning "using old message class name slamware_ros_sdk-srv:<RelocalizationRequest-request> is deprecated: use slamware_ros_sdk-srv:RelocalizationRequest-request instead.")))
(cl:defmethod roslisp-msg-protocol:serialize ((msg <RelocalizationRequest-request>) ostream)
  "Serializes a message object of type '<RelocalizationRequest-request>"
)
(cl:defmethod roslisp-msg-protocol:deserialize ((msg <RelocalizationRequest-request>) istream)
  "Deserializes a message object of type '<RelocalizationRequest-request>"
  msg
)
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql '<RelocalizationRequest-request>)))
  "Returns string type for a service object of type '<RelocalizationRequest-request>"
  "slamware_ros_sdk/RelocalizationRequestRequest")
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql 'RelocalizationRequest-request)))
  "Returns string type for a service object of type 'RelocalizationRequest-request"
  "slamware_ros_sdk/RelocalizationRequestRequest")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql '<RelocalizationRequest-request>)))
  "Returns md5sum for a message object of type '<RelocalizationRequest-request>"
  "358e233cde0c8a8bcfea4ce193f8fc15")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql 'RelocalizationRequest-request)))
  "Returns md5sum for a message object of type 'RelocalizationRequest-request"
  "358e233cde0c8a8bcfea4ce193f8fc15")
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql '<RelocalizationRequest-request>)))
  "Returns full string definition for message of type '<RelocalizationRequest-request>"
  (cl:format cl:nil "~%#request~%~%~%~%"))
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql 'RelocalizationRequest-request)))
  "Returns full string definition for message of type 'RelocalizationRequest-request"
  (cl:format cl:nil "~%#request~%~%~%~%"))
(cl:defmethod roslisp-msg-protocol:serialization-length ((msg <RelocalizationRequest-request>))
  (cl:+ 0
))
(cl:defmethod roslisp-msg-protocol:ros-message-to-list ((msg <RelocalizationRequest-request>))
  "Converts a ROS message object to a list"
  (cl:list 'RelocalizationRequest-request
))
;//! \htmlinclude RelocalizationRequest-response.msg.html

(cl:defclass <RelocalizationRequest-response> (roslisp-msg-protocol:ros-message)
  ((success
    :reader success
    :initarg :success
    :type cl:boolean
    :initform cl:nil))
)

(cl:defclass RelocalizationRequest-response (<RelocalizationRequest-response>)
  ())

(cl:defmethod cl:initialize-instance :after ((m <RelocalizationRequest-response>) cl:&rest args)
  (cl:declare (cl:ignorable args))
  (cl:unless (cl:typep m 'RelocalizationRequest-response)
    (roslisp-msg-protocol:msg-deprecation-warning "using old message class name slamware_ros_sdk-srv:<RelocalizationRequest-response> is deprecated: use slamware_ros_sdk-srv:RelocalizationRequest-response instead.")))

(cl:ensure-generic-function 'success-val :lambda-list '(m))
(cl:defmethod success-val ((m <RelocalizationRequest-response>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader slamware_ros_sdk-srv:success-val is deprecated.  Use slamware_ros_sdk-srv:success instead.")
  (success m))
(cl:defmethod roslisp-msg-protocol:serialize ((msg <RelocalizationRequest-response>) ostream)
  "Serializes a message object of type '<RelocalizationRequest-response>"
  (cl:write-byte (cl:ldb (cl:byte 8 0) (cl:if (cl:slot-value msg 'success) 1 0)) ostream)
)
(cl:defmethod roslisp-msg-protocol:deserialize ((msg <RelocalizationRequest-response>) istream)
  "Deserializes a message object of type '<RelocalizationRequest-response>"
    (cl:setf (cl:slot-value msg 'success) (cl:not (cl:zerop (cl:read-byte istream))))
  msg
)
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql '<RelocalizationRequest-response>)))
  "Returns string type for a service object of type '<RelocalizationRequest-response>"
  "slamware_ros_sdk/RelocalizationRequestResponse")
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql 'RelocalizationRequest-response)))
  "Returns string type for a service object of type 'RelocalizationRequest-response"
  "slamware_ros_sdk/RelocalizationRequestResponse")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql '<RelocalizationRequest-response>)))
  "Returns md5sum for a message object of type '<RelocalizationRequest-response>"
  "358e233cde0c8a8bcfea4ce193f8fc15")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql 'RelocalizationRequest-response)))
  "Returns md5sum for a message object of type 'RelocalizationRequest-response"
  "358e233cde0c8a8bcfea4ce193f8fc15")
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql '<RelocalizationRequest-response>)))
  "Returns full string definition for message of type '<RelocalizationRequest-response>"
  (cl:format cl:nil "~%#response~%bool success~%~%~%"))
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql 'RelocalizationRequest-response)))
  "Returns full string definition for message of type 'RelocalizationRequest-response"
  (cl:format cl:nil "~%#response~%bool success~%~%~%"))
(cl:defmethod roslisp-msg-protocol:serialization-length ((msg <RelocalizationRequest-response>))
  (cl:+ 0
     1
))
(cl:defmethod roslisp-msg-protocol:ros-message-to-list ((msg <RelocalizationRequest-response>))
  "Converts a ROS message object to a list"
  (cl:list 'RelocalizationRequest-response
    (cl:cons ':success (success msg))
))
(cl:defmethod roslisp-msg-protocol:service-request-type ((msg (cl:eql 'RelocalizationRequest)))
  'RelocalizationRequest-request)
(cl:defmethod roslisp-msg-protocol:service-response-type ((msg (cl:eql 'RelocalizationRequest)))
  'RelocalizationRequest-response)
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql 'RelocalizationRequest)))
  "Returns string type for a service object of type '<RelocalizationRequest>"
  "slamware_ros_sdk/RelocalizationRequest")