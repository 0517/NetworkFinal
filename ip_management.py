# -*- coding: utf-8 -*-

__author__ = 'qm'

import re
import json


class IpListManagement(object):

    def __init__(self):
        f = open("ip_list.txt", 'r')
        ip_str = f.read()
        if ip_str == '':
            f.close()
            f = open('ip_list.txt', 'w')
            initial_data = {'len': 0, 'ip_list': []}
            ip_str = json.dumps(initial_data)
            f.write(ip_str)
            f.close()
        else:
            f.close()
        self.ip_pattern = r"^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])$"
        self.ip_data = json.loads(ip_str)

    def add_ip(self, address):
        if re.match(self.ip_pattern, address):
            self.ip_data['ip_list'].append({'id': self.ip_data['len'] + 1, 'address': address})
            self.ip_data['len'] += 1
            f = open('ip_list.txt', 'w')
            f.write(json.dumps(self.ip_data))
            f.close()
            return True
        else:
            return False

    def delete_ip(self, ip_id):
        ip_list = self.ip_data['ip_list']
        for i in ip_list:
            print i, ip_id
            if str(i['id']) == ip_id:
                ip_list.remove(i)
                f = open('ip_list.txt', 'w')
                f.write(json.dumps(self.ip_data))
                f.close()
                return True
        return False

    def modify_ip(self, id, address):
        if not re.match(self.ip_pattern, address):
            return False
        ip_list = self.ip_data['ip_list']
        for i in ip_list:
            if i['id'] == id:
                i['address'] = address
                f = open('ip_list.txt', 'w')
                f.write(json.dumps(self.ip_data))
                f.close()
                return True
        return False
