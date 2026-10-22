USE urbannest;

INSERT INTO blocks (block_id, block_name, total_floors, total_flats, constructed_year, description) VALUES
(1, 'A-Wing', 8, 32, 2018, 'Main residential wing near the gate'),
(2, 'B-Wing', 8, 32, 2018, 'East wing facing the garden'),
(3, 'C-Wing', 10, 40, 2020, 'Tower with clubhouse access'),
(4, 'D-Wing', 6, 24, 2016, 'Older block, recently painted'),
(5, 'E-Wing', 12, 48, 2022, 'Newest tower with stilt parking');

INSERT INTO flats (flat_id, block_id, flat_number, floor_no, bhk_type, area_sqft, occupancy_status) VALUES
(1, 1, 'A-101', 1, '2BHK', 980.00,  'Occupied'),
(2, 1, 'A-102', 1, '1BHK', 640.00,  'Occupied'),
(3, 2, 'B-201', 2, '3BHK', 1350.00, 'Occupied'),
(4, 3, 'C-301', 3, '2BHK', 1010.00, 'Occupied'),
(5, 4, 'D-401', 4, '3BHK', 1420.00, 'Occupied'),
(6, 5, 'E-101', 1, '4BHK', 2100.00, 'Vacant'),
(7, 1, 'A-201', 2, '2BHK', 990.00,  'Maintenance'),
(8, 2, 'B-101', 1, '1BHK', 650.00,  'Occupied');

INSERT INTO residents
(resident_id, flat_id, full_name, email, phone, id_proof_type, id_proof_number,
 resident_type, move_in_date, move_out_date, is_primary_contact) VALUES
(1, 1, 'Rahul Sharma',  'rahul.sharma@email.com',  '9876500001', 'Aadhaar',          'AADH100001', 'Owner',  '2021-06-15', NULL, 1),
(2, 1, 'Priya Sharma',  'priya.sharma@email.com',  '9876500002', 'Aadhaar',          'AADH100002', 'Family', '2021-06-15', NULL, 0),
(3, 3, 'Amit Patel',    'amit.patel@email.com',    '9876500003', 'Passport',         'P1234567',   'Tenant', '2024-01-10', NULL, 1),
(4, 4, 'Sneha Reddy',   'sneha.reddy@email.com',   '9876500004', 'Driving Licence',  'DL-TS-0091', 'Owner',  '2022-03-01', NULL, 1),
(5, 5, 'Vikram Singh',  'vikram.singh@email.com',  '9876500005', 'Voter ID',         'VOT445566',  'Owner',  '2020-11-20', NULL, 1),
(6, 2, 'Meera Iyer',    'meera.iyer@email.com',    '9876500006', 'Aadhaar',          'AADH100006', 'Tenant', '2025-04-01', NULL, 1),
(7, 8, 'Arjun Nair',    'arjun.nair@email.com',    '9876500007', 'Passport',         'P7654321',   'Owner',  '2023-08-12', NULL, 1);

INSERT INTO staff
(staff_id, full_name, role, phone, email, salary, join_date, employment_status) VALUES
(1, 'Kiran Desai',     'Manager',      '9000000001', 'kiran.desai@urbannest.in',     55000.00, '2019-04-01', 'Active'),
(2, 'Ramesh Yadav',    'Security',     '9000000002', 'ramesh.yadav@urbannest.in',    22000.00, '2020-01-15', 'Active'),
(3, 'Anita Fernandes', 'Housekeeping', '9000000003', 'anita.fernandes@urbannest.in', 18000.00, '2021-07-01', 'Active'),
(4, 'Suresh Iyer',     'Accountant',   '9000000004', 'suresh.iyer@urbannest.in',     40000.00, '2019-09-10', 'Active'),
(5, 'Farhan Qureshi',  'Maintenance',  '9000000005', 'farhan.qureshi@urbannest.in',  25000.00, '2022-02-20', 'Active'),
(6, 'Neha Kapoor',     'Security',     '9000000006', 'neha.kapoor@urbannest.in',     22000.00, '2024-05-01', 'On Leave');

INSERT INTO maintenance_bills
(bill_id, resident_id, bill_month, bill_year, amount, due_date, status, generated_on) VALUES
(1, 1, 8,  2026, 4500.00, '2026-08-10', 'Paid',            '2026-08-01'),
(2, 1, 9,  2026, 4500.00, '2026-09-10', 'Partially Paid',  '2026-09-01'),
(3, 3, 9,  2026, 6200.00, '2026-09-10', 'Unpaid',          '2026-09-01'),
(4, 4, 9,  2026, 4800.00, '2026-09-10', 'Paid',            '2026-09-01'),
(5, 5, 8,  2026, 7000.00, '2026-08-10', 'Overdue',         '2026-08-01'),
(6, 6, 9,  2026, 3200.00, '2026-09-10', 'Paid',            '2026-09-01'),
(7, 7, 10, 2026, 3500.00, '2026-10-10', 'Unpaid',          '2026-10-01');

INSERT INTO payments
(payment_id, bill_id, received_by_staff_id, amount_paid, payment_date, payment_mode, transaction_ref) VALUES
(1, 1, 4, 4500.00, '2026-08-05', 'UPI',         'UPI20260805001'),
(2, 2, 4, 2000.00, '2026-09-08', 'UPI',         'UPI20260908014'),
(3, 4, 4, 4800.00, '2026-09-04', 'Net Banking', 'NB20260904007'),
(4, 6, 1, 3200.00, '2026-09-06', 'Card',        'CRD20260906021'),
(5, 2, 4, 1500.00, '2026-09-20', 'Cash',        'CASH20260920003'),
(6, 5, 4, 1000.00, '2026-08-18', 'UPI',         'UPI20260818055');

