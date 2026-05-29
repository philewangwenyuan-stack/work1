;; Auto-generated. Do not edit!


(when (boundp 'grinder_chassis_driver::WheelSpeedCommand)
  (if (not (find-package "GRINDER_CHASSIS_DRIVER"))
    (make-package "GRINDER_CHASSIS_DRIVER"))
  (shadow 'WheelSpeedCommand (find-package "GRINDER_CHASSIS_DRIVER")))
(unless (find-package "GRINDER_CHASSIS_DRIVER::WHEELSPEEDCOMMAND")
  (make-package "GRINDER_CHASSIS_DRIVER::WHEELSPEEDCOMMAND"))

(in-package "ROS")
;;//! \htmlinclude WheelSpeedCommand.msg.html


(defclass grinder_chassis_driver::WheelSpeedCommand
  :super ros::object
  :slots (_left_wheel_speed _right_wheel_speed ))

(defmethod grinder_chassis_driver::WheelSpeedCommand
  (:init
   (&key
    ((:left_wheel_speed __left_wheel_speed) 0)
    ((:right_wheel_speed __right_wheel_speed) 0)
    )
   (send-super :init)
   (setq _left_wheel_speed (round __left_wheel_speed))
   (setq _right_wheel_speed (round __right_wheel_speed))
   self)
  (:left_wheel_speed
   (&optional __left_wheel_speed)
   (if __left_wheel_speed (setq _left_wheel_speed __left_wheel_speed)) _left_wheel_speed)
  (:right_wheel_speed
   (&optional __right_wheel_speed)
   (if __right_wheel_speed (setq _right_wheel_speed __right_wheel_speed)) _right_wheel_speed)
  (:serialization-length
   ()
   (+
    ;; int16 _left_wheel_speed
    2
    ;; int16 _right_wheel_speed
    2
    ))
  (:serialize
   (&optional strm)
   (let ((s (if strm strm
              (make-string-output-stream (send self :serialization-length)))))
     ;; int16 _left_wheel_speed
       (write-word _left_wheel_speed s)
     ;; int16 _right_wheel_speed
       (write-word _right_wheel_speed s)
     ;;
     (if (null strm) (get-output-stream-string s))))
  (:deserialize
   (buf &optional (ptr- 0))
   ;; int16 _left_wheel_speed
     (setq _left_wheel_speed (sys::peek buf ptr- :short)) (incf ptr- 2)
   ;; int16 _right_wheel_speed
     (setq _right_wheel_speed (sys::peek buf ptr- :short)) (incf ptr- 2)
   ;;
   self)
  )

(setf (get grinder_chassis_driver::WheelSpeedCommand :md5sum-) "7c95657b2cfd28ae6e5771e00b505bd4")
(setf (get grinder_chassis_driver::WheelSpeedCommand :datatype-) "grinder_chassis_driver/WheelSpeedCommand")
(setf (get grinder_chassis_driver::WheelSpeedCommand :definition-)
      "int16 left_wheel_speed
int16 right_wheel_speed

")



(provide :grinder_chassis_driver/WheelSpeedCommand "7c95657b2cfd28ae6e5771e00b505bd4")


