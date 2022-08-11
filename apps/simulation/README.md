# LoRa FER Simulator
## Description
A simple script measuring the frame error rate of a flowgraph. The error rate is based on the payload CRC present in each LoRa frame.
## Structure
    - mc_simulator.py: the main script to execute.
    - data: temporary files containing the transmitted payloads, received payloads, and CRC validity for each SNR.
    - flowgraph: A sample flowgraph class 
    - results: A figure of the obtained FER as well as the values of the data. Can be loaded in ```load_results.py``` to compare different simulations.
    - load_results.py: Open prevously obtained curves and plot them alongside each others.
## Usage
    - Open ```mc_simulator.py``` and set the parameters you want to evaluate
    - ```cd``` to this directory 
    - Execute ```python mc_simulator.py``` in a teminal
    - You can load and plot previous simulation results by adding their name inside ```load_results.py```