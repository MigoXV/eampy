import serial.tools.list_ports
import typer

app = typer.Typer()


@app.command(name="list")
def get_ports():
    # 获取所有可用的串口
    ports = serial.tools.list_ports.comports()

    # 输出可用的串口设备
    if ports:
        print("可用的串口设备:")
        for port in ports:
            print(
                f"设备: {port.device}, 描述: {port.description}, 供应商: {port.manufacturer}"
            )
    else:
        print("没有找到可用的串口设备.")
