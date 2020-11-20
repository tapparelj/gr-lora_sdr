#/bin/bash
echo "Making gr-lora_sdr release build"
cmake ../ -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr
#Add -DCMAKE_INSTALL_PREFIX=/usr for Arch Linux users
make
sudo make install