USE urbannest;

CREATE OR REPLACE VIEW vw_flat_occupancy AS
SELECT
  b.block_id,
  b.block_name,
  f.flat_id,
  f.flat_number,
  f.bhk_type,
  f.occupancy_status,
  COUNT(r.resident_id) AS resident_count
FROM blocks b
JOIN flats f ON f.block_id = b.block_id
LEFT JOIN residents r
  ON r.flat_id = f.flat_id
 AND r.move_out_date IS NULL
GROUP BY
  b.block_id, b.block_name, f.flat_id, f.flat_number, f.bhk_type, f.occupancy_status;

CREATE OR REPLACE VIEW vw_resident_dues AS
SELECT
  r.resident_id,
  r.full_name,
  f.flat_number,
  b.block_name,
  COUNT(mb.bill_id) AS bill_count,
  COALESCE(SUM(mb.amount), 0) AS total_billed,
  COALESCE(SUM(pay.paid), 0) AS total_paid,
  COALESCE(SUM(mb.amount), 0) - COALESCE(SUM(pay.paid), 0) AS outstanding
FROM residents r
JOIN flats f ON f.flat_id = r.flat_id
JOIN blocks b ON b.block_id = f.block_id
LEFT JOIN maintenance_bills mb ON mb.resident_id = r.resident_id
LEFT JOIN (
  SELECT bill_id, SUM(amount_paid) AS paid
  FROM payments
  GROUP BY bill_id
) pay ON pay.bill_id = mb.bill_id
GROUP BY r.resident_id, r.full_name, f.flat_number, b.block_name;

CREATE OR REPLACE VIEW vw_complaint_workload AS
SELECT
  c.category,
  c.status,
  COUNT(*) AS complaint_count,
  AVG(TIMESTAMPDIFF(HOUR, c.raised_on, COALESCE(c.resolved_on, NOW()))) AS avg_hours_open
FROM complaints c
GROUP BY c.category, c.status;
