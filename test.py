from grbl import GrblInterface
import sys
import logging
import timeit
logging.basicConfig(level=logging.DEBUG,
    format='%(asctime)s.%(msecs)03d %(name)s %(levelname)s:\t%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

if __name__ == '__main__':
    g = GrblInterface(sys.argv[1])
    log = logging.getLogger(__name__)
    log.info("unlocking...")
    g.unlock()
    g.send_gcode("G92 X0Y0")

    status_update_time = timeit.timeit(lambda: g.update_status(), number=10)/10
    log.info(f"status update time={status_update_time} ms")

    for _ in range(10):
        g.send_gcode("$J=G91X1F1000")
    for _ in range(1000):
        g.update_status()
        print(g.motion_blocks_queued())

