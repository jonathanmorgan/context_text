-- phpMyAdmin SQL Dump
-- version 3.2.2.1deb1
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Apr 07, 2010 at 01:00 AM
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
-- Table structure for table `sourcenet_newspaper`
--

CREATE TABLE IF NOT EXISTS `sourcenet_newspaper` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `description` longtext NOT NULL,
  `organization_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `sourcenet_newspaper_organization_id` (`organization_id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=5 ;

--
-- Dumping data for table `sourcenet_newspaper`
--

INSERT INTO `sourcenet_newspaper` (`id`, `name`, `description`, `organization_id`) VALUES
(1, 'Grand Rapids Press, The', '', 1),
(2, 'Lansing State Journal, The', '', 2),
(3, 'Detroit Free Press, The', '', 3),
(4, 'Detroit News, The', '', 4);
