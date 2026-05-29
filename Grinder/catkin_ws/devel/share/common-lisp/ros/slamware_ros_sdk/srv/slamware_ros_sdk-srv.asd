
(cl:in-package :asdf)

(defsystem "slamware_ros_sdk-srv"
  :depends-on (:roslisp-msg-protocol :roslisp-utils )
  :components ((:file "_package")
    (:file "RelocalizationRequest" :depends-on ("_package_RelocalizationRequest"))
    (:file "_package_RelocalizationRequest" :depends-on ("_package"))
    (:file "SyncGetStcm" :depends-on ("_package_SyncGetStcm"))
    (:file "_package_SyncGetStcm" :depends-on ("_package"))
    (:file "SyncSetStcm" :depends-on ("_package_SyncSetStcm"))
    (:file "_package_SyncSetStcm" :depends-on ("_package"))
  ))