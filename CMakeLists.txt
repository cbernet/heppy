cmake_minimum_required(VERSION 2.8)

project(heppy)

include(CTest)

message(${CMAKE_CURRENT_SOURCE_DIR})
add_test( NAME pyunittest COMMAND python ../test/suite.py)
set_property(TEST pyunittest PROPERTY ENVIRONMENT PYTHONPATH=${CMAKE_CURRENT_SOURCE_DIR}/..:$ENV{PYTHONPATH})
