# SL-LinkA 单下位机协议

## 1. 总览

SL-LinkA 当前面向单下位机模型：
- `0x01` 为 `APP`
- `0x10` 为唯一 `LOWER`
- `0x20` 已删除

协议能力分为 6 类：
- 配网
- 参数读写
- 运行数据读取
- 控制指令下发
- 任务调度
- 地图与视频服务

## 2. 帧格式

| 偏移 | 字段 | 长度 | 说明 |
|------|------|------|------|
| 0 | `STX1` | 1 | `0xFD` |
| 1 | `STX2` | 1 | `0x55` |
| 2 | `VER` | 1 | 协议版本 |
| 3 | `FLAGS` | 1 | 标志位 |
| 4 | `SEQ` | 2 | 序列号，小端 |
| 6 | `ACK_SEQ` | 2 | 确认序列号，小端 |
| 8 | `SRC_ID` | 1 | 源设备 ID |
| 9 | `DST_ID` | 1 | 目标设备 ID |
| 10 | `COMP_ID` | 1 | 组件 ID |
| 11 | `MSG_ID` | 2 | 消息 ID，小端 |
| 13 | `LEN` | 2 | Payload 长度，小端 |
| 15 | `PAYLOAD` | N | protobuf 数据 |
| 15+N | `CRC16` | 2 | CRC16-CCITT |
| 17+N | `TAIL` | 1 | `0xFE` |

## 3. 设备与组件

### 3.1 设备 ID

| ID | 名称 |
|----|------|
| `0x01` | `APP` |
| `0x10` | `LOWER` |
| `0xFF` | `BROADCAST` |

### 3.2 组件 ID

| ID | 名称 |
|----|------|
| `0x00` | `COMP_SYSTEM` |
| `0x04` | `COMP_WIFI` |
| `0x05` | `COMP_SETTINGS` |
| `0x06` | `COMP_MEDIA` |
| `0x07` | `COMP_CONTROL` |
| `0x08` | `COMP_SCHEDULER` |

## 4. 消息定义

### 4.1 配网

| MSG_ID | 名称 | 方向 | 说明 |
|--------|------|------|------|
| `0x0201` | `WifiConfig` | `APP -> LOWER` | 下发 WiFi 配网 |
| `0x0202` | `WifiStatusReport` | `LOWER -> APP` | 返回配网结果 |

```proto
message WifiConfig {
  string ssid = 1;
  string password = 2;
}

message WifiStatusReport {
  WifiResult result = 1;
  string message = 2;
}
```

### 4.2 参数读取与写入

| MSG_ID | 名称 | 方向 | 说明 |
|--------|------|------|------|
| `0x0203` | `SettingsReadRequest` | `APP -> LOWER` | 读取参数 |
| `0x0204` | `SettingsReadResponse` | `LOWER -> APP` | 返回参数 |
| `0x0205` | `SettingsWriteRequest` | `APP -> LOWER` | 写入参数 |
| `0x0206` | `SettingsWriteResponse` | `LOWER -> APP` | 返回写入结果 |

参数按两组组织：

#### 底盘相关 `ChassisSettings`

- 运行速度 `run_speed`
- 磨盘转速 `disc_speed_rpm`
- 磨盘开关 `disc_enabled`
- 模式设置 `work_mode`

#### 地图相关 `MapSettings`

- 小车宽度 `vehicle_width`
- 小车长度 `vehicle_length`
- 默认路径间距 `default_path_spacing`
- 转弯半径 `turn_radius`
- 重叠比例 `overlap_ratio`
- 膨胀半径 `inflation_radius`
- 障碍区域 `obstacle_regions[]`
- 运行区域 `work_regions[]`

区域统一使用多边形结构：

```proto
message PolygonPoint {
  float x = 1;
  float y = 2;
}

enum RegionType {
  REGION_TYPE_UNKNOWN = 0;
  REGION_TYPE_WORK = 1;
  REGION_TYPE_OBSTACLE = 2;
  REGION_TYPE_ERASE = 3;
  REGION_TYPE_CROP = 4;
}

message PolygonRegion {
  string name = 1;
  repeated PolygonPoint points = 2;
  string region_id = 3;
  uint32 priority = 4;
  bool enabled = 5;
  uint32 color_argb = 6;
  bool closed = 7;
  RegionType region_type = 8;
}
```

因此 `障碍区域1/2/3/N` 与 `运行区域1/2/3/N` 都通过数组表达，不再为每个区域单独定义消息。

