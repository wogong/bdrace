#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import logging
import re
import json

import getUrls
import html_parser
import time_detector

# the number of extension urls
URLS_EX_NUM = 10

if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename='tipdmc.log',
                        filemode='w')

    file_input_name = sys.argv[1]
    file_output_name = sys.argv[2]

    file_output = open(file_output_name, 'w')
    with open(file_input_name, 'r') as file_input:
        for url_orig in file_input:
            logging.info('Url building: %s', url_orig)
            # handle every url
            tree_orig = html_parser.build_etree(url_orig)
            # get the topic title for the url
            title_text = html_parser.get_title_text(tree_orig)
            # get all the element with text in the tree by dfs
            elements_orig = html_parser.parser_etree(tree_orig)

            # get the features
            # text frequency
            text_frequency_dict = html_parser.cal_text_frequency(elements_orig)
            # path frequency
            path_frequency_dict = html_parser.cal_path_frequency(elements_orig)
            # text length
            text_length_dict = html_parser.cal_text_length(elements_orig)

            # url extension
            logging.info('Url Extension: %s', url_orig)
            urls_extension = list(set(getUrls.get_n_slr(url_orig, URLS_EX_NUM)))[:URLS_EX_NUM]
            logging.info('Get %d extension urls for %s', len(urls_extension), url_orig)

            logging.info('Processing extended urls for %s', url_orig)
            for url_ex in urls_extension:
                tree_ex = html_parser.build_etree(url_ex)
                elements_ex = html_parser.parser_etree(tree_ex)
                text_frequency_dict_ex = html_parser.cal_text_frequency(elements_ex)
                path_frequency_dict_ex = html_parser.cal_path_frequency(elements_ex)
                text_length_dict_ex = html_parser.cal_text_length(elements_ex)

                # use extended information to update all the features
                text_frequency_dict = html_parser.update_text_frequency(text_frequency_dict, text_frequency_dict_ex)
                path_frequency_dict = html_parser.update_path_frequency(path_frequency_dict, path_frequency_dict_ex)
                text_length_dict = html_parser.update_text_length(text_length_dict, text_length_dict_ex)

            # find the time
            formatted_time_list = []
            for element in elements_orig:
                formatted_time = time_detector.time_formatter(element.text)
                if formatted_time:
                    formatted_time_list.append(formatted_time)
            print formatted_time_list

            # calculate the avg text length
            text_avg_length_dict = {}
            for key in path_frequency_dict.keys():
                text_avg_length_dict[key] = text_length_dict[key] / path_frequency_dict[key]

            frequent_path = ""
            score_max = 0.0
            pat = re.compile('\[\d+\]')
            for element in elements_orig:
                path_modified = pat.sub('', element.path_orig)
                key = path_modified + '_' + ''.join(element.attrib.keys())
                element.score = path_frequency_dict[key] * text_avg_length_dict[key] / text_frequency_dict[element.text]
                if element.score > score_max:
                    score_max = element.score
                    frequent_path = key
            print frequent_path

            bbs_contents = []
            pat = re.compile('\[\d+\]')
            for element in elements_orig:
                path_modified = pat.sub('', element.path_orig)
                key = path_modified + '_' + ''.join(element.attrib.keys())
                if key == frequent_path:
                    bbs_contents.append(element.text)

            for content in bbs_contents:
                print content
            # print urls_extension

            # output bbs info
            bbs_info = {}
            if len(formatted_time_list) > 0:
                if len(formatted_time_list) > len(bbs_contents):
                    for i in xrange(len(formatted_time_list) - len(bbs_contents)):
                        bbs_contents.append("")
                else:
                    bbs_contents = bbs_contents[:len(formatted_time_list)]

                post = {"content": bbs_contents[0], "title": title_text, "publish_date": formatted_time_list[0]}

                replys = []
                for i in xrange(1,len(formatted_time_list)):
                    reply = {"content": bbs_contents[i], "title": title_text, "publish_date": formatted_time_list[i]}
                    replys.append(reply)
                bbs_info = {"post": post, "replys": replys}
            bbs_json = json.dumps(bbs_info, ensure_ascii=False).encode('utf-8')
            file_output.write(url_orig + '\t' + bbs_json)
    file_output.close()
    file_input.close()