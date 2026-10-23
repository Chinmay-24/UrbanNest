-- PostgreSQL Schema for UrbanNest

DROP VIEW IF EXISTS vw_complaint_workload;
DROP VIEW IF EXISTS vw_resident_dues;
DROP VIEW IF EXISTS vw_flat_occupancy;

DROP TABLE IF EXISTS notices CASCADE;
DROP TABLE IF EXISTS facility_bookings CASCADE;
DROP TABLE IF EXISTS facilities CASCADE;
DROP TABLE IF EXISTS complaints CASCADE;
DROP TABLE IF EXISTS visitors CASCADE;
DROP TABLE IF EXISTS payments CASCADE;
DROP TABLE IF EXISTS maintenance_bills CASCADE;
DROP TABLE IF EXISTS staff CASCADE;
DROP TABLE IF EXISTS residents CASCADE;
DROP TABLE IF EXISTS flats CASCADE;
DROP TABLE IF EXISTS blocks CASCADE;

DROP TYPE IF EXISTS bhk_type_enum CASCADE;
DROP TYPE IF EXISTS occupancy_status_enum CASCADE;
DROP TYPE IF EXISTS id_proof_type_enum CASCADE;
DROP TYPE IF EXISTS resident_type_enum CASCADE;
DROP TYPE IF EXISTS staff_role_enum CASCADE;
DROP TYPE IF EXISTS employment_status_enum CASCADE;
DROP TYPE IF EXISTS bill_status_enum CASCADE;
DROP TYPE IF EXISTS payment_mode_enum CASCADE;
DROP TYPE IF EXISTS complaint_category_enum CASCADE;
DROP TYPE IF EXISTS complaint_status_enum CASCADE;
DROP TYPE IF EXISTS booking_status_enum CASCADE;
DROP TYPE IF EXISTS notice_category_enum CASCADE;

CREATE TABLE blocks (
  block_id          SERIAL PRIMARY KEY,
  block_name        VARCHAR(50)  NOT NULL UNIQUE,
  total_floors      INT          NOT NULL,
  total_flats       INT          NOT NULL,
  constructed_year  INT          NOT NULL,
  description       VARCHAR(255) NULL,
  CONSTRAINT chk_blocks_floors CHECK (total_floors > 0),
  CONSTRAINT chk_blocks_flats  CHECK (total_flats > 0)
);

CREATE TYPE bhk_type_enum AS ENUM ('1BHK','2BHK','3BHK','4BHK');
CREATE TYPE occupancy_status_enum AS ENUM ('Vacant','Occupied','Maintenance');

