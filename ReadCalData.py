import re
import os

class ReadFieldErrorException(Exception): pass

def get_text(text, start, end):
    #print 'start:',start,'*** end:',end
    ret = re.findall('('+start+'(.*\s*)*?)'+end, text)
    if ret:
        return ret[0][0]
    else:
        raise ReadFieldErrorException

def text_find(pat, text):
    ret = re.findall(pat, text)
    if ret:
        return ret[0]
    else:
        raise ReadFieldErrorException

def get_Cal(text):
    ret = []
    for i in range(0x20):
        s = 'result\[' + '%02X'%i + '\]=(0x[0-9A-F]*)'
        v = text_find(s, text)
        ret.append(v)
    return ret

def get_ReadCal(text):
    read_cal_text = get_text(text, 'Starting Read calibration', 'Byte 0')
    return get_Cal(read_cal_text)

def get_WriteCal(text):
    write_cal_text = get_text(text, 'Starting Write calibration', 'Byte 0')
    return get_Cal(write_cal_text)


'''
Document for DQS:
The "start" and "end" show the start value and end value of DQS gating "window". Mean is
the middle point of the window. The suggested DQS gating value is calculated base on the
formula max[mean(start,end),end-0.5*tCK].

*******Important*******
On the result, HC means 0.5 cycle, ABS represents 1/256 of a cycle. For example, HC=0x01
ABS=0x58 means that the delay is 0.5 + 88/256 cycle.

'''

def hc_abs_value(hc, abs):
    hc_v = int(hc, 16)
    abs_v = int(abs, 16)
    return (hc_v << 8) + abs_v

def hc_string(v):
    return "0x%02X"%(v>>8)

def abs_string(v):
    return "0x%02X"%(v&0x7F)

def two_hc_abs_string(f, s):
    #f_v = ((f>>7)<<8)
    #f_v += f&0x7F
    #s_v = ((s>>7)<<8)
    #s_v += s&0x7F
    #return "0x%08X"%((f_v<<16) + s_v)
    #change here lala
    return "0x%08X"%((f << 16) + s)

def get_Byte(text):
    ret = []
    byte_text = [get_text(text, 'BYTE '+str(i), 'BYTE') for i in range(3)]
    byte_text.append(get_text(text, 'BYTE 3', 'DQS calibration'))
    for i in range(4):
        start_hc, start_abs = text_find('Start:\s*HC=(0x[0-9A-F]*) ABS=(0x[0-9A-F]*)', byte_text[i])       
        end_hc, end_abs = text_find('End:\s*HC=(0x[0-9A-F]*) ABS=(0x[0-9A-F]*)', byte_text[i])        
        ret.append([hc_abs_value(start_hc, start_abs), hc_abs_value(end_hc, end_abs)])
    return ret

def get_MMDC_MPWLDECTRL(text):
    return text_find('MMDC_MPWLDECTRL0.*?= (0x[0-9A-F]*)', text), text_find('MMDC_MPWLDECTRL1.*?= (0x[0-9A-F]*)', text)

def get_file_context(file_path):
    f = open(file_path)
    return f.read().replace('\r\n', '\n')

def check_file(file_path):
    try:
        t = get_file_context(file_path)
        ctrl = get_MMDC_MPWLDECTRL(t)
        byte = get_Byte(t)
        read_cat = get_ReadCal(t)
        write_cat = get_WriteCal(t)
        return True
    except:
        return False

def calc_hc_abs_final(byte):
    mean = (byte[0] + byte[1]) / 2
    end_half = byte[1] - (1<<8)
    final = max(mean, end_half)
    #print 'Mean: HC=',hc_string(mean),' ABS=',abs_string(mean)
    #print 'end_half: HC=',hc_string(end_half),' ABS=',abs_string(end_half)
    #print 'final: HC=',hc_string(final),' ABS=',abs_string(final)
    return final

