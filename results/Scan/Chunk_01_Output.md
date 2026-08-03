=== FILE: ts-plsql-oracle-forms-hrms-main/data/seed/01_reference_data.sql ===

**Tables Written To:** LOCATIONS, JOB_GRADES, DEPARTMENTS, JOB_TITLES, LEAVE_TYPES, PAY_ELEMENTS, HOLIDAYS, SYSTEM_PARAMETERS

---

**Table: LOCATIONS**
Columns inserted: LOCATION_CODE, LOCATION_NAME, ADDRESS_LINE1, CITY, STATE_PROVINCE, POSTAL_CODE, COUNTRY_CODE, PHONE, ACTIVE_FLAG, CREATED_BY, CREATED_DATE

Rows:
- ('HQ', 'Corporate Headquarters', '100 Main Street', 'New York', 'NY', '10001', 'US', '212-555-1000', 'Y', 'SYSTEM', SYSDATE)
- ('CHI', 'Chicago Regional Office', '200 Michigan Avenue', 'Chicago', 'IL', '60601', 'US', '312-555-2000', 'Y', 'SYSTEM', SYSDATE)
- ('SF', 'San Francisco Branch', '50 California Street', 'San Francisco', 'CA', '94111', 'US', '415-555-3000', 'Y', 'SYSTEM', SYSDATE)

---

**Table: JOB_GRADES**
Columns inserted: GRADE_ID, GRADE_NAME, GRADE_LEVEL, MIN_SALARY, MAX_SALARY, ACTIVE_FLAG, CREATED_BY, CREATED_DATE

Rows (all ACTIVE_FLAG='Y', CREATED_BY='SYSTEM'):
- (1, 'Entry Level',    GRADE_LEVEL=1,  MIN_SALARY=35000,  MAX_SALARY=55000)
- (2, 'Junior',         GRADE_LEVEL=2,  MIN_SALARY=45000,  MAX_SALARY=70000)
- (3, 'Mid-Level',      GRADE_LEVEL=3,  MIN_SALARY=60000,  MAX_SALARY=90000)
- (4, 'Senior',         GRADE_LEVEL=4,  MIN_SALARY=80000,  MAX_SALARY=120000)
- (5, 'Lead',           GRADE_LEVEL=5,  MIN_SALARY=95000,  MAX_SALARY=145000)
- (6, 'Manager',        GRADE_LEVEL=6,  MIN_SALARY=110000, MAX_SALARY=170000)
- (7, 'Senior Manager', GRADE_LEVEL=7,  MIN_SALARY=130000, MAX_SALARY=200000)
- (8, 'Director',       GRADE_LEVEL=8,  MIN_SALARY=160000, MAX_SALARY=250000)
- (9, 'VP',             GRADE_LEVEL=9,  MIN_SALARY=200000, MAX_SALARY=350000)
- (10, 'C-Suite',       GRADE_LEVEL=10, MIN_SALARY=300000, MAX_SALARY=600000)

---

**Table: DEPARTMENTS**
Columns inserted: DEPT_ID, DEPT_CODE, DEPT_NAME, COST_CENTER, PARENT_DEPT_ID, MANAGER_EMP_ID, LOCATION_CODE, ACTIVE_FLAG, CREATED_BY, CREATED_DATE

Rows (all ACTIVE_FLAG='Y', CREATED_BY='SYSTEM', MANAGER_EMP_ID=NULL at insert time):
- (1,  'EXEC',  'Executive Office',       'CC-1000', PARENT=NULL, LOCATION='HQ')
- (10, 'HR',    'Human Resources',         'CC-1100', PARENT=1,    LOCATION='HQ')
- (20, 'FIN',   'Finance & Accounting',    'CC-1200', PARENT=1,    LOCATION='HQ')
- (30, 'IT',    'Information Technology',  'CC-1300', PARENT=1,    LOCATION='CHI')
- (31, 'ITDEV', 'IT - Development',        'CC-1310', PARENT=30,   LOCATION='CHI')
- (32, 'ITOPS', 'IT - Operations',         'CC-1320', PARENT=30,   LOCATION='CHI')
- (40, 'SALES', 'Sales',                   'CC-1400', PARENT=1,    LOCATION='SF')
- (50, 'MKT',   'Marketing',               'CC-1500', PARENT=1,    LOCATION='SF')
- (60, 'OPS',   'Operations',              'CC-1600', PARENT=1,    LOCATION='CHI')
- (70, 'LEGAL', 'Legal & Compliance',      'CC-1700', PARENT=1,    LOCATION='HQ')

---

**Table: JOB_TITLES**
Columns inserted: JOB_ID, JOB_CODE, JOB_TITLE, GRADE_ID, EEO_CATEGORY, ACTIVE_FLAG, CREATED_BY, CREATED_DATE

Rows (all ACTIVE_FLAG='Y', CREATED_BY='SYSTEM'):
- (1,  'CEO',      'Chief Executive Officer',   GRADE_ID=10, EEO='1.1')
- (2,  'CFO',      'Chief Financial Officer',   GRADE_ID=10, EEO='1.1')
- (3,  'CIO',      'Chief Information Officer', GRADE_ID=10, EEO='1.1')
- (10, 'VP-HR',    'VP of Human Resources',     GRADE_ID=9,  EEO='1.1')
- (11, 'VP-FIN',   'VP of Finance',             GRADE_ID=9,  EEO='1.1')
- (12, 'VP-SALES', 'VP of Sales',               GRADE_ID=9,  EEO='1.1')
- (20, 'DIR-IT',   'Director of IT',            GRADE_ID=8,  EEO='1.2')
- (21, 'DIR-HR',   'Director of HR',            GRADE_ID=8,  EEO='1.2')
- (30, 'MGR-DEV',  'Development Manager',       GRADE_ID=6,  EEO='1.2')
- (31, 'MGR-OPS',  'Operations Manager',        GRADE_ID=6,  EEO='1.2')
- (32, 'MGR-PAY',  'Payroll Manager',           GRADE_ID=6,  EEO='1.2')
- (33, 'MGR-SALES','Sales Manager',             GRADE_ID=6,  EEO='1.2')
- (40, 'SR-DEV',   'Senior Developer',          GRADE_ID=4,  EEO='2.0')
- (41, 'SR-DBA',   'Senior DBA',                GRADE_ID=4,  EEO='2.0')
- (42, 'SR-ACCT',  'Senior Accountant',         GRADE_ID=4,  EEO='2.0')
- (43, 'SR-SALES', 'Senior Sales Rep',          GRADE_ID=4,  EEO='2.0')
- (50, 'DEV',      'Software Developer',        GRADE_ID=3,  EEO='2.0')
- (51, 'QA',       'QA Analyst',                GRADE_ID=3,  EEO='2.0')
- (52, 'ACCT',     'Accountant',                GRADE_ID=3,  EEO='2.0')
- (53, 'HR-SPEC',  'HR Specialist',             GRADE_ID=3,  EEO='2.0')
- (54, 'SALES-REP','Sales Representative',      GRADE_ID=3,  EEO='2.0')
- (60, 'JR-DEV',   'Junior Developer',          GRADE_ID=2,  EEO='2.0')
- (61, 'HR-ASST',  'HR Assistant',              GRADE_ID=2,  EEO='5.0')
- (62, 'ACCT-CLK', 'Accounting Clerk',          GRADE_ID=2,  EEO='5.0')
- (70, 'INTERN',   'Intern',                    GRADE_ID=1,  EEO='2.0')
- (71, 'RECEPT',   'Receptionist',              GRADE_ID=1,  EEO='5.0')

---

**Table: LEAVE_TYPES**
Columns inserted: LEAVE_TYPE_ID, LEAVE_TYPE_CODE, LEAVE_TYPE_NAME, ACCRUAL_FLAG, ACCRUAL_RATE, ACCRUAL_FREQUENCY, MAX_BALANCE, CARRYOVER_MAX, CARRYOVER_EXPIRY, REQUIRES_APPROVAL, MIN_TENURE_DAYS, ACTIVE_FLAG, CREATED_BY, CREATED_DATE

Rows (all ACTIVE_FLAG='Y', CREATED_BY='SYSTEM'):
- (1, 'PTO',     'Paid Time Off',        ACCRUAL_FLAG='Y', ACCRUAL_RATE=1.25,  ACCRUAL_FREQUENCY='MONTHLY', MAX_BALANCE=20,   CARRYOVER_MAX=5,  CARRYOVER_EXPIRY=3,    REQUIRES_APPROVAL='Y', MIN_TENURE_DAYS=0)
- (2, 'SICK',    'Sick Leave',           ACCRUAL_FLAG='Y', ACCRUAL_RATE=0.833, ACCRUAL_FREQUENCY='MONTHLY', MAX_BALANCE=10,   CARRYOVER_MAX=10, CARRYOVER_EXPIRY=NULL, REQUIRES_APPROVAL='Y', MIN_TENURE_DAYS=0)
- (3, 'COMP',    'Compensatory Time',    ACCRUAL_FLAG='N', ACCRUAL_RATE=NULL,  ACCRUAL_FREQUENCY=NULL,      MAX_BALANCE=NULL, CARRYOVER_MAX=0,  CARRYOVER_EXPIRY=NULL, REQUIRES_APPROVAL='Y', MIN_TENURE_DAYS=90)
- (4, 'FMLA',    'Family Medical Leave', ACCRUAL_FLAG='N', ACCRUAL_RATE=NULL,  ACCRUAL_FREQUENCY=NULL,      MAX_BALANCE=NULL, CARRYOVER_MAX=0,  CARRYOVER_EXPIRY=NULL, REQUIRES_APPROVAL='Y', MIN_TENURE_DAYS=365)
- (5, 'JURY',    'Jury Duty',            ACCRUAL_FLAG='N', ACCRUAL_RATE=NULL,  ACCRUAL_FREQUENCY=NULL,      MAX_BALANCE=NULL, CARRYOVER_MAX=0,  CARRYOVER_EXPIRY=NULL, REQUIRES_APPROVAL='N', MIN_TENURE_DAYS=0)
- (6, 'BEREAVE', 'Bereavement',          ACCRUAL_FLAG='N', ACCRUAL_RATE=NULL,  ACCRUAL_FREQUENCY=NULL,      MAX_BALANCE=NULL, CARRYOVER_MAX=0,  CARRYOVER_EXPIRY=NULL, REQUIRES_APPROVAL='N', MIN_TENURE_DAYS=0)

**Business Rules — Leave Types:**
- PTO accrues at 1.25 days/month; max balance 20 days; carryover max 5 days; carryover expires after 3 (months/periods); requires approval; no minimum tenure
- Sick accrues at 0.833 days/month; max balance 10 days; carryover max 10 days; no carryover expiry; requires approval; no minimum tenure
- Compensatory Time does not accrue; no max balance; no carryover; requires approval; minimum tenure 90 days
- FMLA does not accrue; no max balance; no carryover; requires approval; minimum tenure 365 days
- Jury Duty does not accrue; no max balance; no carryover; does NOT require approval; no minimum tenure
- Bereavement does not accrue; no max balance; no carryover; does NOT require approval; no minimum tenure

---

**Table: PAY_ELEMENTS**
Columns inserted: ELEMENT_ID, ELEMENT_CODE, ELEMENT_NAME, ELEMENT_TYPE, CALCULATION_TYPE, DEFAULT_AMOUNT, DEFAULT_PERCENTAGE, GL_ACCOUNT_CODE, PRIORITY_ORDER, PRETAX_FLAG, ACTIVE_FLAG, CREATED_BY, CREATED_DATE

