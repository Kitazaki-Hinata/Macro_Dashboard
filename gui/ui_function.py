'''
这里包括所有ui的控件槽函数
动画等函数在gui_animation文件中
'''

import os
import logging


class UiFunctions():  # 删除:mainWindow
    def __init__(self, main_window):
        self.main_window = main_window
    def settings_api_save(self):
        # find whether exist .env file
        print("save")
        path = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(path, "..", ".env")

        # get api_text from line edit
        bea_api = self.main_window.bea_api.text()
        fred_api = self.main_window.fred_api.text()
        bls_api = self.main_window.bls_api.text()

        try:
            # 创建 .env 文件
            with open(path, 'w', encoding='utf-8') as f:
                # 写入基本的环境变量模板
                f.write(f'bea = "{bea_api}" \n')
                f.write(f'fred = "{fred_api}" \n')
                f.write(f'bls = "{bls_api}" ')
            self.main_window.status_label.setText("API key saved successfully")
            self.main_window.status_label.setStyleSheet("color: #90b6e7")
            logging.info(f".env file created successfully at path: {path}")

        except Exception as e:
            self.main_window.status_label.setText("FAILED to save API key, see log file")
            self.main_window.status_label.setStyleSheet("color: #fa88aa")
            logging.error(f"Failed to create .env file at path: {path}, since {e}")