`PolygonRegion` 扩展字段说明：

| 字段 | 含义 |
|------|------|
| `region_id` | 区域唯一 ID，用于更新/删除同一区域（推荐 UUID 或业务唯一字符串） |
| `priority` | 区域优先级，冲突时高优先级覆盖低优先级 |
| `enabled` | 区域是否启用；`false` 时仅保留不参与生效 |
| `color_argb` | 区域显示颜色（`0xAARRGGBB`） |
| `closed` | 多边形是否闭合；建议 `true` 才作为有效区域 |
| `region_type` | 区域类型（工作区/障碍区/擦除区/裁减区） |

### 4.3 上位机读取的数据

#### 4.3.1 运行状态

| MSG_ID | 名称 | 方向 | 说明 |
|--------|------|------|------|
| `0x0301` | `DeviceStatusReport` | `LOWER -> APP` | 自动 `1Hz` 上报运行状态 |

字段包括：
- 左轮速度 `left_wheel_speed`
- 右轮速度 `right_wheel_speed`
- 磨盘转速 `disc_speed_rpm`
- 磨盘开关 `disc_enabled`
- 工作模式 `work_mode`
- 磨盘升降状态 `disc_lift_state`
- 照明灯 `light_enabled`
- 位置 `position`
- 底盘开关状态 `chassis_enabled`

#### 4.3.2 视像头画面

| MSG_ID | 名称 | 方向 | 说明 |
|--------|------|------|------|
| `0x0302` | `CameraFrameRequest` | `APP -> LOWER` | 请求画面快照 |
| `0x0303` | `CameraFrameChunk` | `LOWER -> APP` | 返回画面分片 |

说明：
- 当前按“快照 + 分片回传”定义
- `CameraFrameChunk.data` 为单片数据
- `chunk_index` 与 `total_chunks` 用于上位机重组完整画面

#### 4.3.3 地图

| MSG_ID | 名称 | 方向 | 说明 |
|--------|------|------|------|
| `0x0304` | `MapRequest` | `APP -> LOWER` | 请求地图快照 |
| `0x0305` | `MapChunk` | `LOWER -> APP` | 返回地图分片 |

说明：
- 当前按“快照 + 分片回传”定义
- 支持 `OCCUPANCY_GRID / PNG / JSON` 三种编码标识
- `MapChunk` 统一携带地图信息：`width/height/resolution/origin/frame_id/preview_scale_x/preview_scale_y`

## 5. 控制指令

| MSG_ID | 名称 | 方向 | 说明 |
|--------|------|------|------|
| `0x0401` | `ControlCommand` | `APP -> LOWER` | 控制指令 |
| `0x0402` | `ControlCommandResponse` | `LOWER -> APP` | 控制结果 |

当前支持的控制项：
- 磨盘升降控制 `DiscLiftControl`
- 磨盘控制 `DiscControl`（`enabled + speed_rpm`）
- 照明控制 `LightingControl`
- 手动控制 `ManualDriveControl`
  - 兼容旧模式：`motion + speed_ratio`
  - 新增遥感模式：`remote_x + remote_y + speed_ratio`
  - 坐标约定：
    - 上：`(0.00, -1.00)`
    - 下：`(0.00, 1.00)`
    - 左：`(-1.00, 0.00)`
    - 右：`(1.00, 0.00)`
- 底盘开关控制 `ChassisPowerControl`

## 5.1 调度扩展

