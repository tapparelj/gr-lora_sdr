#/bin/bash
echo "Doing clean debug build for gr-lora-sdr..."
cmake ../ -DCMAKE_BUILD_TYPE=Debug -DCMAKE_INSTALL_PREFIX=/usr
make -j4
sudo make install
