import subprocess

#Base addresses of GPIO ports
GPIOA_BASE_ADDRESS = 0x48000000
GPIOB_BASE_ADDRESS = 0x48000400
GPIOC_BASE_ADDRESS = 0x48000800
GPIOD_BASE_ADDRESS = 0x48000C00
GPIOE_BASE_ADDRESS = 0x48001000
GPIOF_BASE_ADDRESS = 0x48001400
GPIOG_BASE_ADDRESS = 0x48001800

#Offset values for GPIO registers
GPIO_IDR_OFFSET = 0x10
GPIO_ODR_OFFSET = 0x14

def calculate_GPIO_pin_address(base_address, pin_number, offset):
    return base_address + offset + (pin_number // 16) * 0x24

def run_stlink_command(pin_address):
    print(pin_address)
    command = ["st-flash", "--hot-plug", "--connect-under-reset", "read", "output.bin", f"0x48000000", "200"]
    try:
        process = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        for line in process.stdout:
            print(line, end='')  # Print each line from stdout of the subprocess
    except Exception as e:
        print(e)

def display_bin_file_contents(file_path):
    try:
        with open(file_path, 'rb') as f:

            binary_data = f.read()

            hex_data = binary_data.hex()

            
            print("Data: " + hex_data)


    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except Exception as e:
        print("Error:", e)



def main():
    pin_number = 1

    pin_address = calculate_GPIO_pin_address(GPIOA_BASE_ADDRESS, pin_number, GPIO_ODR_OFFSET)

    run_stlink_command(pin_address)

    file_path = "output.bin"

    display_bin_file_contents(file_path)

if __name__ == "__main__":
    main()
