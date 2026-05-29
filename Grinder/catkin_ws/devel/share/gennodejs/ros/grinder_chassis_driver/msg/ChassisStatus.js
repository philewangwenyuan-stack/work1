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

class ChassisStatus {
  constructor(initObj={}) {
    if (initObj === null) {
      // initObj === null is a special case for deserialization where we don't initialize fields
      this.header = null;
      this.connected = null;
      this.enabled = null;
      this.work_mode = null;
      this.disc_speed_target = null;
      this.disc_speed_feedback = null;
      this.disc_enabled = null;
      this.disc_lift_state = null;
      this.light_enabled = null;
      this.consecutive_failures = null;
      this.last_error = null;
    }
    else {
      if (initObj.hasOwnProperty('header')) {
        this.header = initObj.header
      }
      else {
        this.header = new std_msgs.msg.Header();
      }
      if (initObj.hasOwnProperty('connected')) {
        this.connected = initObj.connected
      }
      else {
        this.connected = false;
      }
      if (initObj.hasOwnProperty('enabled')) {
        this.enabled = initObj.enabled
      }
      else {
        this.enabled = false;
      }
      if (initObj.hasOwnProperty('work_mode')) {
        this.work_mode = initObj.work_mode
      }
      else {
        this.work_mode = 0;
      }
      if (initObj.hasOwnProperty('disc_speed_target')) {
        this.disc_speed_target = initObj.disc_speed_target
      }
      else {
        this.disc_speed_target = 0;
      }
      if (initObj.hasOwnProperty('disc_speed_feedback')) {
        this.disc_speed_feedback = initObj.disc_speed_feedback
      }
      else {
        this.disc_speed_feedback = 0;
      }
      if (initObj.hasOwnProperty('disc_enabled')) {
        this.disc_enabled = initObj.disc_enabled
      }
      else {
        this.disc_enabled = false;
      }
      if (initObj.hasOwnProperty('disc_lift_state')) {
        this.disc_lift_state = initObj.disc_lift_state
      }
      else {
        this.disc_lift_state = 0;
      }
      if (initObj.hasOwnProperty('light_enabled')) {
        this.light_enabled = initObj.light_enabled
      }
      else {
        this.light_enabled = false;
      }
      if (initObj.hasOwnProperty('consecutive_failures')) {
        this.consecutive_failures = initObj.consecutive_failures
      }
      else {
        this.consecutive_failures = 0;
      }
      if (initObj.hasOwnProperty('last_error')) {
        this.last_error = initObj.last_error
      }
      else {
        this.last_error = '';
      }
    }
  }

  static serialize(obj, buffer, bufferOffset) {
    // Serializes a message object of type ChassisStatus
    // Serialize message field [header]
    bufferOffset = std_msgs.msg.Header.serialize(obj.header, buffer, bufferOffset);
    // Serialize message field [connected]
    bufferOffset = _serializer.bool(obj.connected, buffer, bufferOffset);
    // Serialize message field [enabled]
    bufferOffset = _serializer.bool(obj.enabled, buffer, bufferOffset);
    // Serialize message field [work_mode]
    bufferOffset = _serializer.uint16(obj.work_mode, buffer, bufferOffset);
    // Serialize message field [disc_speed_target]
    bufferOffset = _serializer.int16(obj.disc_speed_target, buffer, bufferOffset);
    // Serialize message field [disc_speed_feedback]
    bufferOffset = _serializer.int16(obj.disc_speed_feedback, buffer, bufferOffset);
    // Serialize message field [disc_enabled]
    bufferOffset = _serializer.bool(obj.disc_enabled, buffer, bufferOffset);
    // Serialize message field [disc_lift_state]
    bufferOffset = _serializer.uint16(obj.disc_lift_state, buffer, bufferOffset);
    // Serialize message field [light_enabled]
    bufferOffset = _serializer.bool(obj.light_enabled, buffer, bufferOffset);
    // Serialize message field [consecutive_failures]
    bufferOffset = _serializer.uint32(obj.consecutive_failures, buffer, bufferOffset);
    // Serialize message field [last_error]
    bufferOffset = _serializer.string(obj.last_error, buffer, bufferOffset);
    return bufferOffset;
  }