Rows (all ACTIVE_FLAG='Y', CREATED_BY='SYSTEM'):
- (1,   'BASE_PAY',   'Base Salary',                       ELEMENT_TYPE='EARNING',   CALC_TYPE='FLAT',       DEFAULT_AMOUNT=NULL, DEFAULT_PCT=NULL, GL='5100-100', PRIORITY=1,  PRETAX='N')
- (100, 'FED_TAX',    'Federal Income Tax',                ELEMENT_TYPE='TAX',       CALC_TYPE='FORMULA',    DEFAULT_AMOUNT=NULL, DEFAULT_PCT=NULL, GL='2100-100', PRIORITY=10, PRETAX='N')
- (101, 'STATE_TAX',  'State Income Tax',                  ELEMENT_TYPE='TAX',       CALC_TYPE='FORMULA',    DEFAULT_AMOUNT=NULL, DEFAULT_PCT=NULL, GL='2100-200', PRIORITY=11, PRETAX='N')
- (102, 'FICA',       'Social Security (FICA)',            ELEMENT_TYPE='TAX',       CALC_TYPE='FORMULA',    DEFAULT_AMOUNT=NULL, DEFAULT_PCT=NULL, GL='2100-300', PRIORITY=12, PRETAX='N')
- (103, 'MEDICARE',   'Medicare',                          ELEMENT_TYPE='TAX',       CALC_TYPE='FORMULA',    DEFAULT_AMOUNT=NULL, DEFAULT_PCT=NULL, GL='2100-400', PRIORITY=13, PRETAX='N')
- (200, '401K_EE',    '401(k) Employee Contribution',      ELEMENT_TYPE='DEDUCTION', CALC_TYPE='PERCENTAGE', DEFAULT_AMOUNT=NULL, DEFAULT_PCT=6,    GL='2200-100', PRIORITY=20, PRETAX='Y')
- (201, 'MED_EE',     'Medical Insurance (Employee)',      ELEMENT_TYPE='BENEFIT',   CALC_TYPE='FLAT',       DEFAULT_AMOUNT=250,  DEFAULT_PCT=NULL, GL='2200-200', PRIORITY=21, PRETAX='Y')
- (202, 'DENTAL_EE',  'Dental Insurance (Employee)',       ELEMENT_TYPE='BENEFIT',   CALC_TYPE='FLAT',       DEFAULT_AMOUNT=45,   DEFAULT_PCT=NULL, GL='2200-300', PRIORITY=22, PRETAX='Y')
- (203, 'VISION_EE',  'Vision Insurance (Employee)',       ELEMENT_TYPE='BENEFIT',   CALC_TYPE='FLAT',       DEFAULT_AMOUNT=15,   DEFAULT_PCT=NULL, GL='2200-400', PRIORITY=23, PRETAX='Y')
- (204, 'LIFE_INS',   'Life Insurance',                    ELEMENT_TYPE='BENEFIT',   CALC_TYPE='FLAT',       DEFAULT_AMOUNT=25,   DEFAULT_PCT=NULL, GL='2200-500', PRIORITY=24, PRETAX='N')
- (205, 'HSA',        'Health Savings Account',            ELEMENT_TYPE='DEDUCTION', CALC_TYPE='FLAT',       DEFAULT_AMOUNT=150,  DEFAULT_PCT=NULL, GL='2200-600', PRIORITY=25, PRETAX='Y')

**Business Rules — Pay Elements:**
- 401(k) default employee contribution: 6% of pay; pre-tax
- Medical insurance default employee deduction: $250 flat per period; pre-tax
- Dental insurance default employee deduction: $45 flat per period; pre-tax
- Vision insurance default employee deduction: $15 flat per period; pre-tax
- Life insurance default employee deduction: $25 flat per period; NOT pre-tax
- HSA default employee deduction: $150 flat per period; pre-tax
- Processing priority order: BASE_PAY(1) → FED_TAX(10) → STATE_TAX(11) → FICA(12) → MEDICARE(13) → 401K_EE(20) → MED_EE(21) → DENTAL_EE(22) → VISION_EE(23) → LIFE_INS(24) → HSA(25)

---

**Table: HOLIDAYS**
Columns inserted: HOLIDAY_ID, HOLIDAY_NAME, HOLIDAY_DATE, LOCATION_CODE (NULL = all), ACTIVE_FLAG, CREATED_BY, CREATED_DATE

Rows (all LOCATION_CODE=NULL meaning company-wide, ACTIVE_FLAG='Y', CREATED_BY='SYSTEM'):
- (1,  'New Year''s Day',         2024-01-01)
- (2,  'Martin Luther King Jr. Day', 2024-01-15)
- (3,  'Presidents'' Day',        2024-02-19)
- (4,  'Memorial Day',            2024-05-27)
- (5,  'Independence Day',        2024-07-04)
- (6,  'Labor Day',               2024-09-02)
- (7,  'Thanksgiving',            2024-11-28)
- (8,  'Day After Thanksgiving',  2024-11-29)
- (9,  'Christmas Eve',           2024-12-24)
- (10, 'Christmas Day',           2024-12-25)

---

**Table: SYSTEM_PARAMETERS**
Columns inserted: PARAM_ID, PARAM_GROUP, PARAM_CODE, PARAM_VALUE, DESCRIPTION, EDITABLE_FLAG, CREATED_BY, CREATED_DATE

Rows:
- (1,  'SYSTEM',       'APP_VERSION',           '4.2.0',                          EDITABLE='N')
- (2,  'SYSTEM',       'COMPANY_NAME',           'Acme Corporation',               EDITABLE='Y')
- (3,  'PAYROLL',      'DEFAULT_PAY_FREQUENCY',  'MONTHLY',                        EDITABLE='Y')
- (4,  'PAYROLL',      'FISCAL_YEAR_START',      '10',                             EDITABLE='Y')  -- Month 10 = October
- (5,  'SECURITY',     'SESSION_TIMEOUT_MIN',    '30',                             EDITABLE='Y')  -- 30 minutes
- (6,  'SECURITY',     'PASSWORD_MIN_LENGTH',    '8',                              EDITABLE='Y')
- (7,  'NOTIFICATION', 'SMTP_HOST',              'smtp.internal.company.com',      EDITABLE='Y')
- (8,  'NOTIFICATION', 'FROM_ADDRESS',           'hrms-noreply@company.com',       EDITABLE='Y')
- (9,  'INTEGRATION',  'GL_FEED_STATUS',         'ACTIVE',                         EDITABLE='Y')
- (10, 'INTEGRATION',  'BENEFITS_FEED_STATUS',   'ACTIVE',                         EDITABLE='Y')

**Business Rules — System Parameters:**
- Application version: 4.2.0 (not editable)
- Company name: Acme Corporation (editable)
- Default payroll frequency: MONTHLY
- Fiscal year start month: 10 (October)
- Session timeout: 30 minutes
- Minimum password length: 8 characters
- SMTP host: smtp.internal.company.com
- From address: hrms-noreply@company.com
- GL feed status: ACTIVE
- Benefits feed status: ACTIVE

---

=== FILE: ts-plsql-oracle-forms-hrms-main/data/seed/02_employee_data.sql ===

**Tables Written To:** EMPLOYEES, SALARY_RECORDS, DEPARTMENTS (UPDATE)

---

**Table: EMPLOYEES**
Columns: EMP_ID, EMP_NUMBER, FIRST_NAME, LAST_NAME, EMAIL, PHONE_WORK, HIRE_DATE, DEPT_ID, JOB_ID, MANAGER_EMP_ID, LOCATION_CODE, EMPLOYMENT_TYPE, EMPLOYMENT_STATUS, GENDER, DATE_OF_BIRTH, MARITAL_STATUS, ACTIVE_FLAG, CREATED_BY, CREATED_DATE (plus optional: TERMINATION_DATE, TERMINATION_REASON)

Rows (all ACTIVE_FLAG='Y' unless noted, CREATED_BY='SYSTEM'):

Executive:
- (1,  'EMP-000001', 'JAMES',    'RICHARDSON', 'james.richardson@company.com', '212-555-1001', 2010-03-15, DEPT=1,  JOB=1,  MGR=NULL, LOC='HQ',  TYPE='FULL_TIME', STATUS='ACTIVE', GENDER='M', DOB=1968-07-22, MARITAL='MARRIED')
- (2,  'EMP-000002', 'SARAH',    'CHEN',       'sarah.chen@company.com',       '212-555-1002', 2012-06-01, DEPT=20, JOB=2,  MGR=1,    LOC='HQ',  TYPE='FULL_TIME', STATUS='ACTIVE', GENDER='F', DOB=1975-11-03, MARITAL='MARRIED')
- (3,  'EMP-000003', 'MICHAEL',  'OCONNOR',    'michael.oconnor@company.com',  '312-555-2001', 2011-09-12, DEPT=30, JOB=3,  MGR=1,    LOC='CHI', TYPE='FULL_TIME', STATUS='ACTIVE', GENDER='M', DOB=1972-03-18, MARITAL='DIVORCED')

HR Department:
- (10, 'EMP-000010', 'PATRICIA', 'WILLIAMS',   'patricia.williams@company.com','212-555-1101', 2013-02-18, DEPT=10, JOB=10, MGR=1,    LOC='HQ',  TYPE='FULL_TIME', STATUS='ACTIVE', GENDER='F', DOB=1978-09-14, MARITAL='SINGLE')
- (11, 'EMP-000011', 'DAVID',    'MARTINEZ',   'david.martinez@company.com',   '212-555-1102', 2016-08-22, DEPT=10, JOB=53, MGR=10,   LOC='HQ',  TYPE='FULL_TIME', STATUS='ACTIVE', GENDER='M', DOB=1985-04-30, MARITAL='MARRIED')
- (12, 'EMP-000012', 'EMILY',    'JOHNSON',    'emily.johnson@company.com',    '212-555-1103', 2019-01-07, DEPT=10, JOB=61, MGR=10,   LOC='HQ',  TYPE='FULL_TIME', STATUS='ACTIVE', GENDER='F', DOB=1994-12-08, MARITAL='SINGLE')

Finance Department:
- (20, 'EMP-000020', 'ROBERT',   'KUMAR',      'robert.kumar@company.com',     '212-555-1201', 2014-05-12, DEPT=20, JOB=11, MGR=2,    LOC='HQ',  TYPE='FULL_TIME', STATUS='ACTIVE', GENDER='M', DOB=1980-01-25, MARITAL='MARRIED')
- (21, 'EMP-000021', 'JENNIFER', 'PARK',       'jennifer.park@company.com',    '212-555-1202', 2017-03-20, DEPT=20, JOB=32, MGR=20,   LOC='HQ',  TYPE='FULL_TIME', STATUS='ACTIVE', GENDER='F', DOB=1983-06-17, MARITAL='MARRIED')
- (22, 'EMP-000022', 'THOMAS',   'BAKER',      'thomas.baker@company.com',     '212-555-1203', 2018-09-10, DEPT=20, JOB=42, MGR=21,   LOC='HQ',  TYPE='FULL_TIME', STATUS='ACTIVE', GENDER='M', DOB=1987-02-14, MARITAL='SINGLE')
- (23, 'EMP-000023', 'LISA',     'WONG',       'lisa.wong@company.com',        '212-555-1204', 2020-11-02, DEPT=20, JOB=52, MGR=21,   LOC='HQ',  TYPE='FULL_TIME', STATUS='ACTIVE', GENDER='F', DOB=1992-08-21, MARITAL='SINGLE')
- (24, 'EMP-000024', 'ANDREW',   'PATEL',      'andrew.patel@company.com',     '212-555-1205', 2022-06-15, DEPT=20, JOB=62, MGR=21,   LOC='HQ',  TYPE='FULL_TIME', STATUS='ACTIVE', GENDER='M', DOB=1997-10-30, MARITAL='SINGLE')

IT Department:
- (30, 'EMP-000030', 'RACHEL',   'THOMPSON',   'rachel.thompson@company.com',  '312-555-2101', 2015-01-05, DEPT=30, JOB=20, MGR=3,    LOC='CHI', TYPE='FULL_TIME', STATUS='ACTIVE', GENDER='F', DOB=1979-05-12, MARITAL='MARRIED')
- (31, 'EMP-000031', 'KEVIN',    'GARCIA',     'kevin.garcia@company.com',     '312-555-2102', 2016-04-18, DEPT=31, JOB=30, MGR=30,   LOC='CHI', TYPE='FULL_TIME', STATUS='ACTIVE', GENDER='M', DOB=1984-11-07, MARITAL='MARRIED')
- (32, 'EMP-000032', 'MARIA',    'RODRIGUEZ',  'maria.rodriguez@company.com',  '312-555-2103', 2017-07-24, DEPT=31, JOB=40, MGR=31,   LOC='CHI', TYPE='FULL_TIME', STATUS='ACTIVE', GENDER='F', DOB=1986-03-29, MARITAL='SINGLE')
- (33, 'EMP-000033', 'DANIEL',   'LEE',        'daniel.lee@company.com',       '312-555-2104', 2018-02-12, DEPT=31, JOB=41, MGR=31,   LOC='CHI', TYPE='FULL_TIME', STATUS='ACTIVE', GENDER='M', DOB=1982-09-05, MARITAL='MARRIED')
- (34, 'EMP-000034', 'JESSICA',  'NGUYEN',     'jessica.nguyen@company.com',   '312-555-2105', 2019-05-06, DEPT=31, JOB=50, MGR=31,   LOC='CHI', TYPE='FULL_TIME', STATUS='ACTIVE', GENDER='F', DOB=1991-07-15, MARITAL='SINGLE')
- (35, 'EMP-000035', 'CHRIS',    'ANDERSON',   'chris.anderson@company.com',   '312-555-2106', 2020-08-17, DEPT=31, JOB=50, MGR=31,   LOC='CHI', TYPE='FULL_TIME', STATUS='ACTIVE', GENDER='M', DOB=1993-01-22, MARITAL='SINGLE')
- (36, 'EMP-000036', 'PRIYA',    'SHARMA',     'priya.sharma@company.com',     '312-555-2107', 2021-03-22, DEPT=31, JOB=51, MGR=31,   LOC='CHI', TYPE='FULL_TIME', STATUS='ACTIVE', GENDER='F', DOB=1995-06-10, MARITAL='SINGLE')
- (37, 'EMP-000037', 'ALEX',     'TAYLOR',     'alex.taylor@company.com',      '312-555-2108', 2022-01-10, DEPT=31, JOB=60, MGR=31,   LOC='CHI', TYPE='FULL_TIME', STATUS='ACTIVE', GENDER='M', DOB=1998-04-18, MARITAL='SINGLE')

