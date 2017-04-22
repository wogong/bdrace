#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import re


def time_formatter(time_string):
    formatted_time = ""
    time_pattern = re.compile(r'(?<!\d)(\d{2,4})\D(\d{1,2})\D(\d{1,2})(?!\d)')
    time_match = time_pattern.search(time_string)
    if time_match:
        time_year = time_match.group(1)
        time_month = time_match.group(2)
        time_day = time_match.group(3)
        if len(time_month) < 2:
            time_month = '0' + time_month
        if len(time_day) < 2:
            time_day = '0' + time_day
        formatted_time = time_year + time_month + time_day
        # print time_match.group(1) + " " + time_match.group(2) + " " + time_match.group(3)
    return formatted_time

if __name__ == '__main__':
    print time_formatter(sys.argv[1])