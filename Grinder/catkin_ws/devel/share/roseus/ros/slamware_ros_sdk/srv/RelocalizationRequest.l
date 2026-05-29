;; Auto-generated. Do not edit!


(when (boundp 'slamware_ros_sdk::RelocalizationRequest)
  (if (not (find-package "SLAMWARE_ROS_SDK"))
    (make-package "SLAMWARE_ROS_SDK"))
  (shadow 'RelocalizationRequest (find-package "SLAMWARE_ROS_SDK")))
(unless (find-package "SLAMWARE_ROS_SDK::RELOCALIZATIONREQUEST")
  (make-package "SLAMWARE_ROS_SDK::RELOCALIZATIONREQUEST"))
(unless (find-package "SLAMWARE_ROS_SDK::RELOCALIZATIONREQUESTREQUEST")
  (make-package "SLAMWARE_ROS_SDK::RELOCALIZATIONREQUESTREQUEST"))
(unless (find-package "SLAMWARE_ROS_SDK::RELOCALIZATIONREQUESTRESPONSE")
  (make-package "SLAMWARE_ROS_SDK::RELOCALIZATIONREQUESTRESPONSE"))

(in-package "ROS")





(defclass slamware_ros_sdk::RelocalizationRequestRequest
  :super ros::object
  :slots ())

(defmethod slamware_ros_sdk::RelocalizationRequestRequest
  (:init
   (&key
    )
   (send-super :init)
   self)
  (:serialization-length
   ()
   (+
    0
    ))
  (:serialize
   (&optional strm)
   (let ((s (if strm strm
              (make-string-output-stream (send self :serialization-length)))))
     ;;
     (if (null strm) (get-output-stream-string s))))
  (:deserialize
   (buf &optional (ptr- 0))
   ;;
   self)
  )

(defclass slamware_ros_sdk::RelocalizationRequestResponse
  :super ros::object
  :slots (_success ))

(defmethod slamware_ros_sdk::RelocalizationRequestResponse
  (:init
   (&key
    ((:success __success) nil)
    )
   (send-super :init)
   (setq _success __success)
   self)
  (:success
   (&optional (__success :null))
   (if (not (eq __success :null)) (setq _success __success)) _success)
  (:serialization-length
   ()
   (+
    ;; bool _success
    1
    ))
  (:serialize
   (&optional strm)
   (let ((s (if strm strm
              (make-string-output-stream (send self :serialization-length)))))
     ;; bool _success
       (if _success (write-byte -1 s) (write-byte 0 s))
     ;;
     (if (null strm) (get-output-stream-string s))))
  (:deserialize
   (buf &optional (ptr- 0))
   ;; bool _success
     (setq _success (not (= 0 (sys::peek buf ptr- :char)))) (incf ptr- 1)
   ;;
   self)
  )

(defclass slamware_ros_sdk::RelocalizationRequest
  :super ros::object
  :slots ())

(setf (get slamware_ros_sdk::RelocalizationRequest :md5sum-) "358e233cde0c8a8bcfea4ce193f8fc15")
(setf (get slamware_ros_sdk::RelocalizationRequest :datatype-) "slamware_ros_sdk/RelocalizationRequest")
(setf (get slamware_ros_sdk::RelocalizationRequest :request) slamware_ros_sdk::RelocalizationRequestRequest)
(setf (get slamware_ros_sdk::RelocalizationRequest :response) slamware_ros_sdk::RelocalizationRequestResponse)

(defmethod slamware_ros_sdk::RelocalizationRequestRequest
  (:response () (instance slamware_ros_sdk::RelocalizationRequestResponse :init)))

(setf (get slamware_ros_sdk::RelocalizationRequestRequest :md5sum-) "358e233cde0c8a8bcfea4ce193f8fc15")
(setf (get slamware_ros_sdk::RelocalizationRequestRequest :datatype-) "slamware_ros_sdk/RelocalizationRequestRequest")
(setf (get slamware_ros_sdk::RelocalizationRequestRequest :definition-)
      "
#request

---

#response
bool success
")

(setf (get slamware_ros_sdk::RelocalizationRequestResponse :md5sum-) "358e233cde0c8a8bcfea4ce193f8fc15")
(setf (get slamware_ros_sdk::RelocalizationRequestResponse :datatype-) "slamware_ros_sdk/RelocalizationRequestResponse")
(setf (get slamware_ros_sdk::RelocalizationRequestResponse :definition-)
      "
#request

---

#response
bool success
")



(provide :slamware_ros_sdk/RelocalizationRequest "358e233cde0c8a8bcfea4ce193f8fc15")