Sales Department:
- (40, 'EMP-000040', 'MARK',     'DAVIS',      'mark.davis@company.com',       '415-555-3101', 2014-11-03, DEPT=40, JOB=12, MGR=1,    LOC='SF',  TYPE='FULL_TIME', STATUS='ACTIVE', GENDER='M', DOB=1977-08-09, MARITAL='MARRIED')
- (41, 'EMP-000041', 'ASHLEY',   'BROWN',      'ashley.brown@company.com',     '415-555-3102', 2017-06-19, DEPT=40, JOB=33, MGR=40,   LOC='SF',  TYPE='FULL_TIME', STATUS='ACTIVE', GENDER='F', DOB=1985-02-28, MARITAL='SINGLE')
- (42, 'EMP-000042', 'JASON',    'WILSON',     'jason.wilson@company.com',     '415-555-3103', 2019-09-16, DEPT=40, JOB=43, MGR=41,   LOC='SF',  TYPE='FULL_TIME', STATUS='ACTIVE', GENDER='M', DOB=1989-12-01, MARITAL='MARRIED')
- (43, 'EMP-000043', 'SAMANTHA', 'MOORE',      'samantha.moore@company.com',   '415-555-3104', 2021-02-08, DEPT=40, JOB=54, MGR=41,   LOC='SF',  TYPE='FULL_TIME', STATUS='ACTIVE', GENDER='F', DOB=1993-10-25, MARITAL='SINGLE')

Terminated (ACTIVE_FLAG='N'):
- (99, 'EMP-000099', 'BRIAN',    'FOSTER',     'brian.foster@company.com',     '312-555-2199', HIRE=2018-04-02, DEPT=31, JOB=50, MGR=31, LOC='CHI', TYPE='FULL_TIME', STATUS='TERMINATED', TERMINATION_DATE=2023-06-30, TERMINATION_REASON='VOLUNTARY', GENDER='M', DOB=1990-05-14, MARITAL='SINGLE')

---

**Table: SALARY_RECORDS**
Columns: SALARY_ID, EMP_ID, EFFECTIVE_DATE, END_DATE (NULL = current), BASE_SALARY, CURRENCY_CODE, PAY_FREQUENCY, SALARY_BASIS, CHANGE_REASON, ACTIVE_FLAG, CREATED_BY, CREATED_DATE

All records: CURRENCY_CODE='USD', PAY_FREQUENCY='MONTHLY', SALARY_BASIS='ANNUAL', ACTIVE_FLAG='Y', CREATED_BY='SYSTEM'

Rows:
- (SALARY_ID=1,  EMP_ID=1,  EFF=2023-01-01, BASE_SALARY=450000, REASON='Annual review')
- (SALARY_ID=2,  EMP_ID=2,  EFF=2023-01-01, BASE_SALARY=380000, REASON='Annual review')
- (SALARY_ID=3,  EMP_ID=3,  EFF=2023-01-01, BASE_SALARY=370000, REASON='Annual review')
- (SALARY_ID=10, EMP_ID=10, EFF=2023-07-01, BASE_SALARY=240000, REASON='Promotion')
- (SALARY_ID=11, EMP_ID=11, EFF=2023-01-01, BASE_SALARY=78000,  REASON='Annual review')
- (SALARY_ID=12, EMP_ID=12, EFF=2023-01-01, BASE_SALARY=52000,  REASON='Annual review')
- (SALARY_ID=20, EMP_ID=20, EFF=2023-01-01, BASE_SALARY=260000, REASON='Annual review')
- (SALARY_ID=21, EMP_ID=21, EFF=2023-01-01, BASE_SALARY=135000, REASON='Annual review')
- (SALARY_ID=22, EMP_ID=22, EFF=2023-01-01, BASE_SALARY=95000,  REASON='Annual review')
- (SALARY_ID=23, EMP_ID=23, EFF=2023-01-01, BASE_SALARY=72000,  REASON='Annual review')
- (SALARY_ID=24, EMP_ID=24, EFF=2022-06-15, BASE_SALARY=48000,  REASON='New hire')
- (SALARY_ID=30, EMP_ID=30, EFF=2023-01-01, BASE_SALARY=195000, REASON='Annual review')
- (SALARY_ID=31, EMP_ID=31, EFF=2023-01-01, BASE_SALARY=145000, REASON='Annual review')
- (SALARY_ID=32, EMP_ID=32, EFF=2023-01-01, BASE_SALARY=115000, REASON='Annual review')
- (SALARY_ID=33, EMP_ID=33, EFF=2023-01-01, BASE_SALARY=110000, REASON='Annual review')
- (SALARY_ID=34, EMP_ID=34, EFF=2023-01-01, BASE_SALARY=82000,  REASON='Annual review')
- (SALARY_ID=35, EMP_ID=35, EFF=2023-01-01, BASE_SALARY=78000,  REASON='Annual review')
- (SALARY_ID=36, EMP_ID=36, EFF=2023-01-01, BASE_SALARY=70000,  REASON='Annual review')
- (SALARY_ID=37, EMP_ID=37, EFF=2022-01-10, BASE_SALARY=55000,  REASON='New hire')
- (SALARY_ID=40, EMP_ID=40, EFF=2023-01-01, BASE_SALARY=280000, REASON='Annual review')
- (SALARY_ID=41, EMP_ID=41, EFF=2023-01-01, BASE_SALARY=130000, REASON='Annual review')
- (SALARY_ID=42, EMP_ID=42, EFF=2023-01-01, BASE_SALARY=105000, REASON='Annual review')
- (SALARY_ID=43, EMP_ID=43, EFF=2023-01-01, BASE_SALARY=65000,  REASON='Annual review')

---

**UPDATE statements on DEPARTMENTS (setting MANAGER_EMP_ID):**
- DEPT_ID=10: MANAGER_EMP_ID=10 (Patricia Williams, VP-HR)
- DEPT_ID=20: MANAGER_EMP_ID=2  (Sarah Chen, CFO)
- DEPT_ID=30: MANAGER_EMP_ID=3  (then immediately overwritten to 30) — NOTE: two conflicting UPDATEs exist; final value is MANAGER_EMP_ID=30 (Rachel Thompson, Dir IT)
- DEPT_ID=31: MANAGER_EMP_ID=31 (Kevin Garcia, Dev Manager)
- DEPT_ID=40: MANAGER_EMP_ID=40 (Mark Davis, VP-Sales)
- DEPT_ID=1:  MANAGER_EMP_ID=1  (James Richardson, CEO)

---

=== FILE: ts-plsql-oracle-forms-hrms-main/forms/libraries/HRMS_COMMON_LIB.pll.sql ===

**Type:** Oracle Forms PL/SQL Library (PLL). Attached to all HRMS forms. No cross-package dependencies; standalone.

---

**Procedure: handle_error(p_module IN VARCHAR2, p_location IN VARCHAR2)**
- Reads SQLCODE into v_errcode (NUMBER) and SQLERRM into v_errmsg (VARCHAR2(500))
- Calls PKG_COMMON.log_error(p_module, p_location, v_errmsg, NVL(:GLOBAL.current_user, USER)) inside a nested BEGIN/EXCEPTION block; any exception there is silently swallowed (WHEN OTHERS THEN NULL) to prevent recursive error loops
- Calls MESSAGE() twice with the string `p_module || '.' || p_location || ': ' || v_errmsg` — documented as intentional: Oracle Forms requires two MESSAGE calls to ensure display on the status bar
- Raises FORM_TRIGGER_FAILURE
- Exception handling: inner block catches OTHERS silently; outer procedure propagates FORM_TRIGGER_FAILURE

**Procedure: toolbar_save()**
- Body: COMMIT_FORM

**Procedure: toolbar_clear()**
- Body: CLEAR_FORM(ASK_COMMIT)

**Procedure: toolbar_query()**
- Logic: IF :SYSTEM.MODE = 'NORMAL' THEN ENTER_QUERY; ELSIF :SYSTEM.MODE = 'ENTER-QUERY' THEN EXECUTE_QUERY; END IF

**Procedure: toolbar_first()**
- Body: FIRST_RECORD

**Procedure: toolbar_prev()**
- Body: PREVIOUS_RECORD

**Procedure: toolbar_next()**
- Body: NEXT_RECORD

**Procedure: toolbar_last()**
- Body: LAST_RECORD

**Procedure: toolbar_insert()**
- Body: CREATE_RECORD

**Procedure: toolbar_delete()**
- Body: DELETE_RECORD

**Procedure: toolbar_exit()**
- Body: EXIT_FORM(ASK_COMMIT)

**Function: format_date(p_date IN DATE) RETURN VARCHAR2**
- Returns TO_CHAR(p_date, 'MM/DD/YYYY')

**Function: format_datetime(p_date IN DATE) RETURN VARCHAR2**
- Returns TO_CHAR(p_date, 'MM/DD/YYYY HH24:MI:SS')

**Function: get_current_user() RETURN VARCHAR2**
- Returns NVL(:GLOBAL.current_user, USER)

**Function: get_session_id() RETURN NUMBER**
- Returns TO_NUMBER(:GLOBAL.session_id)
- Exception: WHEN VALUE_ERROR THEN RETURN NULL

**Procedure: check_session()**
- Calls get_session_id(); if NULL: MESSAGE('No active session. Please log in.'); RAISE FORM_TRIGGER_FAILURE
- Calls PKG_SECURITY.is_session_valid(get_session_id); if FALSE: MESSAGE('Session has expired. Please log in again.'); RAISE FORM_TRIGGER_FAILURE
- Dependencies: PKG_SECURITY.is_session_valid()

**Procedure: refresh_lov(p_lov_name IN VARCHAR2)**
- Derives v_rg_name as 'RG_' || UPPER(REPLACE(p_lov_name, 'LOV_', ''))
- If FIND_GROUP(v_rg_name) is not null (ID_NULL check), calls POPULATE_GROUP(v_rg_name)

**External Dependencies Referenced:**
- PKG_COMMON.log_error
- PKG_SECURITY.is_session_valid

**Global Variables Referenced:**
- :GLOBAL.current_user
- :GLOBAL.session_id
- :SYSTEM.MODE

---

=== FILE: ts-plsql-oracle-forms-hrms-main/forms/libraries/HRMS_VALIDATION_LIB.pll.sql ===

**Type:** Oracle Forms PL/SQL Library (PLL). Client-side validation. Attached to all HRMS forms.

**Known Issues Documented in Source:**
1. `validate_email`: rejects valid emails with subdomains (e.g., user@mail.company.com) — known drift from server-side PKG_VALIDATION which uses REGEXP_LIKE with a more permissive pattern
2. `validate_salary_range`: comment says "cached local data never refreshed" but actual implementation does a live DB query — comment/code mismatch

---

