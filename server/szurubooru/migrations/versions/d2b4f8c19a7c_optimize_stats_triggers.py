"""
Optimize stats triggers for bulk write performance.

Revision ID: d2b4f8c19a7c
Revises: c9f1a3b2d0e4
Created at: 2026-01-23
"""

from alembic import op


revision = "d2b4f8c19a7c"
down_revision = "c9f1a3b2d0e4"
branch_labels = None
depends_on = None


def upgrade():
    # Drop row-level constraint triggers + functions for heavy tables
    op.execute("DROP TRIGGER IF EXISTS trg_stats_post_tag ON post_tag")
    op.execute("DROP FUNCTION IF EXISTS stats_update_post_tag()")
    op.execute("DROP TRIGGER IF EXISTS trg_stats_pool_post ON pool_post")
    op.execute("DROP FUNCTION IF EXISTS stats_update_pool_post()")

    # Statement-level trigger functions using transition tables
    op.execute(
        """
        CREATE OR REPLACE FUNCTION stats_update_post_tag_stmt_insert() RETURNS trigger AS $$
        BEGIN
            INSERT INTO post_statistics (post_id, tag_count)
            SELECT post_id, COUNT(*) AS cnt
            FROM new_rows
            GROUP BY post_id
            ON CONFLICT (post_id) DO UPDATE SET
                tag_count = post_statistics.tag_count + EXCLUDED.tag_count;

            INSERT INTO tag_statistics (tag_id, usage_count)
            SELECT tag_id, COUNT(*) AS cnt
            FROM new_rows
            GROUP BY tag_id
            ON CONFLICT (tag_id) DO UPDATE SET
                usage_count = tag_statistics.usage_count + EXCLUDED.usage_count;
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION stats_update_post_tag_stmt_delete() RETURNS trigger AS $$
        BEGIN
            UPDATE post_statistics ps
            SET tag_count = ps.tag_count - del.cnt
            FROM (
                SELECT post_id, COUNT(*) AS cnt
                FROM old_rows
                GROUP BY post_id
            ) del
            WHERE ps.post_id = del.post_id;

            UPDATE tag_statistics ts
            SET usage_count = ts.usage_count - del.cnt
            FROM (
                SELECT tag_id, COUNT(*) AS cnt
                FROM old_rows
                GROUP BY tag_id
            ) del
            WHERE ts.tag_id = del.tag_id;
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION stats_update_post_tag_stmt_update() RETURNS trigger AS $$
        BEGIN
            UPDATE post_statistics ps
            SET tag_count = ps.tag_count - del.cnt
            FROM (
                SELECT post_id, COUNT(*) AS cnt
                FROM old_rows
                GROUP BY post_id
            ) del
            WHERE ps.post_id = del.post_id;

            INSERT INTO post_statistics (post_id, tag_count)
            SELECT post_id, COUNT(*) AS cnt
            FROM new_rows
            GROUP BY post_id
            ON CONFLICT (post_id) DO UPDATE SET
                tag_count = post_statistics.tag_count + EXCLUDED.tag_count;

            UPDATE tag_statistics ts
            SET usage_count = ts.usage_count - del.cnt
            FROM (
                SELECT tag_id, COUNT(*) AS cnt
                FROM old_rows
                GROUP BY tag_id
            ) del
            WHERE ts.tag_id = del.tag_id;

            INSERT INTO tag_statistics (tag_id, usage_count)
            SELECT tag_id, COUNT(*) AS cnt
            FROM new_rows
            GROUP BY tag_id
            ON CONFLICT (tag_id) DO UPDATE SET
                usage_count = tag_statistics.usage_count + EXCLUDED.usage_count;
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION stats_update_pool_post_stmt_insert() RETURNS trigger AS $$
        BEGIN
            INSERT INTO pool_statistics (pool_id, post_count)
            SELECT pool_id, COUNT(*) AS cnt
            FROM new_rows
            GROUP BY pool_id
            ON CONFLICT (pool_id) DO UPDATE SET
                post_count = pool_statistics.post_count + EXCLUDED.post_count;

            INSERT INTO post_statistics (post_id, pool_count)
            SELECT post_id, COUNT(*) AS cnt
            FROM new_rows
            GROUP BY post_id
            ON CONFLICT (post_id) DO UPDATE SET
                pool_count = post_statistics.pool_count + EXCLUDED.pool_count;
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION stats_update_pool_post_stmt_delete() RETURNS trigger AS $$
        BEGIN
            UPDATE pool_statistics ps
            SET post_count = ps.post_count - del.cnt
            FROM (
                SELECT pool_id, COUNT(*) AS cnt
                FROM old_rows
                GROUP BY pool_id
            ) del
            WHERE ps.pool_id = del.pool_id;

            UPDATE post_statistics ps2
            SET pool_count = ps2.pool_count - del.cnt
            FROM (
                SELECT post_id, COUNT(*) AS cnt
                FROM old_rows
                GROUP BY post_id
            ) del
            WHERE ps2.post_id = del.post_id;
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION stats_update_pool_post_stmt_update() RETURNS trigger AS $$
        BEGIN
            UPDATE pool_statistics ps
            SET post_count = ps.post_count - del.cnt
            FROM (
                SELECT pool_id, COUNT(*) AS cnt
                FROM old_rows
                GROUP BY pool_id
            ) del
            WHERE ps.pool_id = del.pool_id;

            INSERT INTO pool_statistics (pool_id, post_count)
            SELECT pool_id, COUNT(*) AS cnt
            FROM new_rows
            GROUP BY pool_id
            ON CONFLICT (pool_id) DO UPDATE SET
                post_count = pool_statistics.post_count + EXCLUDED.post_count;

            UPDATE post_statistics ps2
            SET pool_count = ps2.pool_count - del.cnt
            FROM (
                SELECT post_id, COUNT(*) AS cnt
                FROM old_rows
                GROUP BY post_id
            ) del
            WHERE ps2.post_id = del.post_id;

            INSERT INTO post_statistics (post_id, pool_count)
            SELECT post_id, COUNT(*) AS cnt
            FROM new_rows
            GROUP BY post_id
            ON CONFLICT (post_id) DO UPDATE SET
                pool_count = post_statistics.pool_count + EXCLUDED.pool_count;
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    op.execute(
        """
        CREATE TRIGGER trg_stats_post_tag_stmt_insert
        AFTER INSERT ON post_tag
        REFERENCING NEW TABLE AS new_rows
        FOR EACH STATEMENT EXECUTE FUNCTION stats_update_post_tag_stmt_insert();
        """
    )

    op.execute(
        """
        CREATE TRIGGER trg_stats_post_tag_stmt_delete
        AFTER DELETE ON post_tag
        REFERENCING OLD TABLE AS old_rows
        FOR EACH STATEMENT EXECUTE FUNCTION stats_update_post_tag_stmt_delete();
        """
    )

    op.execute(
        """
        CREATE TRIGGER trg_stats_post_tag_stmt_update
        AFTER UPDATE ON post_tag
        REFERENCING NEW TABLE AS new_rows OLD TABLE AS old_rows
        FOR EACH STATEMENT EXECUTE FUNCTION stats_update_post_tag_stmt_update();
        """
    )

    op.execute(
        """
        CREATE TRIGGER trg_stats_pool_post_stmt_insert
        AFTER INSERT ON pool_post
        REFERENCING NEW TABLE AS new_rows
        FOR EACH STATEMENT EXECUTE FUNCTION stats_update_pool_post_stmt_insert();
        """
    )

    op.execute(
        """
        CREATE TRIGGER trg_stats_pool_post_stmt_delete
        AFTER DELETE ON pool_post
        REFERENCING OLD TABLE AS old_rows
        FOR EACH STATEMENT EXECUTE FUNCTION stats_update_pool_post_stmt_delete();
        """
    )

    op.execute(
        """
        CREATE TRIGGER trg_stats_pool_post_stmt_update
        AFTER UPDATE ON pool_post
        REFERENCING NEW TABLE AS new_rows OLD TABLE AS old_rows
        FOR EACH STATEMENT EXECUTE FUNCTION stats_update_pool_post_stmt_update();
        """
    )

    # Add supporting indexes for "last_*" recalculation queries
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_post_favorite_post_time "
        "ON post_favorite (post_id, time DESC)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_post_feature_post_time "
        "ON post_feature (post_id, time DESC)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_comment_post_creation_time "
        "ON comment (post_id, creation_time DESC)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_comment_post_last_edit_time "
        "ON comment (post_id, last_edit_time DESC) "
        "WHERE last_edit_time IS NOT NULL"
    )


def downgrade():
    op.execute("DROP INDEX IF EXISTS ix_comment_post_last_edit_time")
    op.execute("DROP INDEX IF EXISTS ix_comment_post_creation_time")
    op.execute("DROP INDEX IF EXISTS ix_post_feature_post_time")
    op.execute("DROP INDEX IF EXISTS ix_post_favorite_post_time")

    op.execute("DROP TRIGGER IF EXISTS trg_stats_pool_post_stmt_update ON pool_post")
    op.execute("DROP TRIGGER IF EXISTS trg_stats_pool_post_stmt_delete ON pool_post")
    op.execute("DROP TRIGGER IF EXISTS trg_stats_pool_post_stmt_insert ON pool_post")
    op.execute("DROP TRIGGER IF EXISTS trg_stats_post_tag_stmt_update ON post_tag")
    op.execute("DROP TRIGGER IF EXISTS trg_stats_post_tag_stmt_delete ON post_tag")
    op.execute("DROP TRIGGER IF EXISTS trg_stats_post_tag_stmt_insert ON post_tag")
    op.execute("DROP FUNCTION IF EXISTS stats_update_pool_post_stmt_update()")
    op.execute("DROP FUNCTION IF EXISTS stats_update_pool_post_stmt_delete()")
    op.execute("DROP FUNCTION IF EXISTS stats_update_pool_post_stmt_insert()")
    op.execute("DROP FUNCTION IF EXISTS stats_update_post_tag_stmt_update()")
    op.execute("DROP FUNCTION IF EXISTS stats_update_post_tag_stmt_delete()")
    op.execute("DROP FUNCTION IF EXISTS stats_update_post_tag_stmt_insert()")

    # Restore row-level constraint triggers + functions
    op.execute(
        """
        CREATE OR REPLACE FUNCTION stats_update_post_tag() RETURNS trigger AS $$
        BEGIN
            IF TG_OP = 'INSERT' THEN
                INSERT INTO post_statistics (post_id, tag_count)
                VALUES (NEW.post_id, 1)
                ON CONFLICT (post_id) DO UPDATE SET
                    tag_count = post_statistics.tag_count + 1;
                INSERT INTO tag_statistics (tag_id, usage_count)
                VALUES (NEW.tag_id, 1)
                ON CONFLICT (tag_id) DO UPDATE SET
                    usage_count = tag_statistics.usage_count + 1;
            ELSIF TG_OP = 'DELETE' THEN
                UPDATE post_statistics
                SET tag_count = tag_count - 1
                WHERE post_id = OLD.post_id;
                UPDATE tag_statistics
                SET usage_count = usage_count - 1
                WHERE tag_id = OLD.tag_id;
            ELSE
                IF NEW.post_id IS DISTINCT FROM OLD.post_id THEN
                    UPDATE post_statistics
                    SET tag_count = tag_count - 1
                    WHERE post_id = OLD.post_id;
                    INSERT INTO post_statistics (post_id, tag_count)
                    VALUES (NEW.post_id, 1)
                    ON CONFLICT (post_id) DO UPDATE SET
                        tag_count = post_statistics.tag_count + 1;
                END IF;
                IF NEW.tag_id IS DISTINCT FROM OLD.tag_id THEN
                    UPDATE tag_statistics
                    SET usage_count = usage_count - 1
                    WHERE tag_id = OLD.tag_id;
                    INSERT INTO tag_statistics (tag_id, usage_count)
                    VALUES (NEW.tag_id, 1)
                    ON CONFLICT (tag_id) DO UPDATE SET
                        usage_count = tag_statistics.usage_count + 1;
                END IF;
            END IF;
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION stats_update_pool_post() RETURNS trigger AS $$
        BEGIN
            IF TG_OP = 'INSERT' THEN
                INSERT INTO pool_statistics (pool_id, post_count)
                VALUES (NEW.pool_id, 1)
                ON CONFLICT (pool_id) DO UPDATE SET
                    post_count = pool_statistics.post_count + 1;
                INSERT INTO post_statistics (post_id, pool_count)
                VALUES (NEW.post_id, 1)
                ON CONFLICT (post_id) DO UPDATE SET
                    pool_count = post_statistics.pool_count + 1;
            ELSIF TG_OP = 'DELETE' THEN
                UPDATE pool_statistics
                SET post_count = post_count - 1
                WHERE pool_id = OLD.pool_id;
                UPDATE post_statistics
                SET pool_count = pool_count - 1
                WHERE post_id = OLD.post_id;
            ELSE
                IF NEW.pool_id IS DISTINCT FROM OLD.pool_id THEN
                    UPDATE pool_statistics
                    SET post_count = post_count - 1
                    WHERE pool_id = OLD.pool_id;
                    INSERT INTO pool_statistics (pool_id, post_count)
                    VALUES (NEW.pool_id, 1)
                    ON CONFLICT (pool_id) DO UPDATE SET
                        post_count = pool_statistics.post_count + 1;
                END IF;
                IF NEW.post_id IS DISTINCT FROM OLD.post_id THEN
                    UPDATE post_statistics
                    SET pool_count = pool_count - 1
                    WHERE post_id = OLD.post_id;
                    INSERT INTO post_statistics (post_id, pool_count)
                    VALUES (NEW.post_id, 1)
                    ON CONFLICT (post_id) DO UPDATE SET
                        pool_count = post_statistics.pool_count + 1;
                END IF;
            END IF;
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    op.execute(
        """
        CREATE CONSTRAINT TRIGGER trg_stats_post_tag
        AFTER INSERT OR UPDATE OR DELETE ON post_tag
        DEFERRABLE INITIALLY DEFERRED
        FOR EACH ROW EXECUTE FUNCTION stats_update_post_tag();
        """
    )

    op.execute(
        """
        CREATE CONSTRAINT TRIGGER trg_stats_pool_post
        AFTER INSERT OR UPDATE OR DELETE ON pool_post
        DEFERRABLE INITIALLY DEFERRED
        FOR EACH ROW EXECUTE FUNCTION stats_update_pool_post();
        """
    )
