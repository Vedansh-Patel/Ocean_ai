import time
from selenium import webdriver
from selenium.webdriver.common.by import By

# Setup
driver = webdriver.Chrome()
driver.maximize_window()

# Navigate to the page
driver.get(r"C:\Users\vedan\Downloads\Ocean\assets\checkout.html")  # Replace with the actual path to your HTML file

print("Page loaded...")

# Fill in user details
print("Filling user details...")
driver.find_element(By.ID, 'name').send_keys('Vedansh Patel')
driver.find_element(By.ID, 'email').send_keys('vedansh@example.com')

# Apply empty discount code
print("Applying discount...")
driver.find_element(By.ID, 'discount-code').clear()
driver.find_element(By.ID, 'apply-discount').click()

# Check if the "Invalid Code" message is displayed
print("Checking for 'Invalid Code' message...")
discount_msg = driver.find_element(By.ID, 'discount-msg')
if discount_msg.text == 'Invalid Code':
    print("Test passed: 'Invalid Code' message is displayed.")
else:
    print("Test failed: 'Invalid Code' message is not displayed.")

# Submit the form
print("Submitting the form...")
driver.find_element(By.ID, 'pay-now-btn').click()

# Wait for the success message to appear
print("Waiting for the success message...")
time.sleep(5)

# Check if the success message is displayed
print("Checking for the success message...")
success_msg = driver.find_element(By.ID, 'success-message')
if success_msg.text == 'Payment Successful!':
    print("Test passed: Success message is displayed.")
else:
    print("Test failed: Success message is not displayed.")

# Wait for 15 seconds before closing the browser
time.sleep(15)

# Close the browser
driver.quit()