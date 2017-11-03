以下内容主要是DDR Parameters Calibration时需要注意的事项：

1.I.MX6DQSDL DDR3 Script Aid V0.10.xlsx
	这个表格是用来生成DDR init script file(*inc).
	针对自己的DDR硬件需要修改表格的worksheet(Register Configuration).
		Register Configuration共分三项
			Device Information:
				主要描述单个ddr cell的具体信息，需要针对DDR datasheet来修改相应的内容。
				注意其中一项DRAM density(Gb)表示的是位，例如单个ddr cell容量为512M，那此项对应的值为4Gb.
			System Information:
				主要描述系统内整个DDR的信息
				Total DRAM Density(Gb)和Device Information中的注意事项一样。
			SI Configuration
				主要描述一些阻抗的设置（电子相关部分）
		当上述内容都修改后，表格中worksheet(RealView.inc)就是生产的ddr init script file.

2.具体的Calibration过程可以参考i.MX6_DDR_Stress_Tester_V1.0.2_User_Guide.pdf
  DDR Parameters Calibration要求高低温测试，所以需要至少3台机器生产9组数据，即高温3组，低温3组，常温3组。
  

3.由于单体测试结果可能不准确，所以最终写入Uboot的校验参数应该是所有units测试结果的平均值。
	以下为所有参数求平均值得过程：
	3.1 Write leveling calibration
		MMDC_MPWLDECTRL0 ch0: 0x0009000E
		MMDC_MPWLDECTRL1 ch0: 0x001F0016
		多个unit：
			每组MMDC_MPWLDECTRL0/MMDC_MPWLDECTRL1不是0的两个字节之间分别做平均得出MMDC_MPWLDECTRL0和MMDC_MPWLDECTRL1。
			0x0009000E 0x000C000D -->(0x09+0x0C)/2 (0x0E+0x0D)/2 -->0x000A000D
			0x001F0016 0x001D0013 -->(0x1F+0x1D)/2 (0x16+0x13)/2 -->
	3.2 Read DQS Gating calibration
		BYTE 0:
		        Start:           HC=0x02 ABS=0x0C
		        End:             HC=0x04 ABS=0x4C
		        Mean:            HC=0x03 ABS=0x2C
		        End-0.5*tCK:     HC=0x03 ABS=0x4C
		        Final:           HC=0x03 ABS=0x4C
		BYTE 1:
		        Start:           HC=0x02 ABS=0x04
		        End:             HC=0x04 ABS=0x40
		        Mean:            HC=0x03 ABS=0x22
		        End-0.5*tCK:     HC=0x03 ABS=0x40
		        Final:           HC=0x03 ABS=0x40
		BYTE 2:
		        Start:           HC=0x01 ABS=0x6C
		        End:             HC=0x04 ABS=0x30
		        Mean:            HC=0x03 ABS=0x0E
		        End-0.5*tCK:     HC=0x03 ABS=0x30
		        Final:           HC=0x03 ABS=0x30
		BYTE 3:
		        Start:           HC=0x00 ABS=0x70
		        End:             HC=0x04 ABS=0x3C
		        Mean:            HC=0x02 ABS=0x56
		        End-0.5*tCK:     HC=0x03 ABS=0x3C
		        Final:           HC=0x03 ABS=0x3C
		
		
		DQS calibration MMDC0 MPDGCTRL0 = 0x0340034C, MPDGCTRL1 = 0x033C0330
		
		Note: Array result[] holds the DRAM test result of each byte.
		      0: test pass.  1: test fail
		      4 bits respresent the result of 1 byte.
		      result 0001:byte 0 fail.
		      result 0011:byte 0, 1 fail.
		      
		求平均算法：
			一切以HC为标准，可以这样理解，HC为高位，ABS为低位。
			单个Unit：
				End-0.5*tCK 其实就是End组的HC-1，End组的ABS保持不变
				每个BYTE的Mean和End-0.5*tCK相比较，找出最大的一组值得出Final
				最后根据Final值可以这样理解：
				MPDGCTRL0 =  0x03     0x40      0x03     0x4C
					   BYTE1_HC,BYTE1_ABS,BYTE0_HC,BYTE0_ABS 	
			      
			      	MPDGCTRL1 =  0x03     0x3C      0x03     0x30
			      		   BYTE3_HC,BYTE3_ABS,BYTE2_HC,BYTE2_ABS	
			多个unit	：
				以HC为标准，找出所有unit中各个BYTE Start最大的一组以及End最小的一组，相当于一个区间。
				然后得出最后四组数据，再按照以上单个unit的算法，算出最后的平均值。	
				
	3.3  Read calibration
		Starting Read calibration...
		
		ABS_OFFSET=0x00000000   result[00]=0x1111
		ABS_OFFSET=0x04040404   result[01]=0x1111
		ABS_OFFSET=0x08080808   result[02]=0x1111
		ABS_OFFSET=0x0C0C0C0C   result[03]=0x1011
		ABS_OFFSET=0x10101010   result[04]=0x1010
		ABS_OFFSET=0x14141414   result[05]=0x1010
		ABS_OFFSET=0x18181818   result[06]=0x0000
		ABS_OFFSET=0x1C1C1C1C   result[07]=0x0000
		ABS_OFFSET=0x20202020   result[08]=0x0000
		ABS_OFFSET=0x24242424   result[09]=0x0000
		ABS_OFFSET=0x28282828   result[0A]=0x0000
		ABS_OFFSET=0x2C2C2C2C   result[0B]=0x0000
		ABS_OFFSET=0x30303030   result[0C]=0x0000
		ABS_OFFSET=0x34343434   result[0D]=0x0000
		ABS_OFFSET=0x38383838   result[0E]=0x0000
		ABS_OFFSET=0x3C3C3C3C   result[0F]=0x0000
		ABS_OFFSET=0x40404040   result[10]=0x0000
		ABS_OFFSET=0x44444444   result[11]=0x0000
		ABS_OFFSET=0x48484848   result[12]=0x0000
		ABS_OFFSET=0x4C4C4C4C   result[13]=0x0010
		ABS_OFFSET=0x50505050   result[14]=0x0010
		ABS_OFFSET=0x54545454   result[15]=0x0111
		ABS_OFFSET=0x58585858   result[16]=0x0111
		ABS_OFFSET=0x5C5C5C5C   result[17]=0x0111
		ABS_OFFSET=0x60606060   result[18]=0x1111
		ABS_OFFSET=0x64646464   result[19]=0x1111
		ABS_OFFSET=0x68686868   result[1A]=0x1111
		ABS_OFFSET=0x6C6C6C6C   result[1B]=0x1111
		ABS_OFFSET=0x70707070   result[1C]=0x1111
		ABS_OFFSET=0x74747474   result[1D]=0x1111
		ABS_OFFSET=0x78787878   result[1E]=0x1111
		ABS_OFFSET=0x7C7C7C7C   result[1F]=0x1111
		
		MMDC0 MPRDDLCTL = 0x3A2E3030
		
		求平均算法：
			单个Unit：
				result表示四个bytes,和ABS_OFFSET一一对应。
				例如：ABS_OFFSET=0x10101010   result[04]= 1  0  1  0
									10 10 10 10
				以列为基准，从上往下看：
					1->0的0对应ABS_OFFSET和第一次0->1的0对应的ABS_OFFSET，相加，然后除以2，就得出MPRDDLCTL。
			多个unit：
				看表格内容：
					对应于每一位，分别从上往下找出所有unit最上面的全部为0的一行，然后再找出从下往上最下面全部为0的一行
					最后得出四组数据，每组分为上限和下限。再以单个Unit的算法得出最后平均值
			
	3.3 Write calibration
		Starting Write calibration...
		
		ABS_OFFSET=0x00000000   result[00]=0x1111
		ABS_OFFSET=0x04040404   result[01]=0x1111
		ABS_OFFSET=0x08080808   result[02]=0x1111
		ABS_OFFSET=0x0C0C0C0C   result[03]=0x0111
		ABS_OFFSET=0x10101010   result[04]=0x0010
		ABS_OFFSET=0x14141414   result[05]=0x0010
		ABS_OFFSET=0x18181818   result[06]=0x0010
		ABS_OFFSET=0x1C1C1C1C   result[07]=0x0000
		ABS_OFFSET=0x20202020   result[08]=0x0000
		ABS_OFFSET=0x24242424   result[09]=0x0000
		ABS_OFFSET=0x28282828   result[0A]=0x0000
		ABS_OFFSET=0x2C2C2C2C   result[0B]=0x0000
		ABS_OFFSET=0x30303030   result[0C]=0x0000
		ABS_OFFSET=0x34343434   result[0D]=0x0000
		ABS_OFFSET=0x38383838   result[0E]=0x0000
		ABS_OFFSET=0x3C3C3C3C   result[0F]=0x0000
		ABS_OFFSET=0x40404040   result[10]=0x0000
		ABS_OFFSET=0x44444444   result[11]=0x0000
		ABS_OFFSET=0x48484848   result[12]=0x0000
		ABS_OFFSET=0x4C4C4C4C   result[13]=0x0000
		ABS_OFFSET=0x50505050   result[14]=0x0000
		ABS_OFFSET=0x54545454   result[15]=0x0000
		ABS_OFFSET=0x58585858   result[16]=0x0000
		ABS_OFFSET=0x5C5C5C5C   result[17]=0x0000
		ABS_OFFSET=0x60606060   result[18]=0x0000
		ABS_OFFSET=0x64646464   result[19]=0x0000
		ABS_OFFSET=0x68686868   result[1A]=0x1101
		ABS_OFFSET=0x6C6C6C6C   result[1B]=0x1111
		ABS_OFFSET=0x70707070   result[1C]=0x1111
		ABS_OFFSET=0x74747474   result[1D]=0x1111
		ABS_OFFSET=0x78787878   result[1E]=0x1111
		ABS_OFFSET=0x7C7C7C7C   result[1F]=0x1111
		
		MMDC0 MPWRDLCTL = 0x383A423A
		
		求平均算法：（和Read calibration算法一样）
			求平均算法：
			单个Unit：
				result表示四个bytes,和ABS_OFFSET一一对应。
				例如：ABS_OFFSET=0x10101010   result[04]= 1  0  1  0
									10 10 10 10
				以列为基准，从上往下看：
					1->0的0对应ABS_OFFSET和第一次0->1的0对应的ABS_OFFSET，相加，然后除以2，就得出MPRDDLCTL。
			多个unit：
				看表格内容：
					对应于每一位，分别从上往下找出所有unit最上面的全部为0的一行，然后再找出从下往上最下面全部为0的一行
					最后得出四组数据，每组分为上限和下限。再以单个Unit的算法得出最后平均值
		
	
	最后得出的下面参数应该是所有测试板子的平均值然后修改到uboot对应的寄存器中：   
	   MMDC registers updated from calibration
	
	   Read DQS Gating calibration
	   MPDGCTRL0 PHY0 (0x021b083c) = 0x0340034C
	   MPDGCTRL1 PHY0 (0x021b0840) = 0x033C0330
	
	   Read calibration
	   MPRDDLCTL PHY0 (0x021b0848) = 0x3A2E3030
	
	   Write calibration
	   MPWRDLCTL PHY0 (0x021b0850) = 0x383A423A