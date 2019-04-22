-- phpMyAdmin SQL Dump
-- version 3.2.2.1deb1
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Apr 07, 2010 at 10:01 PM
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
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
CREATE TABLE IF NOT EXISTS `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(80) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

--
-- Dumping data for table `auth_group`
--


-- --------------------------------------------------------

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
CREATE TABLE IF NOT EXISTS `auth_group_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `group_id` (`group_id`,`permission_id`),
  KEY `permission_id_refs_id_a7792de1` (`permission_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

--
-- Dumping data for table `auth_group_permissions`
--


-- --------------------------------------------------------

--
-- Table structure for table `auth_message`
--

DROP TABLE IF EXISTS `auth_message`;
CREATE TABLE IF NOT EXISTS `auth_message` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `message` longtext NOT NULL,
  PRIMARY KEY (`id`),
  KEY `auth_message_user_id` (`user_id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=57 ;

--
-- Dumping data for table `auth_message`
--


-- --------------------------------------------------------

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
CREATE TABLE IF NOT EXISTS `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `content_type_id` (`content_type_id`,`codename`),
  KEY `auth_permission_content_type_id` (`content_type_id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=67 ;

--
-- Dumping data for table `auth_permission`
--

INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES
(1, 'Can add permission', 1, 'add_permission'),
(2, 'Can change permission', 1, 'change_permission'),
(3, 'Can delete permission', 1, 'delete_permission'),
(4, 'Can add group', 2, 'add_group'),
(5, 'Can change group', 2, 'change_group'),
(6, 'Can delete group', 2, 'delete_group'),
(7, 'Can add user', 3, 'add_user'),
(8, 'Can change user', 3, 'change_user'),
(9, 'Can delete user', 3, 'delete_user'),
(10, 'Can add message', 4, 'add_message'),
(11, 'Can change message', 4, 'change_message'),
(12, 'Can delete message', 4, 'delete_message'),
(13, 'Can add content type', 5, 'add_contenttype'),
(14, 'Can change content type', 5, 'change_contenttype'),
(15, 'Can delete content type', 5, 'delete_contenttype'),
(16, 'Can add session', 6, 'add_session'),
(17, 'Can change session', 6, 'change_session'),
(18, 'Can delete session', 6, 'delete_session'),
(19, 'Can add site', 7, 'add_site'),
(20, 'Can change site', 7, 'change_site'),
(21, 'Can delete site', 7, 'delete_site'),
(22, 'Can add poll', 8, 'add_poll'),
(23, 'Can change poll', 8, 'change_poll'),
(24, 'Can delete poll', 8, 'delete_poll'),
(25, 'Can add choice', 9, 'add_choice'),
(26, 'Can change choice', 9, 'change_choice'),
(27, 'Can delete choice', 9, 'delete_choice'),
(28, 'Can add log entry', 10, 'add_logentry'),
(29, 'Can change log entry', 10, 'change_logentry'),
(30, 'Can delete log entry', 10, 'delete_logentry'),
(31, 'Can add location', 11, 'add_location'),
(32, 'Can change location', 11, 'change_location'),
(33, 'Can delete location', 11, 'delete_location'),
(34, 'Can add topic', 12, 'add_topic'),
(35, 'Can change topic', 12, 'change_topic'),
(36, 'Can delete topic', 12, 'delete_topic'),
(37, 'Can add person', 13, 'add_person'),
(38, 'Can change person', 13, 'change_person'),
(39, 'Can delete person', 13, 'delete_person'),
(40, 'Can add organization', 14, 'add_organization'),
(41, 'Can change organization', 14, 'change_organization'),
(42, 'Can delete organization', 14, 'delete_organization'),
(43, 'Can add document', 15, 'add_document'),
(44, 'Can change document', 15, 'change_document'),
(45, 'Can delete document', 15, 'delete_document'),
(46, 'Can add newspaper', 16, 'add_newspaper'),
(47, 'Can change newspaper', 16, 'change_newspaper'),
(48, 'Can delete newspaper', 16, 'delete_newspaper'),
(52, 'Can add article_ author', 18, 'add_article_author'),
(53, 'Can change article_ author', 18, 'change_article_author'),
(54, 'Can delete article_ author', 18, 'delete_article_author'),
(55, 'Can add article_ source', 19, 'add_article_source'),
(56, 'Can change article_ source', 19, 'change_article_source'),
(57, 'Can delete article_ source', 19, 'delete_article_source'),
(61, 'Can add article', 21, 'add_article'),
(62, 'Can change article', 21, 'change_article'),
(63, 'Can delete article', 21, 'delete_article'),
(64, 'Can add person_ organization', 22, 'add_person_organization'),
(65, 'Can change person_ organization', 22, 'change_person_organization'),
(66, 'Can delete person_ organization', 22, 'delete_person_organization');

-- --------------------------------------------------------

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
CREATE TABLE IF NOT EXISTS `auth_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(30) NOT NULL,
  `first_name` varchar(30) NOT NULL,
  `last_name` varchar(30) NOT NULL,
  `email` varchar(75) NOT NULL,
  `password` varchar(128) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `last_login` datetime NOT NULL,
  `date_joined` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=3 ;

--
-- Dumping data for table `auth_user`
--

INSERT INTO `auth_user` (`id`, `username`, `first_name`, `last_name`, `email`, `password`, `is_staff`, `is_active`, `is_superuser`, `last_login`, `date_joined`) VALUES
(1, 'jonathanmorgan', 'Jonathan', 'Morgan', 'jonathan.morgan.007@gmail.com', 'sha1$dc585$6fbfda06ae5335feda28b35d2ef118d1bcf8aa5a', 1, 1, 1, '2010-03-31 11:47:41', '2010-02-11 00:09:39'),
(2, 'brianbowe', 'Brian', 'Bowe', 'brianjbowe@gmail.com', 'sha1$3d123$8fbd148bdfc1f610a1b973e1b96c620abfdeab44', 1, 1, 1, '2010-03-25 09:27:23', '2010-03-23 19:03:29');

-- --------------------------------------------------------

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
CREATE TABLE IF NOT EXISTS `auth_user_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`group_id`),
  KEY `group_id_refs_id_f0ee9890` (`group_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

--
-- Dumping data for table `auth_user_groups`
--


-- --------------------------------------------------------

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
CREATE TABLE IF NOT EXISTS `auth_user_user_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`permission_id`),
  KEY `permission_id_refs_id_67e79cb` (`permission_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

--
-- Dumping data for table `auth_user_user_permissions`
--


-- --------------------------------------------------------

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
CREATE TABLE IF NOT EXISTS `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime NOT NULL,
  `user_id` int(11) NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_user_id` (`user_id`),
  KEY `django_admin_log_content_type_id` (`content_type_id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=226 ;

--
-- Dumping data for table `django_admin_log`
--

INSERT INTO `django_admin_log` (`id`, `action_time`, `user_id`, `content_type_id`, `object_id`, `object_repr`, `action_flag`, `change_message`) VALUES
(1, '2010-03-23 18:15:04', 1, 8, '1', 'What''s up?', 2, 'Changed pub_date.'),
(2, '2010-03-23 19:03:29', 1, 3, '2', 'brianbowe', 1, ''),
(3, '2010-03-23 19:04:16', 1, 3, '2', 'brianbowe', 2, 'Changed first_name, last_name, email, is_staff and is_superuser.'),
(4, '2010-03-23 19:04:34', 1, 3, '1', 'jonathanmorgan', 2, 'Changed first_name and last_name.'),
(5, '2010-03-24 01:48:26', 1, 11, '1', 'Lansing Area', 1, ''),
(6, '2010-03-24 01:55:44', 1, 11, '1', 'Lansing Area', 2, 'Changed description, city and state.'),
(7, '2010-03-24 01:56:17', 1, 16, '1', 'Lansing State Journal', 1, ''),
(8, '2010-03-24 02:33:48', 1, 12, '1', 'budget deficit', 1, ''),
(9, '2010-03-24 02:34:41', 1, 13, '1', 'Virg  Bernero', 1, ''),
(10, '2010-03-24 02:34:54', 1, 14, '1', 'City of Lansing', 1, ''),
(11, '2010-03-24 02:56:25', 1, 13, '2', 'Susan  Vela', 1, ''),
(12, '2010-03-24 02:56:34', 1, 18, '1', 'Vela (staff)', 1, ''),
(13, '2010-03-24 03:10:42', 1, 11, '1', 'Lansing Area', 1, ''),
(14, '2010-03-24 03:10:47', 1, 16, '1', 'Lansing State Journal', 1, ''),
(15, '2010-03-24 03:11:46', 1, 12, '1', 'Lansing budget deficit', 1, ''),
(131, '2010-04-03 10:40:58', 1, 11, '2', 'Washington, D.C.', 1, ''),
(17, '2010-03-24 03:12:32', 1, 13, '1', 'Susan  Vela', 1, ''),
(18, '2010-03-24 03:12:37', 1, 18, '1', 'Vela (staff)', 1, ''),
(19, '2010-03-24 03:13:09', 1, 13, '2', 'Verg  Bernero', 1, ''),
(20, '2010-03-24 03:13:22', 1, 14, '1', 'City of Lansing', 1, ''),
(21, '2010-03-24 03:13:50', 1, 19, '1', 'individual', 1, ''),
(22, '2010-03-24 03:18:12', 1, 13, '3', 'Kathy  Dunbar', 1, ''),
(23, '2010-03-24 03:20:25', 1, 19, '2', 'individual', 1, ''),
(24, '2010-03-24 03:21:10', 1, 13, '4', 'Mike  Terranova', 1, ''),
(25, '2010-03-24 03:21:54', 1, 19, '3', 'individual', 1, ''),
(26, '2010-03-24 03:23:40', 1, 13, '5', 'Tom  Krug', 1, ''),
(27, '2010-03-24 03:25:07', 1, 14, '2', 'Lodge 141 of the Fraternal Order of police', 1, ''),
(28, '2010-03-24 03:27:16', 1, 19, '4', 'individual', 1, ''),
(29, '2010-03-24 03:28:05', 1, 13, '6', 'Jerry  Ambrose', 1, ''),
(30, '2010-03-24 03:28:24', 1, 19, '5', 'individual', 1, ''),
(136, '2010-04-03 11:23:40', 1, 12, '1', 'crime', 1, ''),
(32, '2010-03-24 03:29:28', 1, 11, '2', 'City of Lansing', 1, ''),
(135, '2010-04-03 11:23:03', 1, 16, '1', 'Grand Rapids Press', 1, ''),
(34, '2010-03-24 03:32:25', 1, 11, '3', 'Washington Park Ice Complex', 1, ''),
(134, '2010-04-03 11:23:00', 1, 11, '1', 'Grand Rapids', 1, ''),
(36, '2010-03-24 03:32:56', 1, 11, '4', 'Lansing City Hall', 1, ''),
(133, '2010-04-03 10:54:51', 1, 16, '1', 'Grand Rapids Press', 1, ''),
(38, '2010-03-24 03:37:35', 1, 21, '2', 'Lansing State Journal (Mar 23, 2010, A 1) - 4-day week proposed for some city workers', 1, ''),
(39, '2010-03-24 03:38:02', 1, 21, '1', 'Lansing State Journal (Mar 23, 2010, A 1) - 4-day week proposed for some city workers', 3, ''),
(40, '2010-03-25 09:30:09', 2, 12, '2', 'Lansing City Budget', 1, ''),
(130, '2010-04-03 10:40:02', 1, 14, '1', 'Washington Post', 1, ''),
(42, '2010-03-25 09:38:15', 2, 13, '7', 'Randy  Davis', 1, ''),
(43, '2010-03-25 09:38:36', 2, 14, '3', 'Lansing Police Department', 1, ''),
(44, '2010-03-25 09:41:46', 2, 19, '6', 'individual', 1, ''),
(45, '2010-03-25 09:43:32', 2, 19, '7', 'individual', 1, ''),
(46, '2010-03-25 09:45:04', 2, 19, '8', 'individual', 1, ''),
(47, '2010-03-25 09:52:26', 2, 13, '8', 'Alice  Foster-Stocum', 1, ''),
(48, '2010-03-25 09:52:59', 2, 14, '4', 'Michigania', 1, ''),
(49, '2010-03-25 09:53:36', 2, 12, '3', 'Downtown Business', 1, ''),
(50, '2010-03-25 09:53:46', 2, 19, '9', 'individual', 1, ''),
(51, '2010-03-25 09:54:56', 2, 13, '9', 'Doug  Withey', 1, ''),
(52, '2010-03-25 09:55:14', 2, 14, '5', 'Teamsters Local 580', 1, ''),
(53, '2010-03-25 09:56:33', 2, 12, '4', 'Labor Agreements', 1, ''),
(54, '2010-03-25 09:57:23', 2, 19, '10', 'individual', 1, ''),
(55, '2010-03-25 09:58:31', 2, 13, '10', 'Nancy  Scarlet', 1, ''),
(56, '2010-03-25 09:58:55', 2, 14, '6', 'Oakland County', 1, ''),
(57, '2010-03-25 09:59:40', 2, 12, '5', 'Layoffs', 1, ''),
(58, '2010-03-25 09:59:55', 2, 19, '11', 'individual', 1, ''),
(59, '2010-03-25 10:03:30', 2, 13, '11', 'Eva  Patterson', 1, ''),
(60, '2010-03-25 10:04:30', 2, 12, '6', 'City Hall reduced hours', 1, ''),
(61, '2010-03-25 10:04:33', 2, 19, '12', 'individual', 1, ''),
(62, '2010-03-25 10:05:15', 2, 21, '3', 'Lansing State Journal (Mar 24, 2010, Online 0) - Lansing budget plan worries workers, some businesses', 1, ''),
(63, '2010-03-25 10:11:53', 2, 12, '7', 'Department of Human Services Employee Pay-Freeze', 1, ''),
(129, '2010-04-03 10:39:19', 1, 13, '1', 'Richard  Roeper ( Reporter )', 1, ''),
(65, '2010-03-25 10:12:32', 2, 13, '12', 'Scott  Davis', 1, ''),
(66, '2010-03-25 10:12:41', 2, 18, '2', 'Davis (staff)', 1, ''),
(67, '2010-03-25 10:13:25', 2, 13, '13', 'Michelle  Gnesda', 1, ''),
(68, '2010-03-25 10:13:44', 2, 14, '7', 'Michigan Department of Human Services', 1, ''),
(69, '2010-03-25 10:15:20', 2, 19, '13', 'individual', 1, ''),
(70, '2010-03-25 10:16:17', 2, 13, '14', 'Ray  Holman', 1, ''),
(71, '2010-03-25 10:16:36', 2, 14, '8', 'United Auto Workers Local 6000', 1, ''),
(72, '2010-03-25 10:17:10', 2, 19, '14', 'individual', 1, ''),
(73, '2010-03-25 10:17:37', 2, 11, '5', 'State Capitol', 1, ''),
(132, '2010-04-03 10:54:49', 1, 11, '1', 'Grand Rapids', 1, ''),
(75, '2010-03-25 10:18:29', 2, 13, '15', 'Matt  Marsden', 1, ''),
(76, '2010-03-25 10:18:53', 2, 14, '9', 'Senate Majority Leader''s Office', 1, ''),
(77, '2010-03-25 10:19:36', 2, 19, '15', 'individual', 1, ''),
(78, '2010-03-25 10:21:47', 2, 19, '16', 'anonymous', 1, ''),
(79, '2010-03-25 10:22:43', 2, 13, '16', 'Jim  Walkowicz', 1, ''),
(80, '2010-03-25 10:22:57', 2, 14, '10', 'United Auto Workers', 1, ''),
(81, '2010-03-25 10:23:36', 2, 19, '17', 'individual', 1, ''),
(82, '2010-03-25 10:25:12', 2, 13, '17', 'Lou  Jabari', 1, ''),
(83, '2010-03-25 10:25:44', 2, 19, '18', 'individual', 1, ''),
(84, '2010-03-25 10:25:49', 2, 21, '4', 'Lansing State Journal (Mar 24, 2010, ? 0) - 200 state workers rally at capital', 1, ''),
(85, '2010-03-25 10:29:10', 2, 13, '18', 'Kathryn  Prater', 1, ''),
(86, '2010-03-25 10:29:25', 2, 18, '3', 'Prater (staff)', 1, ''),
(87, '2010-03-25 10:31:05', 2, 12, '8', 'Volunteer Community Service', 1, ''),
(128, '2010-04-03 10:37:38', 1, 12, '2', 'homosexuality', 1, ''),
(89, '2010-03-25 10:33:13', 2, 13, '19', 'Wilton  Parsons', 1, ''),
(90, '2010-03-25 10:34:23', 2, 12, '9', 'Volunteer Community Service', 1, ''),
(91, '2010-03-25 10:34:31', 2, 19, '19', 'individual', 1, ''),
(92, '2010-03-25 10:35:35', 2, 13, '20', 'Lance  Queen', 1, ''),
(93, '2010-03-25 10:35:50', 2, 14, '11', 'Tuesday Toolmen', 1, ''),
(94, '2010-03-25 10:36:28', 2, 19, '20', 'individual', 1, ''),
(95, '2010-03-25 10:37:14', 2, 13, '21', 'Katherine  Draper', 1, ''),
(96, '2010-03-25 10:37:45', 2, 14, '12', 'Greater Lansing Housing Coalition', 1, ''),
(97, '2010-03-25 10:38:20', 2, 19, '21', 'individual', 1, ''),
(98, '2010-03-25 10:39:08', 2, 13, '22', 'Bob   Johnson', 1, ''),
(99, '2010-03-25 10:39:52', 2, 14, '13', 'Lansing Department of Planning and Neighborhood Development', 1, ''),
(100, '2010-03-25 10:40:16', 2, 19, '22', 'individual', 1, ''),
(101, '2010-03-25 10:40:35', 2, 21, '5', 'Lansing State Journal (Mar 24, 2010, ? 0) - Volunteers lend hands, tools to help area seniors', 1, ''),
(102, '2010-03-31 12:21:38', 1, 11, '1', 'Lansing', 1, ''),
(103, '2010-03-31 12:21:40', 1, 16, '1', 'Lansing State Journal', 1, ''),
(104, '2010-03-31 12:22:24', 1, 12, '1', 'economy', 1, ''),
(105, '2010-03-31 12:22:30', 1, 12, '2', 'budget', 1, ''),
(127, '2010-04-03 10:37:29', 1, 12, '1', 'race', 1, ''),
(108, '2010-03-31 12:23:14', 1, 13, '1', 'Susan  Vela', 1, ''),
(109, '2010-03-31 12:24:19', 1, 13, '2', 'Randy  Davis', 1, ''),
(110, '2010-03-31 12:24:31', 1, 14, '1', 'Lansing Police Department', 1, ''),
(111, '2010-03-31 12:25:38', 1, 13, '3', 'Alice  Foster-Slocum', 1, ''),
(112, '2010-03-31 12:26:03', 1, 14, '2', 'Michigania', 1, ''),
(113, '2010-03-31 12:28:24', 1, 11, '1', 'Lansing', 1, ''),
(114, '2010-03-31 12:28:26', 1, 16, '1', 'Lansing State Journal', 1, ''),
(115, '2010-03-31 12:28:38', 1, 12, '1', 'budget', 1, ''),
(126, '2010-04-03 10:36:18', 1, 16, '1', 'Chicago Sun-Times', 1, ''),
(117, '2010-03-31 12:28:51', 1, 12, '2', 'economy', 1, ''),
(125, '2010-04-03 10:36:16', 1, 11, '1', 'Chicago', 1, ''),
(119, '2010-03-31 12:29:23', 1, 13, '1', 'Susan  Vela', 1, ''),
(120, '2010-03-31 12:29:37', 1, 13, '2', 'Randy  Davis', 1, ''),
(121, '2010-03-31 12:29:49', 1, 14, '1', 'Lansing Police Department', 1, ''),
(122, '2010-03-31 12:30:12', 1, 13, '3', 'Alice  Foster-Slocum', 1, ''),
(123, '2010-03-31 12:30:20', 1, 14, '2', 'Michigania', 1, ''),
(124, '2010-03-31 12:30:28', 1, 21, '1', 'Lansing State Journal (Mar 24, 2010, A 1) - Lansing budget plan worries workers, some businesses', 1, ''),
(137, '2010-04-03 11:23:52', 1, 12, '2', 'pedophelia', 1, ''),
(138, '2010-04-03 11:24:13', 1, 11, '2', 'Lowell', 1, ''),
(139, '2010-04-03 11:27:11', 1, 14, '1', 'Kent County Sheriff''s Department', 1, ''),
(140, '2010-04-03 11:27:49', 1, 13, '1', 'nobody  important (  )', 1, ''),
(141, '2010-04-03 11:27:53', 1, 21, '1', 'Grand Rapids Press (Apr 02, 2010, A 3) - Man charged in assault', 1, ''),
(142, '2010-04-03 11:37:06', 1, 11, '1', 'Grand Rapids', 1, ''),
(143, '2010-04-03 11:37:08', 1, 16, '1', 'Grand Rapids Press', 1, ''),
(144, '2010-04-03 11:37:40', 1, 12, '1', 'crime', 1, ''),
(145, '2010-04-03 11:38:11', 1, 11, '2', 'Lowell, MI', 1, ''),
(146, '2010-04-03 11:39:17', 1, 11, '3', 'Kent County, MI', 1, ''),
(147, '2010-04-03 11:39:20', 1, 14, '1', 'Kent County Sheriff''s Department', 1, ''),
(148, '2010-04-03 11:39:31', 1, 21, '1', 'Grand Rapids Press (Apr 02, 2010, A 3) - Man charged in assault', 1, ''),
(149, '2010-04-03 12:06:18', 1, 13, '1', 'Jonathan Scott Morgan ( awesome )', 1, ''),
(150, '2010-04-04 20:42:16', 2, 21, '2', 'Grand Rapids Press (Apr 02, 2010,  0) - bjb Man charged in assault', 1, ''),
(151, '2010-04-04 20:48:48', 2, 13, '2', 'John S. Hausman ( Grand Rapids News Service )', 1, ''),
(152, '2010-04-04 20:51:24', 2, 11, '4', 'Muskegon, Muskegon County, MI', 1, ''),
(153, '2010-04-04 20:51:30', 2, 14, '2', 'Muskegon County Sheriff''s Department', 1, ''),
(154, '2010-04-04 20:51:44', 2, 13, '3', 'Dennis   Porter ( Deputy (retired) )', 1, ''),
(155, '2010-04-04 20:52:51', 2, 12, '2', 'Personal Narrative/Feature', 1, ''),
(156, '2010-04-04 20:55:17', 2, 21, '3', 'Grand Rapids Press (Apr 02, 2010, A 3) - 40 years later, dying thief pays for stolen cigarettes - $100 sent anonymously to store owner''s grandson as way of atonement', 1, ''),
(157, '2010-04-04 20:55:54', 2, 21, '2', 'Grand Rapids Press (Apr 02, 2010, A 3) - bjb Man charged in assault', 2, 'Changed section and page.'),
(158, '2010-04-04 20:56:18', 2, 21, '3', 'Grand Rapids Press (Apr 02, 2010, A 3) - bjb 40 years later, dying thief pays for stolen cigarettes - $100 sent anonymously to store owner''s grandson as way of atonement', 2, 'Changed headline.'),
(159, '2010-04-04 21:03:29', 2, 11, '5', 'Hudsonville, Ottawa County, MI', 1, ''),
(160, '2010-04-04 21:03:55', 2, 12, '3', 'Sports (Local)', 1, ''),
(161, '2010-04-04 21:04:13', 2, 12, '4', 'Education/Schools', 1, ''),
(162, '2010-04-04 21:04:45', 2, 21, '4', 'Grand Rapids Press (Apr 02, 2010, A 16) - Freedom Christian seeks use of ball field', 1, ''),
(163, '2010-04-04 21:05:11', 2, 21, '4', 'Grand Rapids Press (Apr 02, 2010, A 16) - bjb Freedom Christian seeks use of ball field', 2, 'Changed headline.'),
(164, '2010-04-04 21:09:05', 2, 13, '4', 'John  Agar', 1, ''),
(165, '2010-04-04 21:28:20', 2, 11, '6', '"Belding", Belding, MI', 1, ''),
(166, '2010-04-04 21:28:23', 2, 14, '3', 'First Bank of West Michigan', 1, ''),
(167, '2010-04-04 21:28:42', 2, 13, '5', 'Michael  Willett ( former vice president  )', 1, ''),
(168, '2010-04-04 21:29:23', 2, 12, '5', 'Business', 1, ''),
(169, '2010-04-04 21:31:34', 2, 13, '6', 'Matthew    Borgula ( Assistant US Attorney )', 1, ''),
(170, '2010-04-04 21:32:21', 2, 21, '5', 'Grand Rapids Press (Apr 02, 2010, A 8) - Former bank VP admits cash, ID theft - He is second of institution''s officers to plead guilty this year', 1, ''),
(171, '2010-04-04 21:32:38', 2, 21, '5', 'Grand Rapids Press (Apr 02, 2010, A 8) - bjb Former bank VP admits cash, ID theft - He is second of institution''s officers to plead guilty this year', 2, 'Changed headline.'),
(172, '2010-04-07 00:11:56', 1, 12, '1', 'military', 1, ''),
(173, '2010-04-07 00:12:08', 1, 12, '2', 'politics', 1, ''),
(174, '2010-04-07 00:12:28', 1, 12, '3', 'government', 1, ''),
(175, '2010-04-07 00:12:38', 1, 12, '4', 'crime', 1, ''),
(176, '2010-04-07 00:12:51', 1, 12, '5', 'disaster/accidents', 1, ''),
(177, '2010-04-07 00:12:58', 1, 12, '6', 'labor and unions', 1, ''),
(178, '2010-04-07 00:13:09', 1, 12, '7', 'economics', 1, ''),
(179, '2010-04-07 00:13:17', 1, 12, '8', 'business', 1, ''),
(180, '2010-04-07 00:13:37', 1, 12, '9', 'public moral problems', 1, ''),
(181, '2010-04-07 00:13:52', 1, 12, '10', 'health', 1, ''),
(182, '2010-04-07 00:13:59', 1, 12, '11', 'welfare', 1, ''),
(183, '2010-04-07 00:14:07', 1, 12, '12', 'education', 1, ''),
(184, '2010-04-07 00:14:16', 1, 12, '13', 'arts', 1, ''),
(185, '2010-04-07 00:14:20', 1, 12, '14', 'science and inventions', 1, ''),
(186, '2010-04-07 00:14:34', 1, 12, '15', 'energy/environment', 1, ''),
(187, '2010-04-07 00:14:48', 1, 12, '16', 'religion', 1, ''),
(188, '2010-04-07 00:14:59', 1, 12, '17', 'miscellaneous', 1, ''),
(189, '2010-04-07 00:31:09', 1, 11, '1', 'Lansing, Ingham County, MI', 1, ''),
(190, '2010-04-07 00:31:15', 1, 16, '1', 'Lansing State Journal', 1, ''),
(191, '2010-04-07 00:31:37', 1, 11, '2', 'Grand Rapids, MI', 1, ''),
(192, '2010-04-07 00:31:41', 1, 16, '2', 'Grand Rapids Press', 1, ''),
(193, '2010-04-07 00:31:59', 1, 11, '3', 'Detroit, MI', 1, ''),
(194, '2010-04-07 00:32:02', 1, 16, '3', 'Detroit News', 1, ''),
(195, '2010-04-07 00:32:12', 1, 16, '4', 'Detroit Free Press', 1, ''),
(196, '2010-04-07 00:55:29', 1, 11, '1', 'Grand Rapids, MI', 1, ''),
(197, '2010-04-07 00:55:31', 1, 14, '1', 'Grand Rapids Press', 1, ''),
(198, '2010-04-07 00:57:33', 1, 16, '1', 'Grand Rapids Press, The', 1, ''),
(199, '2010-04-07 00:58:08', 1, 11, '2', 'Lansing, MI', 1, ''),
(200, '2010-04-07 00:58:10', 1, 14, '2', 'Lansing State Journal', 1, ''),
(201, '2010-04-07 00:58:13', 1, 16, '2', 'Lansing State Journal, The', 1, ''),
(202, '2010-04-07 00:58:54', 1, 11, '3', 'Detroit, MI', 1, ''),
(203, '2010-04-07 00:58:57', 1, 14, '3', 'Detroit Free Press', 1, ''),
(204, '2010-04-07 00:58:59', 1, 16, '3', 'Detroit Free Press, The', 1, ''),
(205, '2010-04-07 00:59:25', 1, 14, '4', 'Detroit News', 1, ''),
(206, '2010-04-07 00:59:28', 1, 16, '4', 'Detroit News, The', 1, ''),
(207, '2010-04-07 14:51:59', 1, 11, '4', 'Lowell, MI', 1, ''),
(208, '2010-04-07 15:12:51', 1, 11, '5', '', 1, ''),
(209, '2010-04-07 15:13:23', 1, 11, '6', 'Kent County, MI', 1, ''),
(210, '2010-04-07 15:13:45', 1, 14, '5', 'Kent County Sheriff''s Department', 1, ''),
(211, '2010-04-07 15:14:19', 1, 21, '1', 'Grand Rapids Press, The (Apr 02, 2010, A 3) - Man charged in assault', 1, ''),
(212, '2010-04-07 15:23:29', 1, 11, '7', 'Muskegon, MI', 1, ''),
(213, '2010-04-07 15:26:44', 1, 11, '8', 'MI', 1, ''),
(214, '2010-04-07 15:26:47', 1, 14, '6', 'Grand Rapids Press News Service', 1, ''),
(215, '2010-04-07 15:27:23', 1, 13, '1', 'John S. Housman', 1, ''),
(216, '2010-04-07 15:37:22', 1, 13, '2', 'Dennis  Porter', 1, ''),
(217, '2010-04-07 15:38:06', 1, 11, '9', 'Muskegon County, MI', 1, ''),
(218, '2010-04-07 15:38:08', 1, 14, '7', 'Muskegon County Sheriff''s Department', 1, ''),
(219, '2010-04-07 15:52:20', 1, 21, '2', 'Grand Rapids Press, The (Apr 02, 2010, A 3) - 40 years later, dying thief pays for stolen cigarettes - $100 sent anonymously to store owner''s grandson as way of atonement', 1, ''),
(220, '2010-04-07 15:54:18', 1, 11, '10', 'Hudsonville, MI', 1, ''),
(221, '2010-04-07 15:59:41', 1, 21, '3', 'Grand Rapids Press, The (Apr 02, 2010, A 16) - Freedom Christian seeks use of ball field', 1, ''),
(222, '2010-04-07 16:02:35', 1, 13, '3', 'John  Agar', 1, ''),
(223, '2010-04-07 16:26:38', 1, 14, '8', 'First Bank of West Michigan', 1, ''),
(224, '2010-04-07 16:35:44', 1, 13, '4', 'Michael  Willett', 1, ''),
(225, '2010-04-07 16:36:49', 1, 21, '4', 'Grand Rapids Press, The (Apr 02, 2010, A 8) - Former bank VP admits cash, ID theft - He is second of institution''s officers to plead guilty this year', 1, '');

-- --------------------------------------------------------

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
CREATE TABLE IF NOT EXISTS `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `app_label` (`app_label`,`model`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=23 ;

--
-- Dumping data for table `django_content_type`
--

INSERT INTO `django_content_type` (`id`, `name`, `app_label`, `model`) VALUES
(1, 'permission', 'auth', 'permission'),
(2, 'group', 'auth', 'group'),
(3, 'user', 'auth', 'user'),
(4, 'message', 'auth', 'message'),
(5, 'content type', 'contenttypes', 'contenttype'),
(6, 'session', 'sessions', 'session'),
(7, 'site', 'sites', 'site'),
(8, 'poll', 'polls', 'poll'),
(9, 'choice', 'polls', 'choice'),
(10, 'log entry', 'admin', 'logentry'),
(11, 'location', 'context_text', 'location'),
(12, 'topic', 'context_text', 'topic'),
(13, 'person', 'context_text', 'person'),
(14, 'organization', 'context_text', 'organization'),
(15, 'document', 'context_text', 'document'),
(16, 'newspaper', 'context_text', 'newspaper'),
(18, 'article_ author', 'context_text', 'article_author'),
(19, 'article_ source', 'context_text', 'article_source'),
(21, 'article', 'context_text', 'article'),
(22, 'person_ organization', 'context_text', 'person_organization');

-- --------------------------------------------------------

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
CREATE TABLE IF NOT EXISTS `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime NOT NULL,
  PRIMARY KEY (`session_key`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `django_session`
--

INSERT INTO `django_session` (`session_key`, `session_data`, `expire_date`) VALUES
('001c733d593af3d964640a9d4f8da49a', 'gAJ9cQEoVRJfYXV0aF91c2VyX2JhY2tlbmRxAlUpZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5k\ncy5Nb2RlbEJhY2tlbmRxA1UNX2F1dGhfdXNlcl9pZHEEigECdS5iYzMyNmE0YzdjZjE2ZjRiMDAy\nNWE2ZTcwZGZmZTM2Yg==\n', '2010-04-08 09:27:23'),
('9e0df2cc85e4159bbce95833e55f198a', 'gAJ9cQEoVRJfYXV0aF91c2VyX2JhY2tlbmRxAlUpZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5k\ncy5Nb2RlbEJhY2tlbmRxA1UNX2F1dGhfdXNlcl9pZHEEigECdS5iYzMyNmE0YzdjZjE2ZjRiMDAy\nNWE2ZTcwZGZmZTM2Yg==\n', '2010-04-07 11:40:27'),
('7ec29e16fc4bb996fdc092941d1ce00b', 'gAJ9cQEoVRJfYXV0aF91c2VyX2JhY2tlbmRxAlUpZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5k\ncy5Nb2RlbEJhY2tlbmRxA1UNX2F1dGhfdXNlcl9pZHEEigEBdS4zY2M4MDkwZGFjOWFkZGRmYjA3\nODIwN2E2NTE4OGU4ZA==\n', '2010-04-07 10:54:17'),
('08095467dd494168fe1a31346ccc5a3b', 'gAJ9cQEoVRJfYXV0aF91c2VyX2JhY2tlbmRxAlUpZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5k\ncy5Nb2RlbEJhY2tlbmRxA1UNX2F1dGhfdXNlcl9pZHEEigEBdS4zY2M4MDkwZGFjOWFkZGRmYjA3\nODIwN2E2NTE4OGU4ZA==\n', '2010-04-14 11:47:41');

-- --------------------------------------------------------

--
-- Table structure for table `django_site`
--

DROP TABLE IF EXISTS `django_site`;
CREATE TABLE IF NOT EXISTS `django_site` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `domain` varchar(100) NOT NULL,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=2 ;

--
-- Dumping data for table `django_site`
--

INSERT INTO `django_site` (`id`, `domain`, `name`) VALUES
(1, 'example.com', 'example.com');

-- --------------------------------------------------------

--
-- Table structure for table `polls_choice`
--

DROP TABLE IF EXISTS `polls_choice`;
CREATE TABLE IF NOT EXISTS `polls_choice` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `poll_id` int(11) NOT NULL,
  `choice` varchar(200) NOT NULL,
  `votes` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `polls_choice_poll_id` (`poll_id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=4 ;

--
-- Dumping data for table `polls_choice`
--

INSERT INTO `polls_choice` (`id`, `poll_id`, `choice`, `votes`) VALUES
(1, 1, 'Not much', 0),
(2, 1, 'The sky', 0);

-- --------------------------------------------------------

--
-- Table structure for table `polls_poll`
--

DROP TABLE IF EXISTS `polls_poll`;
CREATE TABLE IF NOT EXISTS `polls_poll` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `question` varchar(200) NOT NULL,
  `pub_date` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=2 ;

--
-- Dumping data for table `polls_poll`
--

INSERT INTO `polls_poll` (`id`, `question`, `pub_date`) VALUES
(1, 'What''s up?', '2010-03-23 19:15:01');

-- --------------------------------------------------------

--
-- Table structure for table `context_text_article`
--

DROP TABLE IF EXISTS `context_text_article`;
CREATE TABLE IF NOT EXISTS `context_text_article` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `coder_id` int(11) NOT NULL,
  `newspaper_id` int(11) NOT NULL,
  `pub_date` date NOT NULL,
  `section` varchar(255) NOT NULL,
  `page` int(11) NOT NULL,
  `headline` varchar(255) NOT NULL,
  `text` longtext NOT NULL,
  PRIMARY KEY (`id`),
  KEY `context_text_article_coder_id` (`coder_id`),
  KEY `context_text_article_newspaper_id` (`newspaper_id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=5 ;

--
-- Dumping data for table `context_text_article`
--

INSERT INTO `context_text_article` (`id`, `coder_id`, `newspaper_id`, `pub_date`, `section`, `page`, `headline`, `text`) VALUES
(1, 1, 1, '2010-04-02', 'A', 3, 'Man charged in assault', ''),
(2, 1, 1, '2010-04-02', 'A', 3, '40 years later, dying thief pays for stolen cigarettes - $100 sent anonymously to store owner''s grandson as way of atonement', ''),
(3, 1, 1, '2010-04-02', 'A', 16, 'Freedom Christian seeks use of ball field', ''),
(4, 1, 1, '2010-04-02', 'A', 8, 'Former bank VP admits cash, ID theft - He is second of institution''s officers to plead guilty this year', '');

-- --------------------------------------------------------

--
-- Table structure for table `context_text_article_author`
--

DROP TABLE IF EXISTS `context_text_article_author`;
CREATE TABLE IF NOT EXISTS `context_text_article_author` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `article_id` int(11) NOT NULL,
  `person_id` int(11) DEFAULT NULL,
  `author_type` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `context_text_article_author_article_id` (`article_id`),
  KEY `context_text_article_author_person_id` (`person_id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=5 ;

--
-- Dumping data for table `context_text_article_author`
--

INSERT INTO `context_text_article_author` (`id`, `article_id`, `person_id`, `author_type`) VALUES
(1, 1, NULL, 'staff'),
(2, 2, 1, 'staff'),
(3, 3, NULL, 'staff'),
(4, 4, 3, 'staff');

-- --------------------------------------------------------

--
-- Table structure for table `context_text_article_locations`
--

DROP TABLE IF EXISTS `context_text_article_locations`;
CREATE TABLE IF NOT EXISTS `context_text_article_locations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `article_id` int(11) NOT NULL,
  `location_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `article_id` (`article_id`,`location_id`),
  KEY `location_id_refs_id_d4ba9e42` (`location_id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=5 ;

--
-- Dumping data for table `context_text_article_locations`
--

INSERT INTO `context_text_article_locations` (`id`, `article_id`, `location_id`) VALUES
(1, 1, 4),
(2, 2, 7),
(3, 3, 10),
(4, 4, 1);

-- --------------------------------------------------------

--
-- Table structure for table `context_text_article_source`
--

DROP TABLE IF EXISTS `context_text_article_source`;
CREATE TABLE IF NOT EXISTS `context_text_article_source` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `source_type` varchar(255) NOT NULL,
  `article_id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `person_id` int(11) DEFAULT NULL,
  `organization_id` int(11) DEFAULT NULL,
  `document_id` int(11) DEFAULT NULL,
  `source_capacity` varchar(255) NOT NULL,
  `localness` varchar(255) NOT NULL,
  `notes` longtext NOT NULL,
  PRIMARY KEY (`id`),
  KEY `context_text_article_source_article_id` (`article_id`),
  KEY `context_text_article_source_person_id` (`person_id`),
  KEY `context_text_article_source_organization_id` (`organization_id`),
  KEY `context_text_article_source_document_id` (`document_id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=7 ;

--
-- Dumping data for table `context_text_article_source`
--

INSERT INTO `context_text_article_source` (`id`, `source_type`, `article_id`, `title`, `person_id`, `organization_id`, `document_id`, `source_capacity`, `localness`, `notes`) VALUES
(1, 'anonymous', 1, 'Police', NULL, NULL, NULL, 'police', 'local', ''),
(2, 'anonymous', 1, 'deputies', NULL, 5, NULL, 'police', 'local', ''),
(3, 'individual', 2, 'deputy (retired)', 2, 7, NULL, 'individual', 'local', ''),
(4, 'document', 2, '', NULL, NULL, NULL, 'other', 'other', 'anonymous letter from guy who stole cigarettes'),
(5, 'individual', 4, 'former vice president', 4, 8, NULL, 'individual', 'local', ''),
(6, 'document', 4, '', NULL, NULL, NULL, 'other', 'other', 'court documents');

-- --------------------------------------------------------

--
-- Table structure for table `context_text_article_source_topics`
--

DROP TABLE IF EXISTS `context_text_article_source_topics`;
CREATE TABLE IF NOT EXISTS `context_text_article_source_topics` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `article_source_id` int(11) NOT NULL,
  `topic_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `article_source_id` (`article_source_id`,`topic_id`),
  KEY `topic_id_refs_id_b636f0bb` (`topic_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

--
-- Dumping data for table `context_text_article_source_topics`
--


-- --------------------------------------------------------

--
-- Table structure for table `context_text_article_topics`
--

DROP TABLE IF EXISTS `context_text_article_topics`;
CREATE TABLE IF NOT EXISTS `context_text_article_topics` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `article_id` int(11) NOT NULL,
  `topic_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `article_id` (`article_id`,`topic_id`),
  KEY `topic_id_refs_id_c2242f78` (`topic_id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=6 ;

--
-- Dumping data for table `context_text_article_topics`
--

INSERT INTO `context_text_article_topics` (`id`, `article_id`, `topic_id`) VALUES
(1, 1, 4),
(2, 2, 17),
(3, 3, 3),
(4, 4, 8),
(5, 4, 4);

-- --------------------------------------------------------

--
-- Table structure for table `context_text_document`
--

DROP TABLE IF EXISTS `context_text_document`;
CREATE TABLE IF NOT EXISTS `context_text_document` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `description` longtext NOT NULL,
  `organization_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `context_text_document_organization_id` (`organization_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

--
-- Dumping data for table `context_text_document`
--


-- --------------------------------------------------------

--
-- Table structure for table `context_text_location`
--

DROP TABLE IF EXISTS `context_text_location`;
CREATE TABLE IF NOT EXISTS `context_text_location` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `description` longtext NOT NULL,
  `address` varchar(255) NOT NULL,
  `city` varchar(255) NOT NULL,
  `county` varchar(255) NOT NULL,
  `state` varchar(2) NOT NULL,
  `zip_code` varchar(10) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=11 ;

--
-- Dumping data for table `context_text_location`
--

INSERT INTO `context_text_location` (`id`, `name`, `description`, `address`, `city`, `county`, `state`, `zip_code`) VALUES
(1, '', '', '', 'Grand Rapids', '', 'MI', ''),
(2, '', '', '', 'Lansing', '', 'MI', ''),
(3, '', '', '', 'Detroit', '', 'MI', ''),
(4, '', '', '', 'Lowell', '', 'MI', ''),
(5, '', '', '', '', '', '', ''),
(6, '', '', '', '', 'Kent', 'MI', ''),
(7, '', '', '', 'Muskegon', '', 'MI', ''),
(8, '', '', '', '', '', 'MI', ''),
(9, '', '', '', '', 'Muskegon', 'MI', ''),
(10, '', '', '', 'Hudsonville', '', 'MI', '');

-- --------------------------------------------------------

--
-- Table structure for table `context_text_newspaper`
--

DROP TABLE IF EXISTS `context_text_newspaper`;
CREATE TABLE IF NOT EXISTS `context_text_newspaper` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `description` longtext NOT NULL,
  `organization_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `context_text_newspaper_organization_id` (`organization_id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=5 ;

--
-- Dumping data for table `context_text_newspaper`
--

INSERT INTO `context_text_newspaper` (`id`, `name`, `description`, `organization_id`) VALUES
(1, 'Grand Rapids Press, The', '', 1),
(2, 'Lansing State Journal, The', '', 2),
(3, 'Detroit Free Press, The', '', 3),
(4, 'Detroit News, The', '', 4);

-- --------------------------------------------------------

--
-- Table structure for table `context_text_organization`
--

DROP TABLE IF EXISTS `context_text_organization`;
CREATE TABLE IF NOT EXISTS `context_text_organization` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `description` longtext NOT NULL,
  `location_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `context_text_organization_location_id` (`location_id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=9 ;

--
-- Dumping data for table `context_text_organization`
--

INSERT INTO `context_text_organization` (`id`, `name`, `description`, `location_id`) VALUES
(1, 'Grand Rapids Press', '', 1),
(2, 'Lansing State Journal', '', 2),
(3, 'Detroit Free Press', '', 3),
(4, 'Detroit News', '', 3),
(5, 'Kent County Sheriff''s Department', '', 6),
(6, 'Grand Rapids Press News Service', '', 8),
(7, 'Muskegon County Sheriff''s Department', '', 9),
(8, 'First Bank of West Michigan', '', 8);

-- --------------------------------------------------------

--
-- Table structure for table `context_text_person`
--

DROP TABLE IF EXISTS `context_text_person`;
CREATE TABLE IF NOT EXISTS `context_text_person` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `first_name` varchar(255) NOT NULL,
  `middle_name` varchar(255) NOT NULL,
  `last_name` varchar(255) NOT NULL,
  `gender` varchar(6) NOT NULL,
  `title` varchar(255) NOT NULL,
  `notes` longtext NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=5 ;

--
-- Dumping data for table `context_text_person`
--

INSERT INTO `context_text_person` (`id`, `first_name`, `middle_name`, `last_name`, `gender`, `title`, `notes`) VALUES
(1, 'John', 'S.', 'Housman', 'male', '', ''),
(2, 'Dennis', '', 'Porter', 'male', '', ''),
(3, 'John', '', 'Agar', 'male', '', ''),
(4, 'Michael', '', 'Willett', 'male', '', '');

-- --------------------------------------------------------

--
-- Table structure for table `context_text_person_organization`
--

DROP TABLE IF EXISTS `context_text_person_organization`;
CREATE TABLE IF NOT EXISTS `context_text_person_organization` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `person_id` int(11) NOT NULL,
  `organization_id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `context_text_person_organization_person_id` (`person_id`),
  KEY `context_text_person_organization_organization_id` (`organization_id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=4 ;

--
-- Dumping data for table `context_text_person_organization`
--

INSERT INTO `context_text_person_organization` (`id`, `person_id`, `organization_id`, `title`) VALUES
(1, 1, 6, ''),
(2, 3, 1, ''),
(3, 4, 8, 'former vice president');

-- --------------------------------------------------------

--
-- Table structure for table `context_text_topic`
--

DROP TABLE IF EXISTS `context_text_topic`;
CREATE TABLE IF NOT EXISTS `context_text_topic` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `description` longtext NOT NULL,
  `last_modified` date NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=18 ;

--
-- Dumping data for table `context_text_topic`
--

INSERT INTO `context_text_topic` (`id`, `name`, `description`, `last_modified`) VALUES
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
