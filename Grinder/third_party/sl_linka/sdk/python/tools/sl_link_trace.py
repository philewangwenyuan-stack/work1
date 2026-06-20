#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import sys
import time


def add_sdk_path(sdk_dir):
    sdk_dir = os.path.abspath(sdk_dir)
    if sdk_dir not in sys.path:
        sys.path.insert(0, sdk_dir)


def enum_name(pb, enum_name, value):
    desc = pb.DESCRIPTOR.enum_types_by_name.get(enum_name)
    if desc is None:
        return str(value)
    item = desc.values_by_number.get(int(value))
    return item.name if item is not None else str(value)


def build_message_maps(pb):
    pairs = {
        "MSG_ID_SETTINGS_READ_REQUEST": "SettingsReadRequest",
        "MSG_ID_SETTINGS_READ_RESPONSE": "SettingsReadResponse",
        "MSG_ID_SETTINGS_WRITE_REQUEST": "SettingsWriteRequest",
        "MSG_ID_SETTINGS_WRITE_RESPONSE": "SettingsWriteResponse",
        "MSG_ID_DEVICE_STATUS_REPORT": "DeviceStatusReport",
        "MSG_ID_CAMERA_FRAME_REQUEST": "CameraFrameRequest",
        "MSG_ID_CAMERA_FRAME_CHUNK": "CameraFrameChunk",
        "MSG_ID_MAP_REQUEST": "MapRequest",
        "MSG_ID_MAP_CHUNK": "MapChunk",
        "MSG_ID_CONTROL_COMMAND": "ControlCommand",
        "MSG_ID_CONTROL_COMMAND_RESPONSE": "ControlCommandResponse",
        "MSG_ID_TASK_CONFIG": "TaskConfig",
        "MSG_ID_TASK_CONFIG_RESPONSE": "TaskConfigResponse",
        "MSG_ID_TASK_COMMAND": "TaskCommand",
        "MSG_ID_TASK_COMMAND_RESPONSE": "TaskCommandResponse",
        "MSG_ID_TASK_STATUS_REPORT": "TaskStatusReport",
        "MSG_ID_TASK_PATH_REQUEST": "TaskPathRequest",
        "MSG_ID_TASK_PATH_CHUNK": "TaskPathChunk",
        "MSG_ID_MAP_PREVIEW_REQUEST": "MapPreviewRequest",
        "MSG_ID_MAP_PREVIEW_RESPONSE": "MapPreviewResponse",
        "MSG_ID_MAP_EDIT_COMMAND": "MapEditCommand",
        "MSG_ID_MAP_EDIT_RESPONSE": "MapEditResponse",
        "MSG_ID_MAP_EDIT_STATUS_REPORT": "MapEditStatusReport",
        "MSG_ID_VIDEO_STREAM_INFO_REQUEST": "VideoStreamInfoRequest",
        "MSG_ID_VIDEO_STREAM_INFO_RESPONSE": "VideoStreamInfoResponse",
        "MSG_ID_PATH_PLAN_REQUEST": "PathPlanRequest",
        "MSG_ID_PATH_PLAN_RESPONSE": "PathPlanResponse",
        "MSG_ID_MAP_SYNC_REQUEST": "MapSyncRequest",
        "MSG_ID_MAP_SYNC_RESPONSE": "MapSyncResponse",
        "MSG_ID_MAP_MODE_REQUEST": "MapModeRequest",
        "MSG_ID_MAP_MODE_RESPONSE": "MapModeResponse",
        "MSG_ID_MAP_CATALOG_REQUEST": "MapCatalogRequest",
        "MSG_ID_MAP_CATALOG_RESPONSE": "MapCatalogResponse",
        "MSG_ID_MAP_DELETE_REQUEST": "MapDeleteRequest",
        "MSG_ID_MAP_DELETE_RESPONSE": "MapDeleteResponse",
        "MSG_ID_MAP_SAVE_REQUEST": "MapSaveRequest",
        "MSG_ID_MAP_SAVE_RESPONSE": "MapSaveResponse",
        "MSG_ID_MAP_METRICS_REQUEST": "MapMetricsRequest",
        "MSG_ID_MAP_METRICS_RESPONSE": "MapMetricsResponse",
        "MSG_ID_TASK_RESULT_REQUEST": "TaskResultRequest",
        "MSG_ID_TASK_RESULT_RESPONSE": "TaskResultResponse",
        "MSG_ID_LIVE_MAP_CACHE_CLEAR_REQUEST": "LiveMapCacheClearRequest",
        "MSG_ID_LIVE_MAP_CACHE_CLEAR_RESPONSE": "LiveMapCacheClearResponse",
    }
    msg_names = {}
    msg_types = {}
    for name in dir(pb):
        if name.startswith("MSG_ID_"):
            value = getattr(pb, name)
            msg_names[value] = name
            cls_name = pairs.get(name)
            if cls_name and hasattr(pb, cls_name):
                msg_types[value] = getattr(pb, cls_name)
    return msg_names, msg_types


def short_proto_text(message):
    try:
        from google.protobuf.json_format import MessageToDict
    except Exception:
        return str(message).strip().replace("\n", " ")

    value = MessageToDict(
        message,
        preserving_proto_field_name=True,
        use_integers_for_enums=False,
    )

    def compact(obj):
        if isinstance(obj, dict):
            out = {}
            for key, val in obj.items():
                if key in ("image_data", "data", "thumbnail_image_b64", "preview_image"):
                    if isinstance(val, str):
                        out[key] = "<%d chars>" % len(val)
                    else:
                        out[key] = "<bytes>"
                else:
                    out[key] = compact(val)
            return out
        if isinstance(obj, list):
            if len(obj) > 6:
                return [compact(v) for v in obj[:6]] + ["... %d more" % (len(obj) - 6)]
            return [compact(v) for v in obj]
        return obj

    return repr(compact(value))