| MSG_ID | 名称 | 方向 | 说明 |
|--------|------|------|------|
| `0x0500` | `TaskConfig` | `APP -> LOWER` | 下发任务配置 |
| `0x0501` | `TaskConfigResponse` | `LOWER -> APP` | 返回任务配置结果 |
| `0x0502` | `TaskCommand` | `APP -> LOWER` | 开始/暂停/继续/停止 |
| `0x0503` | `TaskCommandResponse` | `LOWER -> APP` | 返回任务控制结果 |
| `0x0504` | `TaskStatusReport` | `LOWER -> APP` | 周期上报任务状态 |
| `0x0505` | `TaskPathRequest` | `APP -> LOWER` | 请求规划路径 |
| `0x0506` | `TaskPathChunk` | `LOWER -> APP` | 返回路径分片 |
| `0x0507` | `MapPreviewRequest` | `APP -> LOWER` | 请求地图缩略图 |
| `0x0508` | `MapPreviewResponse` | `LOWER -> APP` | 返回地图缩略图与编辑层 |
| `0x0509` | `MapEditCommand` | `APP -> LOWER` | 下发地图编辑 |
| `0x050A` | `MapEditResponse` | `LOWER -> APP` | 返回地图编辑结果 |
| `0x050B` | `MapEditStatusReport` | `LOWER -> APP` | 上报地图编辑应用状态 |
| `0x050C` | `VideoStreamInfoRequest` | `APP -> LOWER` | 请求视频流信息 |
| `0x050D` | `VideoStreamInfoResponse` | `LOWER -> APP` | 返回视频流信息 |
| `0x050E` | `PathPlanRequest` | `APP -> LOWER` | 请求立即路径规划 |
| `0x050F` | `PathPlanResponse` | `LOWER -> APP` | 返回路径规划摘要结果 |
| `0x0510` | `MapSyncRequest` | `APP -> LOWER` | 地图同步请求（雷达上传/下载） |
| `0x0511` | `MapSyncResponse` | `LOWER -> APP` | 返回地图同步结果 |
| `0x0512` | `MapModeRequest` | `APP -> LOWER` | 请求雷达切换建图/定位模式 |
| `0x0513` | `MapModeResponse` | `LOWER -> APP` | 返回模式切换指令处理结果 |
| `0x0514` | `MapCatalogRequest` | `APP -> LOWER` | 请求本地地图列表（名称/数量） |
| `0x0515` | `MapCatalogResponse` | `LOWER -> APP` | 返回本地地图列表（含面积/预计耗时/缩略图） |
| `0x0516` | `MapDeleteRequest` | `APP -> LOWER` | 按 map_id 删除本地地图 |
| `0x0517` | `MapDeleteResponse` | `LOWER -> APP` | 返回删除结果 |
| `0x0518` | `MapSaveRequest` | `APP -> LOWER` | 请求从雷达保存地图到本地 |
| `0x0519` | `MapSaveResponse` | `LOWER -> APP` | 返回保存结果与 map_id（含面积/预计耗时/创建时间） |
| `0x051A` | `MapMetricsRequest` | `APP -> LOWER` | 按 map_id 请求地图面积与预计耗时 |
| `0x051B` | `MapMetricsResponse` | `LOWER -> APP` | 返回 map_id/name + 工作区域面积/耗时明细 |
| `0x051C` | `TaskResultRequest` | `APP -> LOWER` | 请求上次任务执行结果（可带 map_id/task_id） |
| `0x051D` | `TaskResultResponse` | `LOWER -> APP` | 返回任务结果图与区域执行结果明细 |
| `0x051E` | `LiveMapCacheClearRequest` | `APP -> LOWER` | 请求清除 LIVE_MAP 缓存（区域缓存/原始地图缓存） |
| `0x051F` | `LiveMapCacheClearResponse` | `LOWER -> APP` | 返回清理结果 |

#### 5.1.1 新增协议速查（建议优先对接）

- `TaskConfig/TaskConfigResponse`：`0x0500/0x0501`
- `PathPlanRequest/PathPlanResponse`：`0x050E/0x050F`
- `MapCatalog/MapSave/MapDelete/MapMetrics`：`0x0514~0x051B`
- `TaskResultRequest/TaskResultResponse`：`0x051C/0x051D`
- `LiveMapCacheClearRequest/Response`：`0x051E/0x051F`

`TaskConfig (0x0500)` 关键字段：

| 字段 | 说明 |
|------|------|
| `task_id` | 任务唯一 ID（建议必传，便于后续控制和结果查询） |
| `map_id` | 任务绑定地图 ID（空值表示当前运行地图） |
| `selected_work_region_ids[]` | 本次执行区域 ID 列表 |
| `region_repeats[]` | 每区域重复次数（`{region_id, repeat}`，默认 `repeat=1`） |

`PathPlanRequest (0x050E)` 关键字段：

| 字段 | 说明 |
|------|------|
| `request_id` | 请求跟踪 ID |
| `map_id` | 目标地图 ID（可空） |
| `global_direction` | 覆盖方向 `x`/`y`，非法或缺省默认 `x` |
| `start_pose` / `end_pose` | 可选起终点（不传由 LOWER 自动选取） |

`TaskResultRequest (0x051C)` 关键字段：

| 字段 | 说明 |
|------|------|
| `map_id` | 查询目标地图 ID（可空） |
| `task_id` | 查询目标任务 ID（可空；空时返回最近任务结果） |

