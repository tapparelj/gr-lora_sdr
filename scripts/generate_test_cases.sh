#bin/bash

echo "This script will generate test_cases and reference data"
echo "This script is to be runned in the scripts folder of grp-lora_sdr folder"

function run_generate {
    mkdir -p results
    mkdir -p test_cases
    python generate_test_cases.py
    autopep8 --in-place --aggressive --aggressive test_cases/qa_tx.py
    autopep8 --in-place --aggressive --aggressive test_cases/qa_rx.py
}

function replace_tests {
    mv test_cases/qa_tx.py ../python/qa_tx.py
    mv test_cases/qa_rx.py ../python/qa_rx.py
}

function replace_reference {
    mv results/* ../test_files/
}


while true; do
    read -p "Do you want to generate all test cases and reference files ?" yn
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
        [Nn]* ) break;;
        * ) echo "Please answer yes or no.";;
    esac
done

while true; do
    read -p "Do you want to replace all refrence data with the newly generated ?" yn
    case $yn in
        [Yy]* ) replace_reference; break;;
        [Nn]* ) exit;;
        * ) echo "Please answer yes or no.";;
    esac
done