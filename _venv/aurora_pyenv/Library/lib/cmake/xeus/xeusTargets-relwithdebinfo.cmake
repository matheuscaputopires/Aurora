#----------------------------------------------------------------
# Generated CMake target import file for configuration "RelWithDebInfo".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "xeus" for configuration "RelWithDebInfo"
set_property(TARGET xeus APPEND PROPERTY IMPORTED_CONFIGURATIONS RELWITHDEBINFO)
set_target_properties(xeus PROPERTIES
  IMPORTED_IMPLIB_RELWITHDEBINFO "${_IMPORT_PREFIX}/lib/libxeus.lib"
  IMPORTED_LOCATION_RELWITHDEBINFO "${_IMPORT_PREFIX}/bin/libxeus.dll"
  )

list(APPEND _IMPORT_CHECK_TARGETS xeus )
list(APPEND _IMPORT_CHECK_FILES_FOR_xeus "${_IMPORT_PREFIX}/lib/libxeus.lib" "${_IMPORT_PREFIX}/bin/libxeus.dll" )

# Import target "xeus-static" for configuration "RelWithDebInfo"
set_property(TARGET xeus-static APPEND PROPERTY IMPORTED_CONFIGURATIONS RELWITHDEBINFO)
set_target_properties(xeus-static PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELWITHDEBINFO "CXX;RC"
  IMPORTED_LOCATION_RELWITHDEBINFO "${_IMPORT_PREFIX}/lib/libxeus-static.lib"
  )

list(APPEND _IMPORT_CHECK_TARGETS xeus-static )
list(APPEND _IMPORT_CHECK_FILES_FOR_xeus-static "${_IMPORT_PREFIX}/lib/libxeus-static.lib" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
