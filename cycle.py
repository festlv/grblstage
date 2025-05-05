import sys
import grbl
import serial


if __name__ == "__main__":
    g = grbl.GrblInterface(serial.Serial(sys.argv[1]))
    g.unlock()
    g.send_gcode("G92 X0")

    feedrate_degs = 60
    feedrate_degmin = feedrate_degs * 60.0

    amplitude_deg = 30
    g.jog_x(amplitude_deg/2, feedrate_degmin)
    g.jog_wait()
    while True:
        try:
            g.jog_x(-amplitude_deg, feedrate_degmin)
            g.jog_wait()
            g.jog_x(amplitude_deg, feedrate_degmin)
            g.jog_wait()
        except KeyboardInterrupt:
            break
    print("Cancelling jog")
    g.jog_cancel()
    g.wait_resp()
    g.send_gcode("G1X0F1000")