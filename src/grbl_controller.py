import serial
import time

class GRBLController:
    def __init__(self, port, baudrate):
        self.ser = None
        self.port = port
        self.baudrate = baudrate
        self.is_jogging = False

    def connect(self):
        try:
            self.ser = serial.Serial(self.port, self.baudrate)
            time.sleep(2)
            self.ser.write(b"\r\n\r\n")
            time.sleep(2)
            self.ser.flushInput()
            return True
        except Exception as e:
            print(f"Error connecting to GRBL: {e}")
            return False

    def send_command(self, command):
        try:
            command += '\n'
            self.ser.write(command.encode())
            grbl_response = self.ser.readline().strip()
            return grbl_response.decode()
        except Exception as e:
            print(f"Error sending command: {e}")
            return ""

    def jog(self, x, y, z, feedrate):
        command = f"$J=G91 G21 X{x} Y{y} Z{z} F{feedrate}"
        return self.send_command(command)

    def get_status(self):
        self.ser.write(b"?\n")
        status = self.ser.readline().strip()
        return status.decode()

    def reset_zero(self):
        command = "G10 P0 L20 X0 Y0 Z0"
        return self.send_command(command)
