; Auto-generated. Do not edit!


(cl:in-package grinder_chassis_driver-msg)


;//! \htmlinclude WheelSpeedCommand.msg.html

(cl:defclass <WheelSpeedCommand> (roslisp-msg-protocol:ros-message)
  ((left_wheel_speed
    :reader left_wheel_speed
    :initarg :left_wheel_speed
    :type cl:fixnum
    :initform 0)
   (right_wheel_speed
    :reader right_wheel_speed
    :initarg :right_wheel_speed
    :type cl:fixnum
    :initform 0))
)

(cl:defclass WheelSpeedCommand (<WheelSpeedCommand>)
  ())

(cl:defmethod cl:initialize-instance :after ((m <WheelSpeedCommand>) cl:&rest args)
  (cl:declare (cl:ignorable args))
  (cl:unless (cl:typep m 'WheelSpeedCommand)
    (roslisp-msg-protocol:msg-deprecation-warning "using old message class name grinder_chassis_driver-msg:<WheelSpeedCommand> is deprecated: use grinder_chassis_driver-msg:WheelSpeedCommand instead.")))

(cl:ensure-generic-function 'left_wheel_speed-val :lambda-list '(m))
(cl:defmethod left_wheel_speed-val ((m <WheelSpeedCommand>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader grinder_chassis_driver-msg:left_wheel_speed-val is deprecated.  Use grinder_chassis_driver-msg:left_wheel_speed instead.")
  (left_wheel_speed m))

(cl:ensure-generic-function 'right_wheel_speed-val :lambda-list '(m))
(cl:defmethod right_wheel_speed-val ((m <WheelSpeedCommand>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader grinder_chassis_driver-msg:right_wheel_speed-val is deprecated.  Use grinder_chassis_driver-msg:right_wheel_speed instead.")
  (right_wheel_speed m))
(cl:defmethod roslisp-msg-protocol:serialize ((msg <WheelSpeedCommand>) ostream)
  "Serializes a message object of type '<WheelSpeedCommand>"
  (cl:let* ((signed (cl:slot-value msg 'left_wheel_speed)) (unsigned (cl:if (cl:< signed 0) (cl:+ signed 65536) signed)))
    (cl:write-byte (cl:ldb (cl:byte 8 0) unsigned) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) unsigned) ostream)
    )
  (cl:let* ((signed (cl:slot-value msg 'right_wheel_speed)) (unsigned (cl:if (cl:< signed 0) (cl:+ signed 65536) signed)))
    (cl:write-byte (cl:ldb (cl:byte 8 0) unsigned) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) unsigned) ostream)
    )
)
(cl:defmethod roslisp-msg-protocol:deserialize ((msg <WheelSpeedCommand>) istream)
  "Deserializes a message object of type '<WheelSpeedCommand>"
    (cl:let ((unsigned 0))
      (cl:setf (cl:ldb (cl:byte 8 0) unsigned) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) unsigned) (cl:read-byte istream))
      (cl:setf (cl:slot-value msg 'left_wheel_speed) (cl:if (cl:< unsigned 32768) unsigned (cl:- unsigned 65536))))
    (cl:let ((unsigned 0))
      (cl:setf (cl:ldb (cl:byte 8 0) unsigned) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) unsigned) (cl:read-byte istream))
      (cl:setf (cl:slot-value msg 'right_wheel_speed) (cl:if (cl:< unsigned 32768) unsigned (cl:- unsigned 65536))))
  msg
)
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql '<WheelSpeedCommand>)))
  "Returns string type for a message object of type '<WheelSpeedCommand>"
  "grinder_chassis_driver/WheelSpeedCommand")
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql 'WheelSpeedCommand)))
  "Returns string type for a message object of type 'WheelSpeedCommand"
  "grinder_chassis_driver/WheelSpeedCommand")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql '<WheelSpeedCommand>)))
  "Returns md5sum for a message object of type '<WheelSpeedCommand>"
  "7c95657b2cfd28ae6e5771e00b505bd4")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql 'WheelSpeedCommand)))
  "Returns md5sum for a message object of type 'WheelSpeedCommand"
  "7c95657b2cfd28ae6e5771e00b505bd4")
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql '<WheelSpeedCommand>)))
  "Returns full string definition for message of type '<WheelSpeedCommand>"
  (cl:format cl:nil "int16 left_wheel_speed~%int16 right_wheel_speed~%~%~%"))
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql 'WheelSpeedCommand)))
  "Returns full string definition for message of type 'WheelSpeedCommand"
  (cl:format cl:nil "int16 left_wheel_speed~%int16 right_wheel_speed~%~%~%"))
(cl:defmethod roslisp-msg-protocol:serialization-length ((msg <WheelSpeedCommand>))
  (cl:+ 0
     2
     2
))
(cl:defmethod roslisp-msg-protocol:ros-message-to-list ((msg <WheelSpeedCommand>))
  "Converts a ROS message object to a list"
  (cl:list 'WheelSpeedCommand
    (cl:cons ':left_wheel_speed (left_wheel_speed msg))
    (cl:cons ':right_wheel_speed (right_wheel_speed msg))
))
