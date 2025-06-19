import serial
import logging
import re
import math

class GrblInterface:
    def __init__(self, device:str):
        self.device = serial.Serial(device)
        self.status_errors = 0
        self.log = logging.getLogger(__name__)
        self.status_re = re.compile(r"<(\w+)\|WPos:([\d.-]+),([\d.-]+),([\d.-]+)\|Bf:(\d+),(\d+)\|.*")
        self.wpos = [0, 0, 0]
        self.planner_total_blocks = None
        self.planner_blocks_available = None
        self.planner_bytes_available = None
        self.update_status()


    def send_gcode(self, gcode:str):
        self.device.write(f"{gcode}\n".encode("ascii"))
        self.wait_resp()

    def unlock(self):
        self.send_gcode("$X")

    def motion_blocks_queued(self) -> int:
        return self.planner_total_blocks - self.planner_blocks_available

    def update_status(self):
        self.device.write(b"?")
        resp = self.device.readline()
        if not b"WPos" in resp:
            self.status_errors += 1
        else:
            resp = resp.decode("ascii")
            matches = self.status_re.match(resp)
            if matches:
                status, x, y, z, bf1, bf2 = matches.groups()
                self.status = str(status)
                self.wpos = (float(x), float(y), float(z))
                self.status_errors = 0
                self.planner_blocks_available = int(bf1)
                self.planner_bytes_available = int(bf2)
                if self.planner_total_blocks is None:
                    self.planner_total_blocks = self.planner_blocks_available
        if self.status_errors > 5:
            print(resp)
            raise Exception("WPos not found in response to ?, configuration error?")

    def jog_x(self, step:float, feedrate:float):
        cmd = f"$J=G91X{step}F{feedrate}\n"
        self.device.write(cmd.encode("ascii"))
        self.wait_resp()

    def jog_xy(self, step_x:float, step_y:float, feedrate:float):
        cmd = f"$J=G91X{step_x}Y{step_y}F{feedrate}\n"
        self.device.write(cmd.encode("ascii"))
        self.wait_resp()

    def jog_wait(self):
        while True:
            self.update_status()
            if self.status == "Idle":
                break


    def jog_cancel(self):
        self.device.write(bytes([0x85]))

    def wait_resp(self):
        self.device.readline()

if __name__ == "__main__":
    int = GrblInterface("/dev/ttyACM0")
    import kbhit
    kb = kbhit.KBHit()
    while True:
        try:
            int.update_status()
            print(f"Pos = {int.wpos[0]:.3f}deg, {int.wpos[0]*math.pi/180*1e3:.1f}mrad")
            if kb.kbhit():
                char = kb.getch()
                if char == "h":
                    int.jog_x(0.1, 1000)
                    int.wait_resp()
                elif char == "j":
                    int.jog_x(0.05, 1000)
                    int.wait_resp()
                elif char == "k":
                    int.jog_x(-0.05, 1000)
                    int.wait_resp()
                elif char == "l":
                    int.jog_x(-0.1, 1000)
                    int.wait_resp()

                elif char == "q":
                    break
        except KeyboardInterrupt:
            break

