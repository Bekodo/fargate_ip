#!/opt/local/bin/python3

import boto3
import os, sys
from datetime import datetime

class ServiceIP(object):
    ip = ''       
    cluster = ''
    service = '' 
    dir_path = os.path.dirname(os.path.abspath(__file__))
    tplfile = os.path.join(dir_path,"fargate.tpl")
    vclfile = os.path.join(dir_path,"fargate.vcl")

    def __init__(self):
        session = boto3.Session(profile_name = 'vilaweb')
        self.ecs = session.client('ecs',region_name = 'eu-west-1')

    def _getIp(self):
        taskArns = self.ecs.list_tasks(
            cluster=self.cluster,
            serviceName=self.service,
            launchType='FARGATE'
        )
        taskArns_data = taskArns['taskArns']
        task_data = self.ecs.describe_tasks(
            cluster=self.cluster,
            tasks=taskArns_data
        )
        for container in task_data['tasks']:
            if container['lastStatus'] == 'RUNNING':
                for ips in container['containers'][0]['networkInterfaces']:
                    self.ip=(ips['privateIpv4Address'])
    
    def _settmplFile(self):
        with open(self.tplfile) as f:
            data = f.read()
        f.close
        self._getIp()
        data = data.replace("IP1",self.ip)
        return data

    def _getvlcFile(self):
        with open(self.vclfile) as f:
            data = f.read()
        f.close
        return data

    def compareConf(self):
        vcl_data = self._getvlcFile()
        tmpl_data = self._settmplFile()
        if (vcl_data != tmpl_data):
            return True
        else:
            return False

    def setvlcFile(self):
        tmpl_data = self._settmplFile()
        vlcf = open(self.vclfile,'w')
        vlcf.write(tmpl_data)
        vlcf.close

if __name__ == '__main__':
    objIP = ServiceIP()
    if (objIP.compareConf()):
        if not objIP.ip:
            sys.exit()
        objIP.setvlcFile()
        os.system("systemctl reload varnish")
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y:%H:%M:%S")
        print('[{}] {}'.format(dt_string, objIP.ip))