**Function: validate_email(p_email IN VARCHAR2) RETURN BOOLEAN**
- Returns TRUE if p_email IS NULL (NULL is valid, not-required check)
- Finds v_at_pos := INSTR(p_email, '@')
- Returns FALSE if v_at_pos = 0 (no @), OR v_at_pos = 1 (@ at start), OR v_at_pos = LENGTH(p_email) (@ at end)
- Finds v_dot_pos := INSTR(p_email, '.', v_at_pos) — first dot after @
- Returns FALSE if v_dot_pos = 0 (no dot after @), OR v_dot_pos = v_at_pos + 1 (dot immediately after @), OR v_dot_pos = LENGTH(p_email) (dot at end)
- Returns TRUE otherwise
- BUG: Only checks for one dot after @; rejects valid subdomains like user@mail.company.com

**Function: validate_phone(p_phone IN VARCHAR2) RETURN BOOLEAN**
- Returns TRUE if p_phone IS NULL
- Strips non-digits: v_digits := TRANSLATE(p_phone, '0123456789()-. +x', '0123456789')
- Business rule: US phone must be 10 or 11 digits; returns FALSE if LENGTH(v_digits) NOT IN (10, 11)
- Returns TRUE otherwise

**Function: validate_ssn(p_ssn IN VARCHAR2) RETURN BOOLEAN**
- Returns TRUE if p_ssn IS NULL
- Strips non-digits: v_digits := TRANSLATE(p_ssn, '0123456789-', '0123456789')
- Returns FALSE if LENGTH(v_digits) != 9
- Returns FALSE if SUBSTR(v_digits, 1, 3) = '000' (area number all zeros)
- Returns FALSE if SUBSTR(v_digits, 4, 2) = '00' (group number all zeros)
- Returns FALSE if SUBSTR(v_digits, 6, 4) = '0000' (serial number all zeros)
- Returns TRUE otherwise

**Function: validate_date_not_future(p_date IN DATE) RETURN BOOLEAN**
- Returns p_date IS NULL OR TRUNC(p_date) <= TRUNC(SYSDATE)

**Function: validate_salary_range(p_salary IN NUMBER, p_grade_id IN NUMBER) RETURN VARCHAR2**
- Returns NULL if p_salary IS NULL OR p_grade_id IS NULL (both must be present to validate)
- Queries: SELECT MIN_SALARY, MAX_SALARY FROM JOB_GRADES WHERE GRADE_ID = p_grade_id
- Returns 'Below minimum (' || TO_CHAR(v_min, 'FM$999,999') || ')' if p_salary < v_min
- Returns 'Exceeds maximum (' || TO_CHAR(v_max, 'FM$999,999') || ')' if p_salary > v_max
- Returns NULL if salary is within range
- Exception: WHEN NO_DATA_FOUND THEN RETURN 'Invalid grade'
- Tables accessed: JOB_GRADES (GRADE_ID, MIN_SALARY, MAX_SALARY)

---

=== FILE: ts-plsql-oracle-forms-hrms-main/forms/menus/HRMS_MENU.mmb.sql ===

**Type:** Oracle Forms Menu Module source representation (compiled binary HRMS_MENU.mmb). Structured comment describing menu hierarchy.

**Menu Bar: MAIN_MENUBAR**

File menu:
- Save → COMMIT_FORM
- Save & Exit → COMMIT_FORM; EXIT_FORM
- Print → RUN_PRODUCT
- Exit → EXIT_FORM

Edit menu:
- Clear Record → CLEAR_RECORD
- Duplicate Record → DUPLICATE_RECORD
- Delete Record → DELETE_RECORD
- Insert Record → CREATE_RECORD

Query menu:
- Enter Query → ENTER_QUERY
- Execute Query → EXECUTE_QUERY
- Cancel Query → EXIT_FORM
- Count Matching → COUNT_QUERY
- Fetch Next Set → SCROLL_DOWN

Navigate menu:
- First Record → FIRST_RECORD
- Previous Record → PREVIOUS_RECORD
- Next Record → NEXT_RECORD
- Last Record → LAST_RECORD
- Previous Block → PREVIOUS_BLOCK
- Next Block → NEXT_BLOCK

Modules menu:
- Employee Management → OPEN_FORM('HRMS_EMPLOYEE')
- Payroll Processing → OPEN_FORM('HRMS_PAYROLL')
- Leave Management → OPEN_FORM('HRMS_LEAVE')
- Performance Reviews → OPEN_FORM('HRMS_PERFORMANCE')
- Reports & Analytics → OPEN_FORM('HRMS_REPORTS')
- System Admin → OPEN_FORM('HRMS_ADMIN')

Admin menu:
- Change Password → SHOW_WINDOW('WIN_CHANGE_PWD')
- System Parameters → requires ADMIN permission
- User Management → requires ADMIN permission

Help menu:
- Contents → WEB.SHOW_DOCUMENT
- About HRMS → SHOW_ALERT('ALT_ABOUT')
- Support → WEB.SHOW_DOCUMENT

**Security:** Menu items enabled/disabled at runtime based on PKG_SECURITY.has_permission() checks in WHEN-NEW-FORM-INSTANCE trigger.

---

=== FILE: ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_EMPLOYEE.xml ===

**Type:** Oracle Forms XML Export. Form Module: HRMS_EMPLOYEE. Oracle Forms Builder 12c (12.2.1.4). Binary: HRMS_EMPLOYEE.fmb.

**Purpose:** Employee maintenance form — master-detail with personal info, job assignment, compensation history, and dependent management.

**Attached Libraries:** HRMS_COMMON_LIB, HRMS_VALIDATION_LIB

**Canvases:**
- CVS_MAIN (Tab canvas, 700×500): Tab pages TP_PERSONAL ("Personal Information"), TP_JOB ("Job & Compensation"), TP_DEPENDENTS ("Dependents"), TP_HISTORY ("Employment History")
- CVS_TOOLBAR (Horizontal Toolbar, 700×38)

**Window:** WIN_EMPLOYEE ("Employee Maintenance"), Document style, 720×550, PrimaryCanvas=CVS_MAIN

---

**Form-Level Trigger: WHEN-NEW-FORM-INSTANCE** (FireInEnterQueryMode=No)
- Reads session_id via TO_NUMBER(GET_APPLICATION_PROPERTY(USERNAME))
- Calls PKG_SECURITY.is_session_valid(v_session_id); if FALSE: MESSAGE('Session expired. Please log in again.'); RAISE FORM_TRIGGER_FAILURE
- Sets MDI window title to 'HRMS - Employee Maintenance [' || :GLOBAL.current_user || ']'
- Calls PKG_SECURITY.has_permission(:GLOBAL.current_emp_id, 'EMPLOYEE', 'EDIT'); if FALSE: sets EMPLOYEE block INSERT_ALLOWED, UPDATE_ALLOWED, DELETE_ALLOWED all to PROPERTY_FALSE
- Sets EMPLOYEE block DEFAULT_WHERE to `EMPLOYMENT_STATUS = 'ACTIVE' AND ACTIVE_FLAG = 'Y'`
- Calls POPULATE_GROUP for 'RG_DEPARTMENTS', 'RG_JOB_TITLES', 'RG_LOCATIONS'
- GO_BLOCK('EMPLOYEE'); EXECUTE_QUERY

**Form-Level Trigger: ON-ERROR** (FireInEnterQueryMode=Yes)
- Reads ERROR_CODE into v_errcode, ERROR_TYPE into v_errtype, ERROR_TEXT into v_errmsg
- ERROR_CODE 40202 ("Field is protected against update"): NULL — suppress silently
- ERROR_CODE 40401 ("No changes to save"): MESSAGE('No changes to save.')
- ERROR_CODE 40501 ("Oracle error: unable to reserve record"): MESSAGE('Record is locked by another user. Please try again.')
- All other error codes: MESSAGE(v_errtype || '-' || TO_CHAR(v_errcode) || ': ' || v_errmsg); RAISE FORM_TRIGGER_FAILURE

**Form-Level Trigger: KEY-EXIT** (FireInEnterQueryMode=Yes)
- If :SYSTEM.FORM_STATUS = 'CHANGED':
  - Show ALT_CONFIRM_EXIT; if ALERT_BUTTON1: COMMIT_FORM
  - If ALERT_BUTTON2: CLEAR_FORM(NO_VALIDATE)
  - Else: RAISE FORM_TRIGGER_FAILURE
- EXIT_FORM

---

**Block: EMPLOYEE**
- QueryDataSource: HRMS.EMPLOYEES (Table)
- DMLDataTarget: HRMS.EMPLOYEES (Table)
- QueryAllRecords: No; RecordsDisplayed: 1; NavigationStyle: Same Record
- KeyMode: Unique; EnforcePrimaryKey: Yes
- Insert/Update/Delete/Query: all Yes (subject to runtime permission restriction)

Items:
- EMP_ID: Number(10), PK=Yes, Visible=No, InsertAllowed=No, UpdateAllowed=No
- EMP_NUMBER: Char(20), Required=Yes, CVS_PERSONAL/TP_PERSONAL, (120,20), 150w, InsertAllowed=No, UpdateAllowed=No (display-only after insert)
- FIRST_NAME: Char(50), Required=Yes, CVS_PERSONAL/TP_PERSONAL, (120,45), 200w, CaseRestriction=Upper
- LAST_NAME: Char(50), Required=Yes, CVS_PERSONAL/TP_PERSONAL, (120,70), 200w, CaseRestriction=Upper
- DATE_OF_BIRTH: Date, FormatMask=MM/DD/YYYY, CVS_PERSONAL/TP_PERSONAL, (120,95), 100w
- GENDER: List/Poplist, Char(1), CVS_PERSONAL/TP_PERSONAL, (120,120), 120w; values: M="Male", F="Female", O="Other"
- MARITAL_STATUS: List/Poplist, Char(10), CVS_PERSONAL/TP_PERSONAL, (120,145), 120w; values: SINGLE="Single", MARRIED="Married", DIVORCED="Divorced", WIDOWED="Widowed"
- EMAIL: Char(100), CVS_PERSONAL/TP_PERSONAL, (120,170), 250w, CaseRestriction=Lower
- PHONE_WORK: Char(30), CVS_PERSONAL/TP_PERSONAL, (120,195), 150w
- PHONE_MOBILE: Char(30), CVS_PERSONAL/TP_PERSONAL, (120,220), 150w
- ADDRESS_LINE1: Char(200), CVS_PERSONAL/TP_PERSONAL, (120,255), 300w
- ADDRESS_LINE2: Char(200), CVS_PERSONAL/TP_PERSONAL, (120,280), 300w
- CITY: Char(100), CVS_PERSONAL/TP_PERSONAL, (120,305), 200w
- STATE_PROVINCE: Char(100), CVS_PERSONAL/TP_PERSONAL, (120,330), 100w
- POSTAL_CODE: Char(20), CVS_PERSONAL/TP_PERSONAL, (300,330), 80w
- HIRE_DATE: Date, FormatMask=MM/DD/YYYY, Required=Yes, CVS_JOB/TP_JOB, (120,20), 100w
- DEPT_ID: Number(10), Required=Yes, CVS_JOB/TP_JOB, (120,45), 80w, LOV=LOV_DEPARTMENTS
- DEPT_NAME_DISP: Display Item, Char(100), CVS_JOB/TP_JOB, (210,45), 200w, DatabaseItem=No
- JOB_ID: Number(10), Required=Yes, CVS_JOB/TP_JOB, (120,70), 80w, LOV=LOV_JOB_TITLES
- JOB_TITLE_DISP: Display Item, Char(100), CVS_JOB/TP_JOB, (210,70), 200w, DatabaseItem=No
- MANAGER_EMP_ID: Number(10), CVS_JOB/TP_JOB, (120,95), 80w, LOV=LOV_MANAGERS
- MANAGER_NAME_DISP: Display Item, Char(101), CVS_JOB/TP_JOB, (210,95), 200w, DatabaseItem=No
- LOCATION_CODE: Char(10), CVS_JOB/TP_JOB, (120,120), 80w, LOV=LOV_LOCATIONS
- EMPLOYMENT_TYPE: List/Poplist, Char(20), CVS_JOB/TP_JOB, (120,145), 120w; values: FULL_TIME="Full-Time", PART_TIME="Part-Time", CONTRACT="Contract", INTERN="Intern"
- EMPLOYMENT_STATUS: List/Poplist, Char(20), CVS_JOB/TP_JOB, (120,170), 120w, UpdateAllowed=No; values: ACTIVE="Active", ON_LEAVE="On Leave", SUSPENDED="Suspended", TERMINATED="Terminated"
- TERMINATION_DATE: Date, FormatMask=MM/DD/YYYY, CVS_JOB/TP_JOB, (120,195), 100w, UpdateAllowed=No
- ACTIVE_FLAG: Char(1), Visible=No
- CREATED_BY: Char(30), Visible=No, InsertAllowed=Yes, UpdateAllowed=No
- CREATED_DATE: Date, Visible=No, InsertAllowed=Yes, UpdateAllowed=No
- MODIFIED_BY: Char(30), Visible=No
- MODIFIED_DATE: Date, Visible=No

