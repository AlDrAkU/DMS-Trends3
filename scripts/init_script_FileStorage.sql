CREATE TABLE FileStorage (
    UUIDColumn VARCHAR(36) PRIMARY KEY,
    FilePath VARCHAR(255),
    TimeStamp TIMESTAMP,
    DocType VARCHAR(10) CHECK(DocType IN ('Invoice', 'Paycheck', 'Other')),
    TempOrPerm VARCHAR(10) CHECK(TempOrPerm IN ('Temporary', 'Permanent')),
    Status VARCHAR(10) CHECK(Status IN ('Active', 'Deleted'))
);