import "dotenv/config";
import { spawnSync } from "node:child_process";

const databaseUrl = process.env.DATABASE_URL;

if (!databaseUrl) {
  console.error("DATABASE_URL is required to run the Phase 2 seed.");
  process.exit(1);
}

const sql = String.raw`
begin;

set search_path = app, public;

create or replace function pg_temp.seed_uuid(seed text)
returns uuid
language sql
immutable
as $$
  select (
    substr(hash, 1, 8) || '-' ||
    substr(hash, 9, 4) || '-4' ||
    substr(hash, 14, 3) || '-8' ||
    substr(hash, 18, 3) || '-' ||
    substr(hash, 21, 12)
  )::uuid
  from (select md5(seed) as hash) hashed;
$$;

create temp table seed_taxonomy_domains (
  id uuid not null,
  name text not null,
  slug text not null,
  description text,
  display_order integer not null
) on commit drop;

insert into seed_taxonomy_domains (id, name, slug, description, display_order)
values
  (pg_temp.seed_uuid('domain:animal-services-veterinary-care'), 'Animal Services & Veterinary Care', 'animal-services-veterinary-care', 'Animal care, training, wellness, control, and veterinary services.', 1),
  (pg_temp.seed_uuid('domain:automotive-transportation'), 'Automotive & Transportation', 'automotive-transportation', 'Vehicle repair, transport, logistics, and supply chain operations.', 2),
  (pg_temp.seed_uuid('domain:building-grounds-maintenance'), 'Building & Grounds Maintenance', 'building-grounds-maintenance', 'Facility, grounds, pest, janitorial, and maintenance services.', 3),
  (pg_temp.seed_uuid('domain:childcare-family-services'), 'Childcare & Family Services', 'childcare-family-services', 'Childcare, estate, senior, youth, and family support services.', 4),
  ('88888888-8888-4888-8888-888888888801', 'Creative, Media & Design', 'creative-media-design', 'Creative production, design, branding, writing, photography, and media services.', 5),
  (pg_temp.seed_uuid('domain:education-instruction'), 'Education & Instruction', 'education-instruction', 'Tutoring, coaching, arts pedagogy, language, and cultural instruction.', 6),
  (pg_temp.seed_uuid('domain:healthcare-wellness-services'), 'Healthcare & Wellness Services', 'healthcare-wellness-services', 'Fitness, wellness, therapy, nutrition, nursing, and family health services.', 7),
  (pg_temp.seed_uuid('domain:hospitality-event-services'), 'Hospitality & Event Services', 'hospitality-event-services', 'Events, food, beverage, lodging, travel, and concierge services.', 8),
  ('88888888-8888-4888-8888-888888888803', 'Professional & Business Services', 'professional-business-services', 'Finance, operations, HR, legal, compliance, marketing, and business services.', 9),
  (pg_temp.seed_uuid('domain:real-estate-property-services'), 'Real Estate & Property Services', 'real-estate-property-services', 'Real estate sales, architecture, interiors, property management, valuation, and law.', 10),
  (pg_temp.seed_uuid('domain:skilled-trades-construction'), 'Skilled Trades & Construction', 'skilled-trades-construction', 'Construction, trades, site management, building systems, and exterior work.', 11),
  ('88888888-8888-4888-8888-888888888802', 'Technical & Digital Infrastructure', 'technical-digital-infrastructure', 'Cybersecurity, data, software, engineering, and digital infrastructure services.', 12);

insert into app.taxonomy_domains (id, name, slug, description, display_order, is_active, updated_at)
select id, name, slug, description, display_order, true, now()
from seed_taxonomy_domains
on conflict (id) do update set
  name = excluded.name,
  slug = excluded.slug,
  description = excluded.description,
  display_order = excluded.display_order,
  is_active = excluded.is_active,
  updated_at = now();

create temp table seed_taxonomy_categories (
  id uuid not null,
  domain_slug text not null,
  name text not null,
  slug text not null,
  display_order integer not null
) on commit drop;

insert into seed_taxonomy_categories (id, domain_slug, name, slug, display_order)
values
  (pg_temp.seed_uuid('category:animal-behavioral-training'), 'animal-services-veterinary-care', 'Animal Behavioral Training', 'animal-behavioral-training', 1),
  (pg_temp.seed_uuid('category:animal-control-wildlife-services'), 'animal-services-veterinary-care', 'Animal Control & Wildlife Services', 'animal-control-wildlife-services', 2),
  (pg_temp.seed_uuid('category:pet-wellness-specialized-care'), 'animal-services-veterinary-care', 'Pet Wellness & Specialized Care', 'pet-wellness-specialized-care', 3),
  (pg_temp.seed_uuid('category:veterinary-clinical-medicine'), 'animal-services-veterinary-care', 'Veterinary & Clinical Medicine', 'veterinary-clinical-medicine', 4),
  (pg_temp.seed_uuid('category:automotive-repair-maintenance'), 'automotive-transportation', 'Automotive Repair & Maintenance', 'automotive-repair-maintenance', 1),
  (pg_temp.seed_uuid('category:fleet-logistics-operations'), 'automotive-transportation', 'Fleet & Logistics Operations', 'fleet-logistics-operations', 2),
  (pg_temp.seed_uuid('category:specialized-transport-services'), 'automotive-transportation', 'Specialized Transport Services', 'specialized-transport-services', 3),
  (pg_temp.seed_uuid('category:supply-chain-logistics-consulting'), 'automotive-transportation', 'Supply Chain & Logistics Consulting', 'supply-chain-logistics-consulting', 4),
  (pg_temp.seed_uuid('category:commercial-janitorial-sanitization'), 'building-grounds-maintenance', 'Commercial Janitorial & Sanitization', 'commercial-janitorial-sanitization', 1),
  (pg_temp.seed_uuid('category:general-facility-maintenance'), 'building-grounds-maintenance', 'General Facility Maintenance', 'general-facility-maintenance', 2),
  (pg_temp.seed_uuid('category:landscaping-arboriculture'), 'building-grounds-maintenance', 'Landscaping & Arboriculture', 'landscaping-arboriculture', 3),
  (pg_temp.seed_uuid('category:professional-pest-control'), 'building-grounds-maintenance', 'Professional Pest Control', 'professional-pest-control', 4),
  (pg_temp.seed_uuid('category:early-childhood-nanny-services'), 'childcare-family-services', 'Early Childhood & Nanny Services', 'early-childhood-nanny-services', 1),
  (pg_temp.seed_uuid('category:household-estate-management'), 'childcare-family-services', 'Household & Estate Management', 'household-estate-management', 2),
  (pg_temp.seed_uuid('category:senior-care-companion-services'), 'childcare-family-services', 'Senior Care & Companion Services', 'senior-care-companion-services', 3),
  (pg_temp.seed_uuid('category:youth-support-mentorship'), 'childcare-family-services', 'Youth Support & Mentorship', 'youth-support-mentorship', 4),
  (pg_temp.seed_uuid('category:digital-interface-ux-design'), 'creative-media-design', 'Digital Interface & UX Design', 'digital-interface-ux-design', 1),
  (pg_temp.seed_uuid('category:fine-arts-specialized-craftsmanship'), 'creative-media-design', 'Fine Arts & Specialized Craftsmanship', 'fine-arts-specialized-craftsmanship', 2),
  (pg_temp.seed_uuid('category:multimedia-video-production'), 'creative-media-design', 'Multimedia & Video Production', 'multimedia-video-production', 3),
  (pg_temp.seed_uuid('category:product-industrial-design'), 'creative-media-design', 'Product & Industrial Design', 'product-industrial-design', 4),
  (pg_temp.seed_uuid('category:professional-photography-imaging'), 'creative-media-design', 'Professional Photography & Imaging', 'professional-photography-imaging', 5),
  ('99999999-9999-4999-8999-999999999901', 'creative-media-design', 'Visual Communications & Branding', 'visual-communications-branding', 6),
  (pg_temp.seed_uuid('category:writing-editorial-translation'), 'creative-media-design', 'Writing, Editorial & Translation', 'writing-editorial-translation', 7),
  (pg_temp.seed_uuid('category:academic-tutoring-test-prep'), 'education-instruction', 'Academic Tutoring & Test Prep', 'academic-tutoring-test-prep', 1),
  (pg_temp.seed_uuid('category:arts-music-pedagogy'), 'education-instruction', 'Arts & Music Pedagogy', 'arts-music-pedagogy', 2),
  (pg_temp.seed_uuid('category:executive-career-life-coaching'), 'education-instruction', 'Executive, Career & Life Coaching', 'executive-career-life-coaching', 3),
  (pg_temp.seed_uuid('category:language-cultural-instruction'), 'education-instruction', 'Language & Cultural Instruction', 'language-cultural-instruction', 4),
  (pg_temp.seed_uuid('category:fitness-wellness-coaching'), 'healthcare-wellness-services', 'Fitness & Wellness Coaching', 'fitness-wellness-coaching', 1),
  (pg_temp.seed_uuid('category:maternal-family-health'), 'healthcare-wellness-services', 'Maternal & Family Health', 'maternal-family-health', 2),
  (pg_temp.seed_uuid('category:mental-health-counseling'), 'healthcare-wellness-services', 'Mental Health & Counseling', 'mental-health-counseling', 3),
  (pg_temp.seed_uuid('category:nutrition-dietetics'), 'healthcare-wellness-services', 'Nutrition & Dietetics', 'nutrition-dietetics', 4),
  (pg_temp.seed_uuid('category:physical-rehabilitative-therapies'), 'healthcare-wellness-services', 'Physical & Rehabilitative Therapies', 'physical-rehabilitative-therapies', 5),
  (pg_temp.seed_uuid('category:specialized-nursing-home-health'), 'healthcare-wellness-services', 'Specialized Nursing & Home Health', 'specialized-nursing-home-health', 6),
  (pg_temp.seed_uuid('category:event-planning-production'), 'hospitality-event-services', 'Event Planning & Production', 'event-planning-production', 1),
  (pg_temp.seed_uuid('category:food-beverage-services'), 'hospitality-event-services', 'Food & Beverage Services', 'food-beverage-services', 2),
  (pg_temp.seed_uuid('category:property-lodging-management'), 'hospitality-event-services', 'Property & Lodging Management', 'property-lodging-management', 3),
  (pg_temp.seed_uuid('category:travel-concierge-management'), 'hospitality-event-services', 'Travel & Concierge Management', 'travel-concierge-management', 4),
  (pg_temp.seed_uuid('category:accounting-finance-tax'), 'professional-business-services', 'Accounting, Finance & Tax', 'accounting-finance-tax', 1),
  ('99999999-9999-4999-8999-999999999903', 'professional-business-services', 'Business Operations & Project Management', 'business-operations-project-management', 2),
  (pg_temp.seed_uuid('category:human-resources-recruiting'), 'professional-business-services', 'Human Resources & Recruiting', 'human-resources-recruiting', 3),
  (pg_temp.seed_uuid('category:legal-compliance-services'), 'professional-business-services', 'Legal & Compliance Services', 'legal-compliance-services', 4),
  (pg_temp.seed_uuid('category:sales-marketing-pr'), 'professional-business-services', 'Sales, Marketing & PR', 'sales-marketing-pr', 5),
  (pg_temp.seed_uuid('category:agency-brokerage-sales'), 'real-estate-property-services', 'Agency, Brokerage & Sales', 'agency-brokerage-sales', 1),
  (pg_temp.seed_uuid('category:architecture-interior-design'), 'real-estate-property-services', 'Architecture & Interior Design', 'architecture-interior-design', 2),
  (pg_temp.seed_uuid('category:property-asset-management'), 'real-estate-property-services', 'Property & Asset Management', 'property-asset-management', 3),
  (pg_temp.seed_uuid('category:valuation-appraisal-law'), 'real-estate-property-services', 'Valuation, Appraisal & Law', 'valuation-appraisal-law', 4),
  (pg_temp.seed_uuid('category:carpentry-finish-work'), 'skilled-trades-construction', 'Carpentry & Finish Work', 'carpentry-finish-work', 1),
  (pg_temp.seed_uuid('category:concrete-masonry-excavation'), 'skilled-trades-construction', 'Concrete, Masonry & Excavation', 'concrete-masonry-excavation', 2),
  (pg_temp.seed_uuid('category:electrical-services'), 'skilled-trades-construction', 'Electrical Services', 'electrical-services', 3),
  (pg_temp.seed_uuid('category:general-contracting-site-management'), 'skilled-trades-construction', 'General Contracting & Site Management', 'general-contracting-site-management', 4),
  (pg_temp.seed_uuid('category:hvac-services'), 'skilled-trades-construction', 'HVAC Services', 'hvac-services', 5),
  (pg_temp.seed_uuid('category:plumbing-gas-fitting'), 'skilled-trades-construction', 'Plumbing & Gas Fitting', 'plumbing-gas-fitting', 6),
  (pg_temp.seed_uuid('category:roofing-exterior-envelope'), 'skilled-trades-construction', 'Roofing & Exterior Envelope', 'roofing-exterior-envelope', 7),
  (pg_temp.seed_uuid('category:cybersecurity-it-infrastructure'), 'technical-digital-infrastructure', 'Cybersecurity & IT Infrastructure', 'cybersecurity-it-infrastructure', 1),
  (pg_temp.seed_uuid('category:data-analytics-database-management'), 'technical-digital-infrastructure', 'Data Analytics & Database Management', 'data-analytics-database-management', 2),
  (pg_temp.seed_uuid('category:mechanical-systems-engineering'), 'technical-digital-infrastructure', 'Mechanical & Systems Engineering', 'mechanical-systems-engineering', 3),
  ('99999999-9999-4999-8999-999999999902', 'technical-digital-infrastructure', 'Software Development & Engineering', 'software-development-engineering', 4);

insert into app.taxonomy_categories (id, domain_id, name, slug, display_order, is_active, updated_at)
select c.id, d.id, c.name, c.slug, c.display_order, true, now()
from seed_taxonomy_categories c
join app.taxonomy_domains d on d.slug = c.domain_slug
on conflict (id) do update set
  domain_id = excluded.domain_id,
  name = excluded.name,
  slug = excluded.slug,
  display_order = excluded.display_order,
  is_active = excluded.is_active,
  updated_at = now();

create temp table seed_taxonomy_tags (
  id uuid not null,
  category_slug text not null,
  name text not null,
  slug text not null
) on commit drop;

insert into seed_taxonomy_tags (id, category_slug, name, slug)
values
  (pg_temp.seed_uuid('tag:k9-obedience'), 'animal-behavioral-training', 'K9 Obedience', 'k9-obedience'),
  (pg_temp.seed_uuid('tag:service-animal-certification'), 'animal-behavioral-training', 'Service Animal Certification', 'service-animal-certification'),
  (pg_temp.seed_uuid('tag:equine-therapy'), 'animal-behavioral-training', 'Equine Therapy', 'equine-therapy'),
  (pg_temp.seed_uuid('tag:humane-animal-control'), 'animal-control-wildlife-services', 'Humane Animal Control', 'humane-animal-control'),
  (pg_temp.seed_uuid('tag:wildlife-relocation'), 'animal-control-wildlife-services', 'Wildlife Relocation', 'wildlife-relocation'),
  (pg_temp.seed_uuid('tag:grooming'), 'pet-wellness-specialized-care', 'Grooming', 'grooming'),
  (pg_temp.seed_uuid('tag:boutique-boarding'), 'pet-wellness-specialized-care', 'Boutique Boarding', 'boutique-boarding'),
  (pg_temp.seed_uuid('tag:animal-nutrition'), 'pet-wellness-specialized-care', 'Animal Nutrition', 'animal-nutrition'),
  (pg_temp.seed_uuid('tag:surgery'), 'veterinary-clinical-medicine', 'Surgery', 'surgery'),
  (pg_temp.seed_uuid('tag:mobile-clinics'), 'veterinary-clinical-medicine', 'Mobile Clinics', 'mobile-clinics'),
  (pg_temp.seed_uuid('tag:lab-diagnostics'), 'veterinary-clinical-medicine', 'Lab Diagnostics', 'lab-diagnostics'),
  (pg_temp.seed_uuid('tag:ase-certified-mechanics'), 'automotive-repair-maintenance', 'ASE Certified Mechanics', 'ase-certified-mechanics'),
  (pg_temp.seed_uuid('tag:collision-repair'), 'automotive-repair-maintenance', 'Collision Repair', 'collision-repair'),
  (pg_temp.seed_uuid('tag:specialized-vehicle-services'), 'automotive-repair-maintenance', 'Specialized Vehicle Services', 'specialized-vehicle-services'),
  (pg_temp.seed_uuid('tag:fleet-maintenance-strategy'), 'fleet-logistics-operations', 'Fleet Maintenance Strategy', 'fleet-maintenance-strategy'),
  (pg_temp.seed_uuid('tag:dot-compliance'), 'fleet-logistics-operations', 'DOT Compliance', 'dot-compliance'),
  (pg_temp.seed_uuid('tag:inventory-management'), 'fleet-logistics-operations', 'Inventory Management', 'inventory-management'),
  (pg_temp.seed_uuid('tag:medical-transport'), 'specialized-transport-services', 'Medical Transport', 'medical-transport'),
  (pg_temp.seed_uuid('tag:luxury-chauffeur-services'), 'specialized-transport-services', 'Luxury Chauffeur Services', 'luxury-chauffeur-services'),
  (pg_temp.seed_uuid('tag:heavy-equipment-transport'), 'specialized-transport-services', 'Heavy Equipment Transport', 'heavy-equipment-transport'),
  (pg_temp.seed_uuid('tag:logistics-network-design'), 'supply-chain-logistics-consulting', 'Logistics Network Design', 'logistics-network-design'),
  (pg_temp.seed_uuid('tag:supply-chain-optimization'), 'supply-chain-logistics-consulting', 'Supply Chain Optimization', 'supply-chain-optimization'),
  (pg_temp.seed_uuid('tag:office-cleaning'), 'commercial-janitorial-sanitization', 'Office Cleaning', 'office-cleaning'),
  (pg_temp.seed_uuid('tag:industrial-floor-care'), 'commercial-janitorial-sanitization', 'Industrial Floor Care', 'industrial-floor-care'),
  (pg_temp.seed_uuid('tag:hazmat-cleaning'), 'commercial-janitorial-sanitization', 'Hazmat Cleaning', 'hazmat-cleaning'),
  (pg_temp.seed_uuid('tag:handyman-repairs'), 'general-facility-maintenance', 'Handyman Repairs', 'handyman-repairs'),
  (pg_temp.seed_uuid('tag:pool-aquatics-management'), 'general-facility-maintenance', 'Pool/Aquatics Management', 'pool-aquatics-management'),
  (pg_temp.seed_uuid('tag:non-licensed-upkeep'), 'general-facility-maintenance', 'Non-Licensed Upkeep', 'non-licensed-upkeep'),
  (pg_temp.seed_uuid('tag:hardscaping'), 'landscaping-arboriculture', 'Hardscaping', 'hardscaping'),
  (pg_temp.seed_uuid('tag:certified-tree-care'), 'landscaping-arboriculture', 'Certified Tree Care', 'certified-tree-care'),
  (pg_temp.seed_uuid('tag:irrigation'), 'landscaping-arboriculture', 'Irrigation', 'irrigation'),
  (pg_temp.seed_uuid('tag:integrated-pest-management'), 'professional-pest-control', 'Integrated Pest Management (IPM)', 'integrated-pest-management'),
  (pg_temp.seed_uuid('tag:extermination'), 'professional-pest-control', 'Extermination', 'extermination'),
  (pg_temp.seed_uuid('tag:career-nannies'), 'early-childhood-nanny-services', 'Career Nannies', 'career-nannies'),
  (pg_temp.seed_uuid('tag:au-pairs'), 'early-childhood-nanny-services', 'Au Pairs', 'au-pairs'),
  (pg_temp.seed_uuid('tag:childcare-coordination'), 'early-childhood-nanny-services', 'Childcare Coordination', 'childcare-coordination'),
  (pg_temp.seed_uuid('tag:private-estate-managers'), 'household-estate-management', 'Private Estate Managers', 'private-estate-managers'),
  (pg_temp.seed_uuid('tag:professional-personal-assistants'), 'household-estate-management', 'Professional Personal Assistants', 'professional-personal-assistants'),
  (pg_temp.seed_uuid('tag:geriatric-care-management'), 'senior-care-companion-services', 'Geriatric Care Management', 'geriatric-care-management'),
  (pg_temp.seed_uuid('tag:companion-care'), 'senior-care-companion-services', 'Companion Care', 'companion-care'),
  (pg_temp.seed_uuid('tag:academic-coaching'), 'youth-support-mentorship', 'Academic Coaching', 'academic-coaching'),
  (pg_temp.seed_uuid('tag:youth-advocacy'), 'youth-support-mentorship', 'Youth Advocacy', 'youth-advocacy'),
  (pg_temp.seed_uuid('tag:behavioral-mentorship'), 'youth-support-mentorship', 'Behavioral Mentorship', 'behavioral-mentorship'),
  (pg_temp.seed_uuid('tag:website-design'), 'digital-interface-ux-design', 'Website Design', 'website-design'),
  (pg_temp.seed_uuid('tag:app-design'), 'digital-interface-ux-design', 'App Design', 'app-design'),
  (pg_temp.seed_uuid('tag:ui-ux-architecture'), 'digital-interface-ux-design', 'UI/UX Architecture', 'ui-ux-architecture'),
  (pg_temp.seed_uuid('tag:drawing'), 'fine-arts-specialized-craftsmanship', 'Drawing', 'drawing'),
  (pg_temp.seed_uuid('tag:painting'), 'fine-arts-specialized-craftsmanship', 'Painting', 'painting'),
  (pg_temp.seed_uuid('tag:sculpting'), 'fine-arts-specialized-craftsmanship', 'Sculpting', 'sculpting'),
  (pg_temp.seed_uuid('tag:molding-clay'), 'fine-arts-specialized-craftsmanship', 'Molding/Clay', 'molding-clay'),
  (pg_temp.seed_uuid('tag:custom-commissions'), 'fine-arts-specialized-craftsmanship', 'Custom Commissions', 'custom-commissions'),
  (pg_temp.seed_uuid('tag:videography'), 'multimedia-video-production', 'Videography', 'videography'),
  (pg_temp.seed_uuid('tag:cinematography'), 'multimedia-video-production', 'Cinematography', 'cinematography'),
  (pg_temp.seed_uuid('tag:post-production'), 'multimedia-video-production', 'Post-Production', 'post-production'),
  (pg_temp.seed_uuid('tag:apparel'), 'product-industrial-design', 'Apparel', 'apparel'),
  (pg_temp.seed_uuid('tag:industrial-design'), 'product-industrial-design', 'Industrial Design', 'industrial-design'),
  (pg_temp.seed_uuid('tag:gym-equipment'), 'product-industrial-design', 'Gym Equipment', 'gym-equipment'),
  (pg_temp.seed_uuid('tag:architectural-product-design'), 'product-industrial-design', 'Architectural Product Design', 'architectural-product-design'),
  (pg_temp.seed_uuid('tag:commercial-photography'), 'professional-photography-imaging', 'Commercial Photography', 'commercial-photography'),
  (pg_temp.seed_uuid('tag:retouching'), 'professional-photography-imaging', 'Retouching', 'retouching'),
  (pg_temp.seed_uuid('tag:drone-imaging'), 'professional-photography-imaging', 'Drone Imaging', 'drone-imaging'),
  ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1', 'visual-communications-branding', 'Logo Design', 'logo-design'),
  ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa2', 'visual-communications-branding', 'Brand Strategy', 'brand-strategy'),
  ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa3', 'visual-communications-branding', 'Environmental Graphics', 'environmental-graphics'),
  (pg_temp.seed_uuid('tag:copywriting'), 'writing-editorial-translation', 'Copywriting', 'copywriting'),
  (pg_temp.seed_uuid('tag:technical-writing'), 'writing-editorial-translation', 'Technical Writing', 'technical-writing'),
  (pg_temp.seed_uuid('tag:literary-translation'), 'writing-editorial-translation', 'Literary Translation', 'literary-translation'),
  (pg_temp.seed_uuid('tag:k-12-core-subjects'), 'academic-tutoring-test-prep', 'K-12 Core Subjects', 'k-12-core-subjects'),
  (pg_temp.seed_uuid('tag:sat-act-prep'), 'academic-tutoring-test-prep', 'SAT/ACT Prep', 'sat-act-prep'),
  (pg_temp.seed_uuid('tag:instrumental-vocal-coaching'), 'arts-music-pedagogy', 'Instrumental/Vocal Coaching', 'instrumental-vocal-coaching'),
  (pg_temp.seed_uuid('tag:fine-arts-instruction'), 'arts-music-pedagogy', 'Fine Arts Instruction', 'fine-arts-instruction'),
  (pg_temp.seed_uuid('tag:life-coaching'), 'executive-career-life-coaching', 'Life Coaching', 'life-coaching'),
  (pg_temp.seed_uuid('tag:leadership-development'), 'executive-career-life-coaching', 'Leadership Development', 'leadership-development'),
  (pg_temp.seed_uuid('tag:icf-coaching'), 'executive-career-life-coaching', 'ICF Coaching', 'icf-coaching'),
  (pg_temp.seed_uuid('tag:foreign-language-teaching'), 'language-cultural-instruction', 'Foreign Language Teaching', 'foreign-language-teaching'),
  (pg_temp.seed_uuid('tag:tesol-tefl'), 'language-cultural-instruction', 'TESOL/TEFL', 'tesol-tefl'),
  (pg_temp.seed_uuid('tag:personal-training'), 'fitness-wellness-coaching', 'Personal Training', 'personal-training'),
  (pg_temp.seed_uuid('tag:yoga'), 'fitness-wellness-coaching', 'Yoga', 'yoga'),
  (pg_temp.seed_uuid('tag:strength-conditioning'), 'fitness-wellness-coaching', 'Strength & Conditioning', 'strength-conditioning'),
  (pg_temp.seed_uuid('tag:prenatal-postnatal-services'), 'maternal-family-health', 'Prenatal & Postnatal Services', 'prenatal-postnatal-services'),
  (pg_temp.seed_uuid('tag:doula-care'), 'maternal-family-health', 'Doula Care', 'doula-care'),
  (pg_temp.seed_uuid('tag:lactation-consulting'), 'maternal-family-health', 'Lactation Consulting', 'lactation-consulting'),
  (pg_temp.seed_uuid('tag:licensed-therapy'), 'mental-health-counseling', 'Licensed Therapy', 'licensed-therapy'),
  (pg_temp.seed_uuid('tag:addiction-counseling'), 'mental-health-counseling', 'Addiction Counseling', 'addiction-counseling'),
  (pg_temp.seed_uuid('tag:registered-dietitian-services'), 'nutrition-dietetics', 'Registered Dietitian (RD) Services', 'registered-dietitian-services'),
  (pg_temp.seed_uuid('tag:metabolic-health'), 'nutrition-dietetics', 'Metabolic Health', 'metabolic-health'),
  (pg_temp.seed_uuid('tag:physical-therapy'), 'physical-rehabilitative-therapies', 'Physical Therapy', 'physical-therapy'),
  (pg_temp.seed_uuid('tag:occupational-therapy'), 'physical-rehabilitative-therapies', 'Occupational Therapy', 'occupational-therapy'),
  (pg_temp.seed_uuid('tag:massage-therapy'), 'physical-rehabilitative-therapies', 'Massage Therapy', 'massage-therapy'),
  (pg_temp.seed_uuid('tag:hospice-care'), 'specialized-nursing-home-health', 'Hospice Care', 'hospice-care'),
  (pg_temp.seed_uuid('tag:medical-assistance'), 'specialized-nursing-home-health', 'Medical Assistance', 'medical-assistance'),
  (pg_temp.seed_uuid('tag:corporate-events'), 'event-planning-production', 'Corporate Events', 'corporate-events'),
  (pg_temp.seed_uuid('tag:wedding-coordination'), 'event-planning-production', 'Wedding Coordination', 'wedding-coordination'),
  (pg_temp.seed_uuid('tag:av-production'), 'event-planning-production', 'AV Production', 'av-production'),
  (pg_temp.seed_uuid('tag:professional-catering'), 'food-beverage-services', 'Professional Catering', 'professional-catering'),
  (pg_temp.seed_uuid('tag:private-chefs'), 'food-beverage-services', 'Private Chefs', 'private-chefs'),
  (pg_temp.seed_uuid('tag:menu-consulting'), 'food-beverage-services', 'Menu Consulting', 'menu-consulting'),
  (pg_temp.seed_uuid('tag:hotel-operations'), 'property-lodging-management', 'Hotel Operations', 'hotel-operations'),
  (pg_temp.seed_uuid('tag:short-term-rental-management'), 'property-lodging-management', 'Short-Term Rental Management', 'short-term-rental-management'),
  (pg_temp.seed_uuid('tag:luxury-travel-advisors'), 'travel-concierge-management', 'Luxury Travel Advisors', 'luxury-travel-advisors'),
  (pg_temp.seed_uuid('tag:destination-management'), 'travel-concierge-management', 'Destination Management', 'destination-management'),
  (pg_temp.seed_uuid('tag:cpa-services'), 'accounting-finance-tax', 'CPA Services', 'cpa-services'),
  (pg_temp.seed_uuid('tag:tax-prep'), 'accounting-finance-tax', 'Tax Prep', 'tax-prep'),
  (pg_temp.seed_uuid('tag:financial-modeling'), 'accounting-finance-tax', 'Financial Modeling', 'financial-modeling'),
  ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa7', 'business-operations-project-management', 'PMP Project Management', 'pmp-project-management'),
  ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa8', 'business-operations-project-management', 'Operational Audits', 'operational-audits'),
  (pg_temp.seed_uuid('tag:talent-acquisition'), 'human-resources-recruiting', 'Talent Acquisition', 'talent-acquisition'),
  (pg_temp.seed_uuid('tag:organizational-development'), 'human-resources-recruiting', 'Organizational Development', 'organizational-development'),
  (pg_temp.seed_uuid('tag:business-formation'), 'legal-compliance-services', 'Business Formation', 'business-formation'),
  (pg_temp.seed_uuid('tag:contract-law'), 'legal-compliance-services', 'Contract Law', 'contract-law'),
  ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa9', 'legal-compliance-services', 'HR Compliance', 'hr-compliance'),
  (pg_temp.seed_uuid('tag:seo-strategy'), 'sales-marketing-pr', 'SEO Strategy', 'seo-strategy'),
  (pg_temp.seed_uuid('tag:public-relations'), 'sales-marketing-pr', 'Public Relations', 'public-relations'),
  (pg_temp.seed_uuid('tag:digital-advertising'), 'sales-marketing-pr', 'Digital Advertising', 'digital-advertising'),
  (pg_temp.seed_uuid('tag:residential-sales'), 'agency-brokerage-sales', 'Residential Sales', 'residential-sales'),
  (pg_temp.seed_uuid('tag:commercial-leasing'), 'agency-brokerage-sales', 'Commercial Leasing', 'commercial-leasing'),
  (pg_temp.seed_uuid('tag:investment-sales'), 'agency-brokerage-sales', 'Investment Sales', 'investment-sales'),
  (pg_temp.seed_uuid('tag:residential-architecture'), 'architecture-interior-design', 'Residential Architecture', 'residential-architecture'),
  (pg_temp.seed_uuid('tag:interior-design'), 'architecture-interior-design', 'Interior Design', 'interior-design'),
  (pg_temp.seed_uuid('tag:long-term-property-management'), 'property-asset-management', 'Long-Term Property Management', 'long-term-property-management'),
  (pg_temp.seed_uuid('tag:commercial-property-management'), 'property-asset-management', 'Commercial Property Management', 'commercial-property-management'),
  (pg_temp.seed_uuid('tag:appraisals'), 'valuation-appraisal-law', 'Appraisals', 'appraisals'),
  (pg_temp.seed_uuid('tag:title-services'), 'valuation-appraisal-law', 'Title Services', 'title-services'),
  (pg_temp.seed_uuid('tag:real-estate-law'), 'valuation-appraisal-law', 'Real Estate Law', 'real-estate-law'),
  (pg_temp.seed_uuid('tag:framing'), 'carpentry-finish-work', 'Framing', 'framing'),
  (pg_temp.seed_uuid('tag:cabinetry'), 'carpentry-finish-work', 'Cabinetry', 'cabinetry'),
  (pg_temp.seed_uuid('tag:finish-carpentry'), 'carpentry-finish-work', 'Finish Carpentry', 'finish-carpentry'),
  (pg_temp.seed_uuid('tag:custom-woodwork'), 'carpentry-finish-work', 'Custom Woodwork', 'custom-woodwork'),
  (pg_temp.seed_uuid('tag:foundations'), 'concrete-masonry-excavation', 'Foundations', 'foundations'),
  (pg_temp.seed_uuid('tag:brickwork'), 'concrete-masonry-excavation', 'Brickwork', 'brickwork'),
  (pg_temp.seed_uuid('tag:stone-masonry'), 'concrete-masonry-excavation', 'Stone Masonry', 'stone-masonry'),
  (pg_temp.seed_uuid('tag:earthmoving-services'), 'concrete-masonry-excavation', 'Earthmoving Services', 'earthmoving-services'),
  (pg_temp.seed_uuid('tag:residential-commercial-wiring'), 'electrical-services', 'Residential/Commercial Wiring', 'residential-commercial-wiring'),
  (pg_temp.seed_uuid('tag:smart-home-integration'), 'electrical-services', 'Smart Home Integration', 'smart-home-integration'),
  (pg_temp.seed_uuid('tag:journeyman-master-electrician'), 'electrical-services', 'Journeyman/Master Electrician', 'journeyman-master-electrician'),
  (pg_temp.seed_uuid('tag:project-oversight'), 'general-contracting-site-management', 'Project Oversight', 'project-oversight'),
  (pg_temp.seed_uuid('tag:agc-construction-management'), 'general-contracting-site-management', 'AGC Construction Management', 'agc-construction-management'),
  (pg_temp.seed_uuid('tag:estimating'), 'general-contracting-site-management', 'Estimating', 'estimating'),
  (pg_temp.seed_uuid('tag:heating-ventilation-air-conditioning'), 'hvac-services', 'Heating, Ventilation, and Air Conditioning Systems', 'heating-ventilation-air-conditioning'),
  (pg_temp.seed_uuid('tag:residential-commercial-hvac'), 'hvac-services', 'Residential/Commercial HVAC', 'residential-commercial-hvac'),
  (pg_temp.seed_uuid('tag:pipe-fitting'), 'plumbing-gas-fitting', 'Pipe Fitting', 'pipe-fitting'),
  (pg_temp.seed_uuid('tag:water-heater-installation'), 'plumbing-gas-fitting', 'Water Heater Installation', 'water-heater-installation'),
  (pg_temp.seed_uuid('tag:licensed-plumbing'), 'plumbing-gas-fitting', 'Licensed Plumbing', 'licensed-plumbing'),
  (pg_temp.seed_uuid('tag:residential-roofing'), 'roofing-exterior-envelope', 'Residential Roofing', 'residential-roofing'),
  (pg_temp.seed_uuid('tag:commercial-membranes'), 'roofing-exterior-envelope', 'Commercial Membranes', 'commercial-membranes'),
  (pg_temp.seed_uuid('tag:specialized-roofing-contractors'), 'roofing-exterior-envelope', 'Specialized Roofing Contractors', 'specialized-roofing-contractors'),
  (pg_temp.seed_uuid('tag:security-auditing'), 'cybersecurity-it-infrastructure', 'Security Auditing', 'security-auditing'),
  (pg_temp.seed_uuid('tag:cloud-migration'), 'cybersecurity-it-infrastructure', 'Cloud Migration', 'cloud-migration'),
  (pg_temp.seed_uuid('tag:data-visualization'), 'data-analytics-database-management', 'Data Visualization', 'data-visualization'),
  (pg_temp.seed_uuid('tag:sql-administration'), 'data-analytics-database-management', 'SQL Administration', 'sql-administration'),
  (pg_temp.seed_uuid('tag:robotics'), 'mechanical-systems-engineering', 'Robotics', 'robotics'),
  (pg_temp.seed_uuid('tag:machine-design'), 'mechanical-systems-engineering', 'Machine Design', 'machine-design'),
  (pg_temp.seed_uuid('tag:industrial-systems-engineering'), 'mechanical-systems-engineering', 'Industrial Systems Engineering', 'industrial-systems-engineering'),
  ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa4', 'software-development-engineering', 'Full-Stack Development', 'full-stack-development'),
  ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa5', 'software-development-engineering', 'Mobile Apps', 'mobile-apps'),
  ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa6', 'software-development-engineering', 'AI/ML Training', 'ai-ml-training');

insert into app.taxonomy_tags (id, category_id, name, slug, is_active, updated_at)
select t.id, c.id, t.name, t.slug, true, now()
from seed_taxonomy_tags t
join app.taxonomy_categories c on c.slug = t.category_slug
on conflict (id) do update set
  category_id = excluded.category_id,
  name = excluded.name,
  slug = excluded.slug,
  is_active = excluded.is_active,
  updated_at = now();

insert into app.users (id, email, handle, display_name, city, state, country, is_public, updated_at)
values
  ('11111111-1111-4111-8111-111111111111', 'seed.gig-poster@workinants.local', 'seed-gig-poster', 'Seed Gig Poster', 'Austin', 'TX', 'US', true, now()),
  ('22222222-2222-4222-8222-222222222222', 'seed.professional@workinants.local', 'seed-professional', 'Seed Professional', 'Seattle', 'WA', 'US', true, now()),
  ('33333333-3333-4333-8333-333333333333', 'seed.candidate@workinants.local', 'seed-candidate', 'Seed Candidate', 'Chicago', 'IL', 'US', true, now()),
  ('44444444-4444-4444-8444-444444444444', 'seed.org-member@workinants.local', 'seed-org-member', 'Seed Organization Member', 'New York', 'NY', 'US', true, now())
on conflict (id) do update set
  email = excluded.email,
  handle = excluded.handle,
  display_name = excluded.display_name,
  city = excluded.city,
  state = excluded.state,
  country = excluded.country,
  is_public = excluded.is_public,
  updated_at = now();

insert into app.user_roles (user_id, role)
values
  ('11111111-1111-4111-8111-111111111111', 'user'),
  ('22222222-2222-4222-8222-222222222222', 'user'),
  ('33333333-3333-4333-8333-333333333333', 'user'),
  ('44444444-4444-4444-8444-444444444444', 'user')
on conflict (user_id, role) do nothing;

insert into app.professional_profiles (
  id, user_id, slug, headline, bio, city, state, country, status, default_currency, updated_at
)
values (
  '55555555-5555-4555-8555-555555555555',
  '22222222-2222-4222-8222-222222222222',
  'seed-professional',
  'Brand and frontend specialist',
  'Seed professional profile for database truth-layer verification.',
  'Seattle',
  'WA',
  'US',
  'active',
  'usd',
  now()
)
on conflict (id) do update set
  headline = excluded.headline,
  bio = excluded.bio,
  status = excluded.status,
  default_currency = excluded.default_currency,
  updated_at = now();

insert into app.candidate_profiles (
  id, user_id, headline, resume_url, portfolio_url, availability, city, state, country, status, is_visible, updated_at
)
values (
  '66666666-6666-4666-8666-666666666666',
  '33333333-3333-4333-8333-333333333333',
  'Frontend candidate',
  'https://example.com/seed-candidate-resume.pdf',
  'https://example.com/seed-candidate',
  'Immediately available',
  'Chicago',
  'IL',
  'US',
  'active',
  true,
  now()
)
on conflict (id) do update set
  headline = excluded.headline,
  resume_url = excluded.resume_url,
  portfolio_url = excluded.portfolio_url,
  availability = excluded.availability,
  status = excluded.status,
  is_visible = excluded.is_visible,
  updated_at = now();

insert into app.organizations (
  id, slug, name, description, industry, city, state, country, status, owner_user_id, updated_at
)
values (
  '77777777-7777-4777-8777-777777777777',
  'seed-hiring-co',
  'Seed Hiring Co',
  'Seed organization for hiring truth-layer verification.',
  'Technology',
  'New York',
  'NY',
  'US',
  'active',
  '44444444-4444-4444-8444-444444444444',
  now()
)
on conflict (id) do update set
  name = excluded.name,
  description = excluded.description,
  status = excluded.status,
  owner_user_id = excluded.owner_user_id,
  updated_at = now();

insert into app.organization_members (organization_id, user_id, role)
values ('77777777-7777-4777-8777-777777777777', '44444444-4444-4444-8444-444444444444', 'owner')
on conflict (organization_id, user_id) do update set role = excluded.role;

insert into app.professional_categories (professional_profile_id, category_id)
values
  ('55555555-5555-4555-8555-555555555555', '99999999-9999-4999-8999-999999999901'),
  ('55555555-5555-4555-8555-555555555555', '99999999-9999-4999-8999-999999999902')
on conflict (professional_profile_id, category_id) do nothing;

insert into app.professional_tags (professional_profile_id, tag_id, source, confidence, verified)
values
  ('55555555-5555-4555-8555-555555555555', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa2', 'admin', 1, true),
  ('55555555-5555-4555-8555-555555555555', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa4', 'admin', 1, true)
on conflict (professional_profile_id, tag_id) do update set
  source = excluded.source,
  confidence = excluded.confidence,
  verified = excluded.verified;

insert into app.candidate_categories (candidate_profile_id, category_id)
values ('66666666-6666-4666-8666-666666666666', '99999999-9999-4999-8999-999999999902')
on conflict (candidate_profile_id, category_id) do nothing;

insert into app.candidate_tags (candidate_profile_id, tag_id, source, confidence, verified)
values ('66666666-6666-4666-8666-666666666666', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa5', 'user', 0.9, false)
on conflict (candidate_profile_id, tag_id) do update set
  source = excluded.source,
  confidence = excluded.confidence,
  verified = excluded.verified;

insert into app.organization_categories (organization_id, category_id)
values ('77777777-7777-4777-8777-777777777777', '99999999-9999-4999-8999-999999999902')
on conflict (organization_id, category_id) do nothing;

insert into app.organization_tags (organization_id, tag_id, source, confidence, verified)
values ('77777777-7777-4777-8777-777777777777', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa6', 'admin', 1, true)
on conflict (organization_id, tag_id) do update set
  source = excluded.source,
  confidence = excluded.confidence,
  verified = excluded.verified;

insert into app.media_assets (
  id, uploaded_by_user_id, bucket, storage_key, public_url, mime_type, size_bytes, alt_text, status
)
values
  ('cccccccc-cccc-4ccc-8ccc-ccccccccccc1', '22222222-2222-4222-8222-222222222222', 'seed-media', 'seed/profile-avatar.png', 'https://example.com/seed/profile-avatar.png', 'image/png', 12000, 'Seed profile avatar', 'ready'),
  ('cccccccc-cccc-4ccc-8ccc-ccccccccccc2', '22222222-2222-4222-8222-222222222222', 'seed-media', 'seed/offering-preview.png', 'https://example.com/seed/offering-preview.png', 'image/png', 24000, 'Seed offering preview', 'ready'),
  ('cccccccc-cccc-4ccc-8ccc-ccccccccccc3', '11111111-1111-4111-8111-111111111111', 'seed-media', 'seed/gig-brief.pdf', 'https://example.com/seed/gig-brief.pdf', 'application/pdf', 32000, 'Seed gig brief', 'ready'),
  ('cccccccc-cccc-4ccc-8ccc-ccccccccccc4', '44444444-4444-4444-8444-444444444444', 'seed-media', 'seed/job-description.pdf', 'https://example.com/seed/job-description.pdf', 'application/pdf', 28000, 'Seed job description', 'ready'),
  ('cccccccc-cccc-4ccc-8ccc-ccccccccccc5', '22222222-2222-4222-8222-222222222222', 'seed-media', 'seed/message-attachment.txt', 'https://example.com/seed/message-attachment.txt', 'text/plain', 512, 'Seed message attachment', 'ready')
on conflict (id) do update set
  uploaded_by_user_id = excluded.uploaded_by_user_id,
  bucket = excluded.bucket,
  storage_key = excluded.storage_key,
  public_url = excluded.public_url,
  mime_type = excluded.mime_type,
  size_bytes = excluded.size_bytes,
  alt_text = excluded.alt_text,
  status = excluded.status;

insert into app.user_media (user_id, media_id, role)
values ('22222222-2222-4222-8222-222222222222', 'cccccccc-cccc-4ccc-8ccc-ccccccccccc1', 'avatar')
on conflict (user_id, media_id) do update set role = excluded.role;

insert into app.professional_profile_media (professional_profile_id, media_id, role)
values ('55555555-5555-4555-8555-555555555555', 'cccccccc-cccc-4ccc-8ccc-ccccccccccc1', 'avatar')
on conflict (professional_profile_id, media_id) do update set role = excluded.role;

insert into app.offerings (
  id, kind, slug, title, summary, description, status, professional_profile_id, domain_id, category_id, price_from_cents, currency, is_public, updated_at
)
values
  ('bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbb1', 'service', 'seed-logo-design-service', 'Seed Logo Design Service', 'A concise logo design package for seed verification.', 'Representative service offering owned by a ProfessionalProfile.', 'active', '55555555-5555-4555-8555-555555555555', '88888888-8888-4888-8888-888888888801', '99999999-9999-4999-8999-999999999901', 65000, 'usd', true, now()),
  ('bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbb2', 'product', 'seed-brand-kit-product', 'Seed Brand Kit Product', 'Downloadable brand starter kit.', 'Representative product offering owned by a ProfessionalProfile.', 'active', '55555555-5555-4555-8555-555555555555', '88888888-8888-4888-8888-888888888801', '99999999-9999-4999-8999-999999999901', 4900, 'usd', true, now()),
  ('bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbb3', 'course', 'seed-nextjs-course', 'Seed Next.js Course', 'Self-paced frontend course.', 'Representative course offering owned by a ProfessionalProfile.', 'active', '55555555-5555-4555-8555-555555555555', '88888888-8888-4888-8888-888888888802', '99999999-9999-4999-8999-999999999902', 19900, 'usd', true, now())
on conflict (id) do update set
  status = excluded.status,
  price_from_cents = excluded.price_from_cents,
  updated_at = now();

insert into app.service_details (offering_id, delivery_mode, duration_minutes, min_start_delay_days, booking_buffer_min)
values ('bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbb1', 'digital', 90, 2, 15)
on conflict (offering_id) do update set
  delivery_mode = excluded.delivery_mode,
  duration_minutes = excluded.duration_minutes,
  min_start_delay_days = excluded.min_start_delay_days,
  booking_buffer_min = excluded.booking_buffer_min;

insert into app.product_details (offering_id, delivery_mode, file_asset_id)
values ('bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbb2', 'download', 'cccccccc-cccc-4ccc-8ccc-ccccccccccc2')
on conflict (offering_id) do update set
  delivery_mode = excluded.delivery_mode,
  file_asset_id = excluded.file_asset_id;

insert into app.course_details (offering_id, delivery_mode, course_length_minutes, lesson_count, access_expires_after_days)
values ('bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbb3', 'self_paced', 240, 12, null)
on conflict (offering_id) do update set
  delivery_mode = excluded.delivery_mode,
  course_length_minutes = excluded.course_length_minutes,
  lesson_count = excluded.lesson_count,
  access_expires_after_days = excluded.access_expires_after_days;

insert into app.pricing_tiers (id, offering_id, name, description, price_cents, currency, display_order, is_active, updated_at)
values
  ('26262626-2626-4262-8262-262626262621', 'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbb1', 'Standard', 'One logo concept and one revision.', 65000, 'usd', 1, true, now()),
  ('26262626-2626-4262-8262-262626262622', 'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbb2', 'Download', 'Brand starter kit files.', 4900, 'usd', 1, true, now()),
  ('26262626-2626-4262-8262-262626262623', 'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbb3', 'Lifetime', 'Lifetime course access.', 19900, 'usd', 1, true, now())
on conflict (id) do update set
  name = excluded.name,
  description = excluded.description,
  price_cents = excluded.price_cents,
  currency = excluded.currency,
  display_order = excluded.display_order,
  is_active = excluded.is_active,
  updated_at = now();

insert into app.offering_tags (offering_id, tag_id, source, confidence, verified)
values
  ('bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbb1', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1', 'admin', 1, true),
  ('bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbb1', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa2', 'admin', 1, true),
  ('bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbb2', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa3', 'admin', 1, true),
  ('bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbb3', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa4', 'admin', 1, true),
  ('bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbb3', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa5', 'admin', 1, true)
on conflict (offering_id, tag_id) do update set
  source = excluded.source,
  confidence = excluded.confidence,
  verified = excluded.verified;

insert into app.offering_media (offering_id, media_id, sort_order)
values
  ('bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbb1', 'cccccccc-cccc-4ccc-8ccc-ccccccccccc2', 1),
  ('bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbb2', 'cccccccc-cccc-4ccc-8ccc-ccccccccccc2', 1)
on conflict (offering_id, media_id) do update set sort_order = excluded.sort_order;

insert into app.gigs (
  id, poster_user_id, title, description, status, visibility, domain_id, category_id, budget_min_cents, budget_max_cents, currency, city, state, country, remote_ok, updated_at
)
values (
  'dddddddd-dddd-4ddd-8ddd-dddddddddddd',
  '11111111-1111-4111-8111-111111111111',
  'Seed logo refresh gig',
  'Public request for a paid logo refresh.',
  'assigned',
  'public',
  '88888888-8888-4888-8888-888888888801',
  '99999999-9999-4999-8999-999999999901',
  50000,
  90000,
  'usd',
  'Austin',
  'TX',
  'US',
  true,
  now()
)
on conflict (id) do update set
  status = excluded.status,
  budget_min_cents = excluded.budget_min_cents,
  budget_max_cents = excluded.budget_max_cents,
  updated_at = now();

insert into app.gig_tags (gig_id, tag_id, source, confidence, verified)
values
  ('dddddddd-dddd-4ddd-8ddd-dddddddddddd', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa2', 'user', 0.8, false),
  ('dddddddd-dddd-4ddd-8ddd-dddddddddddd', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa3', 'user', 0.8, false)
on conflict (gig_id, tag_id) do update set
  source = excluded.source,
  confidence = excluded.confidence,
  verified = excluded.verified;

insert into app.gig_media (gig_id, media_id, role)
values ('dddddddd-dddd-4ddd-8ddd-dddddddddddd', 'cccccccc-cccc-4ccc-8ccc-ccccccccccc3', 'brief')
on conflict (gig_id, media_id) do update set role = excluded.role;

insert into app.gig_responses (
  id, gig_id, responder_user_id, professional_profile_id, message, proposed_cents, currency, estimated_days, status, updated_at
)
values (
  'eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee',
  'dddddddd-dddd-4ddd-8ddd-dddddddddddd',
  '22222222-2222-4222-8222-222222222222',
  '55555555-5555-4555-8555-555555555555',
  'I can refresh this logo with a clean brand-ready direction.',
  75000,
  'usd',
  7,
  'accepted',
  now()
)
on conflict (id) do update set
  proposed_cents = excluded.proposed_cents,
  estimated_days = excluded.estimated_days,
  status = excluded.status,
  updated_at = now();

insert into app.gig_assignments (
  id, gig_id, gig_response_id, professional_profile_id, buyer_user_id, status, title, description, agreed_price_cents, currency, updated_at
)
values (
  'ffffffff-ffff-4fff-8fff-ffffffffffff',
  'dddddddd-dddd-4ddd-8ddd-dddddddddddd',
  'eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee',
  '55555555-5555-4555-8555-555555555555',
  '11111111-1111-4111-8111-111111111111',
  'active',
  'Seed logo refresh assignment',
  'Accepted assignment from the seed gig response.',
  75000,
  'usd',
  now()
)
on conflict (id) do update set
  status = excluded.status,
  agreed_price_cents = excluded.agreed_price_cents,
  updated_at = now();

insert into app.jobs (
  id, organization_id, title, description, status, visibility, employment_type, domain_id, category_id, city, state, country, remote_ok, compensation_min_cents, compensation_max_cents, currency, updated_at
)
values (
  '12121212-1212-4121-8121-121212121212',
  '77777777-7777-4777-8777-777777777777',
  'Seed Frontend Developer Job',
  'Formal hiring post from an organization.',
  'open',
  'public',
  'full_time',
  '88888888-8888-4888-8888-888888888802',
  '99999999-9999-4999-8999-999999999902',
  'New York',
  'NY',
  'US',
  true,
  9000000,
  13000000,
  'usd',
  now()
)
on conflict (id) do update set
  status = excluded.status,
  visibility = excluded.visibility,
  updated_at = now();

insert into app.job_tags (job_id, tag_id, source, confidence, verified)
values
  ('12121212-1212-4121-8121-121212121212', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa4', 'organization', 1, true),
  ('12121212-1212-4121-8121-121212121212', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa5', 'organization', 1, true),
  ('12121212-1212-4121-8121-121212121212', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa6', 'organization', 1, true)
on conflict (job_id, tag_id) do update set
  source = excluded.source,
  confidence = excluded.confidence,
  verified = excluded.verified;

insert into app.job_media (job_id, media_id, role)
values ('12121212-1212-4121-8121-121212121212', 'cccccccc-cccc-4ccc-8ccc-ccccccccccc4', 'description')
on conflict (job_id, media_id) do update set role = excluded.role;

insert into app.job_applications (
  id, job_id, candidate_profile_id, resume_url, cover_letter, answers, status, stage
)
values (
  '13131313-1313-4131-8131-131313131313',
  '12121212-1212-4121-8121-121212121212',
  '66666666-6666-4666-8666-666666666666',
  'https://example.com/seed-candidate-resume.pdf',
  'I am interested in this seed frontend role.',
  '{"yearsExperience":4,"remotePreference":"hybrid"}'::jsonb,
  'submitted',
  'new_'
)
on conflict (id) do update set
  status = excluded.status,
  stage = excluded.stage;

insert into app.orders (
  id, status, source_type, offering_id, buyer_user_id, seller_professional_profile_id, price_cents, currency, paid_at, brief_text, updated_at
)
values (
  '14141414-1414-4141-8141-141414141414',
  'paid',
  'offering',
  'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbb1',
  '11111111-1111-4111-8111-111111111111',
  '55555555-5555-4555-8555-555555555555',
  65000,
  'usd',
  '2026-06-01T12:30:00.000Z',
  'Seed offering purchase brief.',
  now()
)
on conflict (id) do update set
  status = excluded.status,
  price_cents = excluded.price_cents,
  updated_at = now();

insert into app.orders (
  id, status, source_type, gig_assignment_id, buyer_user_id, seller_professional_profile_id, price_cents, currency, paid_at, updated_at
)
values (
  '15151515-1515-4151-8151-151515151515',
  'paid',
  'gig_assignment',
  'ffffffff-ffff-4fff-8fff-ffffffffffff',
  '11111111-1111-4111-8111-111111111111',
  '55555555-5555-4555-8555-555555555555',
  75000,
  'usd',
  '2026-06-01T12:00:00.000Z',
  now()
)
on conflict (id) do update set
  status = excluded.status,
  price_cents = excluded.price_cents,
  updated_at = now();

insert into app.order_events (id, order_id, actor, to_status, name, metadata)
values
  ('16161616-1616-4161-8161-161616161616', '14141414-1414-4141-8141-141414141414', 'system', 'paid', 'seed.order.paid', '{"source":"seed"}'::jsonb),
  ('17171717-1717-4171-8171-171717171717', '15151515-1515-4151-8151-151515151515', 'system', 'paid', 'seed.gig_order.paid', '{"source":"seed"}'::jsonb)
on conflict (id) do update set
  to_status = excluded.to_status,
  name = excluded.name,
  metadata = excluded.metadata;

insert into app.order_files (id, order_id, media_id, role, note)
values ('27272727-2727-4272-8272-272727272727', '14141414-1414-4141-8141-141414141414', 'cccccccc-cccc-4ccc-8ccc-ccccccccccc2', 'professional', 'Seed order delivery file.')
on conflict (id) do update set note = excluded.note;

insert into app.agreements (id, order_id, template_key, pdf_media_id)
values ('18181818-1818-4181-8181-181818181818', '14141414-1414-4141-8141-141414141414', 'seed-basic-service', 'cccccccc-cccc-4ccc-8ccc-ccccccccccc2')
on conflict (id) do update set template_key = excluded.template_key;

insert into app.reviews (id, order_id, reviewer_user_id, professional_profile_id, rating, comment, status)
values ('19191919-1919-4191-8191-191919191919', '14141414-1414-4141-8141-141414141414', '11111111-1111-4111-8111-111111111111', '55555555-5555-4555-8555-555555555555', 5, 'Seed review for representative transaction data.', 'published')
on conflict (id) do update set rating = excluded.rating, status = excluded.status;

insert into app.threads (id, context_type, context_id, order_id, updated_at)
values ('20202020-2020-4202-8202-202020202020', 'order', '14141414-1414-4141-8141-141414141414', '14141414-1414-4141-8141-141414141414', now())
on conflict (id) do update set context_type = excluded.context_type, context_id = excluded.context_id, updated_at = now();

insert into app.thread_participants (thread_id, user_id)
values
  ('20202020-2020-4202-8202-202020202020', '11111111-1111-4111-8111-111111111111'),
  ('20202020-2020-4202-8202-202020202020', '22222222-2222-4222-8222-222222222222')
on conflict (thread_id, user_id) do nothing;

insert into app.messages (id, thread_id, sender_id, content)
values ('21212121-2121-4212-8212-212121212121', '20202020-2020-4202-8202-202020202020', '22222222-2222-4222-8222-222222222222', 'Seed message for messaging shell verification.')
on conflict (id) do update set content = excluded.content;

insert into app.message_media (message_id, media_id)
values ('21212121-2121-4212-8212-212121212121', 'cccccccc-cccc-4ccc-8ccc-ccccccccccc5')
on conflict (message_id, media_id) do nothing;

insert into app.notifications (id, user_id, channel, name, status, payload)
values ('23232323-2323-4232-8232-232323232323', '11111111-1111-4111-8111-111111111111', 'email', 'seed.notification', 'queued', '{"source":"seed"}'::jsonb)
on conflict (id) do update set status = excluded.status, payload = excluded.payload;

insert into app.search_upsert_events (id, entity_type, entity_id, reason, processed)
values ('24242424-2424-4242-8242-242424242424', 'offering', 'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbb1', 'seed', false)
on conflict (id) do update set reason = excluded.reason, processed = excluded.processed;

insert into app.processed_stripe_events (event_id, type)
values ('evt_seed_phase_2', 'checkout.session.completed')
on conflict (event_id) do update set type = excluded.type;

insert into app.audit_events (id, actor_user_id, entity_type, entity_id, action, metadata)
values ('25252525-2525-4252-8252-252525252525', '44444444-4444-4444-8444-444444444444', 'database_seed', '77777777-7777-4777-8777-777777777777', 'seed.phase_2', '{"source":"seed"}'::jsonb)
on conflict (id) do update set action = excluded.action, metadata = excluded.metadata;

commit;
`;

const result = spawnSync("psql", [databaseUrl, "-v", "ON_ERROR_STOP=1"], {
  input: sql,
  stdio: ["pipe", "pipe", "pipe"],
  encoding: "utf8",
  env: {
    ...process.env,
    PGSSLMODE: process.env.PGSSLMODE ?? "require",
  },
});

if (result.status !== 0) {
  console.error("Phase 2 seed failed.");
  if (result.stdout) {
    console.error(result.stdout);
  }
  if (result.stderr) {
    console.error(result.stderr);
  }
  process.exit(result.status ?? 1);
}

console.info("Phase 2 seed completed.");
if (result.stdout) {
  console.info(result.stdout);
}
