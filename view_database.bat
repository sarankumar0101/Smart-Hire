@echo off
echo ========================================
echo SMARTHIRE DATABASE EXPORT TOOL
echo ========================================
echo.
echo Exporting database to Excel...
echo.

python export_to_excel.py

echo.
echo ========================================
echo Export completed!
echo ========================================
echo.
echo Files created:
echo - smarthire_database.xlsx (Excel file)
echo - database_summary.txt (Summary file)
echo.
echo You can now open the Excel file to view your database!
echo.
pause 