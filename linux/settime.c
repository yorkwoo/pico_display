#include <stdio.h>
#include <time.h>
#include <sys/time.h>

/* For 5 function MCU to update time when running standalone */
int main()
{
	struct timeval tv1;
	struct tm *tm_p;
	char buf[128];
	gettimeofday(&tv1, NULL);
	tm_p = localtime(&tv1.tv_sec);
	sprintf(buf, "settime %4d%02d%02d%02d%02d%02d\n",
		tm_p->tm_year+1900, tm_p->tm_mon+1, tm_p->tm_mday,
		tm_p->tm_hour, tm_p->tm_min, tm_p->tm_sec);
	/* printf(buf); */
	FILE *fp = fopen("/dev/ttyACM0", "r+");
	if(fp != NULL){
		fputs(buf, fp);
		char *pb = fgets(buf, 4, fp);
		if(pb != NULL){
			printf("Got %s\n", pb);
		}
		fclose(fp);
	}
	
	return 0;
}
