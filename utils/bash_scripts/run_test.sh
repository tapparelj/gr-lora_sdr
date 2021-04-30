#bin/bash
echo "Running tester"

for i in {1..$1}
do 
echo $i
python lora_sim.py
sleep 10
done