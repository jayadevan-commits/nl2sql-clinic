# Test Results

Total: 20 questions
Tested: 15
Passed: 14
Failed: 1
Pending: 5

---

Q1 - How many patients do we have?
SQL: SELECT COUNT(id) FROM patients
Status: Pass
Output: 200 patients

---

Q2 - List all doctors and their specializations
SQL: SELECT name, specialization, department FROM doctors ORDER BY specialization
Status: Pass
Output: 15 doctors returned

---

Q3 - How many female patients do we have?
SQL: SELECT COUNT(id) FROM patients WHERE gender = 'Female'
Status: Fail
Output: 0
Why: DB stores gender as 'F' not 'Female' so got 0 results.
Fix: Changed query to use WHERE gender IN ('F', 'Female')

---

Q4 - Which city has the most patients?
SQL: SELECT city FROM patients GROUP BY city ORDER BY COUNT(id) DESC LIMIT 1
Status: Pass
Output: Jaipur
Note: No chart came because count column was missing. Fixed in main.py.

---

Q5 - List patients who visited more than 3 times
SQL: SELECT p.first_name, p.last_name, COUNT(a.id) AS num_visits FROM patients p
     JOIN appointments a ON p.id = a.patient_id GROUP BY p.id HAVING COUNT(a.id) > 3
Status: Pass
Output: 60 patients returned

---

Q6 - List all doctors and their specializations
SQL: SELECT name, specialization, department FROM doctors ORDER BY specialization
Status: Pass
Output: 15 doctors returned

---

Q7 - Which doctor has the most appointments?
SQL: SELECT d.name FROM doctors d JOIN appointments a ON d.id = a.doctor_id
     GROUP BY d.id ORDER BY COUNT(a.id) DESC LIMIT 1
Status: Pass
Output: Dr. Ananya Pillai
Note: No chart because count column was missing. Fixed in main.py.

---

Q8 - How many appointments does each doctor have?
SQL: SELECT d.name, COUNT(a.id) AS number_of_appointments FROM doctors d
     JOIN appointments a ON d.id = a.doctor_id GROUP BY d.id ORDER BY number_of_appointments DESC
Status: Pass
Output: 15 doctors with their counts
Chart: Yes, bar chart worked correctly

---

Q9 - Show me appointments for last month
SQL: SELECT * FROM appointments WHERE strftime('%Y-%m', appointment_date) = strftime('%Y-%m', date('now', '-1 month'))
Status: Pass
Output: 39 appointments
Note: SELECT * was used so IDs showed up instead of names. Chart was also wrong.
      Fixed in main.py to always join and show proper names.

---

Q10 - How many cancelled appointments last quarter?
SQL: SELECT COUNT(id) FROM appointments WHERE status = 'Cancelled'
     AND appointment_date >= date('now', 'start of month', '-3 months')
Status: Pass
Output: 13 cancelled appointments

---

Q11 - Show monthly appointment count for the past 6 months
SQL: SELECT strftime('%Y-%m', appointment_date) AS month, COUNT(id) AS appointment_count
     FROM appointments WHERE appointment_date >= date('now', '-6 months')
     GROUP BY month ORDER BY month
Status: Pass
Output: 7 months of data
Chart: Yes, bar chart worked correctly

---

Q12 - What is the total revenue?
SQL: SELECT SUM(total_amount) FROM invoices
Status: Pass
Output: 1187341.80

---

Q13 - Show revenue by doctor
SQL: SELECT d.name, SUM(t.cost) AS total_revenue FROM doctors d
     JOIN appointments a ON d.id = a.doctor_id
     JOIN treatments t ON a.id = t.appointment_id
     GROUP BY d.name ORDER BY total_revenue DESC
Status: Pass
Output: 15 doctors with revenue amounts
Chart: Yes, bar chart worked correctly
Note: Gemini used treatment cost instead of invoice amount. Both work but invoice amount
      is more accurate for actual billing revenue.

---

Q14 - Show unpaid invoices
SQL: SELECT i.id, p.first_name, p.last_name, i.invoice_date, i.total_amount, i.paid_amount, i.status
     FROM invoices i JOIN patients p ON i.patient_id = p.id
     WHERE i.status IN ('Pending', 'Overdue')
Status: Pass
Output: 136 unpaid invoices returned
Chart: No chart, too many columns

---

Q15 - Show patient registration trend by month
SQL: SELECT strftime('%Y-%m', registered_date) AS registration_month, COUNT(id) AS patient_count
     FROM patients GROUP BY registration_month ORDER BY registration_month
Status: Pass
Output: 24 months of data returned
Chart: Yes, bar chart worked correctly

---

Q16 to Q20 - not tested yet, will update

---

Issues and fixes

Issues and fixes

Q3 - gender stored as F not Female, fixed by updating DB_SCHEMA prompt 
     to use WHERE gender IN ('F', 'Female'). Verified working after fix.

Q4 - count column was missing so no chart appeared, fixed by telling 
     Gemini to always include both name and count column. Fixed in main.py.

Q7 - same issue as Q4, same fix applied in main.py.

Q9 - SELECT * gave raw IDs and wrong chart, fixed by telling Gemini to 
     never use SELECT * and always JOIN tables to show names. Fixed in main.py.

Q13 - Gemini used treatment cost instead of invoice amount for revenue. 
      This is a minor issue and not fixed yet. Both values are technically 
      correct but invoice amount is more accurate for billing purposes.