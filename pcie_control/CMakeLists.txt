cmake_minimum_required(VERSION 3.10)
project(pcie_control C)

set(CMAKE_C_STANDARD 11)

add_executable(pcie_control tools/main.c
        tools/main.h
        tools/reg_rw.c
)

target_link_libraries(pcie_control pthread)