**Block Trigger: EMPLOYEE.PRE-INSERT**
- :EMPLOYEE.EMP_ID := SEQ_EMPLOYEE.NEXTVAL
- :EMPLOYEE.EMP_NUMBER := PKG_EMPLOYEE.generate_emp_number
- :EMPLOYEE.ACTIVE_FLAG := 'Y'
- :EMPLOYEE.EMPLOYMENT_STATUS := 'ACTIVE'
- :EMPLOYEE.CREATED_BY := :GLOBAL.current_user
- :EMPLOYEE.CREATED_DATE := SYSDATE

**Block Trigger: EMPLOYEE.PRE-UPDATE**
- :EMPLOYEE.MODIFIED_BY := :GLOBAL.current_user
- :EMPLOYEE.MODIFIED_DATE := SYSDATE

**Block Trigger: EMPLOYEE.POST-QUERY**
- SELECT DEPT_NAME INTO :EMPLOYEE.DEPT_NAME_DISP FROM DEPARTMENTS WHERE DEPT_ID = :EMPLOYEE.DEPT_ID; EXCEPTION WHEN NO_DATA_FOUND: set to NULL
- SELECT JOB_TITLE INTO :EMPLOYEE.JOB_TITLE_DISP FROM JOB_TITLES WHERE JOB_ID = :EMPLOYEE.JOB_ID; EXCEPTION WHEN NO_DATA_FOUND: set to NULL
- SELECT FIRST_NAME || ' ' || LAST_NAME INTO :EMPLOYEE.MANAGER_NAME_DISP FROM EMPLOYEES WHERE EMP_ID = :EMPLOYEE.MANAGER_EMP_ID; EXCEPTION WHEN NO_DATA_FOUND: set to NULL

**Block Trigger: EMPLOYEE.WHEN-VALIDATE-ITEM** (FireInEnterQueryMode=No)
- v_item := :SYSTEM.TRIGGER_ITEM
- If v_item = 'EMPLOYEE.EMAIL': calls PKG_VALIDATION.validate_email_format(:EMPLOYEE.EMAIL); if FALSE: MESSAGE('Invalid email format'); RAISE FORM_TRIGGER_FAILURE
- If v_item = 'EMPLOYEE.HIRE_DATE': if :EMPLOYEE.HIRE_DATE > SYSDATE + 90: MESSAGE('Hire date cannot be more than 90 days in the future'); RAISE FORM_TRIGGER_FAILURE
  - **Business Rule:** Hire date cannot be more than 90 days in the future
- If v_item = 'EMPLOYEE.DEPT_ID': SELECT DEPT_NAME FROM DEPARTMENTS WHERE DEPT_ID=:EMPLOYEE.DEPT_ID AND ACTIVE_FLAG='Y'; EXCEPTION NO_DATA_FOUND: MESSAGE('Invalid department'); RAISE FORM_TRIGGER_FAILURE; also populates DEPT_NAME_DISP
- If v_item = 'EMPLOYEE.JOB_ID': SELECT JOB_TITLE FROM JOB_TITLES WHERE JOB_ID=:EMPLOYEE.JOB_ID AND ACTIVE_FLAG='Y'; EXCEPTION NO_DATA_FOUND: MESSAGE('Invalid job title'); RAISE FORM_TRIGGER_FAILURE; also populates JOB_TITLE_DISP

---

**Block: SALARY** (detail of EMPLOYEE)
- QueryDataSource: HRMS.SALARY_RECORDS; RecordsDisplayed: 5
- Insert/Update/Delete: all No (read-only history display)
- Relation: EMP_SALARY_REL — JoinCondition: SALARY.EMP_ID = EMPLOYEE.EMP_ID; DeleteRecordBehavior: Cascading; AutoQuery: Yes

Items:
- SALARY_ID: PK, Visible=No
- EMP_ID: Visible=No
- EFFECTIVE_DATE: Date, FormatMask=MM/DD/YYYY, 100w, UpdateAllowed=No
- END_DATE: Date, FormatMask=MM/DD/YYYY, 100w
- BASE_SALARY: Number, FormatMask=$999,999,990.00, 120w
- CHANGE_REASON: Char, 120w
- CHANGE_PCT: Number, FormatMask=990.00%, 80w

---

**LOVs:**

LOV_DEPARTMENTS (400×300):
- RG_DEPARTMENTS query: SELECT DEPT_ID, DEPT_CODE, DEPT_NAME, COST_CENTER FROM HRMS.DEPARTMENTS WHERE ACTIVE_FLAG = 'Y' ORDER BY DEPT_NAME
- Returns: DEPT_ID → EMPLOYEE.DEPT_ID; DEPT_NAME → EMPLOYEE.DEPT_NAME_DISP

LOV_JOB_TITLES (450×300):
- RG_JOB_TITLES query: SELECT j.JOB_ID, j.JOB_CODE, j.JOB_TITLE, g.GRADE_NAME FROM HRMS.JOB_TITLES j JOIN HRMS.JOB_GRADES g ON j.GRADE_ID = g.GRADE_ID WHERE j.ACTIVE_FLAG = 'Y' ORDER BY j.JOB_TITLE
- Returns: JOB_ID → EMPLOYEE.JOB_ID; JOB_TITLE → EMPLOYEE.JOB_TITLE_DISP

LOV_MANAGERS (400×300):
- RG_MANAGERS query: SELECT EMP_ID, EMP_NUMBER, FIRST_NAME || ' ' || LAST_NAME AS MANAGER_NAME FROM HRMS.EMPLOYEES WHERE EMPLOYMENT_STATUS = 'ACTIVE' ORDER BY LAST_NAME
- Returns: EMP_ID → EMPLOYEE.MANAGER_EMP_ID; MANAGER_NAME → EMPLOYEE.MANAGER_NAME_DISP

LOV_LOCATIONS (400×300):
- RG_LOCATIONS query: SELECT LOCATION_CODE, LOCATION_NAME, CITY, STATE_PROVINCE FROM HRMS.LOCATIONS WHERE ACTIVE_FLAG = 'Y' ORDER BY LOCATION_NAME
- Returns: LOCATION_CODE → EMPLOYEE.LOCATION_CODE

---

**Alerts:**
- ALT_CONFIRM_EXIT (Caution): "You have unsaved changes. Save before exiting?" — Button1="Save", Button2="Discard", Button3="Cancel"
- ALT_CONFIRM_DELETE (Stop): "Are you sure you want to delete this employee record?" — Button1="Yes", Button2="No"

**External Dependencies:**
- PKG_SECURITY.is_session_valid
- PKG_SECURITY.has_permission (resource='EMPLOYEE', action='EDIT')
- PKG_EMPLOYEE.generate_emp_number
- PKG_VALIDATION.validate_email_format
- Sequences: SEQ_EMPLOYEE

**Database Tables/Views Accessed:**
- HRMS.EMPLOYEES (master block, POST-QUERY lookups)
- HRMS.SALARY_RECORDS (detail block)
- HRMS.DEPARTMENTS (LOV, WHEN-VALIDATE-ITEM, POST-QUERY)
- HRMS.JOB_TITLES (LOV, WHEN-VALIDATE-ITEM, POST-QUERY)
- HRMS.JOB_GRADES (LOV join)
- HRMS.LOCATIONS (LOV)

---

=== FILE: ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_LEAVE.xml ===

**Type:** Oracle Forms XML Export. Form Module: HRMS_LEAVE. Oracle Forms Builder 12c (12.2.1.4). Binary: HRMS_LEAVE.fmb.

**Purpose:** Leave management — request submission, approval workflow, balance inquiry, and team calendar view.

**Attached Libraries:** HRMS_COMMON_LIB

**Canvases:**
- CVS_MAIN (Tab canvas, 700×480): Tab pages TP_MY_REQUESTS ("My Requests"), TP_NEW_REQUEST ("Submit Request"), TP_APPROVALS ("Pending Approvals"), TP_CALENDAR ("Team Calendar")

**Window:** WIN_LEAVE ("Leave Management"), Document style, 720×520, PrimaryCanvas=CVS_MAIN

**Alert:** ALT_CONFIRM_CANCEL (Caution): "Are you sure you want to cancel this leave request?" — Button1="Yes", Button2="No"

---

**Form-Level Trigger: WHEN-NEW-FORM-INSTANCE** (FireInEnterQueryMode=No)
- Calls PKG_SECURITY.is_session_valid(TO_NUMBER(GET_APPLICATION_PROPERTY(USERNAME))); if FALSE: MESSAGE('Session expired.'); RAISE FORM_TRIGGER_FAILURE
- Sets MDI window title to 'HRMS - Leave Management [' || :GLOBAL.current_user || ']'
- Sets LEAVE_REQUEST block DEFAULT_WHERE to `EMP_ID = ` || :GLOBAL.current_emp_id || ` ORDER BY CREATED_DATE DESC`
- POPULATE_GROUP('RG_LEAVE_TYPES')
- GO_BLOCK('LEAVE_REQUEST'); EXECUTE_QUERY
- GO_BLOCK('LEAVE_BALANCE'); EXECUTE_QUERY
- GO_BLOCK('LEAVE_REQUEST')

---

**Block: LEAVE_REQUEST**
- QueryDataSource: HRMS.LEAVE_REQUESTS (Table)
- RecordsDisplayed: 8; NavigationStyle: Change Record
- Insert/Update/Delete: all No (read-only)

Items:
- REQUEST_ID: PK, Visible=No
- EMP_ID: Visible=No
- LEAVE_TYPE_NAME_DISP: Display Item, Char, 120w, DatabaseItem=No
- START_DATE: Date, FormatMask=MM/DD/YYYY, 100w
- END_DATE: Date, FormatMask=MM/DD/YYYY, 100w
- TOTAL_DAYS: Number, FormatMask=990.0, 50w
- STATUS: Char, 100w
- REASON: Char, 200w
- BTN_CANCEL_REQUEST: Push Button, "Cancel Request", 110w×25h

**BTN_CANCEL_REQUEST WHEN-BUTTON-PRESSED:**
- Business rule: if STATUS NOT IN ('PENDING', 'APPROVED'): MESSAGE('Only pending or approved requests can be cancelled.'); RAISE FORM_TRIGGER_FAILURE
- If SHOW_ALERT('ALT_CONFIRM_CANCEL') = ALERT_BUTTON1: calls PKG_LEAVE.cancel_leave_request(:LEAVE_REQUEST.REQUEST_ID, 'Cancelled by employee', :GLOBAL.current_user); MESSAGE('Leave request cancelled.'); EXECUTE_QUERY

**LEAVE_REQUEST.POST-QUERY:**
- SELECT lt.LEAVE_TYPE_NAME FROM LEAVE_TYPES lt JOIN LEAVE_REQUESTS lr ON lt.LEAVE_TYPE_ID = lr.LEAVE_TYPE_ID WHERE lr.REQUEST_ID = :LEAVE_REQUEST.REQUEST_ID → :LEAVE_REQUEST.LEAVE_TYPE_NAME_DISP
- EXCEPTION WHEN NO_DATA_FOUND: LEAVE_TYPE_NAME_DISP := 'Unknown'

---

**Block: NEW_REQUEST** (control block — not backed by a DB table)
- QueryDataSource: None; RecordsDisplayed: 1
- InsertAllowed=Yes, UpdateAllowed=No, DeleteAllowed=No

Items:
- NR_LEAVE_TYPE_ID: Number, 80w, LOV=LOV_LEAVE_TYPES
- NR_LEAVE_TYPE_DISP: Display Item, Char, 150w
- NR_START_DATE: Date, FormatMask=MM/DD/YYYY, 100w
- NR_END_DATE: Date, FormatMask=MM/DD/YYYY, 100w
- NR_HALF_DAY: Check Box, Char, CheckBoxMapping=Y,N, 20w
- NR_REASON: Text Field, Char(500), 300w×60h, MultiLine=Yes
- NR_CALC_DAYS: Display Item, Number, 50w
- NR_BALANCE_DISP: Display Item, Number, 50w
- BTN_SUBMIT: Push Button, "Submit Request", 120w×30h

