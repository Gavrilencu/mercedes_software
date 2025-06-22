import serial
import serial.tools.list_ports
import time
import threading

class OBD2Connection:
    def __init__(self):
        self.serial_connection = None
        self.is_connected = False
        
    def get_available_ports(self):
        """Get list of available COM ports"""
        ports = [port.device for port in serial.tools.list_ports.comports()]
        return ports if ports else []
        
    def test_obd2_communication(self, port, baudrate=38400):
        """Test if OBD2 device is actually connected and responding"""
        try:
            # Try to connect
            test_connection = serial.Serial(port, baudrate, timeout=2)
            time.sleep(1)
            
            # Send ATZ command to reset device
            test_connection.write(b"ATZ\r")
            time.sleep(1)
            
            # Read response
            response = test_connection.readline().decode().strip()
            
            # Send ATE0 to turn off echo
            test_connection.write(b"ATE0\r")
            time.sleep(0.5)
            
            # Send 0100 to test OBD2 communication
            test_connection.write(b"0100\r")
            time.sleep(1)
            
            # Read response
            response = test_connection.readline().decode().strip()
            
            test_connection.close()
            
            # Check if we got a valid OBD2 response
            if "41" in response or "OK" in response or "ELM" in response:
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Test communication error: {e}")
            return False
        
    def connect(self, port, baudrate=38400):
        """Connect to OBD2 device"""
        try:
            # First test if OBD2 device is actually connected
            if not self.test_obd2_communication(port, baudrate):
                print(f"No OBD2 device detected on {port}")
                return False
                
            self.serial_connection = serial.Serial(port, baudrate, timeout=1)
            time.sleep(2)  # Wait for connection
            
            # Initialize OBD2
            self.send_command("ATZ")  # Reset
            time.sleep(1)
            self.send_command("ATE0")  # Echo off
            self.send_command("ATL0")  # Linefeeds off
            
            # Test OBD2 communication
            response = self.send_command("0100")
            if not response or "41" not in response:
                print("OBD2 communication test failed")
                self.disconnect()
                return False
            
            self.is_connected = True
            return True
            
        except Exception as e:
            print(f"Connection error: {e}")
            return False
            
    def disconnect(self):
        """Disconnect from OBD2 device"""
        if self.serial_connection:
            self.serial_connection.close()
        self.is_connected = False
        
    def send_command(self, command):
        """Send command to OBD2 device"""
        if not self.is_connected:
            return None
            
        try:
            self.serial_connection.write(f"{command}\r".encode())
            response = self.serial_connection.readline().decode().strip()
            return response
        except:
            return None
            
    def read_sensor(self, pid):
        """Read specific sensor data"""
        response = self.send_command(pid)
        if response and "41" in response:
            return self.parse_sensor_value(response, pid)
        return None
        
    def parse_sensor_value(self, response, pid):
        """Parse sensor value from OBD2 response"""
        try:
            parts = response.split()
            if len(parts) >= 3:
                data = parts[2]
                
                if pid == "010C":  # RPM
                    a = int(data[:2], 16)
                    b = int(data[2:4], 16)
                    return ((a * 256) + b) / 4
                elif pid == "010D":  # Speed
                    return int(data[:2], 16)
                elif pid == "0105":  # Engine temp
                    return int(data[:2], 16) - 40
                elif pid == "010A":  # Fuel pressure
                    return int(data[:2], 16) * 3
                elif pid == "0111":  # Throttle position
                    return int(data[:2], 16) * 100 / 255
                elif pid == "012F":  # Fuel level
                    return int(data[:2], 16) * 100 / 255
                elif pid == "0142":  # Battery voltage
                    return int(data[:2], 16) / 10
                else:
                    return int(data[:2], 16)
        except:
            return None
            
    def read_error_codes(self):
        """Read diagnostic trouble codes"""
        codes = []
        
        # Read current codes
        response = self.send_command("03")
        if response and "43" in response:
            codes.extend(self.parse_error_codes(response))
            
        # Read pending codes
        response = self.send_command("07")
        if response and "47" in response:
            codes.extend(self.parse_error_codes(response))
            
        return codes
        
    def parse_error_codes(self, response):
        """Parse error codes from OBD2 response"""
        codes = []
        try:
            parts = response.split()
            if len(parts) >= 2:
                data = parts[2]
                for i in range(0, len(data), 4):
                    if i + 3 < len(data):
                        code = data[i:i+4]
                        if code != "0000":
                            codes.append(code)
        except:
            pass
        return codes
        
    def clear_error_codes(self):
        """Clear diagnostic trouble codes"""
        response = self.send_command("04")
        return response and "44" in response
        
    def read_vin(self):
        """Read Vehicle Identification Number"""
        response = self.send_command("0902")
        if response and "49" in response:
            return self.parse_vin(response)
        return None
        
    def parse_vin(self, response):
        """Parse VIN from OBD2 response"""
        try:
            parts = response.split()
            if len(parts) > 2:
                vin_data = "".join(parts[2:])
                vin = ""
                for i in range(0, len(vin_data), 2):
                    if i + 1 < len(vin_data):
                        hex_val = vin_data[i:i+2]
                        try:
                            vin += chr(int(hex_val, 16))
                        except:
                            pass
                return vin[:17]
        except:
            pass
        return None 