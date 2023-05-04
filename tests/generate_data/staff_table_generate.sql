-- Generate some sample data in the source database
-- create a new table called TAP_TEST_500M 
DROP TABLE TAP_TEST_500M;
CREATE TABLE TAP_TEST_500M 
(
          		  "ID" SMALLINT NOT NULL , 
		  "NAME" VARCHAR(9 OCTETS) , 
		  "DEPT" SMALLINT , 
		  "JOB" CHAR(5 OCTETS) , 
		  "YEARS" SMALLINT , 
		  "SALARY" DECIMAL(7,2) , 
		  "COMM" DECIMAL(7,2),
		  "TEST_ID" INT NOT NULL GENERATED ALWAYS AS IDENTITY
                                         (START WITH 100, INCREMENT BY 5)
		  ) ;

TRUNCATE TABLE  TAP_TEST_500M IMMEDIATE;

-- This statement recursively generates rows from a cross-join to the STAFF table in the SAMPLE database
-- adjust the WHERE clause to generate more rows - too high a value can fill the transaction log
INSERT INTO TAP_TEST_500M ("ID","NAME","DEPT","JOB","YEARS","SALARY","COMM")
WITH T (I) AS 
(
SELECT 0 FROM SYSIBM.SYSDUMMY1
    UNION ALL
SELECT I+1 FROM T WHERE I < 2000
)
SELECT Staff.*
FROM T,STAFF;

WITH T (I) AS 
(
SELECT 0 FROM SYSIBM.SYSDUMMY1
    UNION ALL
SELECT I+1 FROM T WHERE I <= 14284
)
SELECT count(*)
FROM T,STAFF;

SELECT count(*)
FROM TAP_TEST_500M;

