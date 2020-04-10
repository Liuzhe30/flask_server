import os
import shutil
from Bio import SeqIO
from sklearn.externals import joblib

from FormatData import Format
from GetFea import Get_Fea_Pssm        
from GetFea import Get_Fea_PCP
from GetFea import Get_Fea_SeqSeg
from GetFea import Build_Fea_Space
from RASA_processing import Process
from Capsule_pred import Capsule
import TMZC_pre_process as zprocess
import TMZC_model as zmodel
import RASA2 as rasa2
import DMCTOP_pre_process as dprocess
import DMCTOP as dmodel
        
class Predict:
    def get_result_tmp_ssurface(self,required_fasta):
        
        process = Process()
        test_data = process.test_data_pre_processing(required_fasta)
        if(test_data == "Error!"):
            return "Error!"
        try:
            capsule = Capsule()
            result = capsule.capsule_prediction(test_data)
            return result
        except TypeError:
            pass
        
    def get_result_tmp_ssurface2(self,required_fasta,zpred):
        
        process = Process()
        #print(zpred)
        test_data = process.data_pre_processing(zpred, required_fasta, '/home/public/', 19)
        if(test_data == "Error!"):
            return "Error!"
        try:
            result = rasa2.run_LSTM(test_data)
            return result
        except TypeError:
            pass    
        
    def get_result_mpls_pred(self,required_fasta):
        
        tmp_path_fasta = '/home/public/tmp/fasta'  # put temp mediam data in this path
        tmp_path_pssm = '/home/public/tmp/pssm'
        tmp_path_fea = '/home/public/tmp/fea'
        path_pcp = '/home/public/PCP-15.pic'
        path_onehot = '/home/public/onehot.pic'
        # blast_bin = '/home/ThirdPartTools/blast/bin/psiblast'
        # blast_db = '/home/ThirdPartTools/blast/db/swissprot'
        blast_bin = 'psiblast'
        blast_db = '/blast/db/swissprot'
        model_uni = '/home/public/model_uni.m'
        output_file = 'result.txt'
        
        win = 3
        
        format = Format()
        pssm = Get_Fea_Pssm()
        pcp = Get_Fea_PCP()
        seqseg = Get_Fea_SeqSeg()
        build = Build_Fea_Space()
        
        required_dic,index_dic = format.split_fasta(required_fasta,tmp_path_fasta)
        
        
        # output features into pickle file
        for index in required_dic:
            pssm.run_blast(index,tmp_path_fasta,tmp_path_pssm,blast_bin,blast_db)
        pssm.get_pssm(required_dic,tmp_path_pssm,tmp_path_fea)       
        pcp.get_pcp(required_dic,path_pcp,tmp_path_fea)
        seqseg.get_seqseg(required_dic,path_onehot,tmp_path_fea)
        
        clf = joblib.load(model_uni)
        
        result_dic = {}
        # build feature space
        for index in required_dic:
            fea_test = build.fea_space(index,required_dic,tmp_path_fea,win)
        
            # predict
            label_pred = list(clf.predict(fea_test))
            result = ''
            for i in range(0,len(label_pred)):
                result = result+str(label_pred[i])
            result_dic[str(index)]=result
        shutil.rmtree('/home/public/tmp')
        return result_dic,index_dic,required_dic

    def get_result_dmctop(self,required_fasta):
        
        id_name = required_fasta.split('/')[-1].split('.')[0]
        dprocess.getpssm(id_name, required_fasta)
        dmodel.main(id_name)
    
    def get_result_TMZC(self,required_fasta):
        
        test_data = zprocess.data_pre_processing(required_fasta)
        if(test_data == "Error!"):
            return "Error!"
        try:
            result = zmodel.cnn_predict(test_data)
            return result
        except TypeError:
            pass
        
