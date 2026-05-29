from dataclasses import dataclass


INT16_MIN = -32768
INT16_MAX = 32767

REGISTER_LEFT_WHEEL_SPEED = 0x4010
REGISTER_RIGHT_WHEEL_SPEED = 0x4011
REGISTER_DISC_SPEED = 0x4012
REGISTER_DISC_ENABLE = 0x4013
REGISTER_WORK_MODE = 0x4014
REGISTER_DISC_LIFT = 0x4015
REGISTER_LIGHT = 0x4016

READ_BLOCK_START = REGISTER_LEFT_WHEEL_SPEED
READ_BLOCK_COUNT = 7

DISC_ENABLE_OFF = 0x0000
DISC_ENABLE_ON = 0x0001

WORK_MODE_AUTO = 0x0001
WORK_MODE_MANUAL = 0x0002

DISC_LIFT_DOWN = 0x0001
DISC_LIFT_UP = 0x0002

LIGHT_OFF = 0x0000
LIGHT_ON = 0x0001


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def to_uint16(value):
    return value & 0xFFFF


def to_int16(value):
    value &= 0xFFFF
    return value - 0x10000 if value & 0x8000 else value


@dataclass
class ChassisCommand:
    left_wheel_speed: int = 0
    right_wheel_speed: int = 0
    disc_speed: int = 0
    disc_enable: int = DISC_ENABLE_OFF
    work_mode: int = WORK_MODE_MANUAL
    disc_lift: int = DISC_LIFT_UP
    light: int = LIGHT_OFF

    def as_register_block(self):
        return [
            to_uint16(self.left_wheel_speed),
            to_uint16(self.right_wheel_speed),
            to_uint16(self.disc_speed),
            self.disc_enable,
            self.work_mode,
            self.disc_lift,
            self.light,
        ]


@dataclass
class RegisterSnapshot:
    left_wheel_speed: int = 0
    right_wheel_speed: int = 0
    disc_speed: int = 0
    disc_enable: int = DISC_ENABLE_OFF
    work_mode: int = WORK_MODE_MANUAL
    disc_lift: int = DISC_LIFT_UP
    light: int = LIGHT_OFF

    @classmethod
    def from_registers(cls, registers):
        if len(registers) < READ_BLOCK_COUNT:
            raise ValueError("Expected at least 7 registers in the snapshot")
        return cls(
            left_wheel_speed=to_int16(registers[0]),
            right_wheel_speed=to_int16(registers[1]),
            disc_speed=to_int16(registers[2]),
            disc_enable=registers[3],
            work_mode=registers[4],
            disc_lift=registers[5],
            light=registers[6],
        )
