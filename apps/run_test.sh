#bin/bash
echo "Running tester"

for i in {1..$1}
do 
echo $i
python frame_detector.py
sleep 0.1
done