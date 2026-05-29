import json
import socket
import socketserver
import threading
import time

from grinder_scheduler.sl_link_loader import ensure_sl_linka_sdk_on_path
try:
    import rospy  # type: ignore
except Exception:
    rospy = None


class SlLinkAServer:
    def __init__(self, sdk_dir, host, port, callback_handler):
        ensure_sl_linka_sdk_on_path(sdk_dir)
        from sl_link.frame import SL_PROTOCOL_VERSION, SlFrame, SlFrameParser
        from sl_link.message_gen import sl_link_pb2 as pb

        self.SL_PROTOCOL_VERSION = SL_PROTOCOL_VERSION
        self.SlFrame = SlFrame
        self.SlFrameParser = SlFrameParser
        self.pb = pb
        self.host = host
        self.port = port
        self._handler = callback_handler
        self._server = None
        self._thread = None
        self._seq = 0

    def start(self):
        outer = self

        class RequestHandler(socketserver.BaseRequestHandler):
            def setup(self):
                self.parser = outer.SlFrameParser()
                self.running = True
                self.status_thread = threading.Thread(target=self._periodic_reports, daemon=True)
                self.status_thread.start()

            def _periodic_reports(self):
                while self.running:
                    try:
                        self._send_payload(*outer._handler.build_device_status_report())
                        self._send_payload(*outer._handler.build_task_status_report())
                    except Exception:
                        pass
                    time.sleep(1.0)

            def handle(self):
                while self.running:
                    try:
                        data = self.request.recv(4096)
                    except socket.timeout:
                        # Keep the connection alive on idle timeout.
                        continue
                    except OSError as exc:
                        if rospy is not None:
                            rospy.logwarn("SL-LinkA socket recv failed: %s", exc)
                        break

                    if not data:
                        break
                    for frame in self.parser.parse(data):
                        if frame.dst_id not in (outer.pb.DEVICE_LOWER, outer.pb.DEVICE_BROADCAST):
                            continue
                        try:
                            outer._dispatch_frame(self, frame)
                        except Exception as exc:
                            if rospy is not None:
                                rospy.logerr(
                                    "SL-LinkA dispatch failed: msg_id=0x%04X seq=%d err=%s",
                                    int(frame.msg_id),
                                    int(frame.seq),
                                    exc,
                                )

            def finish(self):
                self.running = False

            def _send_payload(self, payload, msg_id, comp_id=None, ack_seq=0):
                if payload is None or msg_id is None:
                    return
                frame = outer.SlFrame(
                    version=outer.SL_PROTOCOL_VERSION,
                    flags=0,
                    seq=outer._next_seq(),
                    ack_seq=ack_seq,
                    src_id=outer.pb.DEVICE_LOWER,
                    dst_id=outer.pb.DEVICE_APP,
                    comp_id=comp_id if comp_id is not None else outer.pb.COMP_SYSTEM,
                    msg_id=msg_id,
                    payload=payload,
                )
                self.request.sendall(frame.pack())

        class ThreadedServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
            allow_reuse_address = True

        self._server = ThreadedServer((self.host, self.port), RequestHandler)
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()

    def stop(self):
        if self._server is not None:
            self._server.shutdown()
            self._server.server_close()
            self._server = None

    def _next_seq(self):
        value = self._seq
        self._seq = (self._seq + 1) & 0xFFFF
        return value

    def _dispatch_frame(self, request_handler, frame):
        pb = self.pb
        if frame.msg_id == pb.MSG_ID_SETTINGS_READ_REQUEST:
            payload, msg_id, comp_id = self._handler.handle_settings_read_request(frame.payload)
            request_handler._send_payload(payload, msg_id, comp_id=comp_id, ack_seq=frame.seq)
            return
        if frame.msg_id == pb.MSG_ID_SETTINGS_WRITE_REQUEST:
            payload, msg_id, comp_id = self._handler.handle_settings_write_request(frame.payload)
            request_handler._send_payload(payload, msg_id, comp_id=comp_id, ack_seq=frame.seq)
            return
        if frame.msg_id == pb.MSG_ID_CONTROL_COMMAND:
            payload, msg_id, comp_id = self._handler.handle_control_command(frame.payload)
            request_handler._send_payload(payload, msg_id, comp_id=comp_id, ack_seq=frame.seq)
            return
        if frame.msg_id == pb.MSG_ID_TASK_CONFIG:
            payload, msg_id, comp_id = self._handler.handle_task_config(frame.payload)
            request_handler._send_payload(payload, msg_id, comp_id=comp_id, ack_seq=frame.seq)
            return
        if frame.msg_id == pb.MSG_ID_TASK_COMMAND:
            payload, msg_id, comp_id = self._handler.handle_task_command(frame.payload)
            request_handler._send_payload(payload, msg_id, comp_id=comp_id, ack_seq=frame.seq)
            return
        if frame.msg_id == pb.MSG_ID_TASK_PATH_REQUEST:
            chunks = self._handler.build_task_path_chunks(frame.payload)
            for payload, msg_id, comp_id in chunks:
                request_handler._send_payload(payload, msg_id, comp_id=comp_id, ack_seq=frame.seq)
            return
        if frame.msg_id == pb.MSG_ID_CAMERA_FRAME_REQUEST:
            chunks = self._handler.build_camera_frame_chunks(frame.payload)
            for payload, msg_id, comp_id in chunks:
                request_handler._send_payload(payload, msg_id, comp_id=comp_id, ack_seq=frame.seq)
            return
        if frame.msg_id == pb.MSG_ID_MAP_REQUEST:
            chunks = self._handler.build_map_chunks(frame.payload)
            for payload, msg_id, comp_id in chunks:
                request_handler._send_payload(payload, msg_id, comp_id=comp_id, ack_seq=frame.seq)
            return
        if frame.msg_id == pb.MSG_ID_MAP_PREVIEW_REQUEST:
            payload, msg_id, comp_id = self._handler.handle_map_preview_request(frame.payload)
            request_handler._send_payload(payload, msg_id, comp_id=comp_id, ack_seq=frame.seq)
            return
        if frame.msg_id == pb.MSG_ID_MAP_EDIT_COMMAND:
            if rospy is not None:
                rospy.loginfo(
                    "SL-LinkA RX MapEditCommand: seq=%d ack=%d src=%d dst=%d payload_len=%d",
                    int(frame.seq),
                    int(frame.ack_seq),
                    int(frame.src_id),
                    int(frame.dst_id),
                    len(frame.payload or b""),
                )
            responses = self._handler.handle_map_edit_command(frame.payload)
            if isinstance(responses, tuple):
                responses = [responses]
            for payload, msg_id, comp_id in responses:
                request_handler._send_payload(payload, msg_id, comp_id=comp_id, ack_seq=frame.seq)
            return
        if frame.msg_id == pb.MSG_ID_VIDEO_STREAM_INFO_REQUEST:
            payload, msg_id, comp_id = self._handler.handle_video_stream_request(frame.payload)
            request_handler._send_payload(payload, msg_id, comp_id=comp_id, ack_seq=frame.seq)
            return
        if hasattr(pb, "MSG_ID_MAP_SYNC_REQUEST") and frame.msg_id == pb.MSG_ID_MAP_SYNC_REQUEST:
            payload, msg_id, comp_id = self._handler.handle_map_sync_request(frame.payload)
            request_handler._send_payload(payload, msg_id, comp_id=comp_id, ack_seq=frame.seq)
            return
        if hasattr(pb, "MSG_ID_MAP_MODE_REQUEST") and frame.msg_id == pb.MSG_ID_MAP_MODE_REQUEST:
            payload, msg_id, comp_id = self._handler.handle_map_mode_request(frame.payload)
            request_handler._send_payload(payload, msg_id, comp_id=comp_id, ack_seq=frame.seq)
            return
        if hasattr(pb, "MSG_ID_MAP_CATALOG_REQUEST") and frame.msg_id == pb.MSG_ID_MAP_CATALOG_REQUEST:
            payload, msg_id, comp_id = self._handler.handle_map_catalog_request(frame.payload)
            request_handler._send_payload(payload, msg_id, comp_id=comp_id, ack_seq=frame.seq)
            return
        if hasattr(pb, "MSG_ID_MAP_DELETE_REQUEST") and frame.msg_id == pb.MSG_ID_MAP_DELETE_REQUEST:
            payload, msg_id, comp_id = self._handler.handle_map_delete_request(frame.payload)
            request_handler._send_payload(payload, msg_id, comp_id=comp_id, ack_seq=frame.seq)
            return
        if hasattr(pb, "MSG_ID_MAP_SAVE_REQUEST") and frame.msg_id == pb.MSG_ID_MAP_SAVE_REQUEST:
            payload, msg_id, comp_id = self._handler.handle_map_save_request(frame.payload)
            request_handler._send_payload(payload, msg_id, comp_id=comp_id, ack_seq=frame.seq)
            return
        if hasattr(pb, "MSG_ID_MAP_METRICS_REQUEST") and frame.msg_id == pb.MSG_ID_MAP_METRICS_REQUEST:
            payload, msg_id, comp_id = self._handler.handle_map_metrics_request(frame.payload)
            request_handler._send_payload(payload, msg_id, comp_id=comp_id, ack_seq=frame.seq)
            return
        if hasattr(pb, "MSG_ID_TASK_RESULT_REQUEST") and frame.msg_id == pb.MSG_ID_TASK_RESULT_REQUEST:
            payload, msg_id, comp_id = self._handler.handle_task_result_request(frame.payload)
            request_handler._send_payload(payload, msg_id, comp_id=comp_id, ack_seq=frame.seq)
            return
        if hasattr(pb, "MSG_ID_LIVE_MAP_CACHE_CLEAR_REQUEST") and frame.msg_id == pb.MSG_ID_LIVE_MAP_CACHE_CLEAR_REQUEST:
            payload, msg_id, comp_id = self._handler.handle_live_map_cache_clear_request(frame.payload)
            request_handler._send_payload(payload, msg_id, comp_id=comp_id, ack_seq=frame.seq)
            return
        if hasattr(pb, "MSG_ID_PATH_PLAN_REQUEST") and frame.msg_id == pb.MSG_ID_PATH_PLAN_REQUEST:
            responses = self._handler.handle_path_plan_request(frame.payload)
            if isinstance(responses, tuple):
                responses = [responses]
            for payload, msg_id, comp_id in responses:
                request_handler._send_payload(payload, msg_id, comp_id=comp_id, ack_seq=frame.seq)
            return
        if rospy is not None:
            rospy.logwarn(
                "SL-LinkA RX unhandled msg_id=0x%04X seq=%d src=%d dst=%d payload_len=%d",
                int(frame.msg_id),
                int(frame.seq),
                int(frame.src_id),
                int(frame.dst_id),
                len(frame.payload or b""),
            )
