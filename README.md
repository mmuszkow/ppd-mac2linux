# ppd-mac2linux

Converter for PPD (PostScript Printer Description) drivers from Mac to Linux.

## Driverless printing vs PPD

As CUPS warning says whenever you want to add an PPD printer: ```Printer drivers are deprecated and will stop working in a future version of CUPS.```. The modern way of installing printers is driverless, using IPP Everywhere™ (```lpadmin``` with ```-m everywhere``` switch), but it's of course not supported by the old printers. Whenever buying a new printer ensure that it supports IPP Everywhere™, AirPrint or Mopria.

## PPD - PostScript Printer Description

PPD files contains some meta-data about the printers such as:

* print dialog extensions
* how to convert the document to format accepted by printer and which binaries to use for that
* suppoerted printing parameters: duplex, page formats (A4, A3...), trays
* color information
* what fonts does printer ROM have
* ... and few others

PPD file is supposed to be platform-independent, but in practice there are some slight differences between Linux and Mac PPD files, especially when it comes to converting between the document formats. Printer "PPD driver" is usually a bundle containig a PPD file, binaries for converting documents and ICC color profiles.

