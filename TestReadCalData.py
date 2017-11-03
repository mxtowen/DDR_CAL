from ReadCalData import *

import unittest
folder_path_parent = r'./'
folder_path = r'./unittest/'

#check input file.
class CheckInputFileTestCase(unittest.TestCase):

    def testCorrectFile(self):
        self.failUnless(check_file(folder_path + '1.log'),'Correct file but check failed!')
    
    def testFileNotExist(self):
        self.failIf(check_file(folder_path + 'not_exist.log'),'File Not exist should return false!')   
    
    def testEmptyFile(self):
        self.failIf(check_file(folder_path + 'empty.log'),'Empty file should return false')

    def testCtrlError(self):
        self.failIf(check_file(folder_path + 'ctrl_error.log'),'Ctrl field error should return false')
    
    def testByteError(self):
        self.failIf(check_file(folder_path + 'byte_error.log'),'Byte field error should return false')

    def testReadCalError(self):
        self.failIf(check_file(folder_path + 'read_cal_error.log'),'Read Cal field error should return false')
    
    def testReadCalDataError(self):
        self.failIf(check_file(folder_path + 'read_cal_data_error.log'),'Read Cal field error should return false')

    def testWriteCalError(self):
        self.failIf(check_file(folder_path + 'write_cal_error.log'),'Write Cal field error should return false')
    
    def testWriteCalDataError(self):
        self.failIf(check_file(folder_path + 'write_cal_data_error.log'),'Write Cal field error should return false')

#fill field
class CheckReadDataTestCase(unittest.TestCase):
    def testReadCtrlData(self):
        txt = get_file_context(folder_path + '1.log')
        ctrl = get_MMDC_MPWLDECTRL(txt)

        self.assertEquals(ctrl,('0x00000004','0x00150011'))
        
        byte = get_Byte(txt)
        self.assertEquals(byte[0][0],hc_abs_value('0x02','0x10')) #start
        self.assertEquals(byte[0][1],hc_abs_value('0x04','0x38')) #end

        self.assertEquals(byte[1][0],hc_abs_value('0x02','0x08'))
        self.assertEquals(byte[1][1],hc_abs_value('0x04','0x2C'))

        self.assertEquals(byte[2][0],hc_abs_value('0x02','0x08'))
        self.assertEquals(byte[2][1],hc_abs_value('0x04','0x2C'))

        self.assertEquals(byte[3][0],hc_abs_value('0x01','0x68'))
        self.assertEquals(byte[3][1],hc_abs_value('0x04','0x34'))

        read_cat = get_ReadCal(txt)
        for i in range(0,3):
            self.assertEqual(read_cat[i],'0x1111')
        self.assertEqual(read_cat[3],'0x1011')
        self.assertEqual(read_cat[4],'0x1001')
        self.assertEqual(read_cat[5],'0x1001')
        for i in range(6,0x18):
            self.assertEqual(read_cat[i],'0x0000')
        self.assertEqual(read_cat[0x18],'0x0110')
        self.assertEqual(read_cat[0x19],'0x0111')
        self.assertEqual(read_cat[0x1A],'0x0111')
        for i in range(0x1B,0x20):
            self.assertEqual(read_cat[i],'0x1111')

        #write cal
        write_cat = get_WriteCal(txt)
        for i in range(0,4):
            self.assertEqual(write_cat[i],'0x1111')
        self.assertEqual(write_cat[4],'0x0010')
        self.assertEqual(write_cat[5],'0x0010')
        for i in range(6,0x1A):
            self.assertEqual(write_cat[i],'0x0000')
        self.assertEqual(write_cat[0x1A],'0x0100')
        self.assertEqual(write_cat[0x1B],'0x1100')
        self.assertEqual(write_cat[0x1C],'0x1110')
        for i in range(0x1D,0x20):
            self.assertEqual(write_cat[i],'0x1111')

