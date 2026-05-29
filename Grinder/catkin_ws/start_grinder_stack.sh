#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="${WORKSPACE:-${SCRIPT_DIR}}"
LOG_DIR="${WORKSPACE}/logs/startup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "${LOG_DIR}"

# Runtime options (can be overridden by env before running this script)
AURORA_IP="${AURORA_IP:-192.168.11.1}"
START_NAV="${START_NAV:-1}"
START_CHASSIS="${START_CHASSIS:-1}"
RESET_STATE="${RESET_STATE:-0}"
NAV_MAP_YAML="${NAV_MAP_YAML:-${WORKSPACE}/src/2-dnavigation-package/2dnavigation/teb_local_planner_tutorials/maps/map.yaml}"
HOST_ARCH="$(uname -m)"
MEDIAMTX_BIN="${MEDIAMTX_BIN:-}"

detect_mediamtx_path() {
  if [[ -n "${MEDIAMTX_BIN}" ]]; then
    echo "${MEDIAMTX_BIN}"
    return 0
  fi
  local base="${WORKSPACE}/../tools/mediamtx"
  local common="${base}/mediamtx"
  local arch_candidate=""
  case "${HOST_ARCH}" in
    aarch64|arm64) arch_candidate="${base}/mediamtx_aarch64" ;;
    x86_64|amd64) arch_candidate="${base}/mediamtx_x86_64" ;;
  esac
  if [[ -n "${arch_candidate}" && -x "${arch_candidate}" ]]; then
    echo "${arch_candidate}"
    return 0
  fi
  echo "${common}"
  return 0
}

PIDS=()

cleanup() {
  echo
  echo "[INFO] stopping all launched processes..."
  for pid in "${PIDS[@]:-}"; do
    if kill -0 "${pid}" 2>/dev/null; then
      kill "${pid}" 2>/dev/null || true
    fi
  done
  sleep 1
  for pid in "${PIDS[@]:-}"; do
    if kill -0 "${pid}" 2>/dev/null; then
      kill -9 "${pid}" 2>/dev/null || true
    fi
  done
}

trap cleanup INT TERM

launch_bg() {
  local name="$1"
  local cmd="$2"
  local logfile="${LOG_DIR}/${name}.log"
  echo "[INFO] launch ${name}"
  echo "       ${cmd}"
  bash -lc "source /opt/ros/noetic/setup.bash && source ${WORKSPACE}/devel/setup.bash && ${cmd}" \
    >"${logfile}" 2>&1 &
  local pid=$!
  PIDS+=("${pid}")
  sleep 2
  if ! kill -0 "${pid}" 2>/dev/null; then
    echo "[ERROR] ${name} exited early, check ${logfile}"
    exit 1
  fi
}

echo "[INFO] logs: ${LOG_DIR}"
echo "[INFO] host arch: ${HOST_ARCH}"
if [[ "${RESET_STATE}" == "1" ]]; then
  STATE_DIR="${WORKSPACE}/../temp/grinder_scheduler_state"
  echo "[INFO] RESET_STATE=1, clearing persisted scheduler state: ${STATE_DIR}"
  rm -rf "${STATE_DIR}"
fi

SELECTED_MEDIAMTX="$(detect_mediamtx_path)"
if [[ ! -x "${SELECTED_MEDIAMTX}" ]]; then
  echo "[WARN] mediamtx binary not executable: ${SELECTED_MEDIAMTX}"
fi
if command -v file >/dev/null 2>&1 && [[ -f "${SELECTED_MEDIAMTX}" ]]; then
  MEDIAMTX_FILE_DESC="$(file "${SELECTED_MEDIAMTX}" || true)"
  echo "[INFO] mediamtx: ${SELECTED_MEDIAMTX}"
  echo "[INFO] mediamtx file: ${MEDIAMTX_FILE_DESC}"
fi

# 1) roscore
if ! pgrep -f "roscore" >/dev/null 2>&1; then
  launch_bg "roscore" "roscore"
else
  echo "[INFO] roscore already running, skip."
fi

# 2) full grinder system launch (aurora + chassis + scheduler + optional navigation)
if [[ "${START_CHASSIS}" == "1" ]]; then
  CHASSIS_ARG="start_chassis_driver:=true"
else
  CHASSIS_ARG="start_chassis_driver:=false"
fi

if [[ "${START_NAV}" == "1" ]]; then
  launch_bg "grinder_system" "roslaunch grinder_scheduler grinder_system.launch aurora_ip_address:=${AURORA_IP} ${CHASSIS_ARG} start_navigation:=true navigation_map_yaml_path:=${NAV_MAP_YAML} local_rtsp_mediamtx_path:=${SELECTED_MEDIAMTX}"
else
  launch_bg "grinder_system" "roslaunch grinder_scheduler grinder_system.launch aurora_ip_address:=${AURORA_IP} ${CHASSIS_ARG} start_navigation:=false navigation_map_yaml_path:=${NAV_MAP_YAML} local_rtsp_mediamtx_path:=${SELECTED_MEDIAMTX}"
fi

echo
echo "[INFO] grinder stack started."
echo "[INFO] use Ctrl+C in this terminal to stop all processes started by this script."
echo "[INFO] logs are in ${LOG_DIR}"

wait
