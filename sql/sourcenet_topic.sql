-- phpMyAdmin SQL Dump
-- version 3.2.2.1deb1
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Apr 07, 2010 at 12:17 AM
-- Server version: 5.1.37
-- PHP Version: 5.2.10-2ubuntu6.4

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `django_dev`
--

-- --------------------------------------------------------

--
-- Table structure for table `sourcenet_topic`
--

CREATE TABLE IF NOT EXISTS `sourcenet_topic` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `description` longtext NOT NULL,
  `last_modified` date NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=18 ;

--
-- Dumping data for table `sourcenet_topic`
--

INSERT INTO `sourcenet_topic` (`id`, `name`, `description`, `last_modified`) VALUES
(1, 'military', '', '2010-04-07'),
(2, 'politics', '', '2010-04-07'),
(3, 'government', '', '2010-04-07'),
(4, 'crime', '', '2010-04-07'),
(5, 'disaster/accidents', '', '2010-04-07'),
(6, 'labor and unions', '', '2010-04-07'),
(7, 'economics', '', '2010-04-07'),
(8, 'business', '', '2010-04-07'),
(9, 'public moral problems', 'issues such as abortion, teen pregnancy, and drug and alcohol abuse', '2010-04-07'),
(10, 'health', '', '2010-04-07'),
(11, 'welfare', '', '2010-04-07'),
(12, 'education', '', '2010-04-07'),
(13, 'arts', '', '2010-04-07'),
(14, 'science and inventions', '', '2010-04-07'),
(15, 'energy/environment', '', '2010-04-07'),
(16, 'religion', '', '2010-04-07'),
(17, 'miscellaneous', '', '2010-04-07');
