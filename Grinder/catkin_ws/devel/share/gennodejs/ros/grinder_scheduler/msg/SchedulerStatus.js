// Auto-generated. Do not edit!

// (in-package grinder_scheduler.msg)


"use strict";

const _serializer = _ros_msg_utils.Serialize;
const _arraySerializer = _serializer.Array;
const _deserializer = _ros_msg_utils.Deserialize;
const _arrayDeserializer = _deserializer.Array;
const _finder = _ros_msg_utils.Find;
const _getByteLength = _ros_msg_utils.getByteLength;
let std_msgs = _finder('std_msgs');
let geometry_msgs = _finder('geometry_msgs');

//-----------------------------------------------------------

class SchedulerStatus {
  constructor(initObj={}) {
    if (initObj === null) {
      // initObj === null is a special case for deserialization where we don't initialize fields
      this.header = null;
      this.task_id = null;
      this.state = null;
      this.progress = null;
      this.map_version = null;
      this.map_available = null;
      this.stream_online = null;
      this.replan_requested = null;
      this.last_error = null;
      this.pose = null;
      this.path_point_count = null;
    }
    else {
      if (initObj.hasOwnProperty('header')) {
        this.header = initObj.header
      }
      else {
        this.header = new std_msgs.msg.Header();
      }
      if (initObj.hasOwnProperty('task_id')) {
        this.task_id = initObj.task_id
      }
      else {
        this.task_id = '';
      }
      if (initObj.hasOwnProperty('state')) {
        this.state = initObj.state
      }
      else {
        this.state = '';
      }
      if (initObj.hasOwnProperty('progress')) {
        this.progress = initObj.progress
      }
      else {
        this.progress = 0.0;
      }
      if (initObj.hasOwnProperty('map_version')) {
        this.map_version = initObj.map_version
      }
      else {
        this.map_version = 0;
      }
      if (initObj.hasOwnProperty('map_available')) {
        this.map_available = initObj.map_available
      }
      else {
        this.map_available = false;
      }
      if (initObj.hasOwnProperty('stream_online')) {
        this.stream_online = initObj.stream_online
      }
      else {
        this.stream_online = false;
      }
      if (initObj.hasOwnProperty('replan_requested')) {
        this.replan_requested = initObj.replan_requested
      }
      else {
        this.replan_requested = false;
      }
      if (initObj.hasOwnProperty('last_error')) {
        this.last_error = initObj.last_error
      }
      else {
        this.last_error = '';
      }
      if (initObj.hasOwnProperty('pose')) {
        this.pose = initObj.pose
      }
      else {
        this.pose = new geometry_msgs.msg.Pose2D();
      }
      if (initObj.hasOwnProperty('path_point_count')) {
        this.path_point_count = initObj.path_point_count
      }
      else {
        this.path_point_count = 0;
      }
    }
  }

  static serialize(obj, buffer, bufferOffset) {
    // Serializes a message object of type SchedulerStatus
    // Serialize message field [header]
    bufferOffset = std_msgs.msg.Header.serialize(obj.header, buffer, bufferOffset);
    // Serialize message field [task_id]
    bufferOffset = _serializer.string(obj.task_id, buffer, bufferOffset);
    // Serialize message field [state]
    bufferOffset = _serializer.string(obj.state, buffer, bufferOffset);
    // Serialize message field [progress]
    bufferOffset = _serializer.float32(obj.progress, buffer, bufferOffset);
    // Serialize message field [map_version]
    bufferOffset = _serializer.uint32(obj.map_version, buffer, bufferOffset);
    // Serialize message field [map_available]
    bufferOffset = _serializer.bool(obj.map_available, buffer, bufferOffset);
    // Serialize message field [stream_online]
    bufferOffset = _serializer.bool(obj.stream_online, buffer, bufferOffset);
    // Serialize message field [replan_requested]
    bufferOffset = _serializer.bool(obj.replan_requested, buffer, bufferOffset);
    // Serialize message field [last_error]
    bufferOffset = _serializer.string(obj.last_error, buffer, bufferOffset);
    // Serialize message field [pose]
    bufferOffset = geometry_msgs.msg.Pose2D.serialize(obj.pose, buffer, bufferOffset);
    // Serialize message field [path_point_count]
    bufferOffset = _serializer.uint32(obj.path_point_count, buffer, bufferOffset);
    return bufferOffset;
  }