**BTN_SUBMIT WHEN-BUTTON-PRESSED:**
- Validates: NR_LEAVE_TYPE_ID must not be NULL → MESSAGE('Please select a leave type.')
- Validates: NR_START_DATE must not be NULL → MESSAGE('Please enter a start date.')
- Validates: NR_END_DATE must not be NULL → MESSAGE('Please enter an end date.')
- Calls PKG_LEAVE.submit_leave_request(p_emp_id=>:GLOBAL.current_emp_id, p_leave_type_id=>:NEW_REQUEST.NR_LEAVE_TYPE_ID, p_start_date=>:NEW_REQUEST.NR_START_DATE, p_end_date=>:NEW_REQUEST.NR_END_DATE, p_half_day_flag=>NVL(:NEW_REQUEST.NR_HALF_DAY, 'N'), p_reason=>:NEW_REQUEST.NR_REASON, p_user=>:GLOBAL.current_user) → v_request_id
- MESSAGE('Leave request #' || v_request_id || ' submitted successfully.')
- CLEAR_BLOCK(NO_VALIDATE); GO_BLOCK('LEAVE_REQUEST'); EXECUTE_QUERY

---

**Block: LEAVE_BALANCE**
- QueryDataSource: HRMS.LEAVE_BALANCES (Table)
- RecordsDisplayed: 6; Insert/Update/Delete: all No

Items:
- LEAVE_TYPE_NAME_DISP: Display Item, 120w
- OPENING_BALANCE: Display Item, Number, FormatMask=990.0, 60w
- ACCRUED: Display Item, Number, FormatMask=990.0, 60w
- USED: Display Item, Number, FormatMask=990.0, 60w
- PENDING: Display Item, Number, FormatMask=990.0, 60w
- AVAILABLE: Display Item, Number, FormatMask=990.0, 60w

---

**LOV: LOV_LEAVE_TYPES** (350×250):
- RG_LEAVE_TYPES query: SELECT LEAVE_TYPE_ID, LEAVE_TYPE_CODE, LEAVE_TYPE_NAME FROM HRMS.LEAVE_TYPES WHERE ACTIVE_FLAG = 'Y' ORDER BY LEAVE_TYPE_NAME
- Returns: LEAVE_TYPE_ID → NEW_REQUEST.NR_LEAVE_TYPE_ID; LEAVE_TYPE_NAME → NEW_REQUEST.NR_LEAVE_TYPE_DISP

**External Dependencies:**
- PKG_SECURITY.is_session_valid
- PKG_LEAVE.cancel_leave_request(request_id, reason, user)
- PKG_LEAVE.submit_leave_request(emp_id, leave_type_id, start_date, end_date, half_day_flag, reason, user)

**Database Tables/Views Accessed:**
- HRMS.LEAVE_REQUESTS
- HRMS.LEAVE_BALANCES
- HRMS.LEAVE_TYPES

---

=== FILE: ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_LOGIN.xml ===

**Type:** Oracle Forms XML Export. Form Module: HRMS_LOGIN. Oracle Forms Builder 12c (12.2.1.4). Binary: HRMS_LOGIN.fmb.

**Purpose:** Login form — authenticates user and opens main menu.

**Known Issues Documented in Source:**
1. Password field transmitted in cleartext (Forms applet limitation)
2. No account lockout after failed attempts
3. No CAPTCHA or 2FA support

**Canvases:** CVS_LOGIN (Content, 700×300, BackgroundColor=white)

**Window:** WIN_LOGIN ("HRMS Login"), Dialog style, 700×320; Closeable=No, Minimizable=No, Maximizable=No, MoveAllowed=Yes, ResizeAllowed=No

---

**Form-Level Trigger: WHEN-NEW-FORM-INSTANCE** (FireInEnterQueryMode=No)
- SET_WINDOW_PROPERTY(FORMS_MDI_WINDOW, TITLE, 'HRMS Login')
- SET_WINDOW_PROPERTY('WIN_LOGIN', WINDOW_STATE, NORMAL)
- GO_ITEM('LOGIN.USERNAME')

---

**Block: LOGIN**
- QueryDataSource: None; RecordsDisplayed: 1; NavigationStyle: Same Record
- Insert/Update/Delete: all No

Items:
- COMPANY_LOGO: Image, GIF format, 200w×60h, CVS_LOGIN (250,20)
- USERNAME: Char(100), Required=Yes, CVS_LOGIN (280,120), 200w×24h
- PASSWORD: Char(100), Required=Yes, CVS_LOGIN (280,155), 200w×24h, ConcealData=Yes
- ERROR_MSG: Display Item, Char(200), CVS_LOGIN (200,230), 300w×20h, ForegroundColor=red, FontWeight=Bold
- BTN_LOGIN: Push Button, "Login", 100w×30h, CVS_LOGIN (300,195)

**BTN_LOGIN WHEN-BUTTON-PRESSED:**
- :LOGIN.ERROR_MSG := NULL
- If USERNAME IS NULL OR PASSWORD IS NULL: :LOGIN.ERROR_MSG := 'Please enter username and password.'; RAISE FORM_TRIGGER_FAILURE
- Calls PKG_SECURITY.authenticate(:LOGIN.USERNAME, :LOGIN.PASSWORD, GET_APPLICATION_PROPERTY(CLIENT_HOST)) → v_session_id
- :GLOBAL.session_id := TO_CHAR(v_session_id)
- :GLOBAL.current_user := :LOGIN.USERNAME
- SELECT EMP_ID INTO :GLOBAL.current_emp_id FROM EMPLOYEES WHERE UPPER(EMAIL) = UPPER(:LOGIN.USERNAME) AND EMPLOYMENT_STATUS = 'ACTIVE' AND ROWNUM = 1
  - **Business Rule:** Login username is matched against employee EMAIL (case-insensitive); only ACTIVE employees can log in
- OPEN_FORM('HRMS_MENU', ACTIVATE, SESSION)
- EXCEPTION WHEN OTHERS: :LOGIN.ERROR_MSG := 'Invalid username or password.'; :LOGIN.PASSWORD := NULL; GO_ITEM('LOGIN.PASSWORD'); RAISE FORM_TRIGGER_FAILURE
  - **Security Note:** Generic error message regardless of failure type (username not found vs wrong password)

**Block Trigger: KEY-NEXT-ITEM:**
- If :SYSTEM.CURSOR_ITEM = 'LOGIN.PASSWORD': DO_KEY('WHEN-BUTTON-PRESSED') (Enter key triggers login when cursor is on password field)
- Else: NEXT_ITEM

**External Dependencies:**
- PKG_SECURITY.authenticate(username, password, client_host) → session_id

**Database Tables/Views Accessed:**
- EMPLOYEES (SELECT EMP_ID WHERE UPPER(EMAIL)=UPPER(username) AND EMPLOYMENT_STATUS='ACTIVE' AND ROWNUM=1)

**Global Variables Set:**
- :GLOBAL.session_id
- :GLOBAL.current_user
- :GLOBAL.current_emp_id

---

=== FILE: ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_MENU.xml ===

**Type:** Oracle Forms XML Export. Form Module: HRMS_MENU (Main Navigation Form). Oracle Forms Builder 12c. Binary: HRMS_MENU.fmb.

**Purpose:** MDI parent form — main menu bar and navigation hub. Application shell after successful login.

**Attached Libraries:** HRMS_COMMON_LIB

**Canvases:** CVS_MAIN (Content, 740×400)

**Window:** WIN_MAIN ("HRMS Main Menu"), Document style, 760×420, PrimaryCanvas=CVS_MAIN

---

**Form-Level Trigger: WHEN-NEW-FORM-INSTANCE** (FireInEnterQueryMode=No)
- Sets MDI window title to 'Human Resource Management System (HRMS) v4.2 - ' || :GLOBAL.current_user || ' - Session: ' || :GLOBAL.session_id
- IF NOT PKG_SECURITY.has_permission(:GLOBAL.current_emp_id, 'PAYROLL', 'VIEW'): SET_MENU_ITEM_PROPERTY('MENU_MAIN.MI_PAYROLL', ENABLED, PROPERTY_FALSE)
- IF NOT PKG_SECURITY.has_permission(:GLOBAL.current_emp_id, 'ADMIN', 'VIEW'): SET_MENU_ITEM_PROPERTY('MENU_MAIN.MI_ADMIN', ENABLED, PROPERTY_FALSE)
- IF NOT PKG_SECURITY.has_permission(:GLOBAL.current_emp_id, 'REPORTS', 'VIEW'): SET_MENU_ITEM_PROPERTY('MENU_MAIN.MI_REPORTS', ENABLED, PROPERTY_FALSE)
- GO_BLOCK('MENU_CONTROL')

---

**Block: MENU_CONTROL**
- QueryDataSource: None; RecordsDisplayed: 1; NavigationStyle: Same Record
- Insert/Update/Delete: all No

Items:
- WELCOME_TEXT: Display Item, Char, DefaultValue="Welcome to the Human Resource Management System", CVS_MAIN (50,30), 600w×30h, FontSize=14, FontWeight=Bold
- USER_INFO: Display Item, Char, CVS_MAIN (50,70), 400w×20h
- BTN_EMPLOYEES ("Employee Management", 200w×60h, CVS_MAIN (50,120)): OPEN_FORM('HRMS_EMPLOYEE', ACTIVATE, SESSION)
- BTN_PAYROLL ("Payroll Processing", 200w×60h, CVS_MAIN (270,120)):
  - Check PKG_SECURITY.has_permission(:GLOBAL.current_emp_id, 'PAYROLL', 'VIEW'); if FALSE: MESSAGE('Access denied.'); RAISE FORM_TRIGGER_FAILURE
  - OPEN_FORM('HRMS_PAYROLL', ACTIVATE, SESSION)
- BTN_LEAVE ("Leave Management", 200w×60h, CVS_MAIN (490,120)): OPEN_FORM('HRMS_LEAVE', ACTIVATE, SESSION)
- BTN_PERFORMANCE ("Performance Reviews", 200w×60h, CVS_MAIN (50,200)): OPEN_FORM('HRMS_PERFORMANCE', ACTIVATE, SESSION)
- BTN_REPORTS ("Reports & Analytics", 200w×60h, CVS_MAIN (270,200)):
  - Check PKG_SECURITY.has_permission(:GLOBAL.current_emp_id, 'REPORTS', 'VIEW'); if FALSE: MESSAGE('Access denied.'); RAISE FORM_TRIGGER_FAILURE
  - OPEN_FORM('HRMS_REPORTS', ACTIVATE, SESSION)
- BTN_LOGOUT ("Logout", 200w×60h, CVS_MAIN (490,200)):
  - PKG_SECURITY.logout(TO_NUMBER(:GLOBAL.session_id)); EXIT_FORM

---

**MenuModule: MENU_MAIN**

FILE_MENU:
- MI_LOGOUT: `PKG_SECURITY.logout(TO_NUMBER(:GLOBAL.session_id)); EXIT_FORM;`

MODULES_MENU:
- MI_EMPLOYEES: `OPEN_FORM('HRMS_EMPLOYEE', ACTIVATE, SESSION);`
- MI_PAYROLL: `OPEN_FORM('HRMS_PAYROLL', ACTIVATE, SESSION);`
- MI_LEAVE: `OPEN_FORM('HRMS_LEAVE', ACTIVATE, SESSION);`
- MI_PERFORMANCE: `OPEN_FORM('HRMS_PERFORMANCE', ACTIVATE, SESSION);`
- MI_REPORTS: `OPEN_FORM('HRMS_REPORTS', ACTIVATE, SESSION);`

ADMIN_MENU:
- MI_ADMIN: `OPEN_FORM('HRMS_ADMIN', ACTIVATE, SESSION);`
- MI_CHANGE_PWD: `SHOW_WINDOW('WIN_CHANGE_PWD');`

HELP_MENU:
- MI_ABOUT: `MESSAGE('HRMS v4.2 - Build 2024.03.15');`
  - **Version/Build info:** HRMS v4.2, Build date 2024.03.15

**External Dependencies:**
- PKG_SECURITY.has_permission(emp_id, resource, action) — resources: 'PAYROLL'/'VIEW', 'ADMIN'/'VIEW', 'REPORTS'/'VIEW'
- PKG_SECURITY.logout(session_id)

---

=== FILE: ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_PAYROLL.xml ===

**Type:** Oracle Forms XML Export. Form Module: HRMS_PAYROLL. Oracle Forms Builder 12c. Binary: HRMS_PAYROLL.fmb.

