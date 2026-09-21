-- ============================================================
-- Starting data: the 8 material categories
--
-- DRAFT: have a native Marathi speaker and a native Hindi speaker check the
-- names before they go into the app. The hazard levels are starting guesses;
-- adjust them after checking the safety guidance you will show users.
-- Do NOT add invented recyclers or registration numbers here.
-- Real recyclers come from the CPCB EPR portal after field research.
-- ============================================================

INSERT INTO material_categories (category_id, name_en, name_mr, name_hi, icon, hazard_level) VALUES
('CRT',            'CRT (old TV / monitor)',      'सीआरटी (जुना टीव्ही / मॉनिटर)',   'सीआरटी (पुराना टीवी / मॉनिटर)',   'crt',            'HIGH'),
('LCD_PANEL',      'LCD / LED panel',             'एलसीडी / एलईडी पॅनल',             'एलसीडी / एलईडी पैनल',             'lcd_panel',      'MEDIUM'),
('PCB',            'Circuit boards (PCB)',        'सर्किट बोर्ड (पीसीबी)',            'सर्किट बोर्ड (पीसीबी)',            'pcb',            'MEDIUM'),
('CABLES',         'Cables and wires',            'केबल / तारा',                      'केबल / तार',                      'cables',         'LOW'),
('BATTERIES',      'Batteries',                   'बॅटरी',                            'बैटरी',                            'batteries',      'CRITICAL'),
('MOTORS_MAGNETS', 'Motors / magnet parts',       'मोटर / चुंबक असलेले भाग',          'मोटर / चुंबक वाले पुर्ज़े',          'motors_magnets', 'LOW'),
('MIXED_PLASTICS', 'Mixed plastics',              'मिश्र प्लास्टिक',                  'मिश्रित प्लास्टिक',                 'mixed_plastics', 'LOW'),
('OTHER',          'Other',                       'इतर',                              'अन्य',                            'other',          'LOW');
