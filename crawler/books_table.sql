CREATE TABLE `books` (
  `id` INT NOT NULL,
  `title` VARCHAR(80) NOT NULL,
  `author` VARCHAR(80),
  `text` MEDIUMTEXT NOT NULL,
  `last_updated` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY(`id`)  
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