class TracePrinter:
    def __init__(self, pb, parser_cls, only, show_all):
        self.pb = pb
        self.parsers = {}
        self.msg_names, self.msg_types = build_message_maps(pb)
        self.parser_cls = parser_cls
        self.only = [item.upper() for item in only]
        self.show_all = show_all

    def parse_stream(self, stream_key, payload):
        parser = self.parsers.get(stream_key)
        if parser is None:
            parser = self.parser_cls()
            self.parsers[stream_key] = parser
        return parser.parse(payload)

    def should_print(self, name):
        if self.show_all:
            return True
        if name in ("MSG_ID_DEVICE_STATUS_REPORT", "MSG_ID_TASK_STATUS_REPORT"):
            return False
        if not self.only:
            return True
        return any(token in name for token in self.only)

    def print_frame(self, frame, src=None, dst=None):
        name = self.msg_names.get(int(frame.msg_id), "0x%04X" % int(frame.msg_id))
        if not self.should_print(name):
            return
        direction = "APP->LOWER" if frame.src_id == self.pb.DEVICE_APP else "LOWER->APP"
        if src and dst:
            direction = "%s %s:%s -> %s:%s" % (direction, src[0], src[1], dst[0], dst[1])
        comp = enum_name(self.pb, "ComponentId", frame.comp_id)
        line = "%s %-34s seq=%d ack=%d comp=%s payload=%d" % (
            time.strftime("%H:%M:%S"),
            name,
            int(frame.seq),
            int(frame.ack_seq),
            comp,
            len(frame.payload or b""),
        )
        print(line, flush=True)
        cls = self.msg_types.get(int(frame.msg_id))
        if cls is not None and frame.payload:
            try:
                msg = cls()
                msg.ParseFromString(frame.payload)
                text = short_proto_text(msg)
                if text:
                    print("  %s" % text, flush=True)
            except Exception as exc:
                print("  decode_failed=%s" % exc, flush=True)


def sniff_live(args, printer):
    try:
        from scapy.config import conf
        from scapy.layers.inet import IP, TCP
        from scapy.packet import Raw
        from scapy.sendrecv import sniff
    except Exception as exc:
        raise SystemExit("scapy missing. install: python3 -m pip install scapy. error=%s" % exc)

    iface = args.iface
    if iface == "any":
        iface = [
            item.name
            for item in conf.ifaces.values()
            if item.name not in ("lo", "Loopback", "loopback")
        ]
        if not iface:
            iface = None
        else:
            print("sniff interfaces: %s" % ", ".join(iface), flush=True)

    def on_packet(pkt):
        if TCP not in pkt or Raw not in pkt:
            return
        tcp = pkt[TCP]
        if int(tcp.sport) != args.port and int(tcp.dport) != args.port:
            return
        ip = pkt[IP] if IP in pkt else None
        src = (ip.src if ip else "?", int(tcp.sport))
        dst = (ip.dst if ip else "?", int(tcp.dport))
        key = (src, dst)
        for frame in printer.parse_stream(key, bytes(pkt[Raw].load)):
            printer.print_frame(frame, src=src, dst=dst)

    sniff(iface=iface, filter="tcp port %d" % args.port, prn=on_packet, store=False)


def read_pcap(args, printer):
    try:
        from scapy.layers.inet import IP, TCP
        from scapy.packet import Raw
        from scapy.utils import rdpcap
    except Exception as exc:
        raise SystemExit("scapy missing. install: python3 -m pip install scapy. error=%s" % exc)

    for pkt in rdpcap(args.pcap):
        if TCP not in pkt or Raw not in pkt:
            continue
        tcp = pkt[TCP]
        if int(tcp.sport) != args.port and int(tcp.dport) != args.port:
            continue
        ip = pkt[IP] if IP in pkt else None
        src = (ip.src if ip else "?", int(tcp.sport))
        dst = (ip.dst if ip else "?", int(tcp.dport))
        key = (src, dst)
        for frame in printer.parse_stream(key, bytes(pkt[Raw].load)):
            printer.print_frame(frame, src=src, dst=dst)


def main():
    parser = argparse.ArgumentParser(description="SL-LinkA realtime/pcap trace decoder")
    parser.add_argument("--sdk", required=True, help="Directory containing sl_link/ package")
    parser.add_argument("--iface", default="any", help="Live sniff interface")
    parser.add_argument("--pcap", help="Decode tcpdump pcap file")
    parser.add_argument("--port", type=int, default=8002, help="SL-LinkA TCP port")
    parser.add_argument("--only", action="append", default=[], help="Filter by message-name substring")
    parser.add_argument("--all", action="store_true", help="Show heartbeat/status reports too")
    args = parser.parse_args()

    add_sdk_path(args.sdk)
    from sl_link.frame import SlFrameParser
    from sl_link.message_gen import sl_link_pb2 as pb

    printer = TracePrinter(pb, SlFrameParser, args.only, args.all)
    if args.pcap:
        read_pcap(args, printer)
    else:
        sniff_live(args, printer)


if __name__ == "__main__":
    main()