  static deserialize(buffer, bufferOffset=[0]) {
    //deserializes a message object of type ChassisStatus
    let len;
    let data = new ChassisStatus(null);
    // Deserialize message field [header]
    data.header = std_msgs.msg.Header.deserialize(buffer, bufferOffset);
    // Deserialize message field [connected]
    data.connected = _deserializer.bool(buffer, bufferOffset);
    // Deserialize message field [enabled]
    data.enabled = _deserializer.bool(buffer, bufferOffset);
    // Deserialize message field [work_mode]
    data.work_mode = _deserializer.uint16(buffer, bufferOffset);
    // Deserialize message field [disc_speed_target]
    data.disc_speed_target = _deserializer.int16(buffer, bufferOffset);
    // Deserialize message field [disc_speed_feedback]
    data.disc_speed_feedback = _deserializer.int16(buffer, bufferOffset);
    // Deserialize message field [disc_enabled]
    data.disc_enabled = _deserializer.bool(buffer, bufferOffset);
    // Deserialize message field [disc_lift_state]
    data.disc_lift_state = _deserializer.uint16(buffer, bufferOffset);
    // Deserialize message field [light_enabled]
    data.light_enabled = _deserializer.bool(buffer, bufferOffset);
    // Deserialize message field [consecutive_failures]
    data.consecutive_failures = _deserializer.uint32(buffer, bufferOffset);
    // Deserialize message field [last_error]
    data.last_error = _deserializer.string(buffer, bufferOffset);
    return data;
  }

  static getMessageSize(object) {
    let length = 0;
    length += std_msgs.msg.Header.getMessageSize(object.header);
    length += _getByteLength(object.last_error);
    return length + 20;
  }

  static datatype() {
    // Returns string type for a message object
    return 'grinder_chassis_driver/ChassisStatus';
  }

  static md5sum() {
    //Returns md5sum for a message object
    return '332527d3d7aab4589bcc1f2c43bb82d4';
  }

  static messageDefinition() {
    // Returns full string definition for message
    return `
    std_msgs/Header header
    bool connected
    bool enabled
    uint16 work_mode
    int16 disc_speed_target
    int16 disc_speed_feedback
    bool disc_enabled
    uint16 disc_lift_state
    bool light_enabled
    uint32 consecutive_failures
    string last_error
    
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
    const resolved = new ChassisStatus(null);
    if (msg.header !== undefined) {
      resolved.header = std_msgs.msg.Header.Resolve(msg.header)
    }
    else {
      resolved.header = new std_msgs.msg.Header()
    }

    if (msg.connected !== undefined) {
      resolved.connected = msg.connected;
    }
    else {
      resolved.connected = false
    }

    if (msg.enabled !== undefined) {
      resolved.enabled = msg.enabled;
    }
    else {
      resolved.enabled = false
    }

    if (msg.work_mode !== undefined) {
      resolved.work_mode = msg.work_mode;
    }
    else {
      resolved.work_mode = 0
    }

    if (msg.disc_speed_target !== undefined) {
      resolved.disc_speed_target = msg.disc_speed_target;
    }
    else {
      resolved.disc_speed_target = 0
    }

    if (msg.disc_speed_feedback !== undefined) {
      resolved.disc_speed_feedback = msg.disc_speed_feedback;
    }
    else {
      resolved.disc_speed_feedback = 0
    }

    if (msg.disc_enabled !== undefined) {
      resolved.disc_enabled = msg.disc_enabled;
    }
    else {
      resolved.disc_enabled = false
    }

    if (msg.disc_lift_state !== undefined) {
      resolved.disc_lift_state = msg.disc_lift_state;
    }
    else {
      resolved.disc_lift_state = 0
    }

    if (msg.light_enabled !== undefined) {
      resolved.light_enabled = msg.light_enabled;
    }
    else {
      resolved.light_enabled = false
    }

    if (msg.consecutive_failures !== undefined) {
      resolved.consecutive_failures = msg.consecutive_failures;
    }
    else {
      resolved.consecutive_failures = 0
    }

    if (msg.last_error !== undefined) {
      resolved.last_error = msg.last_error;
    }
    else {
      resolved.last_error = ''
    }

    return resolved;
    }
};

module.exports = ChassisStatus;
