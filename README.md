# FW-Scrack弱口令检测工具
1. **致敬原作者**
	首先致敬原作者wolf@YSRC，根据原作者的工具F-Scrack做了一些修改和优化。
	新的版本就叫FW-Scrack.目前优化了输出信息，取消了no ping功能（mac系统不友好）
2. **功能**  
	FW-Scrack超级弱口令检测工具py版,可用于FTP、MYSQL、MSSQL、MONGODB、REDIS、TELNET、ELASTICSEARCH、POSTGRESQL的检测
3. **特点**  
	命令行、单文件，绿色方便各种情况下的使用。  
	无需任何外库以及外部程序支持，所有协议均采用socket与内置库进行检测。  
	兼容OSX、LINUX、WINDOWS，Python 2.6+(更低版本请自行测试，理论上均可运行)。  
4. **参数说明**  
	python FW-Scrack.py -h 192.168.1 [-p 21,80,3306] [-m 50] [-t 10]  
	-h 必须输入的参数，支持ip(192.168.1.1)，ip段（192.168.1），ip范围指定（192.168.1.1-192.168.1.254）,ip列表文件（ip.ini），最多限制一次可扫描65535个IP。  
	-p 指定要扫描端口列表，多个端口使用,隔开 例如：1433,3306,5432。未指定即使用内置默认端口进行扫描(21,23,1433,3306,5432,6379,9200,11211,27017)  
	-m 指定线程数量 默认100线程  
	-t 指定请求超时时间。  
	-d 指定密码字典
5. **使用例子**  
	python FW-Scrack.py -h 10.111.1.1  
	python FW-Scrack.py -h 192.168.1.1 -d pass.txt  
	python FW-Scrack.py -h 10.111.1.1-10.111.2.254 -p 3306,5432 -m 200 -t 6  
	python FW-Scrack.py -h ip.ini
6. **特别声明**  
	此脚本仅可用于授权的渗透测试以及自身的安全检测中。  
	此脚本仅用于学习以及使用，可自由进行改进，禁止提取加入任何有商业行为的产品中。  