`TaskResultResponse (0x051D)` 关键字段：

| 字段 | 说明 |
|------|------|
| `map_id` / `task_id` | 返回结果对应地图与任务 |
| `final_state` / `all_completed` / `stop_reason` | 任务结束状态 |
| `image_data` / `image_format` / `image_width` / `image_height` | 任务结果图（二进制） |
| `selected_work_region_ids[]` | 本次任务实际执行区域 |
| `region_results[]` | 每区域目标遍数、执行遍数、是否完成、未完成原因 |

`LiveMapCacheClearRequest (0x051E)` 关键字段：

| 字段 | 说明 |
|------|------|
| （无） | 该请求不带参数；清理范围由 LOWER（调度程序）本地配置决定 |

`LiveMapCacheClearResponse (0x051F)` 关键字段：

| 字段 | 说明 |
|------|------|
| `result` / `message` | 清理执行结果 |

`MapEditOperation` 推荐使用（独立操作，不混用）：

- `MAP_EDIT_OP_UPSERT_WORK_REGION`：新增/更新工作区
- `MAP_EDIT_OP_UPSERT_OBSTACLE_REGION`：新增/更新障碍区
- `MAP_EDIT_OP_UPSERT_ERASE_REGION`：新增/更新擦除区
- `MAP_EDIT_OP_UPSERT_CROP_REGION`：新增/更新裁减区
- `MAP_EDIT_OP_DELETE_REGION`：删除区域
- `MAP_EDIT_OP_PAINT_FREE / OCCUPIED / UNKNOWN`：即时刷图

`MapSyncOperation` 语义（同步）：

- `MAP_SYNC_OP_DOWNLOAD_FROM_AURORA`：从雷达下载地图到本地并注册 `map_id`
- `MAP_SYNC_OP_UPLOAD_TO_AURORA`：按 `map_id` 从本地记录地图上传到雷达

本地地图管理新增独立消息（不再依赖 `MapSyncOperation`，并以 `map_id` 作为唯一操作标识）：

- `MapSaveRequest/Response`：从雷达保存地图到本地（支持中文地图名 + 时间戳），并记录当前任务工作区总面积与预计耗时
- `MapSaveResponse.created_at`：地图创建时间（`YYYY-MM-DD HH:MM:SS`，精确到秒）
- `MapCatalogRequest/Response`：查询本地地图名称与数量，并返回地图元信息（面积/预计耗时/缩略图base64）
- `MapDeleteRequest/Response`：按 `map_id` 删除地图
- `MapMetricsRequest/Response`：按 `map_id` 查询地图区域指标，返回 `map_name` 与区域明细
- `TaskResultRequest/Response`：按 `map_id/task_id` 查询任务执行结果（结果图 + 区域遍数完成情况）
- `MapMetricsResponse.region_metrics[]`：工作区域明细（`region_id`、`region_name`、`repeat`、`area_m2`、`estimated_time_h`）
- `LiveMapCacheClearRequest/Response`：清除 LIVE_MAP 缓存（区域状态 + live_map 目录缓存）

`PathPlanResponse` 地图信息字段（用于上位机直接渲染坐标）：

- `width / height`
- `resolution`
- `origin (x, y, heading_deg)`
- `frame_id`
- `preview_scale_x / preview_scale_y`
- `total_work_area_m2`（工作区总面积，平方米）
- `estimated_time_s`（本次规划预计执行时间，秒，`<0` 表示暂不可估计）

### 5.2 坐标系约定（当前工程）

当前联调配置下，地图与导航主链路统一使用以下 TF 关系：

- `slamware_map -> odom -> base_link -> laser`

说明：

- `frame_id` 表示坐标所属坐标系名；返回坐标（`origin`、路径点、区域点）都需与该 `frame_id` 一起使用。
- `MapChunk (0x0305)`、`MapPreviewResponse (0x0508)`、`PathPlanResponse (0x050F)` 均携带 `frame_id` 与地图几何信息（`width/height/resolution/origin`）。
- 历史示例或测试中可能出现 `map`，以运行时返回的 `frame_id` 为准。

## 6. 时序约定

### 6.1 配网

1. APP 发送 `WifiConfig`
2. LOWER 返回 `WifiStatusReport`

### 6.2 参数读取

1. APP 发送 `SettingsReadRequest`
2. LOWER 返回 `SettingsReadResponse`

### 6.3 参数写入