def calc_DQS_cal(byte):
    b = []
    for i in range(4):
        #print 'Byte',i,'\nStart: HC=',hc_string(byte[i][0]),' ABS=',abs_string(byte[i][0])
        #print 'End: HC=',hc_string(byte[i][1]),' ABS=',abs_string(byte[i][1])
        b.append(calc_hc_abs_final(byte[i]))
        print "0x%x"%b[i]
    MPDG_ctrl0 = two_hc_abs_string(b[1], b[0])
    MPDG_ctrl1 = two_hc_abs_string(b[3], b[2])
    return MPDG_ctrl0, MPDG_ctrl1

def calc_DQS_cals(bytes):
    new_byte = []
    #find max start and min end for each byte
    for i in range(4):
        start_arr = []; end_arr = []
        for byte in bytes:
            start_arr.append(byte[i][0])
            end_arr.append(byte[i][1])
        start_v = max(start_arr)
        end_v = min(end_arr)
        #print 'Byte',i,'\nStart: HC=',hc_string(start_v),' ABS=',abs_string(start_v)
        #print 'End: HC=',hc_string(end_v),' ABS=',abs_string(end_v)
        new_byte.append([start_v,end_v])
    return calc_DQS_cal(new_byte)
 
def calc_cal_start_end(cal_arr,index):
    s=0; e=0
    last_value = '1'
    for i in range(len(cal_arr)):
        current_value = cal_arr[i][-(index+1)]
        if '0' == current_value and last_value == '1':
            s = i
        if '1' == current_value and last_value == '0':
            e = i-1
        last_value = current_value
    return s*4, e*4

def calc_cal_values(cals_arr):
    ret = 0
    for i in range(4):
        start_arr = []; end_arr =[]
        for cal in cals_arr:
            start, end = calc_cal_start_end(cal, i)
            start_arr.append(start)
            end_arr.append(end)
        #find min start and max end
        mid = (min(start_arr) + max(end_arr))/2
        ret += (mid << (8 * i))
    return "0x%08X"%ret

def avg_per2bytes(list):
    ret = 0
    list_v = [0,0,0,0]
    for whole_value in list:
        for i in range(4):
            list_v[i] += (whole_value >> (8*i)) & 0xFF
    for i in range(4):
        list_v[i] = list_v[i] / len(list)
        ret +=  list_v[i] << (i*8)
    return ret


def calc_MPWLDECTRL(ctrl_list):
    ctrl0 = [];ctrl1 = []
    for c in ctrl_list:
        ctrl0.append(int(c[0],16))
        ctrl1.append(int(c[1],16))
    str_ctrl0 = "0x%08X"%avg_per2bytes(ctrl0)
    str_ctrl1 = "0x%08X"%avg_per2bytes(ctrl1)
    return str_ctrl0,str_ctrl1


def calc_all_values(file_texts):
    ret = []
    ctrl_list = []
    byte_list = []
    read_cal_list = []
    write_cal_list = []
    for file_text in file_texts:
        ctrl_list.append(get_MMDC_MPWLDECTRL(file_text))
        byte_list.append(get_Byte(file_text))
        read_cal_list.append(get_ReadCal(file_text))
        write_cal_list.append(get_WriteCal(file_text))
    ret.extend(calc_MPWLDECTRL(ctrl_list))
    ret.extend(calc_DQS_cals(byte_list))
    ret.append(calc_cal_values(read_cal_list))
    ret.append(calc_cal_values(write_cal_list))
    return ret

def print_result(result):
    print 'Calibration result:'
    print 'MMDC_MPWLDECTRL0 (080c) = ',result[0]
    print 'MMDC_MPWLDECTRL1 (0810) = ',result[1]
    print 'DQS calibration MMDC0 MPDGCTRL0 = ',result[2],', MPDGCTRL1 = ',result[3]
    print 'Read calibration, MMDC0 MPRDDLCTL = ',result[4]
    print 'Write calibration, MMDC0 MPWRDLCTL = ',result[5]