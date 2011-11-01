-- phpMyAdmin SQL Dump
-- version 3.2.2.1deb1
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Apr 07, 2010 at 01:59 AM
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
-- Table structure for table `sourcenet_organization`
--

CREATE TABLE IF NOT EXISTS `sourcenet_organization` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `description` longtext NOT NULL,
  `location_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `sourcenet_organization_location_id` (`location_id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=5 ;

--
-- Dumping data for table `sourcenet_organization`
--

INSERT INTO `sourcenet_organization` (`id`, `name`, `description`, `location_id`) VALUES
(1, 'Grand Rapids Press', '', 1),
(2, 'Lansing State Journal', '', 2),
(3, 'Detroit Free Press', '', 3),
(4, 'Detroit News', '', 3);
