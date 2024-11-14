import time
import lxc_list_image
import metrics

while True:
    lxc_list_image.send_lxc()
    metrics.send_metrics()
    time.sleep(10)
