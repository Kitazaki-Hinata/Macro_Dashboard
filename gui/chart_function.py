'''从数据库中读取数据并以图标的方式展示'''

import pyqtgraph as pg

class ChartFunction():
    def __init__(self, main_window):
        self.main_window = main_window

    def show_one_chart(self, data_json):
        '''单图表框，在用户使用小窗口选择数据并点击确认后
        先调用选项储存到json，然后调用此函数读取json文件设置并画图'''
        pass