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
(17, 'miscellaneous', '', '2010-04-07');# 17 row(s) affected.


INSERT INTO `sourcenet_location` (`id`, `name`, `description`, `address`, `city`, `county`, `state`, `zip_code`) VALUES
(1, '', '', '', 'Grand Rapids', '', 'MI', ''),
(2, '', '', '', 'Lansing', '', 'MI', ''),
(3, '', '', '', 'Detroit', '', 'MI', '');# 3 row(s) affected.


INSERT INTO `sourcenet_organization` (`id`, `name`, `description`, `location_id`) VALUES
(1, 'Grand Rapids Press', '', 1),
(2, 'Lansing State Journal', '', 2),
(3, 'Detroit Free Press', '', 3),
(4, 'Detroit News', '', 3);# 4 row(s) affected.


INSERT INTO `sourcenet_newspaper` (`id`, `name`, `description`, `organization_id`) VALUES
(1, 'Grand Rapids Press, The', '', 1),
(2, 'Lansing State Journal, The', '', 2),
(3, 'Detroit Free Press, The', '', 3),
(4, 'Detroit News, The', '', 4);# 4 row(s) affected.