#single calculation
class CalcSingleResult(unittest.TestCase):
    def setUp(self):
        self.txt = get_file_context(folder_path + '1.log')

    def testCalcByte(self):
        byte = get_Byte(self.txt)
        self.assertEquals(hc_abs_value('0x03','0x38'),calc_hc_abs_final(byte[0]))
        self.assertEquals(hc_abs_value('0x03','0x2C'),calc_hc_abs_final(byte[1]))
        self.assertEquals(hc_abs_value('0x03','0x2C'),calc_hc_abs_final(byte[2]))
        self.assertEquals(hc_abs_value('0x03','0x34'),calc_hc_abs_final(byte[3]))

    def testQDSResult(self):
        byte = get_Byte(self.txt)
        self.assertEquals(('0x032C0338','0x0334032C'),calc_DQS_cal(byte))
    
    def testFindStartEnd(self):
        read_cat = get_ReadCal(self.txt)
        self.assertEquals((0x18,0x60),calc_cal_start_end(read_cat,0))
        self.assertEquals((0x10,0x5C),calc_cal_start_end(read_cat,1))
        self.assertEquals((0x0C,0x5C),calc_cal_start_end(read_cat,2))
        self.assertEquals((0x18,0x68),calc_cal_start_end(read_cat,3))

        write_cat = get_WriteCal(self.txt)
        self.assertEquals((0x10,0x70),calc_cal_start_end(write_cat,0))
        self.assertEquals((0x18,0x6C),calc_cal_start_end(write_cat,1))
        self.assertEquals((0x10,0x64),calc_cal_start_end(write_cat,2))
        self.assertEquals((0x10,0x68),calc_cal_start_end(write_cat,3))

    def testGetCalValue(self):
        read_cat = get_ReadCal(self.txt)
        self.assertEqual('0x4034363C',calc_cal_values([read_cat]))

        write_cat = get_WriteCal(self.txt)
        self.assertEqual('0x3C3A4240',calc_cal_values([write_cat]))


class Calc2SampleResult(unittest.TestCase):
    def setUp(self):
        self.data_txt_1 = get_file_context(folder_path + '1.log')
        self.data_txt_2 = get_file_context(folder_path + '2.log')

    def testMPWLDE(self):
        file1_ctrl = get_MMDC_MPWLDECTRL(self.data_txt_1)
        file2_ctrl = get_MMDC_MPWLDECTRL(self.data_txt_2)
        ctrl_list = [file1_ctrl,file2_ctrl]
        self.assertEquals(('0x00020007','0x00170010'),calc_MPWLDECTRL(ctrl_list))

    def testCalcByte(self):
        file1_byte = get_Byte(self.data_txt_1)
        file2_byte = get_Byte(self.data_txt_2)
        bytes = [file1_byte,file2_byte]
        self.assertEqual(('0x032C0338','0x0330032C'),calc_DQS_cals(bytes))

    def testCalcCalValue(self):
        file1_read_cal = get_ReadCal(self.data_txt_1)
        file2_read_cal = get_ReadCal(self.data_txt_2)
        cals = [file1_read_cal,file2_read_cal]
        self.assertEqual('0x40323638',calc_cal_values(cals))

        file1_write_cal = get_WriteCal(self.data_txt_1)
        file2_write_cal = get_WriteCal(self.data_txt_2)
        cals = [file1_write_cal,file2_write_cal]
        self.assertEqual('0x383A4440',calc_cal_values(cals))

class CalcMutiResult(unittest.TestCase):
    def setUp(self):
        self.data_txt_1 = get_file_context(folder_path_parent + "log/ddr_calibration_20160427-10'8'3_Radio1_tmp85_1.log")
        self.data_txt_2 = get_file_context(folder_path_parent + "log/ddr_calibration_20160427-11'46'37_Radio3_tmp85_1.log")
        self.data_txt_3 = get_file_context(folder_path_parent + "log/ddr_calibration_20160427-11'49'53_Radio3_tmp85_2.log")

    def test3Samples(self):
        file_text = [self.data_txt_1,self.data_txt_2,self.data_txt_3]
        self.assertEqual(['0x00020008','0x0018000F','0x032C0338','0x0330032C','0x40323638','0x383A4440'],calc_all_values(file_text))

    def testActual(self):
        file_texts = []
        for f in os.listdir(folder_path_parent + "log/"):
            try:
                text = get_file_context(folder_path_parent + "log/" + f)
                file_texts.append(text)
            except:
                print f,' can\'t open'
                continue
        result = calc_all_values(file_texts)
        print_result(result)

try:
    unittest.main()
except:
    pass

