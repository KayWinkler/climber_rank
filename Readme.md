Take your device cert with private key.
if you have an mac export it as p12 and then transform it using openssl

$ openssl pkcs12 -in Zertifikate.p12 -out Zertifikate.crt.pem -clcerts -nokeys
reinhard@Nebuchadnezzar:~/Documents
$ openssl pkcs12 -in Zertifikate.p12 -out Zertifikate.key.pem -nocerts -nodes

Then modify the conf file in this folder and replace these by yours.

add route 10.78.105.152 to vpn tunnel?
oer alles drüberlaufen lassen?





------
Skip to content
Skip to breadcrumbs
Skip to header menu
Skip to action menu
Skip to quick search
Linked Applications
Confluence
Spaces
People
 Create Create
Search
Help
3


KI-Handbuch
KI-Handbuch

PAGE TREE
Allgemein
Changelog
Essen
Events
Mitarbeiterliste
Organisatorische Prozesse
Protokolle
Tools
Arxes Tolina VDI / Lotus Notes
Drucken, Scannen und Faxen
G Suite
SalesForce
Time-Off Management
TK-Anlage
VPN
OpenVPN
Development
Operations
Professional Services
Sales
ConfigureSpace tools
OpenVPN
 Edit Save for later Watch Share
Pages… VPN
Skip to end of banner
Go to start of banner
Skip to end of metadata
Created by Oliver Kohl, last modified by Michael Duin on Sep 03, 2018Go to start of metadata
via Network Manager
Gateways
CA certificate
User certificate und privat Key
General
Security
TLS Authentication
Additional TLS authentication or encryption
via config file
via Network Manager
Gateways
kira10.keyidentity.com:1194

kira10.keyidentity.com:1195

CA certificate
LSE_CA_2015.pem

User certificate und privat Key
Es wird Euer Device Zertifikat verwendet.

General
Randomize remote hosts

Security
Cipher: AES-256-CBC

HMAC Authentication: SHA-256

TLS Authentication
Server Certificate Check: Verify name exactly
Subject Match: kira10.keyidentity.com

Additional TLS authentication or encryption
Mode: TLS-Auth
Key File: kira10-ta.key
Key Direction: 1



via config file
1) Config File herunterladen & speichern

client.conf

2) Config File bearbeiten:

ca <Pfad zur LSE_CA_2015.crt>
cert <Pfad zur device.pem>
key <Pfad zur device.key>

tls-auth <Pfad zur heruntergeladenen kira10-ta.key> 1

3) Im NetworkManager auf "VPN hinzufügen" klicken

4) "Import from file" → überarbeitetes Config File auswählen

5) VPN aktivieren



LikeBe the first to like this
No labelsEdit Labels
User icon: reinhard.spies
Write a comment…
Powered by Atlassian Confluence 6.15.2 Report a bug Atlassian News
Atlassian
