"""
Add statistics tables and triggers for fast read paths.

Revision ID: c9f1a3b2d0e4
Revises: b0f4c7e29a13
Created at: 2026-01-23
"""

import sqlalchemy as sa
from alembic import op


revision = "c9f1a3b2d0e4"
down_revision = "b0f4c7e29a13"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "database_statistics",
        sa.Column(
            "id",
            sa.Boolean(),
            primary_key=True,
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "post_count",
            sa.BigInteger(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "tag_count",
            sa.BigInteger(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "pool_count",
            sa.BigInteger(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "user_count",
            sa.BigInteger(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "comment_count",
            sa.BigInteger(),
            nullable=False,
            server_default="0",
        ),
    )

    op.create_table(
        "tag_statistics",
        sa.Column(
            "tag_id",
            sa.Integer(),
            sa.ForeignKey("tag.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "usage_count",
            sa.BigInteger(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "suggestion_count",
            sa.BigInteger(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "implication_count",
            sa.BigInteger(),
            nullable=False,
            server_default="0",
        ),
    )

    op.create_table(
        "post_statistics",
        sa.Column(
            "post_id",
            sa.Integer(),
            sa.ForeignKey("post.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "tag_count",
            sa.BigInteger(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "pool_count",
            sa.BigInteger(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "note_count",
            sa.BigInteger(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "comment_count",
            sa.BigInteger(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "relation_count",
            sa.BigInteger(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "score",
            sa.BigInteger(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "favorite_count",
            sa.BigInteger(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "feature_count",
            sa.BigInteger(),
            nullable=False,
            server_default="0",
        ),
        sa.Column("last_comment_creation_time", sa.DateTime()),
        sa.Column("last_comment_edit_time", sa.DateTime()),
        sa.Column("last_favorite_time", sa.DateTime()),
        sa.Column("last_feature_time", sa.DateTime()),
    )

    op.create_table(
        "pool_statistics",
        sa.Column(
            "pool_id",
            sa.Integer(),
            sa.ForeignKey("pool.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "post_count",
            sa.BigInteger(),
            nullable=False,
            server_default="0",
        ),
    )

    op.create_table(
        "user_statistics",
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("user.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "upload_count",
            sa.BigInteger(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "comment_count",
            sa.BigInteger(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "favorite_count",
            sa.BigInteger(),
            nullable=False,
            server_default="0",
        ),
    )

    op.create_table(
        "comment_statistics",
        sa.Column(
            "comment_id",
            sa.Integer(),
            sa.ForeignKey("comment.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "score",
            sa.BigInteger(),
            nullable=False,
            server_default="0",
        ),
    )

    op.create_table(
        "tag_category_statistics",
        sa.Column(
            "category_id",
            sa.Integer(),
            sa.ForeignKey("tag_category.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "usage_count",
            sa.BigInteger(),
            nullable=False,
            server_default="0",
        ),
    )

    op.create_table(
        "pool_category_statistics",
        sa.Column(
            "category_id",
            sa.Integer(),
            sa.ForeignKey("pool_category.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "usage_count",
            sa.BigInteger(),
            nullable=False,
            server_default="0",
        ),
    )

    # Backfill statistics
    op.execute(
        """
        INSERT INTO database_statistics (
            id, post_count, tag_count, pool_count, user_count, comment_count
        )
        SELECT
            true,
            (SELECT COUNT(*) FROM post),
            (SELECT COUNT(*) FROM tag),
            (SELECT COUNT(*) FROM pool),
            (SELECT COUNT(*) FROM "user"),
            (SELECT COUNT(*) FROM comment)
        ON CONFLICT (id) DO UPDATE SET
            post_count = EXCLUDED.post_count,
            tag_count = EXCLUDED.tag_count,
            pool_count = EXCLUDED.pool_count,
            user_count = EXCLUDED.user_count,
            comment_count = EXCLUDED.comment_count
        """
    )

    op.execute(
        """
        INSERT INTO tag_category_statistics (category_id, usage_count)
        SELECT
            tc.id,
            COALESCE(COUNT(t.id), 0)
        FROM tag_category tc
        LEFT JOIN tag t ON t.category_id = tc.id
        GROUP BY tc.id
        """
    )

    op.execute(
        """
        INSERT INTO pool_category_statistics (category_id, usage_count)
        SELECT
            pc.id,
            COALESCE(COUNT(p.id), 0)
        FROM pool_category pc
        LEFT JOIN pool p ON p.category_id = pc.id
        GROUP BY pc.id
        """
    )

    op.execute(
        """
        INSERT INTO tag_statistics (
            tag_id, usage_count, suggestion_count, implication_count
        )
        SELECT
            t.id,
            COALESCE(pt.cnt, 0) AS usage_count,
            COALESCE(ts.cnt, 0) AS suggestion_count,
            COALESCE(ti.cnt, 0) AS implication_count
        FROM tag t
        LEFT JOIN (
            SELECT tag_id, COUNT(*) AS cnt
            FROM post_tag
            GROUP BY tag_id
        ) pt ON pt.tag_id = t.id
        LEFT JOIN (
            SELECT parent_id AS tag_id, COUNT(*) AS cnt
            FROM tag_suggestion
            GROUP BY parent_id
        ) ts ON ts.tag_id = t.id
        LEFT JOIN (
            SELECT parent_id AS tag_id, COUNT(*) AS cnt
            FROM tag_implication
            GROUP BY parent_id
        ) ti ON ti.tag_id = t.id
        """
    )

    op.execute(
        """
        INSERT INTO post_statistics (
            post_id, tag_count, pool_count, note_count, comment_count,
            relation_count, score, favorite_count, feature_count,
            last_comment_creation_time, last_comment_edit_time,
            last_favorite_time, last_feature_time
        )
        SELECT
            p.id,
            COALESCE(pt.cnt, 0) AS tag_count,
            COALESCE(pp.cnt, 0) AS pool_count,
            COALESCE(pn.cnt, 0) AS note_count,
            COALESCE(pc.cnt, 0) AS comment_count,
            COALESCE(pr.cnt, 0) AS relation_count,
            COALESCE(ps.sum_score, 0) AS score,
            COALESCE(pf.cnt, 0) AS favorite_count,
            COALESCE(pfeat.cnt, 0) AS feature_count,
            pc.max_creation,
            pc.max_edit,
            pf.max_time,
            pfeat.max_time
        FROM post p
        LEFT JOIN (
            SELECT post_id, COUNT(*) AS cnt
            FROM post_tag
            GROUP BY post_id
        ) pt ON pt.post_id = p.id
        LEFT JOIN (
            SELECT post_id, COUNT(*) AS cnt
            FROM pool_post
            GROUP BY post_id
        ) pp ON pp.post_id = p.id
        LEFT JOIN (
            SELECT post_id, COUNT(*) AS cnt
            FROM post_note
            GROUP BY post_id
        ) pn ON pn.post_id = p.id
        LEFT JOIN (
            SELECT
                post_id,
                COUNT(*) AS cnt,
                MAX(creation_time) AS max_creation,
                MAX(last_edit_time) AS max_edit
            FROM comment
            GROUP BY post_id
        ) pc ON pc.post_id = p.id
        LEFT JOIN (
            SELECT post_id, SUM(score) AS sum_score
            FROM post_score
            GROUP BY post_id
        ) ps ON ps.post_id = p.id
        LEFT JOIN (
            SELECT
                post_id,
                COUNT(*) AS cnt,
                MAX(time) AS max_time
            FROM post_favorite
            GROUP BY post_id
        ) pf ON pf.post_id = p.id
        LEFT JOIN (
            SELECT
                post_id,
                COUNT(*) AS cnt,
                MAX(time) AS max_time
            FROM post_feature
            GROUP BY post_id
        ) pfeat ON pfeat.post_id = p.id
        LEFT JOIN (
            SELECT post_id, COUNT(*) AS cnt
            FROM (
                SELECT parent_id AS post_id FROM post_relation
                UNION ALL
                SELECT child_id AS post_id FROM post_relation
            ) rel
            GROUP BY post_id
        ) pr ON pr.post_id = p.id
        """
    )

    op.execute(
        """
        INSERT INTO pool_statistics (pool_id, post_count)
        SELECT
            p.id,
            COALESCE(pp.cnt, 0) AS post_count
        FROM pool p
        LEFT JOIN (
            SELECT pool_id, COUNT(*) AS cnt
            FROM pool_post
            GROUP BY pool_id
        ) pp ON pp.pool_id = p.id
        """
    )

    op.execute(
        """
        INSERT INTO user_statistics (user_id, upload_count, comment_count, favorite_count)
        SELECT
            u.id,
            COALESCE(p.cnt, 0) AS upload_count,
            COALESCE(c.cnt, 0) AS comment_count,
            COALESCE(f.cnt, 0) AS favorite_count
        FROM "user" u
        LEFT JOIN (
            SELECT user_id, COUNT(*) AS cnt
            FROM post
            WHERE user_id IS NOT NULL
            GROUP BY user_id
        ) p ON p.user_id = u.id
        LEFT JOIN (
            SELECT user_id, COUNT(*) AS cnt
            FROM comment
            WHERE user_id IS NOT NULL
            GROUP BY user_id
        ) c ON c.user_id = u.id
        LEFT JOIN (
            SELECT user_id, COUNT(*) AS cnt
            FROM post_favorite
            WHERE user_id IS NOT NULL
            GROUP BY user_id
        ) f ON f.user_id = u.id
        """
    )

    op.execute(
        """
        INSERT INTO comment_statistics (comment_id, score)
        SELECT
            c.id,
            COALESCE(cs.sum_score, 0) AS score
        FROM comment c
        LEFT JOIN (
            SELECT comment_id, SUM(score) AS sum_score
            FROM comment_score
            GROUP BY comment_id
        ) cs ON cs.comment_id = c.id
        """
    )

    # Indexes for fast sorting/filtering
    op.create_index(
        "ix_tag_statistics_usage_count",
        "tag_statistics",
        ["usage_count"],
    )
    op.create_index(
        "ix_post_statistics_tag_count",
        "post_statistics",
        ["tag_count"],
    )
    op.create_index(
        "ix_post_statistics_comment_count",
        "post_statistics",
        ["comment_count"],
    )
    op.create_index(
        "ix_post_statistics_favorite_count",
        "post_statistics",
        ["favorite_count"],
    )
    op.create_index(
        "ix_post_statistics_score",
        "post_statistics",
        ["score"],
    )
    op.create_index(
        "ix_post_statistics_last_comment_creation_time",
        "post_statistics",
        ["last_comment_creation_time"],
    )
    op.create_index(
        "ix_post_statistics_last_favorite_time",
        "post_statistics",
        ["last_favorite_time"],
    )
    op.create_index(
        "ix_post_statistics_last_feature_time",
        "post_statistics",
        ["last_feature_time"],
    )
    op.create_index(
        "ix_pool_statistics_post_count",
        "pool_statistics",
        ["post_count"],
    )

    # Trigger functions
    op.execute(
        """
        CREATE OR REPLACE FUNCTION stats_update_post() RETURNS trigger AS $$
        BEGIN
            IF TG_OP = 'INSERT' THEN
                INSERT INTO post_statistics (post_id)
                VALUES (NEW.id)
                ON CONFLICT (post_id) DO NOTHING;

                INSERT INTO database_statistics (id, post_count)
                VALUES (true, 1)
                ON CONFLICT (id) DO UPDATE SET
                    post_count = database_statistics.post_count + 1;

                IF NEW.user_id IS NOT NULL THEN
                    INSERT INTO user_statistics (user_id, upload_count)
                    VALUES (NEW.user_id, 1)
                    ON CONFLICT (user_id) DO UPDATE SET
                        upload_count = user_statistics.upload_count + 1;
                END IF;
            ELSIF TG_OP = 'DELETE' THEN
                UPDATE database_statistics
                SET post_count = post_count - 1
                WHERE id = true;

                IF OLD.user_id IS NOT NULL THEN
                    UPDATE user_statistics
                    SET upload_count = upload_count - 1
                    WHERE user_id = OLD.user_id;
                END IF;
            ELSE
                INSERT INTO post_statistics (post_id)
                VALUES (NEW.id)
                ON CONFLICT (post_id) DO NOTHING;

                IF NEW.user_id IS DISTINCT FROM OLD.user_id THEN
                    IF OLD.user_id IS NOT NULL THEN
                        UPDATE user_statistics
                        SET upload_count = upload_count - 1
                        WHERE user_id = OLD.user_id;
                    END IF;
                    IF NEW.user_id IS NOT NULL THEN
                        INSERT INTO user_statistics (user_id, upload_count)
                        VALUES (NEW.user_id, 1)
                        ON CONFLICT (user_id) DO UPDATE SET
                            upload_count = user_statistics.upload_count + 1;
                    END IF;
                END IF;
            END IF;
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION stats_update_user() RETURNS trigger AS $$
        BEGIN
            IF TG_OP = 'INSERT' THEN
                INSERT INTO user_statistics (user_id)
                VALUES (NEW.id)
                ON CONFLICT (user_id) DO NOTHING;

                INSERT INTO database_statistics (id, user_count)
                VALUES (true, 1)
                ON CONFLICT (id) DO UPDATE SET
                    user_count = database_statistics.user_count + 1;
            ELSIF TG_OP = 'DELETE' THEN
                UPDATE database_statistics
                SET user_count = user_count - 1
                WHERE id = true;
            END IF;
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION stats_update_tag_category() RETURNS trigger AS $$
        BEGIN
            IF TG_OP = 'INSERT' THEN
                INSERT INTO tag_category_statistics (category_id, usage_count)
                VALUES (NEW.id, 0)
                ON CONFLICT (category_id) DO NOTHING;
            END IF;
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION stats_update_pool_category() RETURNS trigger AS $$
        BEGIN
            IF TG_OP = 'INSERT' THEN
                INSERT INTO pool_category_statistics (category_id, usage_count)
                VALUES (NEW.id, 0)
                ON CONFLICT (category_id) DO NOTHING;
            END IF;
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION stats_update_tag() RETURNS trigger AS $$
        BEGIN
            IF TG_OP = 'INSERT' THEN
                INSERT INTO tag_statistics (tag_id)
                VALUES (NEW.id)
                ON CONFLICT (tag_id) DO NOTHING;

                INSERT INTO database_statistics (id, tag_count)
                VALUES (true, 1)
                ON CONFLICT (id) DO UPDATE SET
                    tag_count = database_statistics.tag_count + 1;

                INSERT INTO tag_category_statistics (category_id, usage_count)
                VALUES (NEW.category_id, 1)
                ON CONFLICT (category_id) DO UPDATE SET
                    usage_count = tag_category_statistics.usage_count + 1;
            ELSIF TG_OP = 'DELETE' THEN
                UPDATE database_statistics
                SET tag_count = tag_count - 1
                WHERE id = true;

                UPDATE tag_category_statistics
                SET usage_count = usage_count - 1
                WHERE category_id = OLD.category_id;
            ELSE
                IF NEW.category_id IS DISTINCT FROM OLD.category_id THEN
                    UPDATE tag_category_statistics
                    SET usage_count = usage_count - 1
                    WHERE category_id = OLD.category_id;
                    INSERT INTO tag_category_statistics (category_id, usage_count)
                    VALUES (NEW.category_id, 1)
                    ON CONFLICT (category_id) DO UPDATE SET
                        usage_count = tag_category_statistics.usage_count + 1;
                END IF;
            END IF;
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION stats_update_pool() RETURNS trigger AS $$
        BEGIN
            IF TG_OP = 'INSERT' THEN
                INSERT INTO pool_statistics (pool_id)
                VALUES (NEW.id)
                ON CONFLICT (pool_id) DO NOTHING;

                INSERT INTO database_statistics (id, pool_count)
                VALUES (true, 1)
                ON CONFLICT (id) DO UPDATE SET
                    pool_count = database_statistics.pool_count + 1;

                INSERT INTO pool_category_statistics (category_id, usage_count)
                VALUES (NEW.category_id, 1)
                ON CONFLICT (category_id) DO UPDATE SET
                    usage_count = pool_category_statistics.usage_count + 1;
            ELSIF TG_OP = 'DELETE' THEN
                UPDATE database_statistics
                SET pool_count = pool_count - 1
                WHERE id = true;

                UPDATE pool_category_statistics
                SET usage_count = usage_count - 1
                WHERE category_id = OLD.category_id;
            ELSE
                IF NEW.category_id IS DISTINCT FROM OLD.category_id THEN
                    UPDATE pool_category_statistics
                    SET usage_count = usage_count - 1
                    WHERE category_id = OLD.category_id;
                    INSERT INTO pool_category_statistics (category_id, usage_count)
                    VALUES (NEW.category_id, 1)
                    ON CONFLICT (category_id) DO UPDATE SET
                        usage_count = pool_category_statistics.usage_count + 1;
                END IF;
            END IF;
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION stats_update_tag_suggestion() RETURNS trigger AS $$
        BEGIN
            IF TG_OP = 'INSERT' THEN
                INSERT INTO tag_statistics (tag_id, suggestion_count)
                VALUES (NEW.parent_id, 1)
                ON CONFLICT (tag_id) DO UPDATE SET
                    suggestion_count = tag_statistics.suggestion_count + 1;
            ELSIF TG_OP = 'DELETE' THEN
                UPDATE tag_statistics
                SET suggestion_count = suggestion_count - 1
                WHERE tag_id = OLD.parent_id;
            ELSE
                IF NEW.parent_id IS DISTINCT FROM OLD.parent_id THEN
                    UPDATE tag_statistics
                    SET suggestion_count = suggestion_count - 1
                    WHERE tag_id = OLD.parent_id;
                    INSERT INTO tag_statistics (tag_id, suggestion_count)
                    VALUES (NEW.parent_id, 1)
                    ON CONFLICT (tag_id) DO UPDATE SET
                        suggestion_count = tag_statistics.suggestion_count + 1;
                END IF;
            END IF;
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION stats_update_tag_implication() RETURNS trigger AS $$
        BEGIN
            IF TG_OP = 'INSERT' THEN
                INSERT INTO tag_statistics (tag_id, implication_count)
                VALUES (NEW.parent_id, 1)
                ON CONFLICT (tag_id) DO UPDATE SET
                    implication_count = tag_statistics.implication_count + 1;
            ELSIF TG_OP = 'DELETE' THEN
                UPDATE tag_statistics
                SET implication_count = implication_count - 1
                WHERE tag_id = OLD.parent_id;
            ELSE
                IF NEW.parent_id IS DISTINCT FROM OLD.parent_id THEN
                    UPDATE tag_statistics
                    SET implication_count = implication_count - 1
                    WHERE tag_id = OLD.parent_id;
                    INSERT INTO tag_statistics (tag_id, implication_count)
                    VALUES (NEW.parent_id, 1)
                    ON CONFLICT (tag_id) DO UPDATE SET
                        implication_count = tag_statistics.implication_count + 1;
                END IF;
            END IF;
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

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
        CREATE OR REPLACE FUNCTION stats_update_post_note() RETURNS trigger AS $$
        BEGIN
            IF TG_OP = 'INSERT' THEN
                INSERT INTO post_statistics (post_id, note_count)
                VALUES (NEW.post_id, 1)
                ON CONFLICT (post_id) DO UPDATE SET
                    note_count = post_statistics.note_count + 1;
            ELSIF TG_OP = 'DELETE' THEN
                UPDATE post_statistics
                SET note_count = note_count - 1
                WHERE post_id = OLD.post_id;
            ELSE
                IF NEW.post_id IS DISTINCT FROM OLD.post_id THEN
                    UPDATE post_statistics
                    SET note_count = note_count - 1
                    WHERE post_id = OLD.post_id;
                    INSERT INTO post_statistics (post_id, note_count)
                    VALUES (NEW.post_id, 1)
                    ON CONFLICT (post_id) DO UPDATE SET
                        note_count = post_statistics.note_count + 1;
                END IF;
            END IF;
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION stats_update_post_relation() RETURNS trigger AS $$
        BEGIN
            IF TG_OP = 'INSERT' THEN
                INSERT INTO post_statistics (post_id, relation_count)
                VALUES (NEW.parent_id, 1)
                ON CONFLICT (post_id) DO UPDATE SET
                    relation_count = post_statistics.relation_count + 1;
                INSERT INTO post_statistics (post_id, relation_count)
                VALUES (NEW.child_id, 1)
                ON CONFLICT (post_id) DO UPDATE SET
                    relation_count = post_statistics.relation_count + 1;
            ELSIF TG_OP = 'DELETE' THEN
                UPDATE post_statistics
                SET relation_count = relation_count - 1
                WHERE post_id = OLD.parent_id;
                UPDATE post_statistics
                SET relation_count = relation_count - 1
                WHERE post_id = OLD.child_id;
            ELSE
                IF NEW.parent_id IS DISTINCT FROM OLD.parent_id THEN
                    UPDATE post_statistics
                    SET relation_count = relation_count - 1
                    WHERE post_id = OLD.parent_id;
                    INSERT INTO post_statistics (post_id, relation_count)
                    VALUES (NEW.parent_id, 1)
                    ON CONFLICT (post_id) DO UPDATE SET
                        relation_count = post_statistics.relation_count + 1;
                END IF;
                IF NEW.child_id IS DISTINCT FROM OLD.child_id THEN
                    UPDATE post_statistics
                    SET relation_count = relation_count - 1
                    WHERE post_id = OLD.child_id;
                    INSERT INTO post_statistics (post_id, relation_count)
                    VALUES (NEW.child_id, 1)
                    ON CONFLICT (post_id) DO UPDATE SET
                        relation_count = post_statistics.relation_count + 1;
                END IF;
            END IF;
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION stats_update_post_score() RETURNS trigger AS $$
        BEGIN
            IF TG_OP = 'INSERT' THEN
                INSERT INTO post_statistics (post_id, score)
                VALUES (NEW.post_id, NEW.score)
                ON CONFLICT (post_id) DO UPDATE SET
                    score = post_statistics.score + NEW.score;
            ELSIF TG_OP = 'DELETE' THEN
                UPDATE post_statistics
                SET score = score - OLD.score
                WHERE post_id = OLD.post_id;
            ELSE
                IF NEW.post_id IS DISTINCT FROM OLD.post_id THEN
                    UPDATE post_statistics
                    SET score = score - OLD.score
                    WHERE post_id = OLD.post_id;
                    INSERT INTO post_statistics (post_id, score)
                    VALUES (NEW.post_id, NEW.score)
                    ON CONFLICT (post_id) DO UPDATE SET
                        score = post_statistics.score + NEW.score;
                ELSE
                    UPDATE post_statistics
                    SET score = score + (NEW.score - OLD.score)
                    WHERE post_id = NEW.post_id;
                END IF;
            END IF;
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION stats_update_comment_score() RETURNS trigger AS $$
        BEGIN
            IF TG_OP = 'INSERT' THEN
                INSERT INTO comment_statistics (comment_id, score)
                VALUES (NEW.comment_id, NEW.score)
                ON CONFLICT (comment_id) DO UPDATE SET
                    score = comment_statistics.score + NEW.score;
            ELSIF TG_OP = 'DELETE' THEN
                UPDATE comment_statistics
                SET score = score - OLD.score
                WHERE comment_id = OLD.comment_id;
            ELSE
                IF NEW.comment_id IS DISTINCT FROM OLD.comment_id THEN
                    UPDATE comment_statistics
                    SET score = score - OLD.score
                    WHERE comment_id = OLD.comment_id;
                    INSERT INTO comment_statistics (comment_id, score)
                    VALUES (NEW.comment_id, NEW.score)
                    ON CONFLICT (comment_id) DO UPDATE SET
                        score = comment_statistics.score + NEW.score;
                ELSE
                    UPDATE comment_statistics
                    SET score = score + (NEW.score - OLD.score)
                    WHERE comment_id = NEW.comment_id;
                END IF;
            END IF;
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION stats_update_post_favorite() RETURNS trigger AS $$
        BEGIN
            IF TG_OP = 'INSERT' THEN
                INSERT INTO post_statistics (
                    post_id, favorite_count, last_favorite_time
                )
                VALUES (NEW.post_id, 1, NEW.time)
                ON CONFLICT (post_id) DO UPDATE SET
                    favorite_count = post_statistics.favorite_count + 1,
                    last_favorite_time = CASE
                        WHEN post_statistics.last_favorite_time IS NULL
                            OR NEW.time > post_statistics.last_favorite_time
                        THEN NEW.time
                        ELSE post_statistics.last_favorite_time
                    END;

                IF NEW.user_id IS NOT NULL THEN
                    INSERT INTO user_statistics (user_id, favorite_count)
                    VALUES (NEW.user_id, 1)
                    ON CONFLICT (user_id) DO UPDATE SET
                        favorite_count = user_statistics.favorite_count + 1;
                END IF;
            ELSIF TG_OP = 'DELETE' THEN
                UPDATE post_statistics
                SET favorite_count = favorite_count - 1,
                    last_favorite_time = (
                        SELECT MAX(time)
                        FROM post_favorite
                        WHERE post_id = OLD.post_id
                    )
                WHERE post_id = OLD.post_id;

                IF OLD.user_id IS NOT NULL THEN
                    UPDATE user_statistics
                    SET favorite_count = favorite_count - 1
                    WHERE user_id = OLD.user_id;
                END IF;
            ELSE
                IF NEW.post_id IS DISTINCT FROM OLD.post_id THEN
                    UPDATE post_statistics
                    SET favorite_count = favorite_count - 1,
                        last_favorite_time = (
                            SELECT MAX(time)
                            FROM post_favorite
                            WHERE post_id = OLD.post_id
                        )
                    WHERE post_id = OLD.post_id;

                    INSERT INTO post_statistics (
                        post_id, favorite_count, last_favorite_time
                    )
                    VALUES (NEW.post_id, 1, NEW.time)
                    ON CONFLICT (post_id) DO UPDATE SET
                        favorite_count = post_statistics.favorite_count + 1,
                        last_favorite_time = CASE
                            WHEN post_statistics.last_favorite_time IS NULL
                                OR NEW.time > post_statistics.last_favorite_time
                            THEN NEW.time
                            ELSE post_statistics.last_favorite_time
                        END;
                ELSE
                    IF NEW.time IS DISTINCT FROM OLD.time THEN
                        UPDATE post_statistics
                        SET last_favorite_time = (
                            SELECT MAX(time)
                            FROM post_favorite
                            WHERE post_id = NEW.post_id
                        )
                        WHERE post_id = NEW.post_id;
                    END IF;
                END IF;

                IF NEW.user_id IS DISTINCT FROM OLD.user_id THEN
                    IF OLD.user_id IS NOT NULL THEN
                        UPDATE user_statistics
                        SET favorite_count = favorite_count - 1
                        WHERE user_id = OLD.user_id;
                    END IF;
                    IF NEW.user_id IS NOT NULL THEN
                        INSERT INTO user_statistics (user_id, favorite_count)
                        VALUES (NEW.user_id, 1)
                        ON CONFLICT (user_id) DO UPDATE SET
                            favorite_count = user_statistics.favorite_count + 1;
                    END IF;
                END IF;
            END IF;
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION stats_update_post_feature() RETURNS trigger AS $$
        BEGIN
            IF TG_OP = 'INSERT' THEN
                INSERT INTO post_statistics (
                    post_id, feature_count, last_feature_time
                )
                VALUES (NEW.post_id, 1, NEW.time)
                ON CONFLICT (post_id) DO UPDATE SET
                    feature_count = post_statistics.feature_count + 1,
                    last_feature_time = CASE
                        WHEN post_statistics.last_feature_time IS NULL
                            OR NEW.time > post_statistics.last_feature_time
                        THEN NEW.time
                        ELSE post_statistics.last_feature_time
                    END;
            ELSIF TG_OP = 'DELETE' THEN
                UPDATE post_statistics
                SET feature_count = feature_count - 1,
                    last_feature_time = (
                        SELECT MAX(time)
                        FROM post_feature
                        WHERE post_id = OLD.post_id
                    )
                WHERE post_id = OLD.post_id;
            ELSE
                IF NEW.post_id IS DISTINCT FROM OLD.post_id THEN
                    UPDATE post_statistics
                    SET feature_count = feature_count - 1,
                        last_feature_time = (
                            SELECT MAX(time)
                            FROM post_feature
                            WHERE post_id = OLD.post_id
                        )
                    WHERE post_id = OLD.post_id;

                    INSERT INTO post_statistics (
                        post_id, feature_count, last_feature_time
                    )
                    VALUES (NEW.post_id, 1, NEW.time)
                    ON CONFLICT (post_id) DO UPDATE SET
                        feature_count = post_statistics.feature_count + 1,
                        last_feature_time = CASE
                            WHEN post_statistics.last_feature_time IS NULL
                                OR NEW.time > post_statistics.last_feature_time
                            THEN NEW.time
                            ELSE post_statistics.last_feature_time
                        END;
                ELSE
                    IF NEW.time IS DISTINCT FROM OLD.time THEN
                        UPDATE post_statistics
                        SET last_feature_time = (
                            SELECT MAX(time)
                            FROM post_feature
                            WHERE post_id = NEW.post_id
                        )
                        WHERE post_id = NEW.post_id;
                    END IF;
                END IF;
            END IF;
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION stats_update_comment() RETURNS trigger AS $$
        BEGIN
            IF TG_OP = 'INSERT' THEN
                INSERT INTO comment_statistics (comment_id)
                VALUES (NEW.id)
                ON CONFLICT (comment_id) DO NOTHING;

                INSERT INTO post_statistics (
                    post_id,
                    comment_count,
                    last_comment_creation_time,
                    last_comment_edit_time
                )
                VALUES (
                    NEW.post_id,
                    1,
                    NEW.creation_time,
                    NEW.last_edit_time
                )
                ON CONFLICT (post_id) DO UPDATE SET
                    comment_count = post_statistics.comment_count + 1,
                    last_comment_creation_time = GREATEST(
                        COALESCE(
                            post_statistics.last_comment_creation_time,
                            NEW.creation_time
                        ),
                        NEW.creation_time
                    ),
                    last_comment_edit_time = CASE
                        WHEN NEW.last_edit_time IS NULL
                        THEN post_statistics.last_comment_edit_time
                        WHEN post_statistics.last_comment_edit_time IS NULL
                            OR NEW.last_edit_time > post_statistics.last_comment_edit_time
                        THEN NEW.last_edit_time
                        ELSE post_statistics.last_comment_edit_time
                    END;

                INSERT INTO database_statistics (id, comment_count)
                VALUES (true, 1)
                ON CONFLICT (id) DO UPDATE SET
                    comment_count = database_statistics.comment_count + 1;

                IF NEW.user_id IS NOT NULL THEN
                    INSERT INTO user_statistics (user_id, comment_count)
                    VALUES (NEW.user_id, 1)
                    ON CONFLICT (user_id) DO UPDATE SET
                        comment_count = user_statistics.comment_count + 1;
                END IF;
            ELSIF TG_OP = 'DELETE' THEN
                UPDATE post_statistics
                SET comment_count = comment_count - 1,
                    last_comment_creation_time = (
                        SELECT MAX(creation_time)
                        FROM comment
                        WHERE post_id = OLD.post_id
                    ),
                    last_comment_edit_time = (
                        SELECT MAX(last_edit_time)
                        FROM comment
                        WHERE post_id = OLD.post_id
                    )
                WHERE post_id = OLD.post_id;

                UPDATE database_statistics
                SET comment_count = comment_count - 1
                WHERE id = true;

                IF OLD.user_id IS NOT NULL THEN
                    UPDATE user_statistics
                    SET comment_count = comment_count - 1
                    WHERE user_id = OLD.user_id;
                END IF;
            ELSE
                IF NEW.post_id IS DISTINCT FROM OLD.post_id THEN
                    UPDATE post_statistics
                    SET comment_count = comment_count - 1,
                        last_comment_creation_time = (
                            SELECT MAX(creation_time)
                            FROM comment
                            WHERE post_id = OLD.post_id
                        ),
                        last_comment_edit_time = (
                            SELECT MAX(last_edit_time)
                            FROM comment
                            WHERE post_id = OLD.post_id
                        )
                    WHERE post_id = OLD.post_id;

                    INSERT INTO post_statistics (
                        post_id,
                        comment_count,
                        last_comment_creation_time,
                        last_comment_edit_time
                    )
                    VALUES (
                        NEW.post_id,
                        1,
                        NEW.creation_time,
                        NEW.last_edit_time
                    )
                    ON CONFLICT (post_id) DO UPDATE SET
                        comment_count = post_statistics.comment_count + 1,
                        last_comment_creation_time = GREATEST(
                            COALESCE(
                                post_statistics.last_comment_creation_time,
                                NEW.creation_time
                            ),
                            NEW.creation_time
                        ),
                        last_comment_edit_time = CASE
                            WHEN NEW.last_edit_time IS NULL
                            THEN post_statistics.last_comment_edit_time
                            WHEN post_statistics.last_comment_edit_time IS NULL
                                OR NEW.last_edit_time > post_statistics.last_comment_edit_time
                            THEN NEW.last_edit_time
                            ELSE post_statistics.last_comment_edit_time
                        END;
                ELSE
                    IF NEW.creation_time IS DISTINCT FROM OLD.creation_time
                        OR NEW.last_edit_time IS DISTINCT FROM OLD.last_edit_time
                    THEN
                        UPDATE post_statistics
                        SET last_comment_creation_time = (
                            SELECT MAX(creation_time)
                            FROM comment
                            WHERE post_id = NEW.post_id
                        ),
                        last_comment_edit_time = (
                            SELECT MAX(last_edit_time)
                            FROM comment
                            WHERE post_id = NEW.post_id
                        )
                        WHERE post_id = NEW.post_id;
                    END IF;
                END IF;

                IF NEW.user_id IS DISTINCT FROM OLD.user_id THEN
                    IF OLD.user_id IS NOT NULL THEN
                        UPDATE user_statistics
                        SET comment_count = comment_count - 1
                        WHERE user_id = OLD.user_id;
                    END IF;
                    IF NEW.user_id IS NOT NULL THEN
                        INSERT INTO user_statistics (user_id, comment_count)
                        VALUES (NEW.user_id, 1)
                        ON CONFLICT (user_id) DO UPDATE SET
                            comment_count = user_statistics.comment_count + 1;
                    END IF;
                END IF;
            END IF;
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    # Triggers
    op.execute(
        """
        CREATE CONSTRAINT TRIGGER trg_stats_post
        AFTER INSERT OR UPDATE OR DELETE ON post
        DEFERRABLE INITIALLY DEFERRED
        FOR EACH ROW EXECUTE FUNCTION stats_update_post();
        """
    )

    op.execute(
        """
        CREATE CONSTRAINT TRIGGER trg_stats_user
        AFTER INSERT OR DELETE ON "user"
        DEFERRABLE INITIALLY DEFERRED
        FOR EACH ROW EXECUTE FUNCTION stats_update_user();
        """
    )

    op.execute(
        """
        CREATE CONSTRAINT TRIGGER trg_stats_tag_category
        AFTER INSERT ON tag_category
        DEFERRABLE INITIALLY DEFERRED
        FOR EACH ROW EXECUTE FUNCTION stats_update_tag_category();
        """
    )

    op.execute(
        """
        CREATE CONSTRAINT TRIGGER trg_stats_pool_category
        AFTER INSERT ON pool_category
        DEFERRABLE INITIALLY DEFERRED
        FOR EACH ROW EXECUTE FUNCTION stats_update_pool_category();
        """
    )

    op.execute(
        """
        CREATE CONSTRAINT TRIGGER trg_stats_tag
        AFTER INSERT OR UPDATE OR DELETE ON tag
        DEFERRABLE INITIALLY DEFERRED
        FOR EACH ROW EXECUTE FUNCTION stats_update_tag();
        """
    )

    op.execute(
        """
        CREATE CONSTRAINT TRIGGER trg_stats_pool
        AFTER INSERT OR UPDATE OR DELETE ON pool
        DEFERRABLE INITIALLY DEFERRED
        FOR EACH ROW EXECUTE FUNCTION stats_update_pool();
        """
    )

    op.execute(
        """
        CREATE CONSTRAINT TRIGGER trg_stats_tag_suggestion
        AFTER INSERT OR UPDATE OR DELETE ON tag_suggestion
        DEFERRABLE INITIALLY DEFERRED
        FOR EACH ROW EXECUTE FUNCTION stats_update_tag_suggestion();
        """
    )

    op.execute(
        """
        CREATE CONSTRAINT TRIGGER trg_stats_tag_implication
        AFTER INSERT OR UPDATE OR DELETE ON tag_implication
        DEFERRABLE INITIALLY DEFERRED
        FOR EACH ROW EXECUTE FUNCTION stats_update_tag_implication();
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

    op.execute(
        """
        CREATE CONSTRAINT TRIGGER trg_stats_post_note
        AFTER INSERT OR UPDATE OR DELETE ON post_note
        DEFERRABLE INITIALLY DEFERRED
        FOR EACH ROW EXECUTE FUNCTION stats_update_post_note();
        """
    )

    op.execute(
        """
        CREATE CONSTRAINT TRIGGER trg_stats_post_relation
        AFTER INSERT OR UPDATE OR DELETE ON post_relation
        DEFERRABLE INITIALLY DEFERRED
        FOR EACH ROW EXECUTE FUNCTION stats_update_post_relation();
        """
    )

    op.execute(
        """
        CREATE CONSTRAINT TRIGGER trg_stats_post_score
        AFTER INSERT OR UPDATE OR DELETE ON post_score
        DEFERRABLE INITIALLY DEFERRED
        FOR EACH ROW EXECUTE FUNCTION stats_update_post_score();
        """
    )

    op.execute(
        """
        CREATE CONSTRAINT TRIGGER trg_stats_comment_score
        AFTER INSERT OR UPDATE OR DELETE ON comment_score
        DEFERRABLE INITIALLY DEFERRED
        FOR EACH ROW EXECUTE FUNCTION stats_update_comment_score();
        """
    )

    op.execute(
        """
        CREATE CONSTRAINT TRIGGER trg_stats_post_favorite
        AFTER INSERT OR UPDATE OR DELETE ON post_favorite
        DEFERRABLE INITIALLY DEFERRED
        FOR EACH ROW EXECUTE FUNCTION stats_update_post_favorite();
        """
    )

    op.execute(
        """
        CREATE CONSTRAINT TRIGGER trg_stats_post_feature
        AFTER INSERT OR UPDATE OR DELETE ON post_feature
        DEFERRABLE INITIALLY DEFERRED
        FOR EACH ROW EXECUTE FUNCTION stats_update_post_feature();
        """
    )

    op.execute(
        """
        CREATE CONSTRAINT TRIGGER trg_stats_comment
        AFTER INSERT OR UPDATE OR DELETE ON comment
        DEFERRABLE INITIALLY DEFERRED
        FOR EACH ROW EXECUTE FUNCTION stats_update_comment();
        """
    )


def downgrade():
    op.execute("DROP TRIGGER IF EXISTS trg_stats_comment ON comment")
    op.execute("DROP TRIGGER IF EXISTS trg_stats_post_feature ON post_feature")
    op.execute("DROP TRIGGER IF EXISTS trg_stats_post_favorite ON post_favorite")
    op.execute("DROP TRIGGER IF EXISTS trg_stats_comment_score ON comment_score")
    op.execute("DROP TRIGGER IF EXISTS trg_stats_post_score ON post_score")
    op.execute("DROP TRIGGER IF EXISTS trg_stats_post_relation ON post_relation")
    op.execute("DROP TRIGGER IF EXISTS trg_stats_post_note ON post_note")
    op.execute("DROP TRIGGER IF EXISTS trg_stats_pool_post ON pool_post")
    op.execute("DROP TRIGGER IF EXISTS trg_stats_post_tag ON post_tag")
    op.execute("DROP TRIGGER IF EXISTS trg_stats_tag_implication ON tag_implication")
    op.execute("DROP TRIGGER IF EXISTS trg_stats_tag_suggestion ON tag_suggestion")
    op.execute("DROP TRIGGER IF EXISTS trg_stats_pool ON pool")
    op.execute("DROP TRIGGER IF EXISTS trg_stats_tag ON tag")
    op.execute("DROP TRIGGER IF EXISTS trg_stats_pool_category ON pool_category")
    op.execute("DROP TRIGGER IF EXISTS trg_stats_tag_category ON tag_category")
    op.execute("DROP TRIGGER IF EXISTS trg_stats_user ON \"user\"")
    op.execute("DROP TRIGGER IF EXISTS trg_stats_post ON post")

    op.execute("DROP FUNCTION IF EXISTS stats_update_comment()")
    op.execute("DROP FUNCTION IF EXISTS stats_update_post_feature()")
    op.execute("DROP FUNCTION IF EXISTS stats_update_post_favorite()")
    op.execute("DROP FUNCTION IF EXISTS stats_update_comment_score()")
    op.execute("DROP FUNCTION IF EXISTS stats_update_post_score()")
    op.execute("DROP FUNCTION IF EXISTS stats_update_post_relation()")
    op.execute("DROP FUNCTION IF EXISTS stats_update_post_note()")
    op.execute("DROP FUNCTION IF EXISTS stats_update_pool_post()")
    op.execute("DROP FUNCTION IF EXISTS stats_update_post_tag()")
    op.execute("DROP FUNCTION IF EXISTS stats_update_tag_implication()")
    op.execute("DROP FUNCTION IF EXISTS stats_update_tag_suggestion()")
    op.execute("DROP FUNCTION IF EXISTS stats_update_pool()")
    op.execute("DROP FUNCTION IF EXISTS stats_update_tag()")
    op.execute("DROP FUNCTION IF EXISTS stats_update_pool_category()")
    op.execute("DROP FUNCTION IF EXISTS stats_update_tag_category()")
    op.execute("DROP FUNCTION IF EXISTS stats_update_user()")
    op.execute("DROP FUNCTION IF EXISTS stats_update_post()")

    op.drop_index("ix_pool_statistics_post_count", table_name="pool_statistics")
    op.drop_index(
        "ix_post_statistics_last_feature_time", table_name="post_statistics"
    )
    op.drop_index(
        "ix_post_statistics_last_favorite_time", table_name="post_statistics"
    )
    op.drop_index(
        "ix_post_statistics_last_comment_creation_time",
        table_name="post_statistics",
    )
    op.drop_index(
        "ix_post_statistics_score", table_name="post_statistics"
    )
    op.drop_index(
        "ix_post_statistics_favorite_count", table_name="post_statistics"
    )
    op.drop_index(
        "ix_post_statistics_comment_count", table_name="post_statistics"
    )
    op.drop_index(
        "ix_post_statistics_tag_count", table_name="post_statistics"
    )
    op.drop_index(
        "ix_tag_statistics_usage_count", table_name="tag_statistics"
    )

    op.drop_table("pool_category_statistics")
    op.drop_table("tag_category_statistics")
    op.drop_table("comment_statistics")
    op.drop_table("user_statistics")
    op.drop_table("pool_statistics")
    op.drop_table("post_statistics")
    op.drop_table("tag_statistics")
    op.drop_table("database_statistics")
