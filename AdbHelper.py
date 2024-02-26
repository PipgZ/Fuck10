from ppadb.client import Client as AdbClient
from ppadb.device import Device

from DataStruct import DragEvent


class AdbHelper:
    @staticmethod
    def get_client(host, port) -> AdbClient:
        return AdbClient(host=host, port=port)

    @staticmethod
    # 模拟触摸拖拽事件
    def send_drag_event(device: Device, event: DragEvent):
        cmd = f"input swipe {event.start_x} {event.start_y} {event.end_x} {event.end_y} {event.duration_ms}"
        device.shell(cmd)
        # debugInfo("Game Map:", gameMap)

    @staticmethod
    def get_screenshot(device: Device):
        return device.screencap()
