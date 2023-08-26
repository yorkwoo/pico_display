#include <arpa/inet.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <netdb.h>
#include <ifaddrs.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <signal.h>
#include <termios.h>
#include <string>
#include <vector>

const char* SERIALPORT = "/dev/ttyS0";
int g_SerialFd = -1;
bool debugFlag = false;
bool endFile = false;
int waitSecs = 0;

class intrfRec
{
public:
    std::string if_name;
    std::string ip_addr;
};

char linebuf[1024];
int lbend = 0;
fd_set gSelector;
void init_fds()
{
    FD_ZERO(&gSelector);
    FD_SET(g_SerialFd, &gSelector);
}

void printhex(const char *buf, int len)
{
    for(int i=0; i<len; ++i){
        printf("%02x", buf[i]);
    }
    printf("\n");
}

int readbuf(char *buf, int max, bool remove_cr=true)
{
    char tmpbuf[64];
    int ret = 0;
    struct timeval timeLmt;
    timeLmt.tv_sec = 1;
    timeLmt.tv_usec = 0;
    while(true){
        int len = select(g_SerialFd+1, &gSelector, nullptr, nullptr, &timeLmt);
        if(len > 0){
            //printf("select %d bufend %d\n", len, lbend);
            int r = read(g_SerialFd, tmpbuf, 64);
            int in = 0;
            while(in < r){
                char c = tmpbuf[in++];
                linebuf[lbend++] = c;
                if(c == '\n' ||
                    lbend == max-1){
                    if(ret <= 0){   // prevent return twice
                        strncpy(buf, linebuf, lbend);
						if(remove_cr && c == '\n'){
							--lbend;
						}
                        buf[lbend] = 0;
                        ret = lbend;
                        lbend = 0;  // clear buffer
                    }
                }
            }
            if(ret > 0)
                break;
            /* if(lbend > 0){
                printf("readbuf: read %d -> %d: ",r, lbend);
                printhex(tmpbuf, r);
            } */
        } else if(len == 0){
            break;
        }
    }
    if(debugFlag && ret > 0){
        printf("got '%s' len:%d\n", buf, ret);
    }
	return ret;
}

// 送命令，自動加換行
void sendCmd(const char *cmd)
{
	int len=strlen(cmd);
	char *buf = (char *)alloca(len+2);
	strcat(strcpy(buf, cmd), "\n");
	if(debugFlag){
		printf("send '%s'\n", cmd);
	}
	int ret = write(g_SerialFd, buf, len+1);
	if(ret < 0){
		endFile = true;
	}
}

// check for OK or ERR, omit other outputs.
bool checkRet(int waitSec=1)
{
    char rcvBuf[128];
	bool ret = false;
    int cnt = waitSec;
    rcvBuf[0] = 0;
	while(true){
		int rr = readbuf(rcvBuf, 128);
		if(rr > 0){
			if(!strncmp(rcvBuf, "OK", 2)){
				ret = true;
				break;
			} else if(!strncmp(rcvBuf, "ERR", 3)){
				ret = false;
				break;
			}
		} else {
            if(--cnt <= 0)
                break;
        }
	}
    if(debugFlag)
        printf("ret %s\n",(rcvBuf[0]==0?" no response":rcvBuf));
    return ret;
}

void onCtrlBreak(int sig)
{
    if(g_SerialFd > 0){
		if(!endFile){
			sendCmd("exit");
			close(g_SerialFd);
		}
    }
    exit(0);
}

// fill buffer begins from buf with space * len, and replace with str
void fill_string(char *buf, int len, const char *str)
{
    int slen = strlen(str);
    if(slen > len)
        slen = len;
    strncpy(buf, str, slen);
    if(slen < len){
        for(int i=slen; i<len; ++i)
            buf[i] = ' ';
    }
    buf[len] = 0;
}

