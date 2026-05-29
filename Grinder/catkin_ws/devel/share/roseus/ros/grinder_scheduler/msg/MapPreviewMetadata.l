;; Auto-generated. Do not edit!


(when (boundp 'grinder_scheduler::MapPreviewMetadata)
  (if (not (find-package "GRINDER_SCHEDULER"))
    (make-package "GRINDER_SCHEDULER"))
  (shadow 'MapPreviewMetadata (find-package "GRINDER_SCHEDULER")))
(unless (find-package "GRINDER_SCHEDULER::MAPPREVIEWMETADATA")
  (make-package "GRINDER_SCHEDULER::MAPPREVIEWMETADATA"))

(in-package "ROS")
;;//! \htmlinclude MapPreviewMetadata.msg.html
(if (not (find-package "GEOMETRY_MSGS"))
  (ros::roseus-add-msgs "geometry_msgs"))
(if (not (find-package "STD_MSGS"))
  (ros::roseus-add-msgs "std_msgs"))


(defclass grinder_scheduler::MapPreviewMetadata
  :super ros::object
  :slots (_header _map_version _width _height _resolution _origin _frame_id ))

(defmethod grinder_scheduler::MapPreviewMetadata
  (:init
   (&key
    ((:header __header) (instance std_msgs::Header :init))
    ((:map_version __map_version) 0)
    ((:width __width) 0)
    ((:height __height) 0)
    ((:resolution __resolution) 0.0)
    ((:origin __origin) (instance geometry_msgs::Pose :init))
    ((:frame_id __frame_id) "")
    )
   (send-super :init)
   (setq _header __header)
   (setq _map_version (round __map_version))
   (setq _width (round __width))
   (setq _height (round __height))
   (setq _resolution (float __resolution))
   (setq _origin __origin)
   (setq _frame_id (string __frame_id))
   self)
  (:header
   (&rest __header)
   (if (keywordp (car __header))
       (send* _header __header)
     (progn
       (if __header (setq _header (car __header)))
       _header)))
  (:map_version
   (&optional __map_version)
   (if __map_version (setq _map_version __map_version)) _map_version)
  (:width
   (&optional __width)
   (if __width (setq _width __width)) _width)
  (:height
   (&optional __height)
   (if __height (setq _height __height)) _height)
  (:resolution
   (&optional __resolution)
   (if __resolution (setq _resolution __resolution)) _resolution)
  (:origin
   (&rest __origin)
   (if (keywordp (car __origin))
       (send* _origin __origin)
     (progn
       (if __origin (setq _origin (car __origin)))
       _origin)))
  (:frame_id
   (&optional __frame_id)
   (if __frame_id (setq _frame_id __frame_id)) _frame_id)
  (:serialization-length
   ()
   (+
    ;; std_msgs/Header _header
    (send _header :serialization-length)
    ;; uint32 _map_version
    4
    ;; uint32 _width
    4
    ;; uint32 _height
    4
    ;; float32 _resolution
    4
    ;; geometry_msgs/Pose _origin
    (send _origin :serialization-length)
    ;; string _frame_id
    4 (length _frame_id)
    ))
  (:serialize
   (&optional strm)
   (let ((s (if strm strm
              (make-string-output-stream (send self :serialization-length)))))
     ;; std_msgs/Header _header
       (send _header :serialize s)
     ;; uint32 _map_version
       (write-long _map_version s)
     ;; uint32 _width
       (write-long _width s)
     ;; uint32 _height
       (write-long _height s)
     ;; float32 _resolution
       (sys::poke _resolution (send s :buffer) (send s :count) :float) (incf (stream-count s) 4)
     ;; geometry_msgs/Pose _origin
       (send _origin :serialize s)
     ;; string _frame_id
       (write-long (length _frame_id) s) (princ _frame_id s)
     ;;
     (if (null strm) (get-output-stream-string s))))
  (:deserialize
   (buf &optional (ptr- 0))
   ;; std_msgs/Header _header
     (send _header :deserialize buf ptr-) (incf ptr- (send _header :serialization-length))
   ;; uint32 _map_version
     (setq _map_version (sys::peek buf ptr- :integer)) (incf ptr- 4)
   ;; uint32 _width
     (setq _width (sys::peek buf ptr- :integer)) (incf ptr- 4)
   ;; uint32 _height
     (setq _height (sys::peek buf ptr- :integer)) (incf ptr- 4)
   ;; float32 _resolution
     (setq _resolution (sys::peek buf ptr- :float)) (incf ptr- 4)
   ;; geometry_msgs/Pose _origin
     (send _origin :deserialize buf ptr-) (incf ptr- (send _origin :serialization-length))
   ;; string _frame_id
     (let (n) (setq n (sys::peek buf ptr- :integer)) (incf ptr- 4) (setq _frame_id (subseq buf ptr- (+ ptr- n))) (incf ptr- n))
   ;;
   self)
  )

(setf (get grinder_scheduler::MapPreviewMetadata :md5sum-) "48758f15fb7527a0ea9d6aed393eee0c")
(setf (get grinder_scheduler::MapPreviewMetadata :datatype-) "grinder_scheduler/MapPreviewMetadata")
(setf (get grinder_scheduler::MapPreviewMetadata :definition-)
      "std_msgs/Header header
uint32 map_version
uint32 width
uint32 height
float32 resolution
geometry_msgs/Pose origin
string frame_id

================================================================================
MSG: std_msgs/Header
# Standard metadata for higher-level stamped data types.
# This is generally used to communicate timestamped data 
# in a particular coordinate frame.
# 
# sequence ID: consecutively increasing ID 
uint32 seq
#Two-integer timestamp that is expressed as:
# * stamp.sec: seconds (stamp_secs) since epoch (in Python the variable is called 'secs')
# * stamp.nsec: nanoseconds since stamp_secs (in Python the variable is called 'nsecs')
# time-handling sugar is provided by the client library
time stamp
#Frame this data is associated with
string frame_id

================================================================================
MSG: geometry_msgs/Pose
# A representation of pose in free space, composed of position and orientation. 
Point position
Quaternion orientation

================================================================================
MSG: geometry_msgs/Point
# This contains the position of a point in free space
float64 x
float64 y
float64 z

================================================================================
MSG: geometry_msgs/Quaternion
# This represents an orientation in free space in quaternion form.

float64 x
float64 y
float64 z
float64 w

")



(provide :grinder_scheduler/MapPreviewMetadata "48758f15fb7527a0ea9d6aed393eee0c")


