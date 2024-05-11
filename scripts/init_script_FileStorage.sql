CREATE TABLE FileStorage (
    UUIDColumn UUID PRIMARY KEY,
    FilePath VARCHAR(255),
    TempOrPerm VARCHAR(10) CHECK(TempOrPerm IN ('Temporary', 'Permanent')),
    Status VARCHAR(10) CHECK(Status IN ('Active', 'Deleted'))
);