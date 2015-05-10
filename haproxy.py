#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
from haconn import HAconn
from os import path
from jinja2 import Environment, PackageLoader, FileSystemLoader

socket = "/var/run/haproxy/admin.sock"
class HAproxy:
    services = {}
    def __init__(self):
        pass

    def restart(self):
        """ """
        # Need to collect the current sessions before restart!
        # service haproxy reload # < will reload the config with minimal service impact
        # Needs to be run with root privileges
        pr = subprocess.Popen("service haproxy reload".split(), stdout=subprocess.PIPE)
        output, err = pr.communicate()

        if not err:
            return True
        else:
            return False

    def compile(self, servicelist):
        #http://jinja.pocoo.org/docs/dev/api/

        p = path.dirname(path.abspath(__file__))
        # This needs correcting
        env = Environment(loader=FileSystemLoader(path.split(p)[0] + '/etc/'))
        template = env.get_template('haproxy.cfg')

        # Example
        # nodes=[ {'name': 'node01', 'ip': '192.168.128.48','id':1},]
        # services = [{'name': '', 'stage': '', 'port': 10000, 'nodes':
        #               [{'name': 'random', 'ip': 'backend_ip', 'port':'backendport'}]
        #            },]
        with open('/etc/haproxy/haproxy.cfg', 'wb') as f:
            f.write(template.render(services=servicelist))

    def set_online(self, service, nodename):
        conn = HAconn()
        ret = conn.send_cmd('enable server %s/%s\r\n' % (service.name, nodename))
        conn.close()
        return ret

    def set_offline(self, service, nodename):
        conn = HAconn()
        ret = conn.send_cmd('disable server %s/%s\r\n' % (service.name, nodename))
        conn.close()
        return ret

    def drain(self, service, nodename):
        conn = HAconn()
        ret = conn.send_cmd('set server %s/%s state drain\r\n' % (service.name, nodename))
        conn.close()
        return ret


def main():
    ha = HAproxy()
    ha.compile()

if __name__ == '__main__':
    main()
