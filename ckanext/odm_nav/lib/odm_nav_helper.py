#!/usr/bin/env python
# -*- coding: utf-8 -*-

top_topics = [
  ('Agriculture and fishing'),
  ('Aid and development'),
  ('Disasters and emergency response'),
  ('Economy and commerce'),
  ('Energy'),
  ('Environment and natural resources'),
  ('Extractive industries'),
  ('Government'),
  ('Industries'),
  ('Infrastructure'),
  ('Labor'),
  ('Land'),
  ('Law and judiciary'),
  ('Population and censuses'),
  ('Social development'),
  ('Urban administration and development'),
  ('Science and technology')
]

countries = [
  ('Global','Global'),
  ('ASEAN','ASEAN'),
  ('Greater Mekong Subregion (GMS)','Greater Mekong Subregion (GMS)'),
  ('Lower Mekong Basin','Lower Mekong Basin'),
  ('Lower Mekong countries','Lower Mekong countries'),
  ('Cambodia','Cambodia'),
  ('Vietnam','Vietnam'),
  ('Laos','Laos'),
  ('Thailand','Thailand'),
  ('Myanmar','Myanmar')
]

languages = [
  ('my','Burmese'),
  ('en','English'),
  ('kh','Khmer'),
  ('lo','Lao'),
  ('th','Thai'),
  ('vi','Vietnamese'),
  ('zh','Chinese'),
  ('fr','French'),
  ('de','German'),
  ('jp','Japanese'),
  ('ko','Korean'),
  ('other','Other'),
]

ckan_fields= [
  ('version','Version',True)
]

odc_fields = [
  ('file_name_kh','File (Khmer)',False),
  ('file_name_en','File (English)',False),
  ('adopted_date','Adopted Date',False),
  ('number_en','Number (English)',False),
  ('number_kh','Number (Khmer)',False),
  ('published_date','Publication date',False),
  ('published_under','Published under',False)
]

metadata_fields = [
  ('odm_copyright','Copyright',False),
  ('odm_access_and_use_constraints','Access and Use Constraints',False),
  ('odm_language','Language',True),
  ('odm_date_created','Date Created',True),
  ('odm_date_uploaded','Date Uploaded',True),
  ('odm_date_modified','Date Modified',False),
  ('odm_temporal_range','Temporal Range',False),
  ('odm_spatial_range','Geographic area (Spatial Range)',True),
  ('odm_accuracy','Accuracy',False),
  ('odm_logical_consistency','Logical Consistency',False),
  ('odm_completeness','Completeness',False),
  ('odm_process','Process(es)',True),
  ('odm_source','Source(s)',True),
  ('odm_contact','Contact',False),
  ('odm_metadata_reference_information','Metadata Reference Information',False),
  ('odm_attributes','Attributes',False)
]

metadata_fields_compact = [
  ('odm_copyright','Copyright',False),
  ('odm_access_and_use_constraints','Access and Use Constraints',False),
  ('odm_contact','Contact',False),
  ('odm_language','Language',True),
  ('odm_date_uploaded','Date Uploaded',True),
  ('odm_spatial_range','Geographic area (Spatial Range)',True)
]

library_fields = [
  ('marc21_020','ISBN',False),
  ('marc21_022','ISSN',False),
  ('marc21_100','Author',False),
  ('marc21_110','Corporate Author',False),
  ('marc21_245','Title',False),
  ('marc21_246','Varying Form of Title',False),
  ('marc21_250','Edition',False),
  ('marc21_260a','Publication Place',False),
  ('marc21_260b','Publication Name',False),
  ('marc21_260c','Publication Date',False),
  ('marc21_300','Pagination',False),
  ('marc21_500','General Note',False),
  ('marc21_700','Co-Author',False),
  ('marc21_710','Co-Author (Corporate)',False)
]

internal_fields = [
  ('import_trace','Import trace',False)
]

taxonomy_dictionary = 'taxonomy'

session = {}
