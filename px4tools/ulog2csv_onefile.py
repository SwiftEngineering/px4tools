#! /usr/bin/env python

"""
Convert a ULog file into single CSV file(s)
Adapted from ulog2csv.py (https://github.com/PX4/pyulog/blob/master/pyulog/ulog2csv.py)

TODO:
1) Add code to look for fields to output from ulog. If none specified, dump everything.
"""

from __future__ import print_function

import argparse
import os

import pyulog.core
import csv

#pylint: disable=too-many-locals, invalid-name, consider-using-enumerate

def main():
    """Command line interface"""

    parser = argparse.ArgumentParser(description='Convert ULog to CSV')
    parser.add_argument('filename', metavar='file.ulg', help='ULog input file')

    parser.add_argument(
        '-m', '--messages', dest='messages',
        help=("Only consider given messages. Must be a comma-separated list of"
              " names, like 'sensor_combined,vehicle_gps_position'"))
    parser.add_argument('-d', '--delimiter', dest='delimiter', action='store',
                        help="Use delimiter in CSV (default is ',')", default=',')
    parser.add_argument('-o', '--output', dest='output', action='store',
                        help='Output directory (default is same as input file)',
                        metavar='DIR')
    parser.add_argument('-i', '--ignore', dest='ignore', action='store_true',
                        help='Ignore string parsing exceptions', default=False)
    parser.add_argument('-c', '--columns', dest='columns', action='store_true',
                        help='Specific columns in ulog to output', default=False)

    args = parser.parse_args()

    if args.output and not os.path.isdir(args.output):
        print('Creating output directory {:}'.format(args.output))
        os.mkdir(args.output)

    convert_ulog2csv(args.filename, args.messages, args.columns, args.output, args.delimiter, 
    args.ignore)


def convert_ulog2csv(ulog_file_name, messages, columns, output, delimiter, disable_str_exceptions=False):
    """
    Coverts and ULog file to a CSV file.
    :param ulog_file_name: The ULog filename to open and read
    :param messages: A list of message names
    :param output: Output file path
    :param delimiter: CSV delimiter
    :return: None
    """

    msg_filter = messages.split(',') if messages else None

    ulog = pyulog.core.ULog(ulog_file_name, msg_filter, disable_str_exceptions)
    data = ulog.data_list

    output_file_prefix = ulog_file_name
    
    # strip '.ulg'
    if output_file_prefix.lower().endswith('.ulg'):
        output_file_prefix = output_file_prefix[:-4]

    # write to different output path?
    if output:
        base_name = os.path.basename(output_file_prefix)
        output_file_prefix = os.path.join(output, base_name)

    columns_filter = columns.split(',') if columns else None

    output_file_name='output.csv'
    csvfile=open(output_file_name, 'w')

    #Print all the headers first
    header_list=[]
    header_lists_lengths=[]
    num_headers = 0

    #Set the first item in the list length to be zero so that tab amount in first series is zero.
    header_lists_lengths.append(0)
    for d in data:

        # use same field order as in the log, except for the timestamp
        data_keys = [f.field_name for f in d.field_data]
        data_keys.remove('timestamp')
        data_keys.insert(0, 'TIME_StartTime')  # we want timestamp at first position (changed to TIME_StartTime from timestamp for log_sysid)

        # Append each item to the header list
        for p in data_keys:
            header_list.append(p)

        #print(len(data_keys))
        header_lists_lengths.append(len(data_keys))

        num_headers += len(data_keys)

    #Write the header
    csvfile.write(delimiter.join(header_list))
    csvfile.write('\n')

    #Then write the data. TODO: Figure out how to optimize into one loop?

    #Now that the number of headers is known, create a write buffer for the data. Initialize to zero, and fill up areas that only correspond to their respective columns.
    header_lists_lengths_idx=0
    tab_amt=0
    data_list = [''] * num_headers

    for d in data:

        # use same field order as in the log, except for the timestamp
        data_keys = [f.field_name for f in d.field_data]
        data_keys.remove('timestamp')
        data_keys.insert(0, 'timestamp')  # we want timestamp at first position
        
        for i in range(len(d.data['timestamp'])):
            for k in range(len(data_keys)):
                #print ('k: '+str(k)+', i:'+str(i)+', idx: '+str((k+tab_amt))+', len(data_keys)='+str(len(data_keys)))
                data_list[(k+tab_amt)] = str(d.data[data_keys[k]][i]) 
            csvfile.write(delimiter.join(data_list))
            csvfile.write('\n')
            del data_list[:]
            data_list = [''] * num_headers
        
        header_lists_lengths_idx += 1
        tab_amt += header_lists_lengths[header_lists_lengths_idx]

    # Close file.
    csvfile.close

    # Indicate that the process has finished. 
    print("Data converted")
    

if __name__ == '__main__':
    main()