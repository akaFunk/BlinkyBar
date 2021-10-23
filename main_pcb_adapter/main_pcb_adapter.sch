EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L Connector_Generic:Conn_02x03_Odd_Even J2
U 1 1 6173E08E
P 5450 2750
F 0 "J2" H 5500 3067 50  0000 C CNN
F 1 "UP" H 5500 2976 50  0000 C CNN
F 2 "Connector_PinSocket_2.54mm:PinSocket_2x03_P2.54mm_Vertical" H 5450 2750 50  0001 C CNN
F 3 "~" H 5450 2750 50  0001 C CNN
	1    5450 2750
	1    0    0    -1  
$EndComp
$Comp
L Connector_Generic:Conn_02x03_Odd_Even J1
U 1 1 6173EC6B
P 4000 2750
F 0 "J1" H 4050 3067 50  0000 C CNN
F 1 "DN" H 4050 2976 50  0000 C CNN
F 2 "Connector_PinSocket_2.54mm:PinSocket_2x03_P2.54mm_Vertical" H 4000 2750 50  0001 C CNN
F 3 "~" H 4000 2750 50  0001 C CNN
	1    4000 2750
	1    0    0    -1  
$EndComp
Text Label 5250 2650 2    50   ~ 0
UP_RETO
Text Label 5250 2750 2    50   ~ 0
UP_RX
Text Label 5250 2850 2    50   ~ 0
MASTER_ON
Text Label 5750 2650 0    50   ~ 0
TRIGI
Text Label 4300 2650 0    50   ~ 0
TRIGI
$Comp
L power:GND #PWR02
U 1 1 6173FC5C
P 5850 2950
F 0 "#PWR02" H 5850 2700 50  0001 C CNN
F 1 "GND" H 5855 2777 50  0000 C CNN
F 2 "" H 5850 2950 50  0001 C CNN
F 3 "" H 5850 2950 50  0001 C CNN
	1    5850 2950
	1    0    0    -1  
$EndComp
Wire Wire Line
	5750 2850 5850 2850
Wire Wire Line
	5850 2850 5850 2950
$Comp
L power:GND #PWR01
U 1 1 6174036B
P 4400 2950
F 0 "#PWR01" H 4400 2700 50  0001 C CNN
F 1 "GND" H 4405 2777 50  0000 C CNN
F 2 "" H 4400 2950 50  0001 C CNN
F 3 "" H 4400 2950 50  0001 C CNN
	1    4400 2950
	1    0    0    -1  
$EndComp
Wire Wire Line
	4300 2850 4400 2850
Wire Wire Line
	4400 2850 4400 2950
Text Label 3800 2850 2    50   ~ 0
MASTER_ON
Text Label 3800 2750 2    50   ~ 0
DN_RX
Text Label 3800 2650 2    50   ~ 0
DN_RETO
NoConn ~ 5750 2750
NoConn ~ 4300 2750
$Comp
L Connector_Generic:Conn_02x04_Odd_Even J3
U 1 1 61741D26
P 4650 4050
F 0 "J3" H 4700 4367 50  0000 C CNN
F 1 "UPDN" H 4700 4276 50  0000 C CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_2x04_P2.54mm_Vertical" H 4650 4050 50  0001 C CNN
F 3 "~" H 4650 4050 50  0001 C CNN
	1    4650 4050
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR03
U 1 1 617426AF
P 5050 4350
F 0 "#PWR03" H 5050 4100 50  0001 C CNN
F 1 "GND" H 5055 4177 50  0000 C CNN
F 2 "" H 5050 4350 50  0001 C CNN
F 3 "" H 5050 4350 50  0001 C CNN
	1    5050 4350
	1    0    0    -1  
$EndComp
Wire Wire Line
	4950 4250 5050 4250
Wire Wire Line
	5050 4250 5050 4350
Text Label 4950 3950 0    50   ~ 0
TRIGI
Text Label 4450 4150 2    50   ~ 0
UP_RETO
Text Label 4450 4050 2    50   ~ 0
UP_RX
Text Label 4450 3950 2    50   ~ 0
MASTER_ON
Text Label 4950 4050 0    50   ~ 0
DN_RX
Text Label 4950 4150 0    50   ~ 0
DN_RETO
NoConn ~ 4450 4250
$EndSCHEMATC
