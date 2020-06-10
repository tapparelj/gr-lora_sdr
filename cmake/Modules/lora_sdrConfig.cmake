INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_LORA_SDR lora_sdr)

FIND_PATH(
    LORA_SDR_INCLUDE_DIRS
    NAMES lora_sdr/api.h
    HINTS $ENV{LORA_SDR_DIR}/include
        ${PC_LORA_SDR_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    LORA_SDR_LIBRARIES
    NAMES gnuradio-lora_sdr
    HINTS $ENV{LORA_SDR_DIR}/lib
        ${PC_LORA_SDR_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
)

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(LORA_SDR DEFAULT_MSG LORA_SDR_LIBRARIES LORA_SDR_INCLUDE_DIRS)
MARK_AS_ADVANCED(LORA_SDR_LIBRARIES LORA_SDR_INCLUDE_DIRS)

