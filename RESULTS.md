Test Results
Total questions: 20
Tested: 12
Passed: 10
Failed: 1
Pending: 8

Q1 - How many patients do we have?
SQL: SELECT COUNT(id) FROM patients
Status: Pass
Output: 200 patients

Q2 - List all doctors and their specializations
SQL: SELECT name, specialization, department FROM doctors ORDER BY specialization
Status: Pass
Output: 15 doctors returned with their specializations

Q3 - How many female patients do we have?
SQL: SELECT COUNT(id) FROM patients WHERE gender = 'Female'
Status: Fail
Output: 0 (wrong result)
Why it failed: The database stores gender as 'F' not 'Female' so the query returned 0.
Fix: Updated the prompt to use WHERE gender IN ('F', 'Female')

Q4 - Which city has the most patients?
SQL: SELECT city FROM patients GROUP BY city ORDER BY COUNT(id) DESC LIMIT 1
Status: Pass
Output: Jaipur
Note: Chart did not appear because count column was missing in the SQL. Fixed in main.py.

Q5 - List patients who visited more than 3 times
SQL: SELECT p.first_name, p.last_name, COUNT(a.id) AS num_visits
FROM patients p JOIN appointments a ON p.id = a.patient_id
GROUP BY p.id HAVING COUNT(a.id) > 3
Status: Pass
Output: 60 patients returned

Q6 - List all doctors and their specializations
SQL: SELECT name, specialization, department FROM doctors ORDER BY specialization
Status: Pass
Output: 15 doctors returned

Q7 - Which doctor has the most appointments?
SQL: SELECT d.name FROM doctors d
JOIN appointments a ON d.id = a.doctor_id
GROUP BY d.id ORDER BY COUNT(a.id) DESC LIMIT 1
Status: Pass
Output: Dr. Ananya Pillai
Note: Chart did not appear because count column was not included. Fixed in main.py.

Q8 - How many appointments does each doctor have?
SQL: SELECT d.name, COUNT(a.id) AS number_of_appointments
FROM doctors d JOIN appointments a ON d.id = a.doctor_id
GROUP BY d.id ORDER BY number_of_appointments DESC
Status: Pass
Output: 15 doctors with their appointment counts
Chart: Bar chart generated correctly

Q9 - Show me appointments for last month
SQL: SELECT * FROM appointments
WHERE strftime('%Y-%m', appointment_date) = strftime('%Y-%m', date('now', '-1 month'))
Status: Pass
Output: 39 appointments returned
Note: SELECT * was used so raw IDs were shown instead of patient and doctor names.
Also the chart was wrong. Fixed in main.py to always JOIN tables and show names.

Q10 - How many cancelled appointments last quarter?
SQL: SELECT COUNT(id) FROM appointments
WHERE status = 'Cancelled'
AND appointment_date >= date('now', 'start of month', '-3 months')
Status: Pass
Output: 13 cancelled appointments

Q11 - Show monthly appointment count for the past 6 months
SQL: SELECT strftime('%Y-%m', appointment_date) AS month, COUNT(id) AS appointment_count
FROM appointments WHERE appointment_date >= date('now', '-6 months')
GROUP BY month ORDER BY month
Status: Pass
Output: 7 months of data returned
Chart: Bar chart generated correctly

Q12 - What is the total revenue?
SQL: SELECT SUM(total_amount) FROM invoices
Status: Pass
Output: 1187341.80

Q13 to Q20 - Not tested yet (API limit reached, will update soon)

Issues found and fixed
Q3 - gender value mismatch. DB stores F not Female. Fixed using IN operator.
Q4 - count column missing so no chart. Fixed by updating the prompt.
Q7 - same as Q4. Fixed.
Q9 - SELECT * used. Fixed by telling Gemini to always join tables and name columns.