create database scopus_db;
use scopus_db;


-- Tabla de Autores. Deben ser únicos. Así podemos ligarlos a papers
CREATE TABLE `authors` (
  `author_id` varchar(50) NOT NULL,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`author_id`)
);


-- Tabla de Keywords, para no repetir. Y así saber las búsquedas a que keywords se asociaron.
CREATE TABLE `keywords` (
  `id` int NOT NULL AUTO_INCREMENT,
  `keyword` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `keyword` (`keyword`)
);

-- En el query log vendrán todas las búsquedas realizadas. Aquí se generará un "id de búsqueda". En las búsquedas deben asociarse:
-- 1. Por un lado las keywords. Todas las keywords relacionadas a la búsqueda. Aun así, incluyo un query text completo, pero relacionado con las keywords.
-- 2. Por otro lado, debo incluir los papers asociados a una búsqueda, para saber su especialidad o profundidad
CREATE TABLE `query_logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `log_id` varchar(8) NOT NULL,
  `fecha_consulta` datetime DEFAULT NULL,
  `keywords` text,
  `start_year` int DEFAULT NULL,
  `end_year` int DEFAULT NULL,
  `total_resultados` int DEFAULT NULL,
  `query_text` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `log_id` (`log_id`)
);


-- Tabla que ahora si, relaciona query log con keywords. Aquí, una keyword podrá estar incluida en muchas consultas, y una consulta podrá tener muchas keywords.
CREATE TABLE `query_keywords` (
  `query_log_id` varchar(8) NOT null,
  `keyword_id` int NOT NULL,
  PRIMARY KEY (`query_log_id`,`keyword_id`),
  KEY `keyword_id` (`keyword_id`)
);


-- Query details tendrá todos los papers que fueron regresados por una consulta.
CREATE TABLE `query_details` (
  `eid` varchar(50) NOT NULL,
  `log_id` varchar(8) NOT NULL,
  `title` text NOT NULL,
  `citations` int DEFAULT '0',
  `url` text,
  PRIMARY KEY (`eid`,`log_id`)
);



-- Ahora si, tanto paper author como paper references se almacenarán una sola vez. Ya que, aunque el paper aparezca en múltiples consultas,
-- solo requiero guardar una sola vez su autor y sus referencias.
CREATE TABLE `paper_authors` (
  `eid` varchar(50) NOT NULL,
  `author_id` varchar(50) NOT NULL,
  PRIMARY KEY (`eid`,`author_id`),
  KEY `author_id` (`author_id`)
);


CREATE TABLE `paper_references` (
  `id` int NOT NULL AUTO_INCREMENT,
  `source_eid` varchar(50) DEFAULT NULL,
  `ref_id` varchar(100) DEFAULT NULL,
  `ref_title` text,
  `ref_authors` text,
  `ref_url` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_unique_ref` (`source_eid`,`ref_id`)
);