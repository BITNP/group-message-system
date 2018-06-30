-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

-- -----------------------------------------------------
-- Schema groupMessage
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `groupMessage` ;

-- -----------------------------------------------------
-- Schema groupMessage
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `groupMessage` DEFAULT CHARACTER SET utf8 ;
USE `groupMessage` ;

-- -----------------------------------------------------
-- Table `groupMessage`.`User`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `groupMessage`.`User` ;

CREATE TABLE IF NOT EXISTS `groupMessage`.`User` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(45) NOT NULL,
  `password` CHAR(32) NOT NULL,
  `tplIDList` VARCHAR(1000) NULL DEFAULT '',
  `fee` DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  `paid` DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  `createTime` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
  `remark` VARCHAR(1000) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `groupMessage`.`SendStat`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `groupMessage`.`SendStat` ;

CREATE TABLE IF NOT EXISTS `groupMessage`.`SendStat` (
  `mid` INT NOT NULL AUTO_INCREMENT,
  `id` INT NULL,
  `uid` INT NOT NULL,
  `createTime` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
  `content` TEXT(1000) NULL,
  `fee` DECIMAL(10,2) UNSIGNED NULL DEFAULT 0.0,
  `count` INT NULL DEFAULT 1,
  `mobile` CHAR(11) NULL,
  `sid` BIGINT NULL,
  `code` INT NULL,
  `msg` VARCHAR(500) NULL,
  PRIMARY KEY (`mid`),
  INDEX `fk_SendStat_1_idx` (`id` ASC),
  CONSTRAINT `fk_SendStat_1`
    FOREIGN KEY (`id`)
    REFERENCES `groupMessage`.`User` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `groupMessage`.`GroupData`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `groupMessage`.`GroupData` ;

CREATE TABLE IF NOT EXISTS `groupMessage`.`GroupData` (
  `sid` BIGINT NOT NULL,
  `id` INT NULL,
  `uid` INT NULL,
  `mobile` CHAR(13) NULL,
  `code` INT NOT NULL,
  `fee` DECIMAL(10,2) NULL,
  `msg` VARCHAR(500) NULL,
  PRIMARY KEY (`sid`),
  INDEX `fk_GroupData_1_idx` (`id` ASC),
  INDEX `fk_GroupData_2_idx` (`uid` ASC),
  CONSTRAINT `fk_GroupData_1`
    FOREIGN KEY (`id`)
    REFERENCES `groupMessage`.`User` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_GroupData_2`
    FOREIGN KEY (`uid`)
    REFERENCES `groupMessage`.`SendStat` (`mid`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
