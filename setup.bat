@echo off
echo Installing Node.js dependencies...
npm install

echo.
echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Setup complete! You can now run the application with:
echo npm start 