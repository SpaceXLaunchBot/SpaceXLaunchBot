#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE TYPE notification AS ENUM ('all', 'schedule', 'launch');
    CREATE TABLE subscribed_channels (
        channel_id TEXT PRIMARY KEY NOT NULL,
        guild_id TEXT NOT NULL,
        channel_name TEXT NOT NULL,
        notification_type notification NOT NULL,
        launch_mentions TEXT
    );
    CREATE TABLE metrics (
        id serial PRIMARY KEY NOT NULL,
        "action" TEXT NOT NULL,
        guild_id TEXT NOT NULL,
        "time" TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
    );
    CREATE TABLE counts (
        id serial PRIMARY KEY NOT NULL,
        guild_count INT NOT NULL,
        subscribed_count INT NOT NULL,
        "time" TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
    );
    CREATE TABLE log (
        id serial PRIMARY KEY NOT NULL,
        time TEXT,
        level TEXT,
        location TEXT,
        function TEXT,
        message TEXT
    );
EOSQL
