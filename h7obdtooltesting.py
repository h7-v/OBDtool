import obd
import time
import json

connection = obd.Async()


# Get supported PIDs of vehicle in groups of 32. Hex 01 to 20 etc.
connection.watch(obd.commands.PIDS_A)
connection.watch(obd.commands.PIDS_B)
connection.watch(obd.commands.PIDS_C)

connection.start()

time.sleep(1)
supportedPIDs0120 = connection.query(obd.commands.PIDS_A)
print("0120:", supportedPIDs0120.value)
time.sleep(1)
supportedPIDs2140 = connection.query(obd.commands.PIDS_B)
print("2140:", supportedPIDs2140.value)
time.sleep(1)
supportedPIDs4160 = connection.query(obd.commands.PIDS_C)
print("4160:", supportedPIDs4160.value)

# supportedPIDs0120 = "10111110000111101010100000010001"
# supportedPIDs2140 = "10000000000000000001000000000001"
# supportedPIDs4160 = "00000010000000000000000000000000"

# print("0120:", supportedPIDs0120)
# print("2140:", supportedPIDs2140)
# print("4160:", supportedPIDs4160)

supportedPIDs = str(supportedPIDs0120.value) + str(supportedPIDs2140.value) + str(supportedPIDs4160.value)
# supportedPIDs = supportedPIDs0120 + supportedPIDs2140 + supportedPIDs4160

# supportedPIDs = "100000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000000"
print("Supported PIDs String:", supportedPIDs)

time.sleep(1)

# Load PID command table. Table does not contain PID retrieval commands
with open("obd2PIDtable.json", "r") as json_file:
    pid_commands = json.load(json_file)


# Initialize an empty list to store compatible command names
supported_commands = []

# Iterate through the PID-CommandName pairs in pid_commands
pid_index = 0
for pid, command_name in pid_commands.items():

    # Check if the corresponding bit in sequence is "1"
    if supportedPIDs[pid_index] == "1":
        # If the bit is "1", add the command_name to the list
        # Ignore PID support commands as we are finished with them.
        if command_name not in ["PIDS_A", "PIDS_B", "PIDS_C"]:
            supported_commands.append(command_name)

    pid_index += 1
# The list compatible_pids now contains names of compatible commands


# Print the list of compatible PID commands
print("Supported commands:")
for command in supported_commands:
    print(command)
print("")


was_running = connection.running
connection.stop()

print("Adding commands to watch list...")

for command_name in supported_commands:
    command = getattr(obd.commands, command_name)
    connection.watch(command)

print("Commands added.")
print("")

if was_running:
    connection.start()


time.sleep(1)


# Print vehicle info to the console every 0.5s
try:
    while True:

        for command_name in supported_commands:
            # Query obd Async for latest command responses
            command = getattr(obd.commands, command_name)
            response = connection.query(command)
            print(f"{command.name}: {response.value}")

        print("")

        time.sleep(0.5)

finally:
    connection.stop()