1. APP 发送 `SettingsWriteRequest`
2. LOWER 应用参数
3. LOWER 返回 `SettingsWriteResponse`

### 6.4 状态上报

1. LOWER 建立链路后自动上报 `DeviceStatusReport`
2. 默认周期固定为 `1Hz`

### 6.5 媒体/地图读取

1. APP 发送 `CameraFrameRequest` 或 `MapRequest`
2. LOWER 按分片返回 `CameraFrameChunk` 或 `MapChunk`
3. APP 根据 `chunk_index/total_chunks` 重组数据

### 6.6 控制下发

1. APP 发送 `ControlCommand`
2. LOWER 执行后返回 `ControlCommandResponse`

### 6.7 任务调度

1. APP 发送 `TaskConfig`
2. LOWER 返回 `TaskConfigResponse`（成功后缓存任务参数并准备规划）
3. APP 发送 `TaskCommand`
4. LOWER 返回 `TaskCommandResponse`
5. LOWER 周期性发送 `TaskStatusReport`
6. APP 如需全路径则发送 `TaskPathRequest`
7. LOWER 按 `TaskPathChunk` 分片返回
8. APP 可发送 `TaskResultRequest`
9. LOWER 返回 `TaskResultResponse`（任务结果图 + 区域明细）

`TaskConfig` 地图绑定字段：

| 字段 | 含义 |
|------|------|
| `map_id` | 任务绑定地图 ID。传空表示使用当前运行地图；传非空时 LOWER 会校验是否与当前地图一致，不一致将拒绝。 |
| `selected_work_region_ids` | 本次任务要执行的工作区 `region_id` 列表（由安卓侧勾选）。为空时默认执行全部有效工作区。 |
| `region_repeats` | 每个工作区的重复执行次数数组，元素为 `{region_id, repeat}`，`repeat>=1`。未配置的区域默认执行 `1` 次。 |

实现约定：
- 实时建图阶段，当前运行地图 ID 固定为 `LIVE_MAP`（可通过参数 `~live_map_id` 调整）。
- 执行 `MapSave` 成功后，LOWER 会切换到保存生成的真实地图 ID（如 `20260427_102229`）。

`TaskStatusReport` 补充字段（用于任务看板）：

| 字段 | 含义 |
|------|------|
| `progress` | 任务进度（0~1 小数，不是百分比） |
| `total_work_area_m2` | 工作区总面积（平方米） |
| `remaining_work_area_m2` | 剩余待覆盖面积（平方米） |
| `remaining_time_s` | 预计剩余时间（秒，`<0` 表示暂不可估计） |
| `current_region_id` | 当前执行中的基础工作区 `region_id`（不带 `__lap_N` 后缀） |
| `current_region_repeat_index` | 当前区域执行到第几遍（从 `1` 开始） |
| `current_region_repeat_total` | 当前区域总共需要执行几遍 |

`PathPlanRequest` 方向字段：

| 字段 | 含义 |
|------|------|
| `global_direction` | 全局覆盖方向，支持 `x` / `y`。未传或非法值时默认按 `x`。 |

`PathPlanResponse` 关键字段（新增关注）：

| 字段 | 含义 |
|------|------|
| `path_version` | 路径版本号 |
| `path_point_count` | 路径点数 |
| `path_length_m` | 路径总长度（米） |
| `total_work_area_m2` | 工作区总面积（平方米） |
| `estimated_time_s` | 预计执行时间（秒） |
| `preview_image` / `preview_format` | 路径预览图（二进制 + 格式） |

### 6.8 地图预览与编辑

1. APP 发送 `MapPreviewRequest`
2. LOWER 返回 `MapPreviewResponse`
3. APP 发送 `MapEditCommand`
4. LOWER 返回 `MapEditResponse`
5. LOWER 可额外发送 `MapEditStatusReport`

`MapPreviewRequest` 地图选择字段：

| 字段 | 含义 |
|------|------|
| `map_id` | 区域信息/预览读取目标地图 ID。传空表示当前运行地图；传非空时 LOWER 会校验是否与当前地图一致。 |

本地地图管理消息（`0x0514~0x051B`）入参建议：

| 消息 | 核心入参 | 说明 |
|------|----------|------|
| `MapCatalogRequest` | 无必填 | 可按实现决定是否附带缩略图 |
| `MapSaveRequest` | `map_name`（建议） | 地图保存成功后返回 `map_id`、面积、耗时、创建时间 |
| `MapDeleteRequest` | `map_id` | 按 ID 删除，不依赖本地文件名 |
| `MapMetricsRequest` | `map_id` | 返回区域面积/耗时明细（单位小时） |

