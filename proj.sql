-- phpMyAdmin SQL Dump
-- version 4.7.4
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Jan 14, 2019 at 06:42 AM
-- Server version: 5.7.19
-- PHP Version: 7.1.9

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `Project`
--
CREATE DATABASE IF NOT EXISTS `Project` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `Project`;

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
CREATE TABLE IF NOT EXISTS `user` (
  `uid` varchar(64) NOT NULL,
  `name` varchar(255) NOT NULL,
  `rating` int(64) NOT NULL,
  `accnum` varchar(255) NOT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`uid`, `name`, `rating`, `accnum`) VALUES
('12345678', 'user1', 0, '1234123412341234'),
('22345678', 'user2', 0, '2234123412341234'),
('32345678', 'user3', 0, '3234123412341234'),
('42345678', 'user4', 0, '4234123412341234'),
('52345678', 'user5', 0, '5234123412341234'),
('62345678', 'user6', 0, '6234123412341234'),
('72345678', 'user7', 0, '7234123412341234'),
('82345678', 'user8', 0, '8234123412341234');
COMMIT;


--
-- Table structure for table `deal`
--

DROP TABLE IF EXISTS `deal`;
CREATE TABLE IF NOT EXISTS `deal` (
  `dealid` varchar(64) NOT NULL,
  `buyerid` varchar(255) NOT NULL,
  `sellerid` varchar(255) NOT NULL,
  `price` int(64) NOT NULL,
  `status` int(64) NOT NULL,
  PRIMARY KEY (`dealid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `deal`
--

INSERT INTO `deal` (`dealid`, `buyerid`, `sellerid`, `price`, `status`) VALUES
('11111111', '12345678', '22345678', 0, 0);
COMMIT;

--
-- Table structure for table `account`
--

DROP TABLE IF EXISTS `account`;
CREATE TABLE IF NOT EXISTS `account` (
  `accnum` varchar(255) NOT NULL,
  `amount` int(64) NOT NULL,
  PRIMARY KEY (`accnum`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


--
-- Dumping data for table `account`
--

INSERT INTO `account` (`accnum`, `amount`) VALUES
('0000000000000001', 100000),
('1234123412341234', 1000),
('2234123412341234', 2000),
('3234123412341234', 3000),
('4234123412341234', 4000),
('5234123412341234', 5000),
('6234123412341234', 6000),
('7234123412341234', 7000),
('8234123412341234', 8000);
COMMIT;

--
-- Table structure for table `paymentrecord`
--

DROP TABLE IF EXISTS `paymentrecord`;
CREATE TABLE IF NOT EXISTS `paymentrecord` (
  `txnid` varchar(64) NOT NULL,
  `accnum_from` varchar(255) NOT NULL,
  `accnum_to` varchar(255) NOT NULL,
  `txnamt` int(64) NOT NULL,
  `status` varchar(64) NOT NULL,
  PRIMARY KEY (`txnid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `paymentrecord`
--

INSERT INTO `paymentrecord` (`txnid`, `accnum_from`, `accnum_to`, `txnamt`, `status`) VALUES
('1234', '1234123412341234', '0000000000000001', 100, 'successful');
COMMIT;

--
-- Table structure for table `chat`
--

DROP TABLE IF EXISTS `chat`;
CREATE TABLE IF NOT EXISTS `chat` (
  `messageid` varchar(64) NOT NULL,
  `senderid` varchar(64) NOT NULL,
  `receiverid` varchar(64) NOT NULL,
  `message` varchar(255) NOT NULL,
  `sentat` DATETIME DEFAULT now(),
  PRIMARY KEY (`messageid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
DELIMITER //
CREATE TRIGGER before_insert_chat
BEFORE INSERT ON chat
FOR EACH ROW
BEGIN
    SET NEW.messageid = LPAD(FLOOR(RAND() * 100000000), 8, '0'); -- Generates an 8-digit random number
END;
//
DELIMITER ;




--
-- Dumping data for table `chat`
--

INSERT INTO `chat` (`senderid`, `receiverid`, `message`) VALUES
(12345678, 22345678, 'bruh'),
(12345678, 22345678, 'bruhh'),
(12345678, 22345678, 'bruhhh'),
(12345678, 22345678, 'bruhhhh'),
(12345678, 22345678, 'bruhhhhhh');
COMMIT;



/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