**Purpose:** Payroll processing — pay period management, payroll run creation, calculation, approval, and pay register generation.

**Attached Libraries:** HRMS_COMMON_LIB

**Canvases:** CVS_MAIN (Tab canvas, 750×520): Tab pages TP_PERIODS ("Pay Periods"), TP_RUNS ("Payroll Runs"), TP_DETAILS ("Pay Details")

**Window:** WIN_PAYROLL ("Payroll Processing"), Document style, 770×560, PrimaryCanvas=CVS_MAIN

---

**Form-Level Trigger: WHEN-NEW-FORM-INSTANCE** (FireInEnterQueryMode=No)
- v_session_id := TO_NUMBER(GET_APPLICATION_PROPERTY(USERNAME))
- IF NOT PKG_SECURITY.is_session_valid(v_session_id): MESSAGE('Session expired. Please log in again.'); RAISE FORM_TRIGGER_FAILURE
- IF NOT PKG_SECURITY.has_permission(:GLOBAL.current_emp_id, 'PAYROLL', 'VIEW'): MESSAGE('You do not have permission to access the Payroll module.'); RAISE FORM_TRIGGER_FAILURE
- Sets MDI title to 'HRMS - Payroll Processing [' || :GLOBAL.current_user || ']'
- GO_BLOCK('PAY_PERIOD'); SET_BLOCK_PROPERTY DEFAULT_WHERE to `STATUS = 'OPEN' ORDER BY PERIOD_START_DATE DESC`; EXECUTE_QUERY

---

**Block: PAY_PERIOD**
- QueryDataSource: HRMS.PAY_PERIODS (Table)
- RecordsDisplayed: 10; NavigationStyle: Change Record
- Insert/Update/Delete: all No

Items:
- PERIOD_ID: PK, Visible=No
- PERIOD_NAME: Char, 150w
- PERIOD_START_DATE: Date, FormatMask=MM/DD/YYYY, 100w
- PERIOD_END_DATE: Date, FormatMask=MM/DD/YYYY, 100w
- PAY_DATE: Date, FormatMask=MM/DD/YYYY, 100w
- STATUS: Char, 80w

---

**Block: PAYROLL_RUN**
- QueryDataSource: HRMS.PAYROLL_RUNS (Table)
- RecordsDisplayed: 5; NavigationStyle: Change Record
- Insert/Update/Delete: all No
- Relation: PERIOD_RUN_REL — JoinCondition: PAYROLL_RUN.PERIOD_ID = PAY_PERIOD.PERIOD_ID; AutoQuery: Yes

Items:
- RUN_ID: PK, Visible=No
- PERIOD_ID: Visible=No
- RUN_TYPE: Char, 100w
- RUN_DATE: Date, FormatMask=MM/DD/YYYY HH24:MI, 140w
- STATUS: Char, 100w
- EMPLOYEE_COUNT: Number, 60w
- TOTAL_GROSS: Number, FormatMask=$999,999,990.00, 120w
- TOTAL_NET: Number, FormatMask=$999,999,990.00, 120w
- BTN_CREATE_RUN: Push Button, "Create Run", 100w×25h, CVS_RUNS/TP_RUNS
- BTN_CALCULATE: Push Button, "Calculate", 100w×25h, CVS_RUNS/TP_RUNS
- BTN_APPROVE: Push Button, "Approve", 100w×25h, CVS_RUNS/TP_RUNS

**BTN_CREATE_RUN WHEN-BUTTON-PRESSED:**
- v_run_id := PKG_PAYROLL.create_payroll_run(:PAY_PERIOD.PERIOD_ID, 'REGULAR', :GLOBAL.current_user)
- MESSAGE('Payroll run ' || v_run_id || ' created successfully.')
- GO_BLOCK('PAYROLL_RUN'); EXECUTE_QUERY

**BTN_CALCULATE WHEN-BUTTON-PRESSED:**
- Business rule: IF :PAYROLL_RUN.STATUS != 'PENDING': MESSAGE('Can only calculate runs in PENDING status.'); RAISE FORM_TRIGGER_FAILURE
- MESSAGE('Calculating payroll... Please wait.'); SYNCHRONIZE
- PKG_PAYROLL.calculate_payroll(:PAYROLL_RUN.RUN_ID, :GLOBAL.current_user)
- MESSAGE('Payroll calculation complete.'); EXECUTE_QUERY

**BTN_APPROVE WHEN-BUTTON-PRESSED:**
- Business rule: IF NOT PKG_SECURITY.has_permission(:GLOBAL.current_emp_id, 'PAYROLL', 'APPROVE'): MESSAGE('You do not have permission to approve payroll.'); RAISE FORM_TRIGGER_FAILURE
- PKG_PAYROLL.approve_payroll(:PAYROLL_RUN.RUN_ID, :GLOBAL.current_user)
- MESSAGE('Payroll run approved.'); EXECUTE_QUERY

**External Dependencies:**
- PKG_SECURITY.is_session_valid
- PKG_SECURITY.has_permission(emp_id, 'PAYROLL', 'VIEW')
- PKG_SECURITY.has_permission(emp_id, 'PAYROLL', 'APPROVE')
- PKG_PAYROLL.create_payroll_run(period_id, run_type, user) → run_id
- PKG_PAYROLL.calculate_payroll(run_id, user)
- PKG_PAYROLL.approve_payroll(run_id, user)

**Database Tables/Views Accessed:**
- HRMS.PAY_PERIODS
- HRMS.PAYROLL_RUNS

---

=== FILE: ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_PERFORMANCE.xml ===

**Type:** Oracle Forms XML Export. Form Module: HRMS_PERFORMANCE. Oracle Forms Builder 12c. Binary: HRMS_PERFORMANCE.fmb.

**Purpose:** Performance review management — review cycles, self-assessments, manager reviews, goal tracking, and rating calibration.

**Attached Libraries:** HRMS_COMMON_LIB

**Canvases:** CVS_MAIN (Tab canvas, 750×520): Tab pages TP_CYCLES ("Review Cycles"), TP_REVIEWS ("My Reviews"), TP_GOALS ("Goals")

**Window:** WIN_PERFORMANCE ("Performance Management"), Document style, 770×560, PrimaryCanvas=CVS_MAIN

---

**Form-Level Trigger: WHEN-NEW-FORM-INSTANCE** (FireInEnterQueryMode=No)
- IF NOT PKG_SECURITY.is_session_valid(TO_NUMBER(GET_APPLICATION_PROPERTY(USERNAME))): MESSAGE('Session expired.'); RAISE FORM_TRIGGER_FAILURE
- Sets MDI title to 'HRMS - Performance Management [' || :GLOBAL.current_user || ']'
- GO_BLOCK('REVIEW_CYCLE'); SET_BLOCK_PROPERTY DEFAULT_WHERE to `STATUS IN ('OPEN', 'DRAFT') ORDER BY CYCLE_YEAR DESC`; EXECUTE_QUERY

---

**Block: REVIEW_CYCLE**
- QueryDataSource: HRMS.REVIEW_CYCLES (Table)
- RecordsDisplayed: 5; Insert/Update/Delete: all No

Items:
- CYCLE_ID: PK, Visible=No
- CYCLE_NAME: Char, 200w
- CYCLE_YEAR: Number, 50w
- START_DATE: Date, FormatMask=MM/DD/YYYY, 100w
- END_DATE: Date, FormatMask=MM/DD/YYYY, 100w
- STATUS: Char, 80w

---

**Block: PERFORMANCE_REVIEW**
- QueryDataSource: HRMS.PERFORMANCE_REVIEWS (Table)
- RecordsDisplayed: 8; InsertAllowed=No, UpdateAllowed=Yes, DeleteAllowed=No
- Relation: CYCLE_REVIEW_REL — JoinCondition: PERFORMANCE_REVIEW.CYCLE_ID = REVIEW_CYCLE.CYCLE_ID; AutoQuery: Yes

Items:
- REVIEW_ID: PK, Visible=No
- CYCLE_ID: Visible=No
- EMP_ID: Visible=No
- EMP_NAME_DISP: Display Item, Char, 180w
- STATUS: Char, 120w, UpdateAllowed=No
- OVERALL_RATING: Number, FormatMask=9.0, 50w
- RATING_LABEL: Display Item, Char, 150w
- SELF_ASSESSMENT: Char, 300w×80h, MultiLine=Yes
- MANAGER_ASSESSMENT: Char, 300w×80h, MultiLine=Yes

**PERFORMANCE_REVIEW.POST-QUERY:**
- SELECT FIRST_NAME || ' ' || LAST_NAME INTO :PERFORMANCE_REVIEW.EMP_NAME_DISP FROM EMPLOYEES WHERE EMP_ID = :PERFORMANCE_REVIEW.EMP_ID
- EXCEPTION WHEN NO_DATA_FOUND: EMP_NAME_DISP := 'Unknown'

---

**Block: PERFORMANCE_GOAL**
- QueryDataSource: HRMS.PERFORMANCE_GOALS (Table)
- RecordsDisplayed: 5; InsertAllowed=Yes, UpdateAllowed=Yes, DeleteAllowed=No
- Relation: REVIEW_GOAL_REL — JoinCondition: PERFORMANCE_GOAL.REVIEW_ID = PERFORMANCE_REVIEW.REVIEW_ID; AutoQuery: Yes

Items:
- GOAL_ID: PK, Visible=No
- REVIEW_ID: Visible=No
- GOAL_TITLE: Char, 250w
- GOAL_CATEGORY: List/Poplist, Char, 100w; values: BUSINESS="Business", DEVELOPMENT="Development", LEADERSHIP="Leadership"
- WEIGHT_PCT: Number, FormatMask=990, 50w
- PROGRESS_PCT: Number, FormatMask=990, 50w
- STATUS: Char, 100w

**External Dependencies:**
- PKG_SECURITY.is_session_valid

**Database Tables/Views Accessed:**
- HRMS.REVIEW_CYCLES
- HRMS.PERFORMANCE_REVIEWS
- HRMS.PERFORMANCE_GOALS
- HRMS.EMPLOYEES (POST-QUERY lookup)

---

=== FILE: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_AUDIT.pks ===

**Package:** HRMS.PKG_AUDIT — Audit Trail Package specification.

**Dependencies:** None (base package). Called by: all other packages, database triggers.

---

**Procedure: log_action(p_table_name IN VARCHAR2, p_record_id IN NUMBER, p_action IN VARCHAR2, p_user IN VARCHAR2 DEFAULT USER, p_old_values IN CLOB DEFAULT NULL, p_new_values IN CLOB DEFAULT NULL)**

**Procedure: purge_old_records(p_days_to_keep IN NUMBER DEFAULT 365, p_user IN VARCHAR2 DEFAULT USER)**
- Default retention: 365 days

**Function: get_change_history(p_table_name IN VARCHAR2, p_record_id IN NUMBER, p_from_date IN DATE DEFAULT NULL, p_to_date IN DATE DEFAULT NULL) RETURN SYS_REFCURSOR**

---

=== FILE: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_AUDIT.pkb ===

**Package Body:** HRMS.PKG_AUDIT

---

**Procedure: log_action(p_table_name, p_record_id, p_action, p_user DEFAULT USER, p_old_values DEFAULT NULL, p_new_values DEFAULT NULL)**
- PRAGMA AUTONOMOUS_TRANSACTION (never rolls back calling transaction)
- INSERT INTO AUDIT_LOG: AUDIT_ID=SEQ_AUDIT.NEXTVAL, TABLE_NAME=p_table_name, RECORD_ID=p_record_id, ACTION_TYPE=p_action, OLD_VALUES=p_old_values, NEW_VALUES=p_new_values, CHANGED_BY=p_user, CHANGED_DATE=SYSDATE, IP_ADDRESS=SYS_CONTEXT('USERENV','IP_ADDRESS'), SESSION_ID=SYS_CONTEXT('USERENV','SESSIONID')
- COMMIT
- EXCEPTION WHEN OTHERS: ROLLBACK (audit logging must never fail the calling transaction — documented rule)
- Columns written: AUDIT_ID, TABLE_NAME, RECORD_ID, ACTION_TYPE, OLD_VALUES, NEW_VALUES, CHANGED_BY, CHANGED_DATE, IP_ADDRESS, SESSION_ID

