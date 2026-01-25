-- Migration: Remove UNIQUE constraint from parser_debug_id in confirmed_parser_fields (Postgres)
DO $$
DECLARE
    constraint_name text;
BEGIN
    -- Find the constraint name for parser_debug_id unique constraint
    SELECT conname INTO constraint_name
    FROM pg_constraint
    WHERE conrelid = 'confirmed_parser_fields'::regclass
      AND contype = 'u'
      AND array_to_string(conkey, ',') = (
        SELECT array_to_string(array_agg(attnum), ',')
        FROM pg_attribute
        WHERE attrelid = 'confirmed_parser_fields'::regclass
          AND attname = 'parser_debug_id'
      );
    IF constraint_name IS NOT NULL THEN
        EXECUTE format('ALTER TABLE confirmed_parser_fields DROP CONSTRAINT %I', constraint_name);
    END IF;
END$$;
