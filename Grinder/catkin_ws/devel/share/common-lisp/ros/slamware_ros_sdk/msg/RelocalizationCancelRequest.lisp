; Auto-generated. Do not edit!


(cl:in-package slamware_ros_sdk-msg)


;//! \htmlinclude RelocalizationCancelRequest.msg.html

(cl:defclass <RelocalizationCancelRequest> (roslisp-msg-protocol:ros-message)
  ()
)

(cl:defclass RelocalizationCancelRequest (<RelocalizationCancelRequest>)
  ())

(cl:defmethod cl:initialize-instance :after ((m <RelocalizationCancelRequest>) cl:&rest args)
  (cl:declare (cl:ignorable args))
  (cl:unless (cl:typep m 'RelocalizationCancelRequest)
    (roslisp-msg-protocol:msg-deprecation-warning "using old message class name slamware_ros_sdk-msg:<RelocalizationCancelRequest> is deprecated: use slamware_ros_sdk-msg:RelocalizationCancelRequest instead.")))
(cl:defmethod roslisp-msg-protocol:serialize ((msg <RelocalizationCancelRequest>) ostream)
  "Serializes a message object of type '<RelocalizationCancelRequest>"
)
(cl:defmethod roslisp-msg-protocol:deserialize ((msg <RelocalizationCancelRequest>) istream)
  "Deserializes a message object of type '<RelocalizationCancelRequest>"
  msg
)
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql '<RelocalizationCancelRequest>)))
  "Returns string type for a message object of type '<RelocalizationCancelRequest>"
  "slamware_ros_sdk/RelocalizationCancelRequest")
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql 'RelocalizationCancelRequest)))
  "Returns string type for a message object of type 'RelocalizationCancelRequest"
  "slamware_ros_sdk/RelocalizationCancelRequest")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql '<RelocalizationCancelRequest>)))
  "Returns md5sum for a message object of type '<RelocalizationCancelRequest>"
  "d41d8cd98f00b204e9800998ecf8427e")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql 'RelocalizationCancelRequest)))
  "Returns md5sum for a message object of type 'RelocalizationCancelRequest"
  "d41d8cd98f00b204e9800998ecf8427e")
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql '<RelocalizationCancelRequest>)))
  "Returns full string definition for message of type '<RelocalizationCancelRequest>"
  (cl:format cl:nil "# currently nothing in this message~%~%"))
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql 'RelocalizationCancelRequest)))
  "Returns full string definition for message of type 'RelocalizationCancelRequest"
  (cl:format cl:nil "# currently nothing in this message~%~%"))
(cl:defmethod roslisp-msg-protocol:serialization-length ((msg <RelocalizationCancelRequest>))
  (cl:+ 0
))
(cl:defmethod roslisp-msg-protocol:ros-message-to-list ((msg <RelocalizationCancelRequest>))
  "Converts a ROS message object to a list"
  (cl:list 'RelocalizationCancelRequest
))
