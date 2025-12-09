import serial.tools.list_ports

def list_com_ports():
    # Get a list of all available ports
    ports = serial.tools.list_ports.comports()
    usb_ports = []
    
    for port in ports:
        print(port.device)
        # Filter USB ports by checking the description
        if 'USB' in port.description:
            usb_ports.append({
                'device': port.device,
                'name': port.name,
                'description': port.description,
                'hwid': port.hwid
            })
    
    if usb_ports:
        print("USB ports connected:")
        for usb in usb_ports:
            print(f"Device: {usb['device']}, Description: {usb['description']}, HWID: {usb['hwid']}")
    else:
        print("No USB devices found.")

if __name__ == "__main__":
    list_com_ports()