`MapEditCommand` 新增细化控制字段：

| 字段 | 含义 |
|------|------|
| `map_id` | 地图编辑目标地图 ID。传空表示当前运行地图；传非空时 LOWER 会校验是否与当前地图一致，不一致直接拒绝编辑。 |
| `target_region_id` | 指定目标区域 ID（尤其用于 `DELETE_REGION` / 定点更新） |
| `target_region_type` | 指定目标区域类型（工作区/障碍区） |
| `expected_map_version` | 乐观锁版本；不匹配时可拒绝编辑，避免并发覆盖 |
| `dry_run` | 仅校验不落库；用于预检查编辑是否合法 |

`MapPreviewResponse` 关键字段说明：

| 字段 | 含义 |
|------|------|
| `result` / `message` | 结果码与说明 |
| `map_version` | 地图版本号（编辑或刷新后递增） |
| `width` / `height` | 地图原始栅格尺寸（cell） |
| `resolution` | 地图分辨率（米/格） |
| `origin.x` / `origin.y` | 地图原点在 `frame_id` 坐标系下的位置 |
| `frame_id` | 地图坐标系名（如 `slamware_map`） |
| `preview_scale_x` / `preview_scale_y` | 预览图相对原始栅格的缩放比例（像素换算可用） |
| `image_data` | 缩略图二进制（`jpg/png`） |
| `overlay_json` | 编辑层 JSON（区域、多边形、掩膜等） |

### 6.9 视频流信息

1. APP 发送 `VideoStreamInfoRequest`
2. LOWER 返回 `VideoStreamInfoResponse`

### 6.10 安卓请求地图示例（联调用）

1. APP 发送 `MapPreviewRequest`（`MSG_ID=0x0507`）
2. LOWER 返回 `MapPreviewResponse`（`MSG_ID=0x0508`）

请求示例（逻辑字段）：

```json
{
  "msg_id": "0x0507",
  "payload": {
    "max_edge": 512,
    "image_format": "jpg",
    "include_overlay": true,
    "map_id": "20260427_102229"
  }
}
```

响应示例（逻辑字段）：

```json
{
  "msg_id": "0x0508",
  "payload": {
    "result": "RESULT_OK",
    "message": "ok",
    "map_version": 12,
    "width": 260,
    "height": 211,
    "resolution": 0.05,
    "origin": {"x": -5.35, "y": -5.70, "heading_deg": 0.0},
    "frame_id": "slamware_map",
    "preview_scale_x": 1.0,
    "preview_scale_y": 1.0,
    "image_data": "<jpg/png binary>",
    "overlay_json": "{\"work_regions\":[],\"obstacle_regions\":[],\"updated_at\":1776145413}"
  }
}
```

说明：
- `image_data` 是二进制，不是文本；TCP 层会按帧长度分包传输，接收端按协议重组。
- 安卓端可直接使用 `width/height/resolution/origin` 做像素坐标与地图米制坐标换算。
- 如仅需底图，可请求时设置 `include_overlay=false`。

### 6.11 雷达模式切换

1. APP 发送 `MapModeRequest`
2. LOWER 发布到 Aurora ROS 话题：
   - `MAP_MODE_MAPPING` -> `/slamware_ros_sdk_server_node/set_map_update`
   - `MAP_MODE_LOCALIZATION` -> `/slamware_ros_sdk_server_node/set_map_localization`
3. LOWER 返回 `MapModeResponse`

请求示例（进入建图模式）：

```json
{
  "msg_id": "0x0512",
  "payload": {
    "mode": "MAP_MODE_MAPPING",
    "enabled": true,
    "map_kind": 0
  }
}
```

请求示例（进入定位模式）：

```json
{
  "msg_id": "0x0512",
  "payload": {
    "mode": "MAP_MODE_LOCALIZATION",
    "enabled": true,
    "map_kind": 0
  }
}
```

## 7. 方向约定

- 下发类消息：`SRC_ID=0x01`，`DST_ID=0x10`
- 上报类消息：`SRC_ID=0x10`，`DST_ID=0x01`

## 8. 端口约定

- 默认 TCP 端口使用 `8002`
- 模拟器与测试客户端如未显式指定端口，均按 `8002` 处理
