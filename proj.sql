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

--#KAIZHE#--
-- Table structure for table `ReportLog`
--

DROP TABLE IF EXISTS `ReportLog`;
CREATE TABLE IF NOT EXISTS `ReportLog` (
  `ReportID` INT AUTO_INCREMENT PRIMARY KEY,
  `CreatedAt` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `UserID` INT NOT NULL,
  `ReportedUserID` INT NOT NULL,
  `Reason` VARCHAR(225) NOT NULL,
  `Status` VARCHAR(50) NOT NULL DEFAULT 'Pending'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


--Precia
-- Table structure for table `Product`
--

DROP TABLE IF EXISTS `Product`;
CREATE TABLE IF NOT EXISTS `Product` (
  `productid` INT AUTO_INCREMENT PRIMARY KEY,
  `title` VARCHAR(100) NOT NULL,
  `category` VARCHAR(50) NOT NULL,
  `description` TEXT NOT NULL,
  `location` VARCHAR(100) NOT NULL,
  `price` DECIMAL(10, 2) NOT NULL,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `expires_at` DATETIME,
  `userid` varchar(64) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Now insert the sample data into the Product table
INSERT INTO `Product` (`productid`, `title`, `category`, `description`, `location`, `price`, `created_at`, `expires_at`, `userid`) VALUES
(1, '1-for-1 Bubble Tea', 'food', 'Looking for someone to share a bubble tea deal. Valid at all outlets until end of month.', 'Downtown', 5.00, DATE_SUB(NOW(), INTERVAL 1 HOUR), DATE_ADD(NOW(), INTERVAL 7 DAY), '12345678'),
(2, 'Donut Box for $15', 'food', 'Need someone to share a box of donuts. 12 pieces of assorted flavors.', 'North Campus', 15.00, DATE_SUB(NOW(), INTERVAL 1 DAY), NULL, '22345678'),
(3, '50% Off Bluetooth Earbuds', 'electronics', 'I have a coupon for 50% off wireless earbuds at TechStore. Looking to share with someone.', 'East Mall', 25.00, DATE_SUB(NOW(), INTERVAL 2 DAY), NULL, '32345678'),
(4, 'Buy 2 Get 1 Free Books', 'books', 'Bookstore promotion, buy 2 books and get 1 free. Lets pool together to maximize the deal.', 'Central Library', 30.00, DATE_SUB(NOW(), INTERVAL 3 DAY), NULL, '42345678'),
(5, 'Movie Ticket 2-for-1 Special', 'entertainment', 'Cinema offering buy one get one free tickets for weekday showings. Looking for a movie buddy.', 'Westfield Mall', 12.50, DATE_SUB(NOW(), INTERVAL 4 DAY), DATE_ADD(NOW(), INTERVAL 14 DAY), '52345678');

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
