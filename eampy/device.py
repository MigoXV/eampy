import os
import time
import chardet

import serial
import typer
import json
from typing import List
app = typer.Typer()


@app.command(name="list")
def get_files_cli(
    port: str = typer.Argument(..., help="串口设备的端口"),
    output_dir: str = typer.Argument("workspace", help="本地保存文件的目录"),
    baudrate: int = typer.Argument(115200, help="串口波特率"),
    timeout: int = typer.Argument(1, help="串口读取超时时间", show_default=True),
):
    get_files(port, baudrate, output_dir, timeout)

def parse_string(input_str: str) -> List[str]:
    # 使用 \r\n 分隔符将字符串分割成列表
    parsed_list = input_str.split('\r\n')
    return parsed_list

def parse_file_list_str(input_str: str) -> List[str]:
    
    response_list = parse_string(input_str)
    file_list_str = response_list[2]
    file_list_str = file_list_str.replace("\'", "\"")
    file_list = json.loads(file_list_str)
    return file_list

def get_files(port: str, baudrate: int, output_dir: str, timeout: int = 1):
    """
    从 MicroPython 设备获取文件并保存到本地目录
    """

    # 打开串口
    ser = serial.Serial(port, baudrate, timeout=timeout)

    # 确保串口打开成功
    if not ser.is_open:
        print(f"无法打开串口 {port}")
        return
    # 等待设备启动
    time.sleep(2)
    # 1. 发送 Ctrl+C（中断命令），确保设备中断原有程序并进入 REPL
    ser.write(bytes([3]))  
    time.sleep(1)  
    ser.write(bytes([3]))  
    time.sleep(1)
    # 清空缓冲区，避免之前的串口输出干扰后续命令
    ser.reset_input_buffer()  # 清空输入缓冲区
    # 3. 确保设备已经进入 REPL，发送简单的命令进行确认
    ser.write(b"import os\r\n")
    time.sleep(0.2)
    ser.write(b"os.listdir()\r\n")  # 获取文件列表
    time.sleep(1)
    # 读取文件列表
    response = ser.read_all().decode("utf-8")
    file_list = parse_file_list_str(response)
    print("文件列表:")
    print(file_list)
    # 处理文件列表，获取文件名
    files = file_list
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    # 清空缓冲区，避免之前的串口输出干扰后续命令
    ser.reset_input_buffer()  # 清空输入缓冲区


    # 遍历每个文件，读取并保存到本地
    for file in files:
        if file:  # 确保文件名不为空
            print(f"\n正在读取文件: {file}")

            # 发送命令读取每个文件的内容
            ser.write(f'print(open("{file}").read())\r\n'.encode())
            time.sleep(1)
            # 获取并保存文件内容
            file_content = ser.read_all()
            encoding = chardet.detect(file_content)["encoding"]
            file_content = parse_string(file_content.decode(encoding))[1:-1]
            for index in range(len(file_content)):
                if not file_content[index].endswith("\r"):
                    file_content[index] += "\r"
                    
            # 保存到本地文件
            local_file_path = os.path.join(output_dir, file)
            with open(local_file_path, "w",encoding=encoding) as local_file:
                # local_file.write(file_content)
                local_file.writelines(file_content)

            print(f"文件 {file} 已保存到本地: {local_file_path}")

    # 关闭串口
    ser.close()
    print("所有文件已成功复制！")


# # 使用示例
# get_files(port="/dev/ttyUSB0", baudrate=115200, output_dir="micropython_files")
