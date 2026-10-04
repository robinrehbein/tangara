# Distributed under the OSI-approved BSD 3-Clause License.  See accompanying
# file Copyright.txt or https://cmake.org/licensing for details.

cmake_minimum_required(VERSION 3.5)

file(MAKE_DIRECTORY
  "/root/esp-idf-v6/components/bootloader/subproject"
  "/home/user/tangara/firmware-s31-test/a_hello/build/bootloader"
  "/home/user/tangara/firmware-s31-test/a_hello/build/bootloader-prefix"
  "/home/user/tangara/firmware-s31-test/a_hello/build/bootloader-prefix/tmp"
  "/home/user/tangara/firmware-s31-test/a_hello/build/bootloader-prefix/src/bootloader-stamp"
  "/home/user/tangara/firmware-s31-test/a_hello/build/bootloader-prefix/src"
  "/home/user/tangara/firmware-s31-test/a_hello/build/bootloader-prefix/src/bootloader-stamp"
)

set(configSubDirs )
foreach(subDir IN LISTS configSubDirs)
    file(MAKE_DIRECTORY "/home/user/tangara/firmware-s31-test/a_hello/build/bootloader-prefix/src/bootloader-stamp/${subDir}")
endforeach()
if(cfgdir)
  file(MAKE_DIRECTORY "/home/user/tangara/firmware-s31-test/a_hello/build/bootloader-prefix/src/bootloader-stamp${cfgdir}") # cfgdir has leading slash
endif()
