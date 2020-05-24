from __future__ import print_function
import datetime
import sys

if sys.version_info[0] == 3:
    get_input = input
elif sys.version_info[0] == 2:
    get_input = raw_input
else:
    raise NotImplementedError("Unsupported version of Python")

def main():
    unix_ts = int(get_input('Enter a Unix Timestamp to Convert ::\n>> '))
    print(unix_converter(unix_ts))
def unix_converter(timestamp):
    date_ts = datetime.datetime.utcfromtimestamp(timestamp)
    return date_ts.strftime('%m/%d/%Y %I:%M:%S %p')

if __name__ == '__main__':
    main()
