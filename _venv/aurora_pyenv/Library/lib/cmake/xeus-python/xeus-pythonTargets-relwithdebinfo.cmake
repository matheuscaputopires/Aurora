#----------------------------------------------------------------
# Generated CMake target import file for configuration "RelWithDebInfo".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "xeus-python" for configuration "RelWithDebInfo"
set_property(TARGET xeus-python APPEND PROPERTY IMPORTED_CONFIGURATIONS RELWITHDEBINFO)
set_target_properties(xeus-python PROPERTIES
  IMPORTED_IMPLIB_RELWITHDEBINFO "${_IMPORT_PREFIX}/lib/libxeus-python.lib"
  IMPORTED_LOCATION_RELWITHDEBINFO "${_IMPORT_PREFIX}/bin/libxeus-python.dll"
  )

list(APPEND _IMPORT_CHECK_TARGETS xeus-python )
list(APPEND _IMPORT_CHECK_FILES_FOR_xeus-python "${_IMPORT_PREFIX}/lib/libxeus-python.lib" "${_IMPORT_PREFIX}/bin/libxeus-python.dll" )

# Import target "xeus-python-static" for configuration "RelWithDebInfo"
set_property(TARGET xeus-python-static APPEND PROPERTY IMPORTED_CONFIGURATIONS RELWITHDEBINFO)
set_target_properties(xeus-python-static PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELWITHDEBINFO "CXX;RC"
  IMPORTED_LOCATION_RELWITHDEBINFO "${_IMPORT_PREFIX}/lib/libxeus-python-static.lib"
  )

list(APPEND _IMPORT_CHECK_TARGETS xeus-python-static )
list(APPEND _IMPORT_CHECK_FILES_FOR_xeus-python-static "${_IMPORT_PREFIX}/lib/libxeus-python-static.lib" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
