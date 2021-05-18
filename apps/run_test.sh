#bin/bash
echo "Running tester"

for i in {1..$1}
do 
python lora_sim.py
done