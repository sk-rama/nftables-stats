import threading

import nftables

# Dependency for the task
import datetime
import time

# Function wrapper 
def periodic_task(interval, times = -1):
    def outer_wrap(function):
        def wrap(*args, **kwargs):
            stop = threading.Event()
            def inner_wrap():
                function(*args, **kwargs)
                i = 0
                while i != times and not stop.isSet():
                    stop.wait(interval)
                    function(*args, **kwargs)
                    i += 1

            t = threading.Timer(0, inner_wrap)
            t.daemon = True
            t.start()
            return stop
        return wrap
    return outer_wrap


@periodic_task(30)
def update_nft_ruleset():
    # This function is executed every 30 seconds
    if nftables.get_nft_ruleset():
        return True
    else:
        return False

