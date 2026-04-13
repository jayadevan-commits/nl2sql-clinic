# Test Results

Total: 20 questions
Passed: 19
Failed: 1

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
Output: 0 (wrong)
Why it failed: I stored gender as 'F' in the database but Gemini used 'Female' so it returned 0.
Fix: Added a rule in the prompt to use WHERE gender IN ('F', 'Female')

---

Q4 - Which city has the most patients?
SQL: SELECT city FROM patients GROUP BY city ORDER BY COUNT(id) DESC LIMIT 1
Status: Pass
Output: Jaipur
Note: No chart appeared because Gemini only returned the city name without the count.
      Fixed by telling Gemini to always include both name and count in the query.

---

Q5 - List patients who visited more than 3 times
SQL: SELECT p.first_name, p.last_name, COUNT(a.id) AS num_visits
     FROM patients p JOIN appointments a ON p.id = a.patient_id
     GROUP BY p.id HAVING COUNT(a.id) > 3
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
Note: Same issue as Q4. Only the name came back without the count so no chart appeared.
      Same fix applied.

---

Q8 - How many appointments does each doctor have?
SQL: SELECT d.name, COUNT(a.id) AS number_of_appointments FROM doctors d
     JOIN appointments a ON d.id = a.doctor_id
     GROUP BY d.id ORDER BY number_of_appointments DESC
Status: Pass
Output: 15 doctors with their appointment counts
Chart: Bar chart generated correctly

---

Q9 - Show me appointments for last month
SQL: SELECT * FROM appointments
     WHERE strftime('%Y-%m', appointment_date) = strftime('%Y-%m', date('now', '-1 month'))
Status: Pass
Output: 39 appointments returned
Note: Gemini used SELECT * so the result showed raw IDs instead of patient and doctor names.
      The chart was wrong too because it was plotting id vs patient_id.
      Fixed by adding a strict rule to never use SELECT * and always join tables.

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
Chart: Bar chart generated correctly

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
Output: 15 doctors with revenue returned
Chart: Bar chart generated correctly
Note: Gemini used treatment cost instead of invoice amount. Treatment cost is what each
      procedure cost, invoice amount is what was billed to the patient. Invoice amount
      is more accurate for revenue but both give a reasonable answer. Not fixed.

---

Q14 - Show unpaid invoices
SQL: SELECT i.id, p.first_name, p.last_name, i.invoice_date,
          i.total_amount, i.paid_amount, i.status
     FROM invoices i JOIN patients p ON i.patient_id = p.id
     WHERE i.status IN ('Pending', 'Overdue')
Status: Pass
Output: 136 unpaid invoices
Chart: No chart, too many columns

---

Q15 - Show patient registration trend by month
SQL: SELECT strftime('%Y-%m', registered_date) AS registration_month,
          COUNT(id) AS patient_count
     FROM patients GROUP BY registration_month ORDER BY registration_month
Status: Pass
Output: 24 months of registration data
Chart: Bar chart generated correctly

---

Q16 - Revenue trend by month
SQL: SELECT strftime('%Y-%m', invoice_date) AS sales_month,
          SUM(total_amount) AS monthly_revenue
     FROM invoices WHERE status = 'Paid'
     GROUP BY sales_month ORDER BY sales_month
Status: Pass
Output: 13 months of revenue data
Chart: Bar chart generated correctly

---

Q17 - Average appointment duration by doctor
SQL: SELECT d.name AS doctor_name, AVG(t.duration_minutes) AS average_duration_minutes
     FROM doctors d JOIN appointments a ON d.id = a.doctor_id
     JOIN treatments t ON a.id = t.appointment_id GROUP BY d.name
Status: Pass
Output: 15 doctors with average duration in minutes
Chart: Bar chart generated correctly

---

Q18 - List patients with overdue invoices
SQL: SELECT DISTINCT p.first_name, p.last_name, p.email, p.phone
     FROM patients p JOIN invoices i ON p.id = i.patient_id
     WHERE i.status = 'Overdue'
Status: Pass
Output: 48 patients with overdue invoices
Chart: No chart, columns are names and contact details

---

Q19 - Compare revenue between departments
SQL: SELECT d.department, SUM(t.cost) AS total_revenue FROM treatments t
     JOIN appointments a ON t.appointment_id = a.id
     JOIN doctors d ON a.doctor_id = d.id
     GROUP BY d.department ORDER BY total_revenue DESC
Status: Pass
Output: 5 departments with revenue
Chart: Bar chart generated correctly

---

Q20 - Average treatment cost by specialization
SQL: SELECT d.specialization, AVG(t.cost) AS average_treatment_cost
     FROM doctors d JOIN appointments a ON d.id = a.doctor_id
     JOIN treatments t ON a.id = t.appointment_id
     GROUP BY d.specialization
Status: Pass
Output: 5 specializations with average treatment cost
Chart: Bar chart generated correctly

---

Issues and fixes

Q3 - I stored gender as 'F' in the database but Gemini used 'Female' in the query so it
     returned 0. Fixed by updating the prompt to use WHERE gender IN ('F', 'Female').

Q4 - Gemini only returned the city name without the count column so no chart appeared.
     Fixed by telling Gemini in the prompt to always include both name and count.

Q7 - Gemini only returned the doctor's name without the appointment count so no chart appeared. Fixed by telling Gemini in the prompt to always include both the name and the count in the query.

Q9 - Gemini used SELECT * so raw IDs came back instead of names and the chart was wrong.
     Fixed by adding a rule in the prompt to never use SELECT * and always join tables.

Q13 - Gemini used treatment cost for revenue instead of invoice amount. Both are valid
      but invoice amount is more accurate. This was a minor issue and was left as is.