void outputInfos(const char *serialLn, std::vector<intrfRec>& dataz)
{
    char rcvBuf[64];
    
    if(serialLn == nullptr)
        serialLn = SERIALPORT;
	
	if(waitSecs > 0){
		if(debugFlag)
			printf("wait %d seconds before open %s\n", waitSecs, serialLn);
		sleep(waitSecs);
	}
        
	g_SerialFd = open(serialLn, O_RDWR | O_NDELAY);
    if(g_SerialFd < 0){
        sprintf(rcvBuf, "Can't open port %s", serialLn);
        perror(rcvBuf);
        return;
    }
	printf("open %s for desc %d\n", serialLn, g_SerialFd);
    bool isUart = !strncmp(serialLn, "/dev/ttyS", 9);
    struct termios opts;
    tcgetattr(g_SerialFd, &opts);
    opts.c_lflag &= ~ECHO;
    if(isUart){
        cfsetispeed(&opts, B115200);
        cfsetospeed(&opts, B115200);
    }
	tcsetattr(g_SerialFd, TCSANOW, &opts);
    init_fds();
    
    bool isResponse = false;
	int helocnt = 0;
    do {
        sendCmd("helo");
		if(endFile){
			// 可能暫時無法寫入，等下...
			if(++helocnt < 10){
				printf("helocnt: %d\n", helocnt);
				endFile = false;
				sleep(1);
			} else {
				perror("helo cmd fail");
				exit(0);
			}
		} else {
			if(checkRet(10)){
				isResponse = true;
			}
		}
    } while(!isResponse);
    
	sendCmd("info");
    readbuf(rcvBuf, 64);
    printf("info returns:%s\n",rcvBuf);

    bool chkNet = false;
    int netCnt = 0;
    char ipbuf[17];
    while(!endFile){
        std::vector<intrfRec>::iterator dp;
        for(dp = dataz.begin(); dp != dataz.end(); ++dp){
            //printf("%s: %s\n", dp->if_name.c_str(), dp->ip_addr.c_str());
            if(!strcmp(dp->if_name.c_str(), "lo") ||
                !strncmp(dp->if_name.c_str(), "docker", 6) ||
                !strncmp(dp->if_name.c_str(), "veth", 4))
                continue;
            if(!chkNet)
                ++netCnt;
			
			sendCmd("clear");
			checkRet();

            fill_string(ipbuf, 15, dp->if_name.c_str());
			sprintf(rcvBuf, "text,0,0,%s", ipbuf);
			sendCmd(rcvBuf);
            checkRet();
            
            fill_string(ipbuf, 15, dp->ip_addr.c_str());
			sprintf(rcvBuf, "text,0,1,%s", ipbuf);
			sendCmd(rcvBuf);
            checkRet();

			sendCmd("flush");
            checkRet();
            
            sleep(5);
        }
        chkNet = true;
        if(netCnt < 1){
			sendCmd("text,0,0,No Networks.");
            checkRet();
            sleep(10);
        }
    }
}

const char *devName = "";
void parse_args(int argc, char **argv)
{
    for(int i=1; i<argc; ++i){
        if(argv[i][0] == '-'){
            char ch = argv[i][1];
            if(ch == 'd' || ch == 'D'){
                debugFlag = true;
            } else if(ch == 'w'){
				if(++i < argc){
					waitSecs = atoi(argv[i]);
				} else {
					printf("-w must specify seconds to wait\n");
				}
			}
        } else if(!strncmp(argv[i], "/dev/tty", 8)){
            devName = argv[i];
        }
    }
}

int main(int argc, char *argv[])
{
    struct ifaddrs *ifaddr, *ifa;
    int family, s;
    char host[NI_MAXHOST];

    if (getifaddrs(&ifaddr) == -1) 
    {
        perror("getifaddrs");
        exit(EXIT_FAILURE);
    }
    parse_args(argc, argv);
    if(strlen(devName) < 4){
        devName = SERIALPORT;
    }
    
    std::vector<intrfRec> networks;

    for (ifa = ifaddr; ifa != NULL; ifa = ifa->ifa_next) 
    {
        if (ifa->ifa_addr == NULL)
            continue;  

        s=getnameinfo(ifa->ifa_addr,sizeof(struct sockaddr_in),host, NI_MAXHOST, NULL, 0, NI_NUMERICHOST);

        /*if((strcmp(ifa->ifa_name,"wlan0")==0)&&(ifa->ifa_addr->sa_family==AF_INET)) */
        if(ifa->ifa_addr->sa_family==AF_INET)
        {
            if (s != 0)
            {
                printf("getnameinfo() failed: %s\n", gai_strerror(s));
                exit(EXIT_FAILURE);
            }
            intrfRec ifrec;
            ifrec.if_name = ifa->ifa_name;
            ifrec.ip_addr = host;
            networks.push_back(ifrec);
        }
    }

    freeifaddrs(ifaddr);

    signal(SIGINT, onCtrlBreak);
    outputInfos(devName, networks);
    
    exit(EXIT_SUCCESS);
}