CREATE TABLE flats (
  flat_id           SERIAL PRIMARY KEY,
  block_id          INT          NOT NULL,
  flat_number       VARCHAR(10)  NOT NULL,
  floor_no          INT          NOT NULL,
  bhk_type          bhk_type_enum NOT NULL,
  area_sqft         DECIMAL(7,2) NOT NULL,
  occupancy_status  occupancy_status_enum NOT NULL,
  CONSTRAINT fk_flats_block
    FOREIGN KEY (block_id) REFERENCES blocks(block_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT uq_flat_in_block UNIQUE (block_id, flat_number),
  CONSTRAINT chk_flats_floor CHECK (floor_no >= 0),
  CONSTRAINT chk_flats_area  CHECK (area_sqft > 0)
);

CREATE TYPE id_proof_type_enum AS ENUM ('Aadhaar','Passport','Driving Licence','Voter ID');
CREATE TYPE resident_type_enum AS ENUM ('Owner','Tenant','Family');

CREATE TABLE residents (
  resident_id          SERIAL PRIMARY KEY,
  flat_id              INT          NOT NULL,
  full_name            VARCHAR(100) NOT NULL,
  email                VARCHAR(120) NOT NULL UNIQUE,
  phone                VARCHAR(15)  NOT NULL UNIQUE,
  id_proof_type        id_proof_type_enum NOT NULL,
  id_proof_number      VARCHAR(30)  NOT NULL UNIQUE,
  resident_type        resident_type_enum NOT NULL,
  move_in_date         DATE         NOT NULL,
  move_out_date        DATE         NULL,
  is_primary_contact   SMALLINT     NOT NULL DEFAULT 0,
  CONSTRAINT fk_residents_flat
    FOREIGN KEY (flat_id) REFERENCES flats(flat_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT chk_residents_dates
    CHECK (move_out_date IS NULL OR move_out_date >= move_in_date),
  CONSTRAINT chk_residents_primary
    CHECK (is_primary_contact IN (0, 1))
);

CREATE TYPE staff_role_enum AS ENUM ('Manager','Security','Housekeeping','Accountant','Maintenance');
CREATE TYPE employment_status_enum AS ENUM ('Active','On Leave','Resigned');

CREATE TABLE staff (
  staff_id            SERIAL PRIMARY KEY,
  full_name           VARCHAR(100) NOT NULL,
  role                staff_role_enum NOT NULL,
  phone               VARCHAR(15)  NOT NULL UNIQUE,
  email               VARCHAR(120) NOT NULL UNIQUE,
  salary              DECIMAL(10,2) NOT NULL,
  join_date           DATE         NOT NULL,
  employment_status   employment_status_enum NOT NULL DEFAULT 'Active',
  CONSTRAINT chk_staff_salary CHECK (salary > 0)
);

CREATE TYPE bill_status_enum AS ENUM ('Unpaid','Partially Paid','Paid','Overdue');

CREATE TABLE maintenance_bills (
  bill_id       SERIAL PRIMARY KEY,
  resident_id   INT           NOT NULL,
  bill_month    SMALLINT      NOT NULL,
  bill_year     SMALLINT      NOT NULL,
  amount        DECIMAL(10,2) NOT NULL,
  due_date      DATE          NOT NULL,
  status        bill_status_enum NOT NULL DEFAULT 'Unpaid',
  generated_on  DATE          NOT NULL,
  CONSTRAINT fk_bills_resident
    FOREIGN KEY (resident_id) REFERENCES residents(resident_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT uq_bill_period UNIQUE (resident_id, bill_month, bill_year),
  CONSTRAINT chk_bill_month  CHECK (bill_month BETWEEN 1 AND 12),
  CONSTRAINT chk_bill_year   CHECK (bill_year >= 2020),
  CONSTRAINT chk_bill_amount CHECK (amount > 0)
);

CREATE TYPE payment_mode_enum AS ENUM ('Cash','UPI','Card','Net Banking');

CREATE TABLE payments (
  payment_id            SERIAL PRIMARY KEY,
  bill_id               INT           NOT NULL,
  received_by_staff_id  INT           NOT NULL,
  amount_paid           DECIMAL(10,2) NOT NULL,
  payment_date          DATE          NOT NULL,
  payment_mode          payment_mode_enum NOT NULL,
  transaction_ref       VARCHAR(40)   NOT NULL UNIQUE,
  CONSTRAINT fk_payments_bill
    FOREIGN KEY (bill_id) REFERENCES maintenance_bills(bill_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_payments_staff
    FOREIGN KEY (received_by_staff_id) REFERENCES staff(staff_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT chk_payment_amount CHECK (amount_paid > 0)
);

CREATE TABLE visitors (
  visitor_log_id    SERIAL PRIMARY KEY,
  host_resident_id  INT          NOT NULL,
  visitor_name      VARCHAR(100) NOT NULL,
  visitor_phone     VARCHAR(15)  NOT NULL,
  purpose           VARCHAR(120) NOT NULL,
  entry_time        TIMESTAMP    NOT NULL,
  exit_time         TIMESTAMP    NULL,
  vehicle_number    VARCHAR(20)  NULL,
  CONSTRAINT fk_visitors_resident
    FOREIGN KEY (host_resident_id) REFERENCES residents(resident_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT chk_visitor_times
    CHECK (exit_time IS NULL OR exit_time >= entry_time)
);

CREATE TYPE complaint_category_enum AS ENUM ('Plumbing','Electrical','Security','Cleaning','Other');
CREATE TYPE complaint_status_enum AS ENUM ('Open','In Progress','Resolved','Closed');

CREATE TABLE complaints (
  complaint_id       SERIAL PRIMARY KEY,
  resident_id        INT          NOT NULL,
  assigned_staff_id  INT          NULL,
  category           complaint_category_enum NOT NULL,
  title              VARCHAR(150) NOT NULL,
  description        TEXT         NOT NULL,
  status             complaint_status_enum NOT NULL DEFAULT 'Open',
  raised_on          TIMESTAMP    NOT NULL,
  resolved_on        TIMESTAMP    NULL,
  CONSTRAINT fk_complaints_resident
    FOREIGN KEY (resident_id) REFERENCES residents(resident_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_complaints_staff
    FOREIGN KEY (assigned_staff_id) REFERENCES staff(staff_id)
    ON UPDATE CASCADE ON DELETE SET NULL,
  CONSTRAINT chk_complaint_dates
    CHECK (resolved_on IS NULL OR resolved_on >= raised_on)
);

CREATE TABLE facilities (
  facility_id    SERIAL PRIMARY KEY,
  facility_name  VARCHAR(80)   NOT NULL UNIQUE,
  location       VARCHAR(80)   NOT NULL,
  capacity       INT           NOT NULL,
  hourly_rate    DECIMAL(8,2)  NOT NULL,
  is_active      SMALLINT      NOT NULL DEFAULT 1,
  CONSTRAINT chk_facility_capacity CHECK (capacity > 0),
  CONSTRAINT chk_facility_rate     CHECK (hourly_rate >= 0),
  CONSTRAINT chk_facility_active   CHECK (is_active IN (0, 1))
);

CREATE TYPE booking_status_enum AS ENUM ('Booked','Cancelled','Completed');

CREATE TABLE facility_bookings (
  booking_id    SERIAL PRIMARY KEY,
  facility_id   INT           NOT NULL,
  resident_id   INT           NOT NULL,
  booking_date  DATE          NOT NULL,
  start_time    TIME          NOT NULL,
  end_time      TIME          NOT NULL,
  status        booking_status_enum NOT NULL DEFAULT 'Booked',
  total_charge  DECIMAL(10,2) NOT NULL,
  CONSTRAINT fk_bookings_facility
    FOREIGN KEY (facility_id) REFERENCES facilities(facility_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_bookings_resident
    FOREIGN KEY (resident_id) REFERENCES residents(resident_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT chk_booking_time   CHECK (end_time > start_time),
  CONSTRAINT chk_booking_charge CHECK (total_charge >= 0)
);

CREATE TYPE notice_category_enum AS ENUM ('General','Maintenance','Emergency','Event');

CREATE TABLE notices (
  notice_id              SERIAL PRIMARY KEY,
  published_by_staff_id  INT          NOT NULL,
  title                  VARCHAR(150) NOT NULL,
  content                TEXT         NOT NULL,
  category               notice_category_enum NOT NULL,
  publish_date           DATE         NOT NULL,
  expiry_date            DATE         NULL,
  is_active              SMALLINT     NOT NULL DEFAULT 1,
  CONSTRAINT fk_notices_staff
    FOREIGN KEY (published_by_staff_id) REFERENCES staff(staff_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT chk_notice_dates  CHECK (expiry_date IS NULL OR expiry_date >= publish_date),
  CONSTRAINT chk_notice_active CHECK (is_active IN (0, 1))
);