**Procedure: purge_old_records(p_days_to_keep IN NUMBER DEFAULT 365, p_user IN VARCHAR2 DEFAULT USER)**
- DELETE FROM AUDIT_LOG WHERE CHANGED_DATE < SYSDATE - p_days_to_keep
- v_deleted := SQL%ROWCOUNT; COMMIT
- DBMS_OUTPUT.PUT_LINE('Purged ' || v_deleted || ' audit records older than ' || p_days_to_keep || ' days')
- **Business Rule:** Default retention period is 365 days; records older than p_days_to_keep days are deleted

**Function: get_change_history(p_table_name, p_record_id, p_from_date DEFAULT NULL, p_to_date DEFAULT NULL) RETURN SYS_REFCURSOR**
- Opens cursor: SELECT AUDIT_ID, TABLE_NAME, RECORD_ID, ACTION_TYPE, OLD_VALUES, NEW_VALUES, CHANGED_BY, CHANGED_DATE, IP_ADDRESS FROM AUDIT_LOG WHERE TABLE_NAME=p_table_name AND RECORD_ID=p_record_id AND (p_from_date IS NULL OR CHANGED_DATE >= p_from_date) AND (p_to_date IS NULL OR CHANGED_DATE <= p_to_date) ORDER BY CHANGED_DATE DESC
- Returns SYS_REFCURSOR

**Database Tables/Sequences Accessed:**
- AUDIT_LOG (INSERT, DELETE, SELECT)
- SEQ_AUDIT.NEXTVAL

**SYS_CONTEXT calls:**
- SYS_CONTEXT('USERENV', 'IP_ADDRESS')
- SYS_CONTEXT('USERENV', 'SESSIONID')

---

=== FILE: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_COMMON.pks ===

**Package:** HRMS.PKG_COMMON — Shared Utility Package specification. Logging, date utilities, formatting, configuration parameter access.

**Dependencies:** None (base package — no cross-package dependencies). Called by: all other packages, all forms.

---

**Type: t_error_rec (RECORD)**
- error_id: NUMBER
- package_name: VARCHAR2(60)
- procedure_name: VARCHAR2(60)
- error_message: VARCHAR2(4000)
- error_date: DATE
- username: VARCHAR2(30)

**Procedure: log_error(p_package IN VARCHAR2, p_procedure IN VARCHAR2, p_message IN VARCHAR2, p_user IN VARCHAR2 DEFAULT USER)**

**Procedure: log_info(p_package IN VARCHAR2, p_procedure IN VARCHAR2, p_message IN VARCHAR2, p_user IN VARCHAR2 DEFAULT USER)**

**Function: get_param(p_group IN VARCHAR2, p_code IN VARCHAR2) RETURN VARCHAR2**

**Function: get_param_number(p_group IN VARCHAR2, p_code IN VARCHAR2) RETURN NUMBER**

**Function: get_param_date(p_group IN VARCHAR2, p_code IN VARCHAR2) RETURN DATE**

**Procedure: set_param(p_group IN VARCHAR2, p_code IN VARCHAR2, p_value IN VARCHAR2, p_user IN VARCHAR2 DEFAULT USER)**

**Function: business_days_between(p_start_date IN DATE, p_end_date IN DATE) RETURN NUMBER**

**Function: add_business_days(p_date IN DATE, p_days IN NUMBER) RETURN DATE**

**Function: get_fiscal_year(p_date IN DATE DEFAULT SYSDATE) RETURN NUMBER**

**Function: get_fiscal_quarter(p_date IN DATE DEFAULT SYSDATE) RETURN NUMBER**

**Function: format_phone(p_phone IN VARCHAR2) RETURN VARCHAR2**

**Function: format_ssn_masked(p_ssn IN VARCHAR2) RETURN VARCHAR2**

**Function: format_currency(p_amount IN NUMBER, p_currency_code IN VARCHAR2 DEFAULT 'USD') RETURN VARCHAR2**

**Function: format_name(p_first_name IN VARCHAR2, p_last_name IN VARCHAR2, p_format IN VARCHAR2 DEFAULT 'FL') RETURN VARCHAR2**
- p_format values: 'FL' = First Last, 'LF' = Last, First

**Function: is_valid_email(p_email IN VARCHAR2) RETURN BOOLEAN**

**Function: is_valid_phone(p_phone IN VARCHAR2) RETURN BOOLEAN**

**Function: is_valid_ssn(p_ssn IN VARCHAR2) RETURN BOOLEAN**

---

=== FILE: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_COMMON.pkb ===

**Package Body:** HRMS.PKG_COMMON

---

**Procedure: log_error(p_package, p_procedure, p_message, p_user DEFAULT USER)**
- PRAGMA AUTONOMOUS_TRANSACTION
- INSERT INTO AUDIT_LOG: AUDIT_ID=SEQ_AUDIT.NEXTVAL, TABLE_NAME='ERROR_LOG', RECORD_ID=0, ACTION_TYPE='INSERT', OLD_VALUES=NULL, NEW_VALUES='{"package":"' || p_package || '","procedure":"' || p_procedure || '","message":"' || REPLACE(SUBSTR(p_message, 1, 3000), '"', '\"') || '"}', CHANGED_BY=p_user, CHANGED_DATE=SYSDATE
- COMMIT
- EXCEPTION WHEN OTHERS: DBMS_OUTPUT.PUT_LINE('ERROR LOG FAILED: ' || p_package || '.' || p_procedure || ': ' || p_message); ROLLBACK
- Message truncated to 3000 characters (SUBSTR(p_message, 1, 3000))

**Procedure: log_info(p_package, p_procedure, p_message, p_user DEFAULT USER)**
- PRAGMA AUTONOMOUS_TRANSACTION
- INSERT INTO AUDIT_LOG: AUDIT_ID=SEQ_AUDIT.NEXTVAL, TABLE_NAME='INFO_LOG', RECORD_ID=0, ACTION_TYPE='INSERT', NEW_VALUES='{"package":"' || p_package || '","procedure":"' || p_procedure || '","message":"' || SUBSTR(p_message, 1, 3000) || '"}', CHANGED_BY=p_user, CHANGED_DATE=SYSDATE
- COMMIT
- EXCEPTION WHEN OTHERS: ROLLBACK

**Function: get_param(p_group IN VARCHAR2, p_code IN VARCHAR2) RETURN VARCHAR2**
- SELECT PARAM_VALUE FROM SYSTEM_PARAMETERS WHERE PARAM_GROUP = p_group AND PARAM_CODE = p_code
- EXCEPTION WHEN NO_DATA_FOUND: RETURN NULL

**Function: get_param_number(p_group, p_code) RETURN NUMBER**
- Calls TO_NUMBER(get_param(p_group, p_code))
- EXCEPTION WHEN VALUE_ERROR: RETURN NULL

**Function: get_param_date(p_group, p_code) RETURN DATE**
- Calls TO_DATE(get_param(p_group, p_code), 'YYYY-MM-DD')
- EXCEPTION WHEN OTHERS: RETURN NULL

**Procedure: set_param(p_group, p_code, p_value, p_user DEFAULT USER)**
- UPDATE SYSTEM_PARAMETERS SET PARAM_VALUE=p_value, MODIFIED_BY=p_user, MODIFIED_DATE=SYSDATE WHERE PARAM_GROUP=p_group AND PARAM_CODE=p_code AND EDITABLE_FLAG='Y'
- IF SQL%ROWCOUNT = 0: RAISE_APPLICATION_ERROR(-20900, 'Parameter not found or not editable: ' || p_group || '.' || p_code)
- **Business Rule:** Only parameters with EDITABLE_FLAG='Y' can be updated; error code -20900 raised otherwise

**Function: business_days_between(p_start_date IN DATE, p_end_date IN DATE) RETURN NUMBER**
- v_count := 0; v_date := TRUNC(p_start_date)
- Loop WHILE v_date <= TRUNC(p_end_date): IF TO_CHAR(v_date, 'DY', 'NLS_DATE_LANGUAGE=AMERICAN') NOT IN ('SAT', 'SUN'): v_count := v_count + 1; v_date := v_date + 1
- Returns v_count
- **Business Rule:** Counts business days inclusive of both start and end date; Saturday and Sunday are excluded; NLS forced to American

**Function: add_business_days(p_date IN DATE, p_days IN NUMBER) RETURN DATE**
- v_result := TRUNC(p_date); v_added := 0
- Loop WHILE v_added < p_days: v_result := v_result + 1; IF TO_CHAR(v_result, 'DY', 'NLS_DATE_LANGUAGE=AMERICAN') NOT IN ('SAT', 'SUN'): v_added := v_added + 1
- Returns v_result

**Function: get_fiscal_year(p_date IN DATE DEFAULT SYSDATE) RETURN NUMBER**
- IF EXTRACT(MONTH FROM p_date) >= 10: RETURN EXTRACT(YEAR FROM p_date) + 1
- ELSE: RETURN EXTRACT(YEAR FROM p_date)
- **Business Rule:** Fiscal year starts October (month 10); October through December of year N belongs to fiscal year N+1; January through September of year N belongs to fiscal year N

**Function: get_fiscal_quarter(p_date IN DATE DEFAULT SYSDATE) RETURN NUMBER**
- v_month := EXTRACT(MONTH FROM p_date)
- CASE: months 10,11,12 → Q1; months 1,2,3 → Q2; months 4,5,6 → Q3; months 7,8,9 → Q4
- **Business Rule:** Fiscal quarters based on October fiscal year start: Q1=Oct-Dec, Q2=Jan-Mar, Q3=Apr-Jun, Q4=Jul-Sep

**Function: format_phone(p_phone IN VARCHAR2) RETURN VARCHAR2**
- v_digits := REGEXP_REPLACE(p_phone, '[^0-9]', '') — strip all non-digits
- If LENGTH(v_digits) = 10: return '(' || SUBSTR(v_digits,1,3) || ') ' || SUBSTR(v_digits,4,3) || '-' || SUBSTR(v_digits,7,4)
- Elsif LENGTH(v_digits) = 11 AND SUBSTR(v_digits,1,1) = '1': return '+1 (' || SUBSTR(v_digits,2,3) || ') ' || SUBSTR(v_digits,5,3) || '-' || SUBSTR(v_digits,8,4)
- Else: return p_phone unchanged

**Function: format_ssn_masked(p_ssn IN VARCHAR2) RETURN VARCHAR2**
- If p_ssn IS NULL OR LENGTH(p_ssn) < 4: RETURN '***-**-****'
- Else: RETURN '***-**-' || SUBSTR(p_ssn, -4) — shows only last 4 digits

**Function: format_currency(p_amount IN NUMBER, p_currency_code IN VARCHAR2 DEFAULT 'USD') RETURN VARCHAR2**
- CASE p_currency_code:
  - 'USD' → '$'
  - 'EUR' → CHR(8364) (€)
  - 'GBP' → CHR(163) (£)
  - else → p_currency_code || ' '
- Appended with TO_CHAR(p_amount, 'FM999,999,990.00')

**Function: format_name(p_first_name, p_last_name, p_format DEFAULT 'FL') RETURN VARCHAR2**
- If p_format = 'LF': RETURN INITCAP(p_last_name) || ', ' || INITCAP(p_first_name)
- Else (default 'FL'): RETURN INITCAP(p_first_name) || ' ' || INITCAP(p_last_name)

**Function: is_valid_email(p_email IN VARCHAR2) RETURN BOOLEAN**
- RETURN REGEXP_LIKE(p_email, '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
- **Note:** Server-side validation uses REGEXP_LIKE with this more permissive pattern that accepts subdomains, unlike the client-side validate_email in HRMS_VALIDATION_LIB

**Function: is_valid_phone(p_phone IN VARCHAR2) RETURN BOOLEAN**
- v_digits := REGEXP_REPLACE(p_phone, '[^0-9]', '')
- RETURN LENGTH(v_digits) BETWEEN 10 AND 11

**Function: is_valid_ssn(p_ssn IN VARCHAR2) RETURN BOOLEAN**
- RETURN REGEXP_LIKE(REGEXP_REPLACE(p_ssn, '[^0-9]', ''), '^\d{9}$')

**Database Tables/Sequences Accessed:**
- AUDIT_LOG (INSERT via log_error, log_info)
- SYSTEM_PARAMETERS (SELECT via get_param; UPDATE via set_param)
- SEQ_AUDIT.NEXTVAL

**Exceptions Raised:**
- RAISE_APPLICATION_ERROR(-20900, 'Parameter not found or not editable: ' || p_group || '.' || p_code) — from set_param when EDITABLE_FLAG != 'Y' or parameter not found
