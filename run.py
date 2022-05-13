from datetime import datetime
import os
import subprocess
import time
import signal
import re
import logging

class MultibashManager():
    def __init__(self) -> None:
        self.bash_lines = []
        with open('run.txt', 'r') as f:
            for line in f.readlines():
                if line:
                    self.bash_lines.append(line.strip())
        self.n = len(self.bash_lines)
        self._log_filenames = ['log/bash_{}.log'.format(bash_line.strip().split('/')[-1]) for i, bash_line in enumerate(self.bash_lines)]
        self._processes = []
        self._lastlines = ['' for _ in range(self.n)]
        
        os.system('mkdir -p log')
        self.logfile = 'log/main.log'
        logging.basicConfig(filename=self.logfile, filemode='a', format='%(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger('main')
        self.logger.setLevel(logging.DEBUG)
    
    def run_bash(self, process_id):
        bash_line = self.bash_lines[process_id]
        fout = open(self._log_filenames[process_id], 'a')
        p = subprocess.Popen(bash_line, stdout=fout, shell=True)
        return p

    def bash_monitor(self):
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
        while(True):
            online_list = []
            for i in range(self.n):
                logfile = self._log_filenames[i]
                with open(logfile, 'r') as f:
                    lines = f.readlines()
                    last_line = ''
                    if lines:
                        last_line = lines[-1].strip()
                    if self.is_stuck(i, last_line):
                        self.restart_process(i)
                    if 'record start:' in last_line:
                        online_list.append(self._log_filenames[i].split('_')[-1].split('.')[0])
            self.logger.info('monitor process. online: {}'.format(', '.join(online_list)))
            time.sleep(300)
    
    def is_stuck(self, i, last_line):
        if self._lastlines[i] != last_line or not re.match('.*status 0', last_line):
            self._lastlines[i] = last_line
            return False
        self.logger.warning('process {} is stucked. Lastline: {}. See log file: {}'.format(i, last_line, self._log_filenames[i]))
        return True
                
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
        for i in range(self.n):
            self._processes.append(self.run_bash(i))
        
        self.bash_monitor()

if __name__ == '__main__':
    mm = MultibashManager()
    mm.run()