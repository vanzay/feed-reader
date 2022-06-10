CREATE TABLE "feed_type"
(
    "feed_type_id" integer PRIMARY KEY,
    "code"         varchar(16) NOT NULL,
    CONSTRAINT "feed_type_code_unique" UNIQUE ("code")
);


CREATE TABLE "feed_group"
(
    "feed_group_id" integer PRIMARY KEY,
    "title"         varchar(64) NOT NULL,
    "sort_order"    int DEFAULT NULL
);


CREATE SEQUENCE "feed_id_seq";
CREATE TABLE "feed"
(
    "feed_id"       integer PRIMARY KEY DEFAULT nextval('feed_id_seq'),
    "title"         varchar(64)  NOT NULL,
    "url"           varchar(256) NOT NULL,
    "sort_order"    int          NOT NULL,
    "feed_type_id"  int          NOT NULL,
    "feed_group_id" int                 DEFAULT NULL,
    CONSTRAINT "feed_url_unique" UNIQUE ("url"),
    CONSTRAINT "fk_feed_feed_group" FOREIGN KEY ("feed_group_id") REFERENCES "feed_group" ("feed_group_id"),
    CONSTRAINT "fk_feed_feed_type" FOREIGN KEY ("feed_type_id") REFERENCES "feed_type" ("feed_type_id")
);
CREATE INDEX "fk_feed_feed_type_idx" ON "feed" ("feed_type_id");
CREATE INDEX "fk_feed_feed_group_idx" ON "feed" ("feed_group_id");
ALTER SEQUENCE "feed_id_seq" OWNED BY "feed"."feed_id";


CREATE SEQUENCE "feed_item_id_seq";
CREATE TABLE "feed_item"
(
    "feed_item_id" integer PRIMARY KEY   DEFAULT nextval('feed_item_id_seq'),
    "guid"         varchar(256) NOT NULL,
    "link"         varchar(256) NOT NULL,
    "title"        varchar(256) NOT NULL,
    "description"  text,
    "pub_date"     timestamp    NOT NULL,
    "is_read"      boolean      NOT NULL DEFAULT false,
    "feed_id"      int          NOT NULL,
    CONSTRAINT "fk_feed_item_feed" FOREIGN KEY ("feed_id") REFERENCES "feed" ("feed_id")
);
CREATE INDEX "fk_feed_item_feed_idx" ON "feed_item" ("feed_id");
ALTER SEQUENCE "feed_item_id_seq" OWNED BY "feed_item"."feed_item_id";
