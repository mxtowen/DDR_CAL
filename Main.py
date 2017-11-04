from ReadCalData import *

folder_path = r'./logt/' #TODO: change log files folder name

'''
Usage:
1. put all log files text into array
2. call calc_all_values will get the result.
 return (MMDC_MPWLDECTRL0, MMDC_MPWLDECTRL1, MPDGCTRL0, MPDGCTRL1, MPRDDLCTL, MPWRDLCTL)
3. print_result can show the result
'''
def get_actual():
        file_texts = []
        for f in os.listdir(folder_path ):
            try:
                fp = folder_path + f                
                if check_file(fp):
                    text = get_file_context(fp)
                    file_texts.append(text)
                else:
                    print 'Check ',f,' Failed!'
            except:
                print ' can\'t open',f
                continue
        result = calc_all_values(file_texts)
        print_result(result)
get_actual()

