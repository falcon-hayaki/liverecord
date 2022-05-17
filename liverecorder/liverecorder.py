from datetime import datetime, timedelta
import os
import subprocess
import time
import signal
import re
import logging

from utils.fileio import read_json

class LiveRecorder():
    def __init__(self, record_list) -> None:
        self.record_list = read_json('resources/{}.json'.format(record_list))
        self._n = len(self.record_list)
        self._processes = []
        self._live_status = [0 for _ in range(self._n)]
        
        os.system('mkdir -p log')
        self.logfile = 'log/main.log'
        logging.basicConfig(filename=self.logfile, filemode='a', format='%(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger('main')
        self.logger.setLevel(logging.DEBUG)
    
    def run_bash(self, process_id):
        bash_line = self.get_record_bash(self.record_list[process_id])
        self.logger.debug(bash_line)
        fout = open(self.get_log_name(self.record_list[process_id]), 'a')
        p = subprocess.Popen(bash_line, stdout=fout, shell=True)
        return p

    def bash_monitor(self):
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
        while(True):
            for i in range(self._n):
                logfile = self.get_log_name(self.record_list[i])
                with open(logfile, 'r') as f:
                    lines = f.readlines()
                    for line_idx, line in enumerate(lines[::-1]):
                        res = re.match('\[(.+)\] metadata.*status ([01])', line)
                        if res:
                            time_str, status = res.groups()
                            if line_idx == 0 and self.is_stuck(time_str):
                                self.restart_process(i)
                            self._live_status[i] = int(status)
                    
            self.logger.info('monitor process. online: {}'.format(', '.join([self.record_list[i]['name'] for i, status in enumerate(self._live_status) if status == 1])))
            time.sleep(300)
    
    def is_stuck(self, time_str):
        if datetime.now() - datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S') > timedelta(minutes=5):
            return True
        return False
                
    def restart_process(self, process_id):
        self._processes[process_id].kill()
        self._processes[process_id] = self.run_bash(process_id)
    
    def stop(self):
        for p in self._processes:
            p.kill()

    def signal_handler(self, signum, frame):
        self.logger.info('Capture terminate signal. Exiting...')
        self.stop()
        exit()

    def run(self):
        for i in range(self._n):
            self._processes.append(self.run_bash(i))
        
        self.bash_monitor()
        
    @staticmethod
    def get_record_bash(record_config: dict):
        return 'record_new.sh {} "{}" -o "videos/{}"{}{}'.format(
            record_config['type'],
            record_config['roomid'],
            record_config['name'],
            ' {}'.format(' '.join(['-u {}{}'.format(u, record_config['name']) for u in record_config['upload']])),
            ' {}'.format(' '.join([a for a in record_config['args']])),
        )
    
    @staticmethod
    def get_log_name(record_config: dict):
        return 'log/bash_{}.log'.format(record_config['name'])