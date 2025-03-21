/*
 * This file is part of the Xilinx DMA IP Core driver tools for Linux
 *
 * Copyright (c) 2016-present,  Xilinx, Inc.
 * All rights reserved.
 *
 * This source code is licensed under BSD-style license (found in the
 * LICENSE file in the root directory of this source tree)
 */

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <byteswap.h>
#include <string.h>
#include <errno.h>
#include <fcntl.h>
#include <ctype.h>
#include "main.h"
#include <sys/types.h>
#include <sys/mman.h>

/* ltoh: little endian to host */
/* htol: host to little endian */
#if __BYTE_ORDER == __LITTLE_ENDIAN
#define ltohl(x)       (x)
#define ltohs(x)       (x)
#define htoll(x)       (x)
#define htols(x)       (x)
#elif __BYTE_ORDER == __BIG_ENDIAN
#define ltohl(x)     __bswap_32(x)
#define ltohs(x)     __bswap_16(x)
#define htoll(x)     __bswap_32(x)
#define htols(x)     __bswap_16(x)
#endif
int reg_rw(int argc, char **argv,int fdi)
{
	int fd = fdi;
	void *map;
	uint32_t read_result, writeval;
	off_t target;
	off_t pgsz, target_aligned, offset;
	/* access width */
	char access_width = 'w';
//	char *device;

	/* not enough arguments given? */
	if (argc < 3) {
		fprintf(stderr,
			"\nUsage:\t%s <device> <address> [[type] data]\n"
			"\tdevice  : character device to access\n"
			"\taddress : memory address to access\n"
			"\ttype    : access operation type : [b]yte, [h]alfword, [w]ord\n"
			"\tdata    : data to be written for a write\n\n",
			argv[0]);
		exit(1);
	}

//	device = strdup(argv[1]);
	target = strtoul(argv[2], 0, 0);
	/* check for target page alignment */
	pgsz = sysconf(_SC_PAGESIZE);
	offset = target & (pgsz - 1);
	target_aligned = target & (~(pgsz - 1));

//	printf("address read!.\n", argv[1]);

	map = mmap(NULL, offset + 4, PROT_READ | PROT_WRITE, MAP_SHARED, fd,
		       	target_aligned);

	map += offset;
	/* read only */
	if (argc <= 4) {
		switch (access_width) {
		case 'b':
			read_result = *((uint8_t *) map);
			break;
		case 'h':
			read_result = *((uint16_t *) map);
			read_result = ltohs(read_result);
			break;
		case 'w':
			read_result = *((uint32_t *) map);
			/* swap 32-bit endianess if host is not little-endian */
			read_result = ltohl(read_result);
			break;
		default:
			goto unmap;
		}
	}

	/* data value given, i.e. writing? */
	if (argc >= 5) {
		writeval = strtoul(argv[4], 0, 0);
		switch (access_width) {
		case 'b':

			*((uint8_t *) map) = writeval;
			break;
		case 'h':
			/* swap 16-bit endianess if host is not little-endian */
			writeval = htols(writeval);
			*((uint16_t *) map) = writeval;
			break;
		case 'w':
			/* swap 32-bit endianess if host is not little-endian */
			writeval = htoll(writeval);
			*((uint32_t *) map) = writeval;
			break;
		default:
			goto unmap;
		}
	}
unmap:
	map -= offset;
	if (munmap(map, offset + 4) == -1) {
		printf("Memory 0x%lx mapped failed: %s.\n",
			target, strerror(errno));
	}

	return read_result;
}
