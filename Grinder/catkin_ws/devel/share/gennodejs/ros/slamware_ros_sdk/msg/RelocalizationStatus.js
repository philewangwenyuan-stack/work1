// Auto-generated. Do not edit!

// (in-package slamware_ros_sdk.msg)


"use strict";

const _serializer = _ros_msg_utils.Serialize;
const _arraySerializer = _serializer.Array;
const _deserializer = _ros_msg_utils.Deserialize;
const _arrayDeserializer = _deserializer.Array;
const _finder = _ros_msg_utils.Find;
const _getByteLength = _ros_msg_utils.getByteLength;

//-----------------------------------------------------------

class RelocalizationStatus {
  constructor(initObj={}) {
    if (initObj === null) {
      // initObj === null is a special case for deserialization where we don't initialize fields
      this.timestamp_ns = null;
      this.status = null;
    }
    else {
      if (initObj.hasOwnProperty('timestamp_ns')) {
        this.timestamp_ns = initObj.timestamp_ns
      }
      else {
        this.timestamp_ns = 0;
      }
      if (initObj.hasOwnProperty('status')) {
        this.status = initObj.status
      }
      else {
        this.status = '';
      }
    }
  }

  static serialize(obj, buffer, bufferOffset) {
    // Serializes a message object of type RelocalizationStatus
    // Serialize message field [timestamp_ns]
    bufferOffset = _serializer.uint64(obj.timestamp_ns, buffer, bufferOffset);
    // Serialize message field [status]
    bufferOffset = _serializer.string(obj.status, buffer, bufferOffset);
    return bufferOffset;
  }

  static deserialize(buffer, bufferOffset=[0]) {
    //deserializes a message object of type RelocalizationStatus
    let len;
    let data = new RelocalizationStatus(null);
    // Deserialize message field [timestamp_ns]
    data.timestamp_ns = _deserializer.uint64(buffer, bufferOffset);
    // Deserialize message field [status]
    data.status = _deserializer.string(buffer, bufferOffset);
    return data;
  }

  static getMessageSize(object) {
    let length = 0;
    length += _getByteLength(object.status);
    return length + 12;
  }

  static datatype() {
    // Returns string type for a message object
    return 'slamware_ros_sdk/RelocalizationStatus';
  }

  static md5sum() {
    //Returns md5sum for a message object
    return 'ccc1e4824af73d0a8de6d07224862f42';
  }

  static messageDefinition() {
    // Returns full string definition for message
    return `
    
    uint64 timestamp_ns
    string status
    
    `;
  }

  static Resolve(msg) {
    // deep-construct a valid message object instance of whatever was passed in
    if (typeof msg !== 'object' || msg === null) {
      msg = {};
    }
    const resolved = new RelocalizationStatus(null);
    if (msg.timestamp_ns !== undefined) {
      resolved.timestamp_ns = msg.timestamp_ns;
    }
    else {
      resolved.timestamp_ns = 0
    }

    if (msg.status !== undefined) {
      resolved.status = msg.status;
    }
    else {
      resolved.status = ''
    }

    return resolved;
    }
};

module.exports = RelocalizationStatus;
