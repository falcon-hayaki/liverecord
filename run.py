import argparse

from liverecorder import LiveRecorder, version

args = None

def arg_parser():
    parser = argparse.ArgumentParser(description="Self use. version: {}".format(version))
    parser.add_argument('-record_list', '-l', help='Use filename in resources/ (without extension). Default is "run"', required=False, default='run')
    
    global args
    args = parser.parse_args()

if __name__ == '__main__':
    arg_parser()
    mm = LiveRecorder(args.record_list)
    mm.run()