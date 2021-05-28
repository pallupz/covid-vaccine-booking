import time


def handle_rate_limited():
    print('Rate-limited by CoWIN. Waiting for 5 seconds.\n'
          '(You can reduce your refresh frequency. Please note that other devices/browsers '
          'using CoWIN/Umang/Arogya Setu also contribute to same limit.)')
    time.sleep(5)