class Outputs():
    
    def output_result_tmp_ssurface(self, data_fasta, y_pred, output_file):
        f_out = open(output_file,'a+')
        f_out.write('<br>\r\nThank you for using TMP-SSurface<br>\r\n<br>\r\n')
        f = open("/home/public/predict.txt")
        fasta = open(data_fasta)
        line = f.readline()
        fa = fasta.readline()
        while fa:
            if(fa[0] == '>'):
                f_out.write("<br><br>ID: " + str(fa[1:]) + "<br>\r\n")
                fa = fasta.readline()
            if(fa[0] == '\n'):
                fa = fasta.readline()
            for i in fa:
                if(i != "\n"):
                    f_out.write(str(i) + " ")
                    f_out.write(str(format(float(line),'0.2f')) + "<br>\r\n")
                    line = f.readline()
            fa = fasta.readline()
        
    def print_result_tmp_ssurface(self, data_fasta, y_pred, output_file):
        f_out = open(output_file,'a+')
        f = open("/home/public/predict.txt")
        fasta = open(data_fasta)
        line = f.readline()
        fa = fasta.readline()
        while fa:
            if(fa[0] == '>'):
                f_out.write("ID: " + str(fa[1:]) + "\r\n\n")
                fa = fasta.readline()
            if(fa[0] == '\n'):
                fa = fasta.readline()
            for i in fa:
                if(i != "\n"):
                    f_out.write(str(i) + " ")
                    f_out.write(str(format(float(line),'0.2f')) + "\r\n\n")
                    line = f.readline()
            fa = fasta.readline()
            
    def output_result_mpls_pred(self,required_dic,index_dic,result_dic,output_file):
        f_out = open(output_file,'a')
        f_out.write('\nThank you for using MPLs_Pred\n\n')
        for index in index_dic:
            ID = index_dic[index]
            seq = required_dic[index]
            result = result_dic[index]
            print(ID)
            f_out.write('\nResults of your ubmited protein: '+ID+'\n')
            f_out.write('predicted binding position: ')
            for i in range (0,len(result)):
                if result[i] == '1' or result[i] == 1:
                    f_out.write(str(i+1)+'   ')
                    print(i+1)
            f_out.write('\nSequence:\n'+str(seq)+'\nResult:\n'+str(result))
            
    def output_result_dmctop(self, data_fasta, output_file):
        f_out = open(output_file,'a+')
        f_out.write('<br>\r\nThank you for using DMCTOP<br>\r\n<br>\r\n')
        
        fasta = open(data_fasta, 'r')
        line = fasta.readline()
        f_out.write(line + '<br>\r\n')  
        line = fasta.readline()
        f_out.write(line + '<br>\r\n')  
        f_out.write('Results:<br>\r\n')  
        topo = open('/home/public/DMCTOP_result.topo', 'r')
        line = topo.readline()
        f_out.write(line + '<br>\r\n')  
        
    def print_result_dmctop(self, data_fasta, output_file):
        f_out = open(output_file,'a+')
        f = open('/home/public/DMCTOP_result.topo', 'r')
        fasta = open(data_fasta)
        line = f.readline()
        fa = fasta.readline()
        f_out.write("ID: " + str(fa[1:]) + "\r\n\n")
        fa = fasta.readline()
        f_out.write(fa + "\r\n\n")
        f_out.write('Results:' + "\n")
        f_out.write(line + "\r\n\n")
        
    
    def output_result_TMZC(self, data_fasta, y_pred, output_file):
        f_out = open(output_file,'a+')
        f_out.write('<br>\r\nThank you for using TM-ZC!<br>\r\n')
        f = open("/home/public/TM-ZC_predict.txt")
        fasta = open(data_fasta)
        line = f.readline()
        fa = fasta.readline()
        while fa:
            if(fa[0] == '>'):
                f_out.write("<br><br>ID: " + str(fa[1:]) + "<br>\r\n")
                fa = fasta.readline()
            if(fa[0] == '\n'):
                fa = fasta.readline()
            for i in fa:
                if(i != "\n"):
                    f_out.write(str(i) + " ")
                    f_out.write(str(format(float(line),'0.2f')) + "<br>\r\n")
                    line = f.readline()
            fa = fasta.readline()
        
    def print_result_TMZC(self, data_fasta, y_pred, output_file):
        f_out = open(output_file,'a+')
        f = open("/home/public/TM-ZC_predict.txt")
        fasta = open(data_fasta)
        line = f.readline()
        fa = fasta.readline()
        while fa:
            if(fa[0] == '>'):
                f_out.write("ID: " + str(fa[1:]) + "\r\n\n")
                fa = fasta.readline()
            if(fa[0] == '\n'):
                fa = fasta.readline()
            for i in fa:
                if(i != "\n"):
                    f_out.write(str(i) + " ")
                    f_out.write(str(format(float(line),'0.2f')) + "\r\n\n")
                    line = f.readline()
            fa = fasta.readline()
            
    def output_result_tmp_ssurface_2(self, data_fasta, y_pred, output_file):
        f_out = open(output_file,'a+')
        f_out.write('<br>\r\nThank you for using TMP-SSurface 2.0<br>\r\n<br>\r\n')
        f = open("/home/public/rasa2_predict.txt")
        fasta = open(data_fasta)
        line = f.readline()
        fa = fasta.readline()
        while fa:
            if(fa[0] == '>'):
                f_out.write("<br><br>ID: " + str(fa[1:]) + "<br>\r\n")
                fa = fasta.readline()
            if(fa[0] == '\n'):
                fa = fasta.readline()
            for i in fa:
                if(i != "\n"):
                    f_out.write(str(i) + " ")
                    f_out.write(str(format(float(line),'0.2f')) + "<br>\r\n")
                    line = f.readline()
            fa = fasta.readline()
        
    def print_result_tmp_ssurface_2(self, data_fasta, y_pred, output_file):
        f_out = open(output_file, 'a+')
        f = open("/home/public/rasa2_predict.txt")
        fasta = open(data_fasta)
        line = f.readline()
        fa = fasta.readline()
        while fa:
            if(fa[0] == '>'):
                f_out.write("ID: " + str(fa[1:]) + "\r\n\n")
                fa = fasta.readline()
            if(fa[0] == '\n'):
                fa = fasta.readline()
            for i in fa:
                if(i != "\n"):
                    f_out.write(str(i) + " ")
                    f_out.write(str(format(float(line),'0.2f')) + "\r\n\n")
                    line = f.readline()
            fa = fasta.readline()
            
if __name__ == '__main__':
    required_fasta = './required.fasta' # Read from text
    output_file = './result.txt'
    
    pre = Predict()
    result_dic,index_dic,required_dic = pre.get_result(required_fasta)
    out = Output()
    out.output_result(required_dic, index_dic, result_dic, output_file)