INSERT INTO visitors
(visitor_log_id, host_resident_id, visitor_name, visitor_phone, purpose,
 entry_time, exit_time, vehicle_number) VALUES
(1, 1, 'Rohit Mehta',   '9811100001', 'Family visit',     '2026-10-20 10:15:00', '2026-10-20 12:40:00', 'MH12AB1234'),
(2, 3, 'Courier Desk',  '9811100002', 'Parcel delivery',  '2026-10-21 11:05:00', '2026-10-21 11:18:00', NULL),
(3, 4, 'Dr. Anjali Rao','9811100003', 'Home consultation','2026-10-21 16:00:00', '2026-10-21 16:45:00', 'TS09CD7788'),
(4, 5, 'Kabir Khan',    '9811100004', 'Guest stay',       '2026-10-22 09:30:00', NULL,                  'DL8CAF9021'),
(5, 6, 'Plumber Raju',  '9811100005', 'Repair visit',     '2026-10-19 14:10:00', '2026-10-19 15:55:00', NULL),
(6, 7, 'Nisha Menon',   '9811100006', 'Social visit',     '2026-10-22 18:20:00', NULL,                  'KA05EF3344');

INSERT INTO complaints
(complaint_id, resident_id, assigned_staff_id, category, title, description,
 status, raised_on, resolved_on) VALUES
(1, 1, 5, 'Plumbing',   'Kitchen tap leak',     'Continuous drip under the sink.',
 'Resolved',     '2026-09-12 09:20:00', '2026-09-13 17:00:00'),
(2, 3, 5, 'Electrical', 'Corridor light fused', 'B-Wing 2nd floor light not working.',
 'In Progress',  '2026-10-18 19:05:00', NULL),
(3, 4, 2, 'Security',   'Gate pass delay',      'Visitor wait time exceeded 20 minutes.',
 'Closed',       '2026-08-02 11:00:00', '2026-08-03 10:00:00'),
(4, 5, 3, 'Cleaning',   'Staircase not swept',  'D-Wing stairs dusty since Monday.',
 'Open',         '2026-10-21 08:40:00', NULL),
(5, 6, 5, 'Other',      'Intercom fault',       'Cannot reach security from A-102.',
 'In Progress',  '2026-10-15 13:10:00', NULL),
(6, 7, NULL, 'Plumbing','Low water pressure',   'Morning supply is very weak.',
 'Open',         '2026-10-22 07:30:00', NULL);

INSERT INTO facilities
(facility_id, facility_name, location, capacity, hourly_rate, is_active) VALUES
(1, 'Clubhouse',      'Ground floor, C-Wing', 80, 1500.00, 1),
(2, 'Gym',            'Basement, A-Wing',     25,  200.00, 1),
(3, 'Swimming Pool',  'Podium, C-Wing',       30,  400.00, 1),
(4, 'Party Hall',     '1st floor, B-Wing',    60, 2500.00, 1),
(5, 'Tennis Court',   'Outdoor court',         4,  300.00, 1),
(6, 'Guest Rooms',    'E-Wing stilt',          8,  800.00, 0);

INSERT INTO facility_bookings
(booking_id, facility_id, resident_id, booking_date, start_time, end_time, status, total_charge) VALUES
(1, 1, 1, '2026-10-25', '18:00:00', '21:00:00', 'Booked',     4500.00),
(2, 2, 3, '2026-10-20', '07:00:00', '08:00:00', 'Completed',   200.00),
(3, 4, 4, '2026-11-01', '16:00:00', '20:00:00', 'Booked',    10000.00),
(4, 3, 5, '2026-10-12', '10:00:00', '11:30:00', 'Cancelled',     0.00),
(5, 5, 6, '2026-10-23', '17:00:00', '18:00:00', 'Booked',      300.00),
(6, 2, 7, '2026-10-22', '19:00:00', '20:00:00', 'Completed',   200.00);

INSERT INTO notices
(notice_id, published_by_staff_id, title, content, category,
 publish_date, expiry_date, is_active) VALUES
(1, 1, 'Diwali decoration guidelines', 'Common area lights only on podium till 10 PM.',
 'General',     '2026-10-10', '2026-11-05', 1),
(2, 1, 'Water shutdown 24 Oct',        'A-Wing supply off 10 AM–2 PM for tank cleaning.',
 'Maintenance', '2026-10-20', '2026-10-24', 1),
(3, 2, 'Fire drill',                   'Mandatory drill on 30 Oct at 11 AM near C-Wing.',
 'Emergency',   '2026-10-15', '2026-10-30', 1),
(4, 1, 'Annual general meeting',       'AGM in party hall on 8 Nov, 6 PM.',
 'Event',       '2026-10-18', '2026-11-08', 1),
(5, 4, 'Maintenance due reminder',     'September dues must be cleared to avoid penalty.',
 'General',     '2026-09-25', '2026-10-15', 0),
(6, 1, 'Gym timing change',            'Gym open 6 AM–10 PM from 1 Nov.',
 'General',     '2026-10-21', '2026-11-30', 1);
