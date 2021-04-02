# Changelog

## v0.2
- Made seperate git modules for test-case-generator and profiler
- Large improbments and updates of profiler 
- Revamped system to use gnuradio stream tagging function in order to close simulation mode
- Added new data_source_sim block for simulation mode
- Made Tx and Rx block that house all individual components of the receiving and transmitting side.
- Added new assertions in grc 
## v0.1
#### Enhancements:

- Compatible with gnuradio3.8
- Added static string option in data_source 
- Unit testing for all options (still somewhat WIP)
- Test case generator to generate test cases
- Far more documentation and automatic documentation extraction from the source code (using doxygen)
- Automatic build/test/docs using github actions
- README update
- Added new logo of the project
- New Cmake build structure 
- Improved logging by making use of gnuradio logging options instead of stdout
- Added .gitignore file

#### Bug Fixes:

- Several compile errors and warnings when compiling
- Several Cmake compile warnings

