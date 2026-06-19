/*
 * @file server_work_data.cpp
 * @brief Implementation of the ServerWorkData class for the SLAMWARE ROS SDK.
 */

#include "server_work_data.h"

#include <cstring>

namespace slamware_ros_sdk
{

    ServerWorkData::ServerWorkData()
        : syncMapRequested(true),
          hasMapYawAlignment(false),
          mapYawAlignmentYaw(0.0),
          hasAugmentedPose(false),
          augmentedPoseTimestampNs(0),
          augmentedPoseMode(SLAMTEC_AURORA_SDK_POSE_AUGMENTATION_MODE_VISUAL_ONLY),
          poseAugmentationStarted(false),
          poseAugmentationFailed(false),
          selectedPoseTimestampNs(0),
          hasSelectedPose(false),
          hasPoseCovariance(false),
          poseCovarianceTimestampNs(0)
    {
        memset(&augmentedPose, 0, sizeof(augmentedPose));
        memset(&poseCovarianceReadable, 0, sizeof(poseCovarianceReadable));
        selectedPoseSource = "raw";
    }

}
