"""Third iteration of the setupapi.dev.log parser."""
from __future__ import print_function
import argparse
from io import open
import os
import sys
import usb_lookup

__authors__ = ["Noah M"]
__date__ = 20200101
__description__ = """This scripts reads a Windows 7 Setup API
    log and prints USB Devices to the user"""

def main(in_file, local_usb_ids=None):
    """
    Main function to handle operation
    :param in_file: Str - Path to setupapi log to analyze
    :return: None
    """

    if os.path.isfile(in_file):
        device_information = parse_setupapi(in_file)
        usb_ids = prep_usb_lookup(local_usb_ids)
        for device in device_information:
            parsed_info = parse_device_info(device)
            if isinstance(parsed_info, dict):
                parsed_info = get_device_names(usb_ids,
                                               parsed_info)
            if parsed_info is not None:
                print_output(parsed_info)
        print('\n\n{} parsed and printed successfully.'.format(
            in_file))

    else:
        print("Input: {} was not found. Please check your path "
              "and permissions.".format(in_file))
        sys.exit(1)


def parse_setupapi(setup_log):
    """
    Read data from provided file for Device Install Events for
        USB Devices
    :param setup_log: str - Path to valid setup api log
    :return: tuple of str - Device name and date
    """
    device_list = list()
    unique_list = set()
    with open(setup_log) as in_file:
        for line in in_file:
            lower_line = line.lower()
            if 'device install (hardware initiated)' in \
                    lower_line and ('vid' in lower_line or
                                    'ven' in lower_line):
                device_name = line.split('-')[1].strip()
                date = next(in_file).split('start')[1].strip()
                if device_name not in unique_list:
                    device_list.append((device_name, date))
                    unique_list.add(device_name)

    return device_list


def parse_device_info(device_info):
    """
    Parses Vendor, Product, Revision and UID from a Setup API
        entry
    :param device_info: string of device information to parse
    :return: dictionary of parsed information or original string
        if error
    """
    # Initialize variables
    vid = ''
    pid = ''
    rev = ''
    uid = ''

    # Split string into segments on \\
    segments = device_info[0].split('\\')

    if 'usb' not in segments[0].lower():
        return None
        # Eliminate non-USB devices from output
        # May hide other storage devices

    for item in segments[1].split('&'):
        lower_item = item.lower()
        if 'ven' in lower_item or 'vid' in lower_item:
            vid = item.split('_', 1)[-1]
        elif 'dev' in lower_item or 'pid' in lower_item or \
                'prod' in lower_item:
            pid = item.split('_', 1)[-1]
        elif 'rev' in lower_item or 'mi' in lower_item:
            rev = item.split('_', 1)[-1]

    if len(segments) >= 3:
        uid = segments[2].strip(']')

    if vid != '' or pid != '':
        return {'Vendor ID': vid.lower(),
                'Product ID': pid.lower(),
                'Revision': rev,
                'UID': uid,
                'First Installation Date': device_info[1]}
    # Unable to parse data, returning whole string
    return device_info


def prep_usb_lookup(local_usb_ids=None):
    """
    Prepare the lookup of USB devices through accessing the most
    recent copy of the database at http://linux-usb.org/usb.ids
    or using the provided file and parsing it into a queriable
    dictionary format.
    """
    if local_usb_ids:
        usb_file = open(local_usb_ids, encoding='latin1')
    else:
        usb_file = usb_lookup.get_usb_file()
    return usb_lookup.parse_file(usb_file)


def get_device_names(usb_dict, device_info):
    """
    Query `usb_lookup.py` for device information based on VID/PID.
    :param usb_dict: Dictionary from usb_lookup.py of known
        devices.
    :param device_info: Dictionary containing 'Vendor ID' and
        'Product ID' keys and values.
    :return: original dictionary with 'Vendor Name' and
        'Product Name' keys and values
    """
    device_name = usb_lookup.search_key(
        usb_dict, [device_info['Vendor ID'],
            device_info['Product ID']])

    device_info['Vendor Name'] = device_name[0]
    device_info['Product Name'] = device_name[1]

    return device_info


def print_output(usb_information):
    """
    Print formatted information about USB Device
    :param usb_information: dictionary containing key/value
        data about each device or tuple of device information
    :return: None
    """
    print('{:-^15}'.format(''))

    if isinstance(usb_information, dict):
        for key_name, value_name in usb_information.items():
            print('{}: {}'.format(key_name, value_name))
    elif isinstance(usb_information, tuple):
        print('Device: {}'.format(usb_information[0]))
        print('Date: {}'.format(usb_information[1]))

if __name__ == '__main__':
    # Run this code if the script is run from the command line.
    parser = argparse.ArgumentParser(
        description=__description__,
        epilog='Built by {}. Version {}'.format(
            ", ".join(__authors__), __date__),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument('IN_FILE',
                        help='Windows 7 SetupAPI file')
    parser.add_argument('--local',
                        help='Path to local usb.ids file')

    args = parser.parse_args()

    # Run main program
    main(args.IN_FILE, args.local)
