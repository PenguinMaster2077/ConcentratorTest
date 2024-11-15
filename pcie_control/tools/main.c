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

//Gl vector

int event_rd = 0;

int size = 0x10000000;
int file_num = 0;
int event_waitflag = 1;
// first event
// 1 = 0x0 ~ 0x10000000
// 0 = 0x10000000 ~ 0x20000000

void read_data(int fd,int *c2h_align_mem,const char *file_name, int offset)
{
    if (fd<0)
    {
        printf("open failed");
        printf("%d",fd);
    }
    else
    {
        printf("open c2h");
    }
    FILE *record_fp = fopen(file_name, "wb");
    lseek(fd,offset,SEEK_SET);
    read(fd, c2h_align_mem, size);
    fwrite(c2h_align_mem, size, 1, record_fp);
    printf("\n%s\n",file_name);
}

void *c2h_data_process(int fd_c2h,int fd_usr, int *c2h_align_mem, const char* file_path)
{
    //读取的数据写文件
    char file[256];
    // char file_path[]=;
    char file_pack[]=".bin";
    sprintf(file,"%.100s/%d%.30s",file_path,file_num,file_pack);
    int offset;

    //read restart
    char *reg_wr_0[]={"0","/dev/xdma0_user","0x0","w","1"};
    char *reg_wr_1[]={"0","/dev/xdma0_user","0x0","w","0"};

    //read event
    char *reg_rd[]={"0","/dev/xdma0_user","0x10000","w"};
    event_rd = reg_rw(4,reg_rd,fd_usr);

    switch(event_rd){
        case 2:
        break;
        case 1:
            if(event_waitflag == 1) {
                offset = 0x0;
                read_data(fd_c2h, c2h_align_mem, file, offset);
                event_waitflag = 0;
                printf("read done ram1!\n");
                file_num = file_num + 1;
                break;
            }
            else
            {
                break;
            }
        break;
        case 0:
            if(event_waitflag == 0) {
                offset = 0x10000000;
                read_data(fd_c2h, c2h_align_mem, file, offset);
                event_waitflag = 1;
                printf("read done ram2!\n");
                file_num = file_num + 1;
                break;
            }
            else
            {
                break;
            }

        case 3:
            offset = 0;
            read_data(fd_c2h,c2h_align_mem,file,offset);
            printf("\nread restart!\n");
            reg_rw(5, reg_wr_1,fd_usr);
            reg_rw(5, reg_wr_0,fd_usr);
            break;
        default:
            break;

    }
//    printf("%d\n",event_rd);
}

int main(int argc, const char* argv[])
{
    printf("Begin to write %s file data to directory: %s", argv[1], argv[2]);
    setbuf(stdout,NULL);
    int File_NUM = atoi(argv[1]);
    const char* outputDir = argv[2];

    int fd_c2h = open("/dev/xdma0_c2h_0",O_RDWR);
    int fd_usr = open("/dev/xdma0_user",O_RDWR);

    char *reg_restart0[]={"0","/dev/xdma0_user","0x0","w","1"};
    char *reg_restart1[]={"0","/dev/xdma0_user","0x0","w","0"};
    reg_rw(5, reg_restart0,fd_usr);
    reg_rw(5, reg_restart1,fd_usr);

    while(1) {
        if (file_num < File_NUM) {
            int *c2h_align_mem = (int*)malloc(size);
            c2h_data_process(fd_c2h,fd_usr,c2h_align_mem, outputDir);
            free(c2h_align_mem);
        } else {
            break;
        }
    }
    printf ("\nWrite done! %d files\n",file_num);



    return 0;
}
