if [ ! -n "$1" ] ; then
    nohup python3 run.py > nohup.out 2>&1 &
else
    nohup python3 run.py "$1" > nohup.out 2>&1 &