#-*- encoding:utf-8 -*-
import sys
import os
reload(sys)
sys.setdefaultencoding("utf8")
import shutil
import time
from ScrolledText import ScrolledText
#FTP相关

from ftplib import FTP
from Tkinter import *
import tkMessageBox
import pyperclip



def get_screen_size(window):
    return window.winfo_screenwidth(),window.winfo_screenheight()

def get_window_size(window):
    return window.winfo_reqwidth(),window.winfo_reqheight()

#设置窗口居中显示
def center_window(root,width,height):
    screenwidth = root.winfo_screenwidth()
    screenheight = root.winfo_screenheight()
    size = '%dx%d+%d+%d' % (width, height, (screenwidth - width)/2, (screenheight - height-200)/2)
    root.geometry(size)

class Window:
    def __init__(self):

        #创建容器，设置标题
        self.tk = Tk()
        self.tk.title(u"拉取mn文件")
        center_window(self.tk,600,400)

        #设置单选按钮radio，分别对应e_mn,eapi_mn,eapi_report_mn
        self.radVal = IntVar()
        self.rad1 = Radiobutton(self.tk, value = 1, variable = self.radVal, text = "eapi_mn")
        self.rad1.grid(column = 0,row = 0)
        self.rad2 = Radiobutton(self.tk, value = 2, variable = self.radVal, text = "e_mn")
        self.rad2.grid(column = 1,row = 0)
        self.rad3 = Radiobutton(self.tk, value = 3 , variable = self.radVal, text = "eapireport_mn")
        self.rad3.grid(column = 2,row = 0)
        self.rad1.select()

        #设置路径label
        self.flabel = Label(self.tk,text = "路径:")
        self.flabel.grid(column = 0,row = 1)

        #设置文件路径输入框
        self.filepath = StringVar()
        self.fpath = Entry(self.tk, textvariable=self.filepath, width = 55)
        self.fpath.grid(column = 1 , row = 1 , columns = 2)
        self.fpath.focus()

        #设置一下个清空的btn
        self.clearbtn = Button(self.tk,text = "清空",command = self.clickclearbtn,width = 5,height =1)
        self.clearbtn.grid(column = 3,row = 1)


        #设置是否带平铺radio
        self.radVal_pp = IntVar()
        self.rad1_pp = Radiobutton(self.tk, value = 1, variable = self.radVal_pp, text = "带平铺文件")
        self.rad1_pp.grid(column = 0,row = 2)
        self.rad2_pp = Radiobutton(self.tk, value = 2, variable = self.radVal_pp, text = "不带平铺文件")
        self.rad2_pp.grid(column = 1,row = 2)
        self.rad2_pp.select()

        #设置按钮
        self.btn1= Button(self.tk,text = "执行",command = self.clickbtn1,width = 10)
        self.btn1.grid(column = 1,row = 3, columns = 1)


        #设置路径，输入
        # self.label_Val = StringVar()
        # #justify多行文本对齐，left、right、center
        # self.readmelabel = Label(self.tk,textvariable = self.label_Val,justify = LEFT)
        # self.readmelabel.grid(column = 0,row = 4,columns = 4,sticky = W)

        #用text来展示运行结果，新增及修改的文件
        self.showtext = Text(self.tk,borderwidth=0,height = 15)
        self.showtext.grid(column = 0,row = 4,columns=4,sticky=W)

        #设置yscrollbar
        self.y_scroll = Scrollbar(self.tk)
        self.y_scroll.grid(row=4,column=4,sticky='ns')
        self.y_scroll.configure(command = self.showtext.yview)
        self.showtext.configure(yscrollcommand=self.y_scroll.set)

        #设置xscrollbar
        self.x_scroll = Scrollbar(self.tk,orient='horizontal')
        self.x_scroll.grid(row=5,column=0,columns=4,sticky='we')
        self.x_scroll.configure(command = self.showtext.xview)
        self.showtext.configure(xscrollcommand = self.x_scroll.set)

        #加一个一键复制对比结果按钮
        self.btnall = Button(self.tk,text = "一键复制对比结果",command = self.clickbtnall,width = 15)
        self.btnall.grid(column = 1,row = 6, columns = 1)

        #绘制
        self.tk.mainloop()

    #清空filepath
    def clickclearbtn(self):
        self.filepath.set('')

    #点击执行
    def clickbtn1(self):

        self.showtext.delete(0.0,END)

        type = int(self.radVal.get())
        filepath = self.filepath.get()

        val_radio_pp = int(self.radVal_pp.get())

        if not filepath:
            tkMessageBox.showinfo(title = '错误',message='路径不能为空噢')
            return False
        if type not in (1,2,3):
            tkMessageBox.showinfo(title = '错误',message='请选择拉取哪个路径')
            return False

        self.getfiles(type,filepath,val_radio_pp)


    #点击一键复制
    def clickbtnall(self):
        textvalue = self.showtext.get(0.0,END)
        pyperclip.copy(textvalue)
        return pyperclip.copy(textvalue)



    def getfiles(self,type,path,val_radio_pp):
        filelog = ''
        ftp = FTP()
        ftp.set_debuglevel(0)
        ftp.connect('10.2.20.153',10086)
        ftype = ''
        if type == 1:
            ftp.login('eapi_mn','hxsd_eapimn')
            ftype = 'eapi_mn'
        elif type == 2:
            ftp.login('e_mn','hxsd_emn')
            ftype = 'e_mn'
        elif type == 3:
            ftype = 'report_mn'
            ftp.login('report_mn','hxsd_reportmn')
        else:
            print u"输入了错误的数据,请选择要拉取的环境"
            return False

        new_files = []

        pathmain = path + '/'
        pathpar = os.path.abspath(os.path.join(pathmain,os.pardir))
        path_mn = pathpar + '/old_' + ftype + '/'

        # 判断有没有old_mn文件夹，如果有的话则删除
        if os.path.exists(path_mn):
            shutil.rmtree(path_mn)

        # 得到输入路径下所有的文件（只文件，不包括路径）
        for root,dirs,files in os.walk(pathmain):
            root = root.split(pathmain)[1]
            for file in files:
                new_files.append(os.path.join(root,file).replace('\\','/'))

        new_file_list = []
        #开始循环，如果mn机器上文件存在，则在本地新建一个本文件，如果没有，则跳过，抛出异常
        for i in new_files:
            path,filename = os.path.split(i)
            path = os.path.abspath(os.path.join(path_mn,path))

            if os.path.exists(path):
                pass
            else:
                os.makedirs(path)
            file_handle = open(path+'/'+filename,'wb')
            file_write = file_handle.write

            try:
                ftp.retrbinary("RETR %s" % i,file_write,1024)

            except Exception,e:
                new_file_list.append(i)
                file_handle.close()
                hehehehe = u''+str(os.path.abspath(os.path.join(path,filename)))
                os.remove(hehehehe)

            #如果带平铺文件的话，则进行下面的操作
            if val_radio_pp == 1:
                file_handle_pingpu = open(pathpar + '/' + filename,'wb')
                file_write_pingpu = file_handle_pingpu.write
                try:
                    ftp.retrbinary("RETR %s" % i,file_write_pingpu,1024)
                except Exception,e:
                    file_handle_pingpu.close()
                    hohohoho = u''+str(os.path.abspath(os.path.join(pathpar,filename)))
                    os.remove(hohohoho)

        modify_file_list = new_files
        new_file_string = '新增文件:\n'
        for i in new_file_list:
            new_file_string += '/'+str(i)+'\n'
            modify_file_list.remove(i)

        modify_file_string = '修改文件:\n'
        for m in modify_file_list:
            modify_file_string += '/'+str(m)+'\n'



        # self.label_Val.set(new_file_string + modify_file_string)
        self.showtext.insert(1.0,new_file_string + modify_file_string)


        ftp.set_debuglevel(0)

        ftp.close()
        tkMessageBox.showinfo(title='信息',message='执行完成！')

if __name__ == '__main__':

    w = Window()

