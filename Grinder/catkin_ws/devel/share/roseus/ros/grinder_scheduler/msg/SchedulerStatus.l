;; Auto-generated. Do not edit!


(when (boundp 'grinder_scheduler::SchedulerStatus)
  (if (not (find-package "GRINDER_SCHEDULER"))
    (make-package "GRINDER_SCHEDULER"))
  (shadow 'SchedulerStatus (find-package "GRINDER_SCHEDULER")))
(unless (find-package "GRINDER_SCHEDULER::SCHEDULERSTATUS")
  (make-package "GRINDER_SCHEDULER::SCHEDULERSTATUS"))

(in-package "ROS")
;;//! \htmlinclude SchedulerStatus.msg.html
(if (not (find-package "GEOMETRY_MSGS"))
  (ros::roseus-add-msgs "geometry_msgs"))
(if (not (find-package "STD_MSGS"))
  (ros::roseus-add-msgs "std_msgs"))


(defclass grinder_scheduler::SchedulerStatus
  :super ros::object
  :slots (_header _task_id _state _progress _map_version _map_available _stream_online _replan_requested _last_error _pose _path_point_count ))

(defmethod grinder_scheduler::SchedulerStatus
  (:init
   (&key
    ((:header __header) (instance std_msgs::Header :init))
    ((:task_id __task_id) "")
    ((:state __state) "")
    ((:progress __progress) 0.0)
    ((:map_version __map_version) 0)
    ((:map_available __map_available) nil)
    ((:stream_online __stream_online) nil)
    ((:replan_requested __replan_requested) nil)
    ((:last_error __last_error) "")
    ((:pose __pose) (instance geometry_msgs::Pose2D :init))
    ((:path_point_count __path_point_count) 0)
    )
   (send-super :init)
   (setq _header __header)
   (setq _task_id (string __task_id))
   (setq _state (string __state))
   (setq _progress (float __progress))
   (setq _map_version (round __map_version))
   (setq _map_available __map_available)
   (setq _stream_online __stream_online)
   (setq _replan_requested __replan_requested)
   (setq _last_error (string __last_error))
   (setq _pose __pose)
   (setq _path_point_count (round __path_point_count))
   self)
  (:header
   (&rest __header)
   (if (keywordp (car __header))
       (send* _header __header)
     (progn
       (if __header (setq _header (car __header)))
       _header)))
  (:task_id
   (&optional __task_id)
   (if __task_id (setq _task_id __task_id)) _task_id)
  (:state
   (&optional __state)
   (if __state (setq _state __state)) _state)
  (:progress
   (&optional __progress)
   (if __progress (setq _progress __progress)) _progress)
  (:map_version
   (&optional __map_version)
   (if __map_version (setq _map_version __map_version)) _map_version)
  (:map_available
   (&optional (__map_available :null))
   (if (not (eq __map_available :null)) (setq _map_available __map_available)) _map_available)
  (:stream_online
   (&optional (__stream_online :null))
   (if (not (eq __stream_online :null)) (setq _stream_online __stream_online)) _stream_online)
  (:replan_requested
   (&optional (__replan_requested :null))
   (if (not (eq __replan_requested :null)) (setq _replan_requested __replan_requested)) _replan_requested)
  (:last_error
   (&optional __last_error)
   (if __last_error (setq _last_error __last_error)) _last_error)
  (:pose
   (&rest __pose)
   (if (keywordp (car __pose))
       (send* _pose __pose)
     (progn
       (if __pose (setq _pose (car __pose)))
       _pose)))
  (:path_point_count
   (&optional __path_point_count)
   (if __path_point_count (setq _path_point_count __path_point_count)) _path_point_count)
  (:serialization-length
   ()
   (+
    ;; std_msgs/Header _header
    (send _header :serialization-length)
    ;; string _task_id
    4 (length _task_id)
    ;; string _state
    4 (length _state)
    ;; float32 _progress
    4
    ;; uint32 _map_version
    4
    ;; bool _map_available
    1
    ;; bool _stream_online
    1
    ;; bool _replan_requested
    1
    ;; string _last_error
    4 (length _last_error)
    ;; geometry_msgs/Pose2D _pose
    (send _pose :serialization-length)
    ;; uint32 _path_point_count
    4
    ))
  (:serialize
   (&optional strm)
   (let ((s (if strm strm
              (make-string-output-stream (send self :serialization-length)))))
     ;; std_msgs/Header _header
       (send _header :serialize s)
     ;; string _task_id
       (write-long (length _task_id) s) (princ _task_id s)
     ;; string _state
       (write-long (length _state) s) (princ _state s)
     ;; float32 _progress
       (sys::poke _progress (send s :buffer) (send s :count) :float) (incf (stream-count s) 4)
     ;; uint32 _map_version
       (write-long _map_version s)
     ;; bool _map_available
       (if _map_available (write-byte -1 s) (write-byte 0 s))
     ;; bool _stream_online
       (if _stream_online (write-byte -1 s) (write-byte 0 s))
     ;; bool _replan_requested
       (if _replan_requested (write-byte -1 s) (write-byte 0 s))
     ;; string _last_error
       (write-long (length _last_error) s) (princ _last_error s)
     ;; geometry_msgs/Pose2D _pose
       (send _pose :serialize s)
     ;; uint32 _path_point_count
       (write-long _path_point_count s)
     ;;
     (if (null strm) (get-output-stream-string s))))
  (:deserialize
   (buf &optional (ptr- 0))
   ;; std_msgs/Header _header
     (send _header :deserialize buf ptr-) (incf ptr- (send _header :serialization-length))
   ;; string _task_id
     (let (n) (setq n (sys::peek buf ptr- :integer)) (incf ptr- 4) (setq _task_id (subseq buf ptr- (+ ptr- n))) (incf ptr- n))
   ;; string _state
     (let (n) (setq n (sys::peek buf ptr- :integer)) (incf ptr- 4) (setq _state (subseq buf ptr- (+ ptr- n))) (incf ptr- n))
   ;; float32 _progress
     (setq _progress (sys::peek buf ptr- :float)) (incf ptr- 4)
   ;; uint32 _map_version
     (setq _map_version (sys::peek buf ptr- :integer)) (incf ptr- 4)
   ;; bool _map_available
     (setq _map_available (not (= 0 (sys::peek buf ptr- :char)))) (incf ptr- 1)
   ;; bool _stream_online
     (setq _stream_online (not (= 0 (sys::peek buf ptr- :char)))) (incf ptr- 1)
   ;; bool _replan_requested
     (setq _replan_requested (not (= 0 (sys::peek buf ptr- :char)))) (incf ptr- 1)
   ;; string _last_error
     (let (n) (setq n (sys::peek buf ptr- :integer)) (incf ptr- 4) (setq _last_error (subseq buf ptr- (+ ptr- n))) (incf ptr- n))
   ;; geometry_msgs/Pose2D _pose
     (send _pose :deserialize buf ptr-) (incf ptr- (send _pose :serialization-length))
   ;; uint32 _path_point_count
     (setq _path_point_count (sys::peek buf ptr- :integer)) (incf ptr- 4)
   ;;
   self)
  )

(setf (get grinder_scheduler::SchedulerStatus :md5sum-) "5f4e9266173ca1d3c3829a5e19868d37")
(setf (get grinder_scheduler::SchedulerStatus :datatype-) "grinder_scheduler/SchedulerStatus")
(setf (get grinder_scheduler::SchedulerStatus :definition-)
      "std_msgs/Header header
string task_id
string state
float32 progress
uint32 map_version
bool map_available
bool stream_online
bool replan_requested
string last_error
geometry_msgs/Pose2D pose
uint32 path_point_count

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
MSG: geometry_msgs/Pose2D
# Deprecated
# Please use the full 3D pose.

# In general our recommendation is to use a full 3D representation of everything and for 2D specific applications make the appropriate projections into the plane for their calculations but optimally will preserve the 3D information during processing.

# If we have parallel copies of 2D datatypes every UI and other pipeline will end up needing to have dual interfaces to plot everything. And you will end up with not being able to use 3D tools for 2D use cases even if they're completely valid, as you'd have to reimplement it with different inputs and outputs. It's not particularly hard to plot the 2D pose or compute the yaw error for the Pose message and there are already tools and libraries that can do this for you.


# This expresses a position and orientation on a 2D manifold.

float64 x
float64 y
float64 theta

")



(provide :grinder_scheduler/SchedulerStatus "5f4e9266173ca1d3c3829a5e19868d37")


