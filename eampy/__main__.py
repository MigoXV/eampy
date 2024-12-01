import typer

from eampy import com, device

app = typer.Typer()

app.add_typer(com.app, name="com")
app.add_typer(device.app, name="device")


def main():
    app()
    
if __name__ == "__main__":
    main()
