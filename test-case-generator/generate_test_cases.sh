#bin/bash

echo "This script will generate test_cases and reference data"
echo "This script is to be runned in the scripts folder of grp-lora_sdr folder"

function run_generate {
    python main.py
}

function replace_tests {
    mv test_cases/ ../python/
}

while true; do
    read -p "Do you want to generate all test cases ?" yn
    case $yn in
        [Yy]* ) run_generate; break;;
        [Nn]* ) break;;
        * ) echo "Please answer yes or no.";;
    esac
done

while true; do
    read -p "Do you want to replace all test cases with the newly generated ?" yn
    case $yn in
        [Yy]* ) replace_tests; break;;
        [Nn]* ) exit;;
        * ) echo "Please answer yes or no.";;
    esac
done

