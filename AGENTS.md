# AGENTS.md

## Project Map

- This repository contains a ROS Noetic/catkin project for the Grinder robot.
- Main workspace: `Grinder/catkin_ws`.
- Main in-house packages:
  - `Grinder/catkin_ws/src/grinder_scheduler`
  - `Grinder/catkin_ws/src/grinder_chassis_driver`
- Navigation and vendor code lives under `Grinder/catkin_ws/src/2-dnavigation-package`.
- External SDKs, reference code, archives, and generated protocol code live under `Grinder/third_party`.
- Runtime tools and binaries live under `Grinder/tools`.
- Product docs and spreadsheets live under `Grinder/doc`.

## Context Rules

- Default replies for this project should be concise Chinese, following the user's requested caveman-style brevity: keep technical accuracy, drop filler, prefer short direct fragments, and expand only when precision or safety needs it.
- Prefer reading source files under `Grinder/catkin_ws/src/grinder_scheduler` and `Grinder/catkin_ws/src/grinder_chassis_driver` before searching the whole repository.
- Treat `build`, `devel`, `install`, `logs`, `temp`, `__pycache__`, and generated media files as noise unless the task is explicitly about build output, runtime logs, or generated artifacts.
- Do not inspect large archives, binaries, `.docx`, `.xlsx`, images, or videos unless the user asks about those assets.
- When searching, use `rg` with targeted globs first. Avoid broad reads of `Grinder/catkin_ws/build`, `Grinder/catkin_ws/devel`, `Grinder/catkin_ws/logs`, and `Grinder/temp`.
- Chinese comments, docs, file names, and UI strings are intentional. Preserve them and avoid translating them unless the task asks for translation.
- If Chinese text looks garbled in terminal output, assume a console encoding/display issue first; verify file encoding before changing content.

## Build And Run

- Build from `Grinder/catkin_ws` on Linux with ROS Noetic installed:
  - `./build_grinder_platform.sh`
  - `PROFILE=runtime ./build_grinder_platform.sh`
  - `PROFILE=scheduler ./build_grinder_platform.sh`
  - `PROFILE=chassis ./build_grinder_platform.sh`
- Start the stack from `Grinder/catkin_ws`:
  - `AURORA_IP=192.168.0.114 ./start_grinder_stack.sh`
- These scripts are Linux/ROS scripts. On Windows, inspect and edit code, but do not expect them to run natively.

## Verification

- For chassis driver Python changes, prefer focused tests:
  - `python3 -m pytest Grinder/catkin_ws/src/grinder_chassis_driver/test`
- For scheduler changes, inspect launch/config interactions and run the narrowest package build available:
  - `cd Grinder/catkin_ws && PROFILE=scheduler ./build_grinder_platform.sh`
- For full integration changes, use:
  - `cd Grinder/catkin_ws && PROFILE=runtime ./build_grinder_platform.sh`

## Editing Guidance

- Keep changes scoped to the package or script involved in the task.
- Do not modify third-party/vendor code unless the task explicitly targets it.
- Do not remove tracked generated files or large artifacts without user confirmation.
- Preserve existing ROS topic names, message names, launch argument names, and config keys unless a migration is requested.
