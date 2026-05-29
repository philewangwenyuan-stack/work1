;; Auto-generated. Do not edit!


(when (boundp 'slamware_ros_sdk::RelocalizationStatus)
  (if (not (find-package "SLAMWARE_ROS_SDK"))
    (make-package "SLAMWARE_ROS_SDK"))
  (shadow 'RelocalizationStatus (find-package "SLAMWARE_ROS_SDK")))
(unless (find-package "SLAMWARE_ROS_SDK::RELOCALIZATIONSTATUS")
  (make-package "SLAMWARE_ROS_SDK::RELOCALIZATIONSTATUS"))

(in-package "ROS")
;;//! \htmlinclude RelocalizationStatus.msg.html


(defclass slamware_ros_sdk::RelocalizationStatus
  :super ros::object
  :slots (_timestamp_ns _status ))

(defmethod slamware_ros_sdk::RelocalizationStatus
  (:init
   (&key
    ((:timestamp_ns __timestamp_ns) 0)
    ((:status __status) "")
    )
   (send-super :init)
   (setq _timestamp_ns (round __timestamp_ns))
   (setq _status (string __status))
   self)
  (:timestamp_ns
   (&optional __timestamp_ns)
   (if __timestamp_ns (setq _timestamp_ns __timestamp_ns)) _timestamp_ns)
  (:status
   (&optional __status)
   (if __status (setq _status __status)) _status)
  (:serialization-length
   ()
   (+
    ;; uint64 _timestamp_ns
    8
    ;; string _status
    4 (length _status)
    ))
  (:serialize
   (&optional strm)
   (let ((s (if strm strm
              (make-string-output-stream (send self :serialization-length)))))
     ;; uint64 _timestamp_ns
#+(or :alpha :irix6 :x86_64)
       (progn (sys::poke _timestamp_ns (send s :buffer) (send s :count) :long) (incf (stream-count s) 8))
#-(or :alpha :irix6 :x86_64)
       (cond ((and (class _timestamp_ns) (= (length (_timestamp_ns . bv)) 2)) ;; bignum
              (write-long (ash (elt (_timestamp_ns . bv) 0) 0) s)
              (write-long (ash (elt (_timestamp_ns . bv) 1) -1) s))
             ((and (class _timestamp_ns) (= (length (_timestamp_ns . bv)) 1)) ;; big1
              (write-long (elt (_timestamp_ns . bv) 0) s)
              (write-long (if (>= _timestamp_ns 0) 0 #xffffffff) s))
             (t                                         ;; integer
              (write-long _timestamp_ns s)(write-long (if (>= _timestamp_ns 0) 0 #xffffffff) s)))
     ;; string _status
       (write-long (length _status) s) (princ _status s)
     ;;
     (if (null strm) (get-output-stream-string s))))
  (:deserialize
   (buf &optional (ptr- 0))
   ;; uint64 _timestamp_ns
     
#+(or :alpha :irix6 :x86_64)
      (setf _timestamp_ns (prog1 (sys::peek buf ptr- :long) (incf ptr- 8)))
#-(or :alpha :irix6 :x86_64)
      (setf _timestamp_ns (let ((b0 (prog1 (sys::peek buf ptr- :integer) (incf ptr- 4)))
                  (b1 (prog1 (sys::peek buf ptr- :integer) (incf ptr- 4))))
              (cond ((= b1 -1) b0)
                     ((and (= b1  0)
                           (<= lisp::most-negative-fixnum b0 lisp::most-positive-fixnum))
                      b0)
                    ((= b1  0) (make-instance bignum :size 1 :bv (integer-vector b0)))
                    (t (make-instance bignum :size 2 :bv (integer-vector b0 (ash b1 1)))))))
   ;; string _status
     (let (n) (setq n (sys::peek buf ptr- :integer)) (incf ptr- 4) (setq _status (subseq buf ptr- (+ ptr- n))) (incf ptr- n))
   ;;
   self)
  )

(setf (get slamware_ros_sdk::RelocalizationStatus :md5sum-) "ccc1e4824af73d0a8de6d07224862f42")
(setf (get slamware_ros_sdk::RelocalizationStatus :datatype-) "slamware_ros_sdk/RelocalizationStatus")
(setf (get slamware_ros_sdk::RelocalizationStatus :definition-)
      "
uint64 timestamp_ns
string status

")



(provide :slamware_ros_sdk/RelocalizationStatus "ccc1e4824af73d0a8de6d07224862f42")


