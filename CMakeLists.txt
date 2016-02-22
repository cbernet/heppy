cmake_minimum_required(VERSION 2.8)

project(heppy)

include(CTest)

add_test( NAME pyunittest COMMAND python -m unittest discover -s ${CMAKE_CURRENT_SOURCE_DIR})
set_property(TEST pyunittest PROPERTY ENVIRONMENT PYTHONPATH=${CMAKE_CURRENT_SOURCE_DIR}/..:$ENV{PYTHONPATH})
