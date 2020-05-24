""" Lookup USB Product and Vendor details from PID and VID """
from __future__ import print_function
try:
    from urllib2 import urlopen
except ImportError:
    from urllib.request import urlopen
import argparse

__authors__ = ["N Miller"]
__date__ = 20200524
__descrption__ = "Lookup USB Product and Vendor details from PID and VID"

# Create dictionary of vendor and product IDs, stored in usbs

def main(vid, pid, ids_file=None):
    if ids_file:
        usb_file = open(ids_file, encoding='latin1')
    else:
        usb_file = get_usb_file()
    usbs = parse_file(usb_file)
    results = search_key(usbs, (vid,pid))
    print("Vendor: {}\nProduct: {}".format(results[0], results[1]))

def get_usb_file():
    url = 'http://www.linux-usb.org/usb.ids'
    return urlopen(url)

def parse_file(usb_file):
    usbs = {}
    curr_id = ''
    for line in usb_file:
        if isinstance(line, bytes):
            line = line.decode('latin-1')
        if line.startswith('#') or line in ('\n', '\t'):
            continue
        else:
            if not(line.startswith('\t')) and line[0].isalnum():
                uid, name = line.strip().split(' ', 1)
                curr_id = uid
                usbs[uid] = [name.strip(), {}]
            elif line.startswith('\t') and line.count('\t') == 1:
                uid, name = line.strip().split(' ', 1)
                usbs[curr_id][1][uid] = name.strip()
    return usbs

def get_record(record_line):
    split = record_line.find(' ')
    record_id = record_line[:split]
    record_name = record_line[split + 1:]
    return record_id, record_name


def search_key(usb_dict, ids):
    vendor_key = ids[0]
    product_key = ids[1]

    vendor, vendor_data = usb_dict.get(vendor_key, ['unknown', {}])
    product = 'unknown'
    if vendor != 'unknown':
        product = vendor_data.get(product_key, 'unknown')
    return vendor, product


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__descrption__,
        epilog='Built by {}. Version {}'.format(", ".join(__authors__), __date__),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('vid', help="VID Value")
    parser.add_argument('pid', help="PID Value")
    parser.add_argument('--ids', '-i', help='Local path to the usb.ids file')
    args = parser.parse_args()
    main(args.vid, args.pid, args.ids)
