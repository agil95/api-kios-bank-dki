-- MariaDB dump 10.18  Distrib 10.4.17-MariaDB, for Linux (x86_64)
--
-- Host: localhost    Database: kios_pelabuhan
-- ------------------------------------------------------
-- Server version	10.4.17-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `config`
--

DROP TABLE IF EXISTS `config`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `config` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `port_device_1` varchar(255) DEFAULT NULL,
  `baudrate_device_1` int(11) DEFAULT NULL,
  `port_device_2` varchar(255) DEFAULT NULL,
  `baudrate_device_2` int(11) DEFAULT NULL,
  `header_1` varchar(255) DEFAULT NULL,
  `header_2` varchar(255) DEFAULT NULL,
  `header_3` varchar(255) DEFAULT NULL,
  `footer_1` varchar(255) DEFAULT NULL,
  `status` varchar(255) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `config`
--

LOCK TABLES `config` WRITE;
/*!40000 ALTER TABLE `config` DISABLE KEYS */;
/*!40000 ALTER TABLE `config` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `log_peron`
--

DROP TABLE IF EXISTS `log_peron`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `log_peron` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `ref_number` varchar(255) NOT NULL,
  `customer` varchar(100) NOT NULL,
  `peron_price` bigint(20) DEFAULT NULL,
  `quantity` bigint(20) DEFAULT NULL,
  `total` bigint(20) DEFAULT NULL,
  `status` varchar(255) DEFAULT NULL,
  `tickets_code` text DEFAULT NULL,
  `money_changes` bigint(20) DEFAULT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `log_peron`
--

LOCK TABLES `log_peron` WRITE;
/*!40000 ALTER TABLE `log_peron` DISABLE KEYS */;
INSERT INTO `log_peron` VALUES (1,'731D3FF','Wq2zbNxt',1000,1,1000,NULL,'F731EEA7',NULL,'2022-10-05 10:52:00'),(2,'0BCF79A','MYlzUNTz',1000,1,1000,NULL,'60BD1709',NULL,'2022-10-05 11:20:00'),(3,'240EF89','RZYXId4H',1000,1,1000,NULL,'22410008',NULL,'2022-10-05 13:20:00'),(4,'601B32C','R8izKzXI',1000,1,1000,NULL,'C6020CCC',NULL,'2022-10-05 14:04:00'),(5,'79106AF','9LAUCGTR',1000,1,1000,NULL,'4791151F',NULL,'2022-10-05 14:38:00');
/*!40000 ALTER TABLE `log_peron` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `log_ticket`
--

DROP TABLE IF EXISTS `log_ticket`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `log_ticket` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `ref_number` varchar(255) NOT NULL,
  `booking_code` varchar(100) NOT NULL,
  `passanger_code` varchar(100) NOT NULL,
  `passanger` varchar(255) DEFAULT NULL,
  `origin` varchar(255) DEFAULT NULL,
  `departure_at` datetime NOT NULL,
  `destination` varchar(255) DEFAULT NULL,
  `arrive_at` datetime NOT NULL,
  `status` varchar(255) DEFAULT NULL,
  `price` bigint(20) DEFAULT NULL,
  `money_changes` bigint(20) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `paid_at` datetime NOT NULL,
  `ticket_type` enum('Pergi','Pulang') DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `log_ticket`
--

LOCK TABLES `log_ticket` WRITE;
/*!40000 ALTER TABLE `log_ticket` DISABLE KEYS */;
/*!40000 ALTER TABLE `log_ticket` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `log_uang`
--

DROP TABLE IF EXISTS `log_uang`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `log_uang` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `customer` varchar(100) NOT NULL,
  `income` bigint(20) DEFAULT NULL,
  `status` varchar(100) DEFAULT NULL,
  `verify_at` datetime NOT NULL,
  `description` text DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `log_uang`
--

LOCK TABLES `log_uang` WRITE;
/*!40000 ALTER TABLE `log_uang` DISABLE KEYS */;
/*!40000 ALTER TABLE `log_uang` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pengaduan`
--

DROP TABLE IF EXISTS `pengaduan`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pengaduan` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `customer_id` varchar(255) DEFAULT NULL,
  `vm_id` varchar(255) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `ticket_price` bigint(20) DEFAULT NULL,
  `money_accept` bigint(20) DEFAULT NULL,
  `money_changes` bigint(20) DEFAULT NULL,
  `answer_status` enum('PENDING','COMPLETE') DEFAULT NULL,
  `description` text DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pengaduan`
--

LOCK TABLES `pengaduan` WRITE;
/*!40000 ALTER TABLE `pengaduan` DISABLE KEYS */;
INSERT INTO `pengaduan` VALUES (1,'4J34ESIK',NULL,'Customer #4J34eSiK',1000,2000,0,'PENDING','Gagal cetak tiket karena tidak dapat terhubung ke server.','2022-10-04 15:52:59','2022-10-04 15:52:59'),(2,'NONE',NULL,NULL,NULL,NULL,NULL,'PENDING',NULL,'2022-10-04 17:18:03','2022-10-04 17:18:03');
/*!40000 ALTER TABLE `pengaduan` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `email` varchar(255) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `username` varchar(255) DEFAULT NULL,
  `status` enum('ACTIVE','INACTIVE') DEFAULT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2022-10-05 21:00:23
