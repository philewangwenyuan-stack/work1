std_msgs/Header header

uint8 STATE_UNKNOWN=0
uint8 STATE_OK=1
uint8 STATE_WARN=2
uint8 STATE_FAULT=3

uint8 state
string state_label
string reason

string pose_source
bool pose_augmentation_enabled
bool pose_augmentation_active
bool pose_augmentation_fallback
uint64 pose_timestamp_ns
float32 pose_age_sec

bool covariance_available
uint64 covariance_timestamp_ns
float32 covariance_age_sec
float32 xy95_m
float32 yaw_1sigma_deg

float32 warn_xy95_m
float32 fault_xy95_m
float32 warn_yaw_deg
float32 fault_yaw_deg

string system_status
string relocalization_status
