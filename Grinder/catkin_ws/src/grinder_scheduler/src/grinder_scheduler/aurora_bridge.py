import os
import threading

import cv2

import rospy
from cv_bridge import CvBridge, CvBridgeError
from nav_msgs.msg import OccupancyGrid, Odometry
from sensor_msgs.msg import Image
from tf.transformations import euler_from_quaternion


class AuroraBridge:
    def __init__(
        self,
        map_topic,
        odom_topic,
        left_image_topic,
        right_image_topic,
        first_frame_save_dir="",
        save_first_frame_on_startup=False,
        use_depth_colorized_image=False,
        depth_image_colorized_topic="",
    ):
        self._lock = threading.Lock()
        self._bridge = CvBridge()
        self._map_msg = None
        self._pose = {"x": 0.0, "y": 0.0, "heading_deg": 0.0}
        self._initial_pose = None
        self._left_image = None
        self._right_image = None
        self._depth_image = None
        self._left_stamp = rospy.Time(0)
        self._right_stamp = rospy.Time(0)
        self._depth_stamp = rospy.Time(0)
        self._left_recv_stamp = rospy.Time(0)
        self._right_recv_stamp = rospy.Time(0)
        self._depth_recv_stamp = rospy.Time(0)
        default_dir = os.path.abspath(os.path.join(os.getcwd(), "temp"))
        self._first_frame_save_dir = first_frame_save_dir.strip() or default_dir
        self._save_first_frame_on_startup = bool(save_first_frame_on_startup)
        self._saved_left_frame = False
        self._saved_right_frame = False
        self._saved_depth_frame = False
        self._use_depth_colorized_image = bool(use_depth_colorized_image)

        rospy.Subscriber(map_topic, OccupancyGrid, self._map_callback, queue_size=1)
        rospy.Subscriber(odom_topic, Odometry, self._odom_callback, queue_size=10)
        if self._use_depth_colorized_image:
            rospy.Subscriber(
                depth_image_colorized_topic,
                Image,
                self._depth_image_callback,
                queue_size=1,
                buff_size=2 ** 24,
                tcp_nodelay=True,
            )
        else:
            rospy.Subscriber(
                left_image_topic,
                Image,
                self._left_image_callback,
                queue_size=1,
                buff_size=2 ** 24,
                tcp_nodelay=True,
            )
            rospy.Subscriber(
                right_image_topic,
                Image,
                self._right_image_callback,
                queue_size=1,
                buff_size=2 ** 24,
                tcp_nodelay=True,
            )

    def _map_callback(self, msg):
        with self._lock:
            self._map_msg = msg

    def _odom_callback(self, msg):
        orientation = msg.pose.pose.orientation
        _, _, yaw = euler_from_quaternion([orientation.x, orientation.y, orientation.z, orientation.w])
        pose = {
            "x": msg.pose.pose.position.x,
            "y": msg.pose.pose.position.y,
            "heading_deg": yaw * 180.0 / 3.141592653589793,
            "orientation": {
                "x": float(orientation.x),
                "y": float(orientation.y),
                "z": float(orientation.z),
                "w": float(orientation.w),
            },
        }
        with self._lock:
            self._pose = pose
            if self._initial_pose is None:
                self._initial_pose = dict(pose)

    def _left_image_callback(self, msg):
        try:
            image = self._bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except CvBridgeError as exc:
            rospy.logwarn_throttle(2.0, "Failed to convert left image: %s", exc)
            return
        with self._lock:
            self._left_image = image
            self._left_stamp = msg.header.stamp
            self._left_recv_stamp = rospy.Time.now()
            should_save = self._save_first_frame_on_startup and (not self._saved_left_frame)
            if should_save:
                self._saved_left_frame = True
        if should_save:
            self._save_first_frame("left", image, msg.header.stamp)

    def _right_image_callback(self, msg):
        try:
            image = self._bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except CvBridgeError as exc:
            rospy.logwarn_throttle(2.0, "Failed to convert right image: %s", exc)
            return
        with self._lock:
            self._right_image = image
            self._right_stamp = msg.header.stamp
            self._right_recv_stamp = rospy.Time.now()
            should_save = self._save_first_frame_on_startup and (not self._saved_right_frame)
            if should_save:
                self._saved_right_frame = True
        if should_save:
            self._save_first_frame("right", image, msg.header.stamp)

    def _save_first_frame(self, side, image, stamp):
        try:
            os.makedirs(self._first_frame_save_dir, exist_ok=True)
            stamp_ns = stamp.to_nsec() if stamp and stamp != rospy.Time(0) else 0
            filename = os.path.join(self._first_frame_save_dir, "aurora_first_{}_{}.jpg".format(side, stamp_ns))
            if cv2.imwrite(filename, image):
                rospy.loginfo("Saved first %s Aurora image to %s", side, filename)
            else:
                rospy.logwarn("Failed to save first %s Aurora image to %s", side, filename)
        except Exception as exc:
            rospy.logwarn("Failed to save first %s Aurora image: %s", side, exc)

    def _depth_image_callback(self, msg):
        try:
            image = self._bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except CvBridgeError as exc:
            rospy.logwarn_throttle(2.0, "Failed to convert depth_image_colorized: %s", exc)
            return
        with self._lock:
            self._depth_image = image
            self._depth_stamp = msg.header.stamp
            self._depth_recv_stamp = rospy.Time.now()
            should_save = self._save_first_frame_on_startup and (not self._saved_depth_frame)
            if should_save:
                self._saved_depth_frame = True
        if should_save:
            self._save_first_frame("depth_colorized", image, msg.header.stamp)

    def get_map(self):
        with self._lock:
            return self._map_msg

    def get_pose(self):
        with self._lock:
            return dict(self._pose)

    def get_initial_pose(self):
        with self._lock:
            return None if self._initial_pose is None else dict(self._initial_pose)

    def get_latest_frames(self):
        with self._lock:
            if self._use_depth_colorized_image:
                depth = None if self._depth_image is None else self._depth_image.copy()
                stamp = self._depth_recv_stamp if self._depth_recv_stamp != rospy.Time(0) else self._depth_stamp
                return depth, None, stamp, rospy.Time(0)
            left = None if self._left_image is None else self._left_image.copy()
            right = None if self._right_image is None else self._right_image.copy()
            left_stamp = self._left_recv_stamp if self._left_recv_stamp != rospy.Time(0) else self._left_stamp
            right_stamp = self._right_recv_stamp if self._right_recv_stamp != rospy.Time(0) else self._right_stamp
            return left, right, left_stamp, right_stamp
