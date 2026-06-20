/**
 * @file server_work_data.h
 * @brief Defines the ServerWorkData structure and related types for managing server work data in the SLAMWARE ROS SDK.
 */

#pragma once

#include <atomic>
#include <ros/ros.h>
#include <string>

#include "server_map_holder.h"

#include <aurora_pubsdk_inc.h>
#include <geometry_msgs/PoseStamped.h>

namespace slamware_ros_sdk
{

    struct ServerWorkData
    {
    public:
        geometry_msgs::PoseStamped robotPose;

        std::atomic<bool> syncMapRequested;
        std::atomic<bool> hasMapYawAlignment;
        std::atomic<double> mapYawAlignmentYaw;
        std::atomic<double> mapYawAlignmentInitialYaw;
        std::atomic<double> mapYawAlignmentFrontYawDeg;
        ServerMapHolder exploreMapHolder;

        bool hasAugmentedPose;
        slamtec_aurora_sdk_pose_se3_t augmentedPose;
        uint64_t augmentedPoseTimestampNs;
        ros::Time augmentedPoseRosTime;
        slamtec_aurora_sdk_pose_augmentation_mode_t augmentedPoseMode;
        bool poseAugmentationStarted;
        bool poseAugmentationFailed;
        std::string poseAugmentationFailureReason;
        std::string selectedPoseSource;
        uint64_t selectedPoseTimestampNs;
        ros::Time selectedPoseRosTime;
        bool hasSelectedPose;
        ros::Time firstSelectedPoseRosTime;

        bool hasPoseCovariance;
        rp::standalone::aurora::PoseCovariance poseCovariance;
        slamtec_aurora_sdk_pose_covariance_readable_t poseCovarianceReadable;
        uint64_t poseCovarianceTimestampNs;
        ros::Time poseCovarianceRosTime;

        std::string latestSystemStatus;
        ros::Time latestSystemStatusRosTime;
        std::string latestRelocalizationStatus;
        ros::Time latestRelocalizationStatusRosTime;

    public:
        ServerWorkData();

    public:
        static inline bool sfIsDigitalSensorValueImpact(float fVal) { return fVal < FLT_EPSILON; }
    };

    typedef std::shared_ptr<ServerWorkData> ServerWorkData_Ptr;
    typedef std::shared_ptr<const ServerWorkData> ServerWorkData_ConstPtr;

}
