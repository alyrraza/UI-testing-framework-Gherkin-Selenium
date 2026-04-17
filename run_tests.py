import subprocess
import os

os.makedirs("allure-results", exist_ok=True)
os.makedirs("allure-report", exist_ok=True)

print("Running tests...")

result = subprocess.run([
    "behave",
    "--format", "allure_behave.formatter:AllureFormatter",
    "--outfile", "allure-results",
    "--no-capture"
], capture_output=False)

print(f"\nTests done: exit code {result.returncode}")
print("\nRun these commands manually:")
print("  allure generate allure-results --clean -o allure-report")
print("  allure open allure-report")