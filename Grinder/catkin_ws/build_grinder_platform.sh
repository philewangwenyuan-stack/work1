#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WS_DIR="${WS_DIR:-${SCRIPT_DIR}}"

PROFILE="${PROFILE:-full}"                # full|runtime|nav|aurora|scheduler|chassis
CLEAN_ON_ARCH_CHANGE="${CLEAN_ON_ARCH_CHANGE:-1}"
SKIP_G2O="${SKIP_G2O:-0}"

HOST_ARCH="$(uname -m)"
HOST_OS="$(uname -s)"

if [[ "${HOST_OS}" != "Linux" ]]; then
  echo "[ERROR] Only Linux is supported by this script. Current: ${HOST_OS}"
  exit 1
fi

case "${HOST_ARCH}" in
  x86_64) ARCH_TAG="x86_64" ;;
  aarch64|arm64) ARCH_TAG="aarch64" ;;
  *)
    echo "[ERROR] Unsupported architecture: ${HOST_ARCH}. Expected x86_64 or aarch64."
    exit 1
    ;;
esac

if [[ -z "${CATKIN_JOBS:-}" ]]; then
  if [[ "${ARCH_TAG}" == "aarch64" ]]; then
    CATKIN_JOBS=2
    CATKIN_LOAD=2
  else
    CATKIN_JOBS="$(nproc)"
    CATKIN_LOAD="$(nproc)"
  fi
else
  CATKIN_LOAD="${CATKIN_LOAD:-${CATKIN_JOBS}}"
fi

echo "[INFO] workspace: ${WS_DIR}"
echo "[INFO] host arch: ${HOST_ARCH} -> ${ARCH_TAG}"
echo "[INFO] profile: ${PROFILE}"
echo "[INFO] catkin jobs: -j${CATKIN_JOBS} -l${CATKIN_LOAD}"

BUILD_CACHE="${WS_DIR}/build/CMakeCache.txt"
if [[ -f "${BUILD_CACHE}" ]]; then
  PREV_ARCH="$(grep -E '^CMAKE_SYSTEM_PROCESSOR:INTERNAL=' "${BUILD_CACHE}" | sed 's/.*=//' || true)"
  if [[ -n "${PREV_ARCH}" && "${PREV_ARCH}" != "${HOST_ARCH}" && "${PREV_ARCH}" != "${ARCH_TAG}" ]]; then
    if [[ "${CLEAN_ON_ARCH_CHANGE}" == "1" ]]; then
      TS="$(date +%Y%m%d_%H%M%S)"
      echo "[WARN] build cache architecture mismatch: ${PREV_ARCH} -> ${HOST_ARCH}"
      for d in build devel install; do
        if [[ -d "${WS_DIR}/${d}" ]]; then
          mv "${WS_DIR}/${d}" "${WS_DIR}/${d}.bak.${PREV_ARCH}.${TS}"
          echo "[INFO] moved ${d} -> ${d}.bak.${PREV_ARCH}.${TS}"
        fi
      done
    else
      echo "[ERROR] build cache architecture mismatch: ${PREV_ARCH} -> ${HOST_ARCH}"
      echo "[ERROR] set CLEAN_ON_ARCH_CHANGE=1 or manually clean build/devel/install."
      exit 1
    fi
  fi
fi

run_catkin_pkg() {
  local pkg="$1"
  echo
  echo "[INFO] building package whitelist: ${pkg}"
  (
    cd "${WS_DIR}"
    source /opt/ros/noetic/setup.bash
    catkin_make -j"${CATKIN_JOBS}" -l"${CATKIN_LOAD}" -DCATKIN_WHITELIST_PACKAGES="${pkg}"
  )
}

build_nav_stack() {
  local nav_pkgs=(
    "voxel_grid"
    "costmap_2d"
    "nav_core"
    "base_local_planner"
    "carrot_planner"
    "clear_costmap_recovery"
    "rotate_recovery"
    "navfn"
    "global_planner"
    "dwa_local_planner"
    "map_server"
    "base_global_planner"
    "teb_local_planner"
    "teb_local_planner_tutorials"
    "move_base"
  )
  for p in "${nav_pkgs[@]}"; do
    run_catkin_pkg "${p}"
  done
}

build_aurora_pkg() {
  run_catkin_pkg "slamware_ros_sdk"
}

if [[ "${SKIP_G2O}" != "1" ]]; then
  G2O_MAKE_SH="${WS_DIR}/src/2-dnavigation-package/3rdparty/g2omake.sh"
  if [[ -f "${G2O_MAKE_SH}" ]]; then
    echo
    echo "[INFO] ensuring g2o dependency via ${G2O_MAKE_SH}"
    bash "${G2O_MAKE_SH}" || true
  fi
fi

case "${PROFILE}" in
  full)
    run_catkin_pkg "grinder_chassis_driver"
    build_aurora_pkg
    run_catkin_pkg "grinder_scheduler"
    build_nav_stack
    ;;
  runtime)
    run_catkin_pkg "grinder_chassis_driver"
    build_aurora_pkg
    run_catkin_pkg "grinder_scheduler"
    ;;
  nav)
    build_nav_stack
    ;;
  aurora)
    build_aurora_pkg
    ;;
  scheduler)
    run_catkin_pkg "grinder_scheduler"
    ;;
  chassis)
    run_catkin_pkg "grinder_chassis_driver"
    ;;
  *)
    echo "[ERROR] unknown PROFILE=${PROFILE}"
    echo "[ERROR] valid values: full|runtime|nav|aurora|scheduler|chassis"
    exit 1
    ;;
esac

echo
echo "[INFO] build finished for profile=${PROFILE} arch=${ARCH_TAG}"
echo "[INFO] source ${WS_DIR}/devel/setup.bash before running nodes."
