// Auto-generated. Do not edit!

// (in-package slamware_ros_sdk.srv)


"use strict";

const _serializer = _ros_msg_utils.Serialize;
const _arraySerializer = _serializer.Array;
const _deserializer = _ros_msg_utils.Deserialize;
const _arrayDeserializer = _deserializer.Array;
const _finder = _ros_msg_utils.Find;
const _getByteLength = _ros_msg_utils.getByteLength;

//-----------------------------------------------------------


//-----------------------------------------------------------

class SyncSetStcmRequest {
  constructor(initObj={}) {
    if (initObj === null) {
      // initObj === null is a special case for deserialization where we don't initialize fields
      this.mapfile = null;
    }
    else {
      if (initObj.hasOwnProperty('mapfile')) {
        this.mapfile = initObj.mapfile
      }
      else {
        this.mapfile = '';
      }
    }
  }

  static serialize(obj, buffer, bufferOffset) {
    // Serializes a message object of type SyncSetStcmRequest
    // Serialize message field [mapfile]
    bufferOffset = _serializer.string(obj.mapfile, buffer, bufferOffset);
    return bufferOffset;
  }

  static deserialize(buffer, bufferOffset=[0]) {
    //deserializes a message object of type SyncSetStcmRequest
    let len;
    let data = new SyncSetStcmRequest(null);
    // Deserialize message field [mapfile]
    data.mapfile = _deserializer.string(buffer, bufferOffset);
    return data;
  }

  static getMessageSize(object) {
    let length = 0;
    length += _getByteLength(object.mapfile);
    return length + 4;
  }

  static datatype() {
    // Returns string type for a service object
    return 'slamware_ros_sdk/SyncSetStcmRequest';
  }

  static md5sum() {
    //Returns md5sum for a message object
    return 'a1fb0700a7732a0f727e4b828cc211b4';
  }

  static messageDefinition() {
    // Returns full string definition for message
    return `
    #request
    string mapfile
    
    `;
  }

  static Resolve(msg) {
    // deep-construct a valid message object instance of whatever was passed in
    if (typeof msg !== 'object' || msg === null) {
      msg = {};
    }
    const resolved = new SyncSetStcmRequest(null);
    if (msg.mapfile !== undefined) {
      resolved.mapfile = msg.mapfile;
    }
    else {
      resolved.mapfile = ''
    }

    return resolved;
    }
};

class SyncSetStcmResponse {
  constructor(initObj={}) {
    if (initObj === null) {
      // initObj === null is a special case for deserialization where we don't initialize fields
      this.success = null;
      this.message = null;
    }
    else {
      if (initObj.hasOwnProperty('success')) {
        this.success = initObj.success
      }
      else {
        this.success = false;
      }
      if (initObj.hasOwnProperty('message')) {
        this.message = initObj.message
      }
      else {
        this.message = '';
      }
    }
  }

  static serialize(obj, buffer, bufferOffset) {
    // Serializes a message object of type SyncSetStcmResponse
    // Serialize message field [success]
    bufferOffset = _serializer.bool(obj.success, buffer, bufferOffset);
    // Serialize message field [message]
    bufferOffset = _serializer.string(obj.message, buffer, bufferOffset);
    return bufferOffset;
  }

  static deserialize(buffer, bufferOffset=[0]) {
    //deserializes a message object of type SyncSetStcmResponse
    let len;
    let data = new SyncSetStcmResponse(null);
    // Deserialize message field [success]
    data.success = _deserializer.bool(buffer, bufferOffset);
    // Deserialize message field [message]
    data.message = _deserializer.string(buffer, bufferOffset);
    return data;
  }

  static getMessageSize(object) {
    let length = 0;
    length += _getByteLength(object.message);
    return length + 5;
  }

  static datatype() {
    // Returns string type for a service object
    return 'slamware_ros_sdk/SyncSetStcmResponse';
  }

  static md5sum() {
    //Returns md5sum for a message object
    return '937c9679a518e3a18d831e57125ea522';
  }

  static messageDefinition() {
    // Returns full string definition for message
    return `
    
    #response
    bool success
    string message
    
    
    `;
  }

  static Resolve(msg) {
    // deep-construct a valid message object instance of whatever was passed in
    if (typeof msg !== 'object' || msg === null) {
      msg = {};
    }
    const resolved = new SyncSetStcmResponse(null);
    if (msg.success !== undefined) {
      resolved.success = msg.success;
    }
    else {
      resolved.success = false
    }

    if (msg.message !== undefined) {
      resolved.message = msg.message;
    }
    else {
      resolved.message = ''
    }

    return resolved;
    }
};

module.exports = {
  Request: SyncSetStcmRequest,
  Response: SyncSetStcmResponse,
  md5sum() { return '919cbda8c3832c78ab0496dedc3e5520'; },
  datatype() { return 'slamware_ros_sdk/SyncSetStcm'; }
};
