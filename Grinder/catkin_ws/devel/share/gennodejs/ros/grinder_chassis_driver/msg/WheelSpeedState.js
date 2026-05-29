// Auto-generated. Do not edit!

// (in-package grinder_chassis_driver.msg)


"use strict";

const _serializer = _ros_msg_utils.Serialize;
const _arraySerializer = _serializer.Array;
const _deserializer = _ros_msg_utils.Deserialize;
const _arrayDeserializer = _deserializer.Array;
const _finder = _ros_msg_utils.Find;
const _getByteLength = _ros_msg_utils.getByteLength;
let std_msgs = _finder('std_msgs');

//-----------------------------------------------------------

class WheelSpeedState {
  constructor(initObj={}) {
    if (initObj === null) {
      // initObj === null is a special case for deserialization where we don't initialize fields
      this.header = null;
      this.target_left_wheel_speed = null;
      this.target_right_wheel_speed = null;
      this.feedback_left_wheel_speed = null;
      this.feedback_right_wheel_speed = null;
      this.feedback_valid = null;
    }
    else {
      if (initObj.hasOwnProperty('header')) {
        this.header = initObj.header
      }
      else {
        this.header = new std_msgs.msg.Header();
      }
      if (initObj.hasOwnProperty('target_left_wheel_speed')) {
        this.target_left_wheel_speed = initObj.target_left_wheel_speed
      }
      else {
        this.target_left_wheel_speed = 0;
      }
      if (initObj.hasOwnProperty('target_right_wheel_speed')) {
        this.target_right_wheel_speed = initObj.target_right_wheel_speed
      }
      else {
        this.target_right_wheel_speed = 0;
      }
      if (initObj.hasOwnProperty('feedback_left_wheel_speed')) {
        this.feedback_left_wheel_speed = initObj.feedback_left_wheel_speed
      }
      else {
        this.feedback_left_wheel_speed = 0;
      }
      if (initObj.hasOwnProperty('feedback_right_wheel_speed')) {
        this.feedback_right_wheel_speed = initObj.feedback_right_wheel_speed
      }
      else {
        this.feedback_right_wheel_speed = 0;
      }
      if (initObj.hasOwnProperty('feedback_valid')) {
        this.feedback_valid = initObj.feedback_valid
      }
      else {
        this.feedback_valid = false;
      }
    }
  }

  static serialize(obj, buffer, bufferOffset) {
    // Serializes a message object of type WheelSpeedState
    // Serialize message field [header]
    bufferOffset = std_msgs.msg.Header.serialize(obj.header, buffer, bufferOffset);
    // Serialize message field [target_left_wheel_speed]
    bufferOffset = _serializer.int16(obj.target_left_wheel_speed, buffer, bufferOffset);
    // Serialize message field [target_right_wheel_speed]
    bufferOffset = _serializer.int16(obj.target_right_wheel_speed, buffer, bufferOffset);
    // Serialize message field [feedback_left_wheel_speed]
    bufferOffset = _serializer.int16(obj.feedback_left_wheel_speed, buffer, bufferOffset);
    // Serialize message field [feedback_right_wheel_speed]
    bufferOffset = _serializer.int16(obj.feedback_right_wheel_speed, buffer, bufferOffset);
    // Serialize message field [feedback_valid]
    bufferOffset = _serializer.bool(obj.feedback_valid, buffer, bufferOffset);
    return bufferOffset;
  }

  static deserialize(buffer, bufferOffset=[0]) {
    //deserializes a message object of type WheelSpeedState
    let len;
    let data = new WheelSpeedState(null);
    // Deserialize message field [header]
    data.header = std_msgs.msg.Header.deserialize(buffer, bufferOffset);
    // Deserialize message field [target_left_wheel_speed]
    data.target_left_wheel_speed = _deserializer.int16(buffer, bufferOffset);
    // Deserialize message field [target_right_wheel_speed]
    data.target_right_wheel_speed = _deserializer.int16(buffer, bufferOffset);
    // Deserialize message field [feedback_left_wheel_speed]
    data.feedback_left_wheel_speed = _deserializer.int16(buffer, bufferOffset);
    // Deserialize message field [feedback_right_wheel_speed]
    data.feedback_right_wheel_speed = _deserializer.int16(buffer, bufferOffset);
    // Deserialize message field [feedback_valid]
    data.feedback_valid = _deserializer.bool(buffer, bufferOffset);
    return data;
  }

  static getMessageSize(object) {
    let length = 0;
    length += std_msgs.msg.Header.getMessageSize(object.header);
    return length + 9;
  }

  static datatype() {
    // Returns string type for a message object
    return 'grinder_chassis_driver/WheelSpeedState';
  }

  static md5sum() {
    //Returns md5sum for a message object
    return 'f50663abf771ecfd2d1486cfc892cbc3';
  }

  static messageDefinition() {
    // Returns full string definition for message
    return `
    std_msgs/Header header
    int16 target_left_wheel_speed
    int16 target_right_wheel_speed
    int16 feedback_left_wheel_speed
    int16 feedback_right_wheel_speed
    bool feedback_valid
    
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
    
    `;
  }

  static Resolve(msg) {
    // deep-construct a valid message object instance of whatever was passed in
    if (typeof msg !== 'object' || msg === null) {
      msg = {};
    }
    const resolved = new WheelSpeedState(null);
    if (msg.header !== undefined) {
      resolved.header = std_msgs.msg.Header.Resolve(msg.header)
    }
    else {
      resolved.header = new std_msgs.msg.Header()
    }

    if (msg.target_left_wheel_speed !== undefined) {
      resolved.target_left_wheel_speed = msg.target_left_wheel_speed;
    }
    else {
      resolved.target_left_wheel_speed = 0
    }

    if (msg.target_right_wheel_speed !== undefined) {
      resolved.target_right_wheel_speed = msg.target_right_wheel_speed;
    }
    else {
      resolved.target_right_wheel_speed = 0
    }

    if (msg.feedback_left_wheel_speed !== undefined) {
      resolved.feedback_left_wheel_speed = msg.feedback_left_wheel_speed;
    }
    else {
      resolved.feedback_left_wheel_speed = 0
    }

    if (msg.feedback_right_wheel_speed !== undefined) {
      resolved.feedback_right_wheel_speed = msg.feedback_right_wheel_speed;
    }
    else {
      resolved.feedback_right_wheel_speed = 0
    }

    if (msg.feedback_valid !== undefined) {
      resolved.feedback_valid = msg.feedback_valid;
    }
    else {
      resolved.feedback_valid = false
    }

    return resolved;
    }
};

module.exports = WheelSpeedState;