  static deserialize(buffer, bufferOffset=[0]) {
    //deserializes a message object of type SchedulerStatus
    let len;
    let data = new SchedulerStatus(null);
    // Deserialize message field [header]
    data.header = std_msgs.msg.Header.deserialize(buffer, bufferOffset);
    // Deserialize message field [task_id]
    data.task_id = _deserializer.string(buffer, bufferOffset);
    // Deserialize message field [state]
    data.state = _deserializer.string(buffer, bufferOffset);
    // Deserialize message field [progress]
    data.progress = _deserializer.float32(buffer, bufferOffset);
    // Deserialize message field [map_version]
    data.map_version = _deserializer.uint32(buffer, bufferOffset);
    // Deserialize message field [map_available]
    data.map_available = _deserializer.bool(buffer, bufferOffset);
    // Deserialize message field [stream_online]
    data.stream_online = _deserializer.bool(buffer, bufferOffset);
    // Deserialize message field [replan_requested]
    data.replan_requested = _deserializer.bool(buffer, bufferOffset);
    // Deserialize message field [last_error]
    data.last_error = _deserializer.string(buffer, bufferOffset);
    // Deserialize message field [pose]
    data.pose = geometry_msgs.msg.Pose2D.deserialize(buffer, bufferOffset);
    // Deserialize message field [path_point_count]
    data.path_point_count = _deserializer.uint32(buffer, bufferOffset);
    return data;
  }

  static getMessageSize(object) {
    let length = 0;
    length += std_msgs.msg.Header.getMessageSize(object.header);
    length += _getByteLength(object.task_id);
    length += _getByteLength(object.state);
    length += _getByteLength(object.last_error);
    return length + 51;
  }

  static datatype() {
    // Returns string type for a message object
    return 'grinder_scheduler/SchedulerStatus';
  }

  static md5sum() {
    //Returns md5sum for a message object
    return '5f4e9266173ca1d3c3829a5e19868d37';
  }

  static messageDefinition() {
    // Returns full string definition for message
    return `
    std_msgs/Header header
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
    
    `;
  }

  static Resolve(msg) {
    // deep-construct a valid message object instance of whatever was passed in
    if (typeof msg !== 'object' || msg === null) {
      msg = {};
    }
    const resolved = new SchedulerStatus(null);
    if (msg.header !== undefined) {
      resolved.header = std_msgs.msg.Header.Resolve(msg.header)
    }
    else {
      resolved.header = new std_msgs.msg.Header()
    }

    if (msg.task_id !== undefined) {
      resolved.task_id = msg.task_id;
    }
    else {
      resolved.task_id = ''
    }

    if (msg.state !== undefined) {
      resolved.state = msg.state;
    }
    else {
      resolved.state = ''
    }

    if (msg.progress !== undefined) {
      resolved.progress = msg.progress;
    }
    else {
      resolved.progress = 0.0
    }

    if (msg.map_version !== undefined) {
      resolved.map_version = msg.map_version;
    }
    else {
      resolved.map_version = 0
    }

    if (msg.map_available !== undefined) {
      resolved.map_available = msg.map_available;
    }
    else {
      resolved.map_available = false
    }

    if (msg.stream_online !== undefined) {
      resolved.stream_online = msg.stream_online;
    }
    else {
      resolved.stream_online = false
    }

    if (msg.replan_requested !== undefined) {
      resolved.replan_requested = msg.replan_requested;
    }
    else {
      resolved.replan_requested = false
    }

    if (msg.last_error !== undefined) {
      resolved.last_error = msg.last_error;
    }
    else {
      resolved.last_error = ''
    }

    if (msg.pose !== undefined) {
      resolved.pose = geometry_msgs.msg.Pose2D.Resolve(msg.pose)
    }
    else {
      resolved.pose = new geometry_msgs.msg.Pose2D()
    }

    if (msg.path_point_count !== undefined) {
      resolved.path_point_count = msg.path_point_count;
    }
    else {
      resolved.path_point_count = 0
    }

    return resolved;
    }
};

module.exports = SchedulerStatus;
