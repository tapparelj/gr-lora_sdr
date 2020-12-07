#/bin/bash
echo "Doing clean debug build for gr-lora-sdr..."
make clean
cmake ../ -DCMAKE_BUILD_TYPE=Debug -DCMAKE_INSTALL_PREFIX=/usr
make
echo "Running gr-lora-sdr tests..."
make test