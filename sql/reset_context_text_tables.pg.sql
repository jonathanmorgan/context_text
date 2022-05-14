DROP TABLE context_text_alternate_author_match;
DROP TABLE context_text_alternate_name;
DROP TABLE context_text_alternate_subject_match;
DROP TABLE context_text_article_author;
DROP TABLE context_text_article_data_locations;
DROP TABLE context_text_article_data_notes;
DROP TABLE context_text_article_data_projects;
DROP TABLE context_text_article_data_topics;
DROP TABLE context_text_article_notes;
DROP TABLE context_text_article_rawdata;
DROP TABLE context_text_article_subject_mention;
DROP TABLE context_text_article_subject_quotation;
DROP TABLE context_text_article_subject_topics;
DROP TABLE context_text_article_text;
DROP TABLE context_text_articles_to_migrate;
DROP TABLE context_text_import_error;
DROP TABLE context_text_person_external_uuid;
DROP TABLE context_text_person_newspaper;
DROP TABLE context_text_person_organization;
DROP TABLE context_text_subject_organization;
DROP TABLE context_text_article_subject;
DROP TABLE context_text_document;
DROP TABLE context_text_article_data;
DROP TABLE context_text_organization;
DROP TABLE context_text_location;
DROP TABLE context_text_person;
DROP TABLE context_text_project;
DROP TABLE context_text_temp_section;
DROP TABLE context_text_topic;
DROP TABLE context_text_article;
DROP TABLE context_text_newspaper;

-- remove migration log from django_migrations table so we can re-migrate.
DELETE FROM django_migrations WHERE app = 'context_text';