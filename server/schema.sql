BEGIN TRANSACTION;

DROP TABLE IF EXISTS utmp;
CREATE TABLE utmp (
	host     varchar(255)  NOT NULL,
	user     varchar(64)   NOT NULL,
	uid      integer,
	rhost    varchar(255),
	line     varchar(32),
	time     integer,
	updated  integer
);

COMMIT;
