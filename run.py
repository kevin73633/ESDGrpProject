import subprocess
import time

# List of Flask scripts to run in order
scripts = ["deal.py", "product.py", "user.py", "payment.py", "account.py", "paymentrecord.py", "confirm_deal.py", "verify_deal.py"]

processes = []

for script in scripts:
    print(f"Starting {script}...")
    process = subprocess.Popen(["python", script])
    processes.append(process)
    time.sleep(2)  # Adjust delay if needed

# Keep the script running
try:
    for process in processes:
        process.wait()
except KeyboardInterrupt:
    print("Shutting down processes...")
    for process in processes:
        process.terminate()