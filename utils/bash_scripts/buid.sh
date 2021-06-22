#!/bin/bash
echo "Building gr_lora_sdr"

cpu=$(grep 'cpu cores' /proc/cpuinfo | uniq | awk '{print $4}')
echo "Found $cpu cores"

if [ $1 == "debug"]; then
    if [ -f "/etc/arch-release" ]; then
        cmake ../ -DCMAKE_BUILD_TYPE=Debug -DCMAKE_INSTALL_PREFIX=/usr
    else
        cmake ../ -DCMAKE_BUILD_TYPE=Debug
    fi
else
    if [ -f "/etc/arch-release" ]; then
        cmake ../ -DCMAKE_INSTALL_PREFIX=/usr
    else
        cmake ../
    fi
fi

# make -j $cpu
# sudo make install
