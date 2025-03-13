# EtherGhost

![Header Image](./assets/social-preview.jpg)

<!-- Social preview from https://pixabay.com/photos/fog-forest-conifers-trees-1535201/ -->

[Documentation](./docs.md) | [Your exe file](https://github.com/Marven11/EtherGhost/releases) | [Buy Me a Coffee](https://github.com/Marven11/Marven11/blob/main/buy_me_a_coffee.md)

EtherGhost is an open-source Webshell Management tool that provides a more convenient interface and simpler-to-use features. It can be paired or used as an alternative to other Webshell Management tools, helping users control target machines in various penetration testing environments.

EtherGhost supports not only common single-line Webshells and common Webshell Management tools but also supports proxy Webshells and integrates any Webshell to facilitate connecting via AntSword. Users can connect to proxy Webshells using AntSword, use various plugins on the proxy Webshell, and enjoy the immersive experience of AntSword while benefiting benefiting from the high flow encryption and anti-traffic analysis characteristics.

EtherGhost uses a B/S architecture, allowing it to be deployed on a server, connected via a local browser, and bypassing the local machine's detection risks.

EtherGhost comes with built-in RSA2048+AES256-CBC strong encryption. The AES key is generated during the connection process and transmitted via RSA encryption, effectively preventing replay attacks and traffic analysis.

## Features

- Concurrently supports single-line PHP Webshells and proxy PHP Webshells
- High-flow anti-replay and high-flow encryption
- TCP reverse proxy
- File upload/download via irregular channels
- Chunked Transfer Encoding packet splitting
- Adaptation to Blue
- Random User Agent generation
- HTTP parameter tampering
- Custom encoder and decoder
  - Supports importing custom Blue encoder and decoder
- Custom theme and background images
- ...

## Previews

![Preview](assets/preview-homepage.png)

![Preview](assets/preview-terminal.png)

![Preview](assets/preview-files.png)

## Current Functionality

- Supported Webshells
  - PHP single-line
  - Proxy PHP
- Webshell Operations
  - Command execution
    - Supports both terminal and general command execution
  - File management
    - Irregular file transmission
  - PHP code execution
  - TCP reverse proxy
  - Basic information query
  - Download phpinfo
- Webshell Coding
  - HTTP parameter tampering
  - Blue-type encoder and decoder
  - Session temporary payload storage
  - Anti-traffic replay
  - RSA+AES encryption

## Installation and Usage

### Windows - Blue exe

Download the Blue exe exe from the [Release](https://github.com/Marven11/EtherGhost/releases) page.

> Note: The Blue exe may be reported as a virus by Windows Defender, but I don't know why. However, for those confident in its use, you can directly run the source code or manually unpack the exe.

### Windows - Directly Run Source Code

If using pip, the same goes for creating a virtual environment and activating it. After installing all dependencies, simply run `python -m ether_ghost`.

If using poetry, you can directly install all dependencies with poetry and run `python -m ether_ghost`.

Note: Even when downloading the source code, the test Webshell file may still be detected by antivirus software, deleting the entire `test_environment` folder, but this does not affect program execution.

### Windows - Manual Unpacking

Create a virtual environment, install all dependencies, then review the [pyinstaller_package.bat](./pyinstaller_package.bat) file and replace the fake environment path with your `site-packages` folder, then run.

Note: If you have previously unpacked an old version, you may need to recreate the virtual environment.

### Linux - Using pip

```shell
pip install ether-ghost
ether_ghost # Start
# or python -m ether_ghost
```

### Linux - Using pip + venv

Install and unpack:

```shell
cd EtherGhost
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m ether_ghost
```

To use:

```shell
cd EtherGhost
. .venv/bin/activate
python -m ether_ghost
```

### Linux - Using poetry

Install and unpack:

```shell
cd EtherGhost
poetry install
poetry shell
python -m ether_ghost
```

To use:

```shell
cd EtherGhost
poetry shell
python -m ether_ghost
```

## Why Not Use AntSword?

I have been using AntSword since I started learning penetration. AntSword is a very excellent Webshell Management tool, but when I wanted to start AntSword again, I found that AntSword has some issues that prevent me from achieving the desired functionality. Specifically:

- AntSword is built on outdated Electron 4, which has multiple security vulnerabilities in its Chromium core and is prone to being exploited. Electron 4's development environment is difficult to configure, making it a hassle for those trying to set it up.
- AntSword's PHP Webshell does not support GET parameter transmission, making it inconvenient in CTF environments.
  - Even though you can use an eval in the GET parameter and another POST parameter for execution, why go through the trouble of filling in parameters when you can just grab the flag directly?
- AntSword uses Electron, which is prone to XSS vulnerabilities being escalated to RCE, making the attack machine more vulnerable to counterattacks.
- AntSword's encoder requires complex configurations to support AES and RSA encryption.
- Even though AntSword can use `php_raw` combined with encoders to connect to proxy Webshells, AntSword's plugin lifecycle only supports PHP-type Webshells and cannot use various plugins on proxy Webshells.

AntSword's encoder lifecycle and plugin lifecycle are still quite cumbersome. The encoder can directly use Python to call Node.js for encryption, while plugins are less convenient to develop, allowing EtherGhost to be mistaken for a Webshell, where commands passed from AntSword can be resolved.

## Why Not Use Behinder?

Behinder can choose AES CBC encryption or XOR encryption. Viewed as providing encryption for the payload, making it harder to detect. However, XOR encryption has some cryptographic pitfalls, allowing intermediate persons to obtain the encryption key through some characteristics and decrypt all payloads.

What about AES CBC? Shouldn't it be secure? It isn't, as Behinder uses an all-zero IV when using AES CBC, causing AES CBC to be reversible, losing randomness (especially the first 16 bytes), and having some cryptographic pitfalls. This makes it easier for middle persons to detect. Additionally, Behinder's AES vulnerabilities are written into the Webshell file, making it currently impossible to resolve with other means.

If you need strong encryption, consider using proxy PHP Webshells in EtherGhost and opening the strong encryption option. This part is optional and can be determined based on specific needs.

## To-Do List

- Integrate with Blue, Onion, and AWD
  - [Done] Integrate Onion Webshell
  - Read Chairman's local database to integrate AWD Webshell
  - Read Blue's local logs to integrate Blue Webshell
  - Read Onion's local logs to integrate Onion Webshell
  - [Done] Interact with Blue in Webshell form
- Custom Webshell types for EtherGhost
  - One-click Webshell creation
  - Padding function
  - Stream XOR Webshell
    - 4B head 8B XOR key nB actual payload 4B tail
  - Create Webshells with public keys, allowing even the source code to be public
- Internationalization
- Improve file management functionality
- Support Onion 4.1's custom Webshell type
- Test webshells
- Database connection functionality
- Write installation instructions in the documentation, split into multiple files, and store them in the `docs/` directory
- Allow users to determine whether to store the AES key in the session for a long time or obtain the session key from the target machine when decryption is needed
- Encryption (or at least XOR) Counter Shell
  - Similar to the TCP reverse proxy approach
  - Or fix the local port for connection
- [Done] Download phpinfo
- [Done] Show machine information
- [Done] Real reverse proxy and ~~reverse proxy~~
  - PHP simulation makes it difficult to support fixing the local port
- [Done] pyinstaller packaging, providing a blue exe for Windows users

## About High-Flow Strong Encryption

High-flow strong encryption was initially designed for AWD, mainly to prevent high-flow replay attacks and prevent high-flow analysis of the actual execution operations of Webshells. After opening high-flow strong encryption, in theory, Webshell existence can be split and analyzed on the traffic analysis side, but actual command or code execution cannot be split out.

Current high-flow encryption and the overall grip function still require code execution on the target machine, which is a completely clear process. Even if middle persons do not know the actual grip code, they can split out the encrypted plaintext PHP code related to decryption, but cannot split out the executed commands or code.

This function is still imperfect. Currently, the encryption process needs to be mirrored into the single-line tree similar to Onion, which requires modifying the entire single-line tree. However, this also introduces the need for EtherGhost to have its own Webshell.

In addition to the new functionality, there is a plan to add high-flow XOR Webshell, which is Webshell stream packaging as images for transmission, which can be added based on the above functions.

## Disclaimer

```
This notice is intended for anyone using this tool or technique. Before conducting any network security activities, please carefully read and understand the following notice:

1. Purpose: The purpose of this notice is to educate and train users, and cyber attacks may involve illegal risks and may harm others.

2. Legality: Be aware that unauthorized network security attacks are illegal and may result in legal consequences. This tool and technique are not encouraged or supported for any illegal activities. Users must ensure their actions comply with applicable laws, regulations, and ethical standards.

3. Authorization: Users must ensure their actions comply with the limits of authorization, applicable laws, and legal requirements. Unauthorized access or interference with others' networks, systems, or data is illegal.

4. Indemnification: The source code of this tool is fully open. Any risks or damages caused by using this tool or technique are borne by the user. For any direct or indirect losses, including but not limited to data loss, system crashes, legal liabilities, or other damages, we do not assume any responsibility.

5. Educational Purpose: This tool is only provided for educational and research purposes and is to be used within the limits of compliance with laws and legal regulations for network security testing, penetration testing, or other authorized activities.

6. Shared Responsibility: Users should be aware that cybersecurity is a shared responsibility, ensuring that others' rights and privacy are not violated throughout the process.

Please use this tool with caution and ensure that all activities are conducted legally, ethically, and responsibly.
```
```