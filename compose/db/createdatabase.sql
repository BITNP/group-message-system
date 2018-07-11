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
  `fee` DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  `paid` DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  `createTime` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
  `remark` VARCHAR(1000) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `username_UNIQUE` (`username` ASC))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `groupMessage`.`SendStat`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `groupMessage`.`SendStat` ;

CREATE TABLE IF NOT EXISTS `groupMessage`.`SendStat` (
  `extend` INT NOT NULL AUTO_INCREMENT,
  `id` INT NULL,
  `api` INT NOT NULL COMMENT '保留\n',
  `ext` CHAR(32) NULL COMMENT '保留\n',
  `createTime` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
  `tpl_id` BIGINT NULL,
  `content` TEXT(500) NULL COMMENT '如果没有使用模板发送这个值必填',
  `fee` DECIMAL(10,2) UNSIGNED NULL DEFAULT 0.0,
  `count` INT NULL DEFAULT 1,
  `totalCount` INT NULL COMMENT '返回的结果',
  PRIMARY KEY (`extend`),
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
  `pid` BIGINT NOT NULL AUTO_INCREMENT,
  `sid` CHAR(32) NULL,
  `id` INT NOT NULL,
  `extend` INT NOT NULL,
  `createTime` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
  `param` TEXT(500) NULL,
  `mobile` CHAR(13) NULL,
  `result` INT NULL,
  `fee` DECIMAL(10,2) NULL DEFAULT 0.00,
  `errmsg` VARCHAR(500) NULL,
  `reply` VARCHAR(500) NULL,
  INDEX `fk_GroupData_1_idx` (`id` ASC),
  PRIMARY KEY (`pid`),
  CONSTRAINT `fk_GroupData_1`
    FOREIGN KEY (`id`)
    REFERENCES `groupMessage`.`User` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `groupMessage`.`Tpl`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `groupMessage`.`Tpl` ;

CREATE TABLE IF NOT EXISTS `groupMessage`.`Tpl` (
  `pid` BIGINT NOT NULL AUTO_INCREMENT,
  `id` INT NULL,
  `tpl_id` BIGINT NULL,
  `api` INT NOT NULL DEFAULT 0,
  `public` INT NULL DEFAULT 0,
  `createTime` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
  `text` VARCHAR(500) NOT NULL,
  `title` VARCHAR(200) NULL,
  `remark` VARCHAR(200) NULL,
  `result` INT NULL,
  `errmsg` VARCHAR(100) NULL,
  `status` INT NULL,
  PRIMARY KEY (`pid`),
  INDEX `fk_Tpl_1_idx` (`id` ASC),
  CONSTRAINT `fk_Tpl_1`
    FOREIGN KEY (`id`)
    REFERENCES `groupMessage`.`User` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
