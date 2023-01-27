PID=$(ps -ef | grep "python3 run.py" | grep -v grep | awk '{ print $2 }')
echo kill -9 $PID
kill -9 $PID

PID=$(ps -ef | grep "bash record" | grep -v grep | awk '{ print $2 }')
if [ -z "$PID" ]
then
echo Application is already stopped
else
echo kill -9 $PID
kill -9 $PID
fi

rm -r log/ videos/