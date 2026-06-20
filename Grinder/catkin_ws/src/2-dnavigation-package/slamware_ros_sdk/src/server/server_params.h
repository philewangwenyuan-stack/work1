/**
 * @file server_params.h
 * @brief This file defines the ServerParams structure and related constants for configuring the SLAMWARE ROS SDK server.
 */

#pragma once

#include <ros/ros.h>

namespace slamware_ros_sdk
{

    extern const float C_FLT_PI;
    extern const float C_FLT_2PI;

    struct ServerParams
    {
        std::string ip_address;
        int robot_port;
        int reconn_wait_ms;

        bool angle_compensate;
        bool ladar_data_clockwise;

        std::string robot_frame;
        std::string laser_frame;
        std::string map_frame;

        std::string imu_frame;
        std::string camera_left;
        std::string camera_right;

        float robot_pose_pub_period;
        float scan_pub_period;
        float map_update_period;
        float map_pub_period;
        float map_sync_once_get_max_wh;
        float map_update_near_robot_half_wh;

        float imu_raw_data_period;
        float system_status_pub_period;
        float stereo_image_pub_period;
        float point_cloud_pub_period;
        float robot_basic_state_pub_period;
        float odometry_pub_period;
        float enhanced_imaging_pub_period;
        float pose_quality_pub_period;

        float event_period;

        std::string scan_topic;
        std::string map_topic;
        std::string map_info_topic;
        std::string system_status_topic_name;
        std::string relocalization_status_topic_name;
        std::string left_image_raw_topic_name;
        std::string right_image_raw_topic_name;
        std::string point_cloud_topic_name;
        std::string stereo_keypoints_topic_name;
        std::string imu_raw_data_topic;
        std::string robot_pose_topic;
        std::string odom_topic;
        std::string pose_quality_topic_name;
        std::string odom_frame;
        std::string depth_image_raw_topic_name;
        std::string depth_image_colorized_topic_name;
        std::string semantic_segmentation_topic_name;

        bool pose_augmentation_enabled;
        int pose_augmentation_frequency_hz;
        std::string pose_augmentation_mode;
        bool pose_augmentation_smoothing_enabled;
        float pose_augmentation_smoothing_factor;
        bool pose_augmentation_fallback_to_raw;
        float pose_augmentation_timeout_sec;
        float pose_quality_covariance_timeout_sec;
        float pose_quality_warn_xy95_m;
        float pose_quality_fault_xy95_m;
        float pose_quality_warn_yaw_deg;
        float pose_quality_fault_yaw_deg;
     
        // 0528修改==========================================================================
        bool slam_pose_is_laser_frame;
        bool publish_laser_pose_tf;
        bool align_map_to_initial_yaw;
        std::string map_alignment_mode;
        double aligned_front_yaw_deg;
        std::string aligned_map_frame;
        std::string aligned_map_topic;
        std::string aligned_map_info_topic;
        double base_to_laser_x;
        double base_to_laser_y;
        double base_to_laser_z;
        double base_to_laser_roll;
        double base_to_laser_pitch;
        double base_to_laser_yaw;
        // ===========================================================================
        bool raw_ladar_data;
        bool no_preview_image;
        bool raw_image_on;

        ServerParams();

        void resetToDefault();
        void setBy(const ros::NodeHandle &nhRos);
    };

}
