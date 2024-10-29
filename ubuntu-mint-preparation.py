import subprocess
import os
import sys
import pwd
import grp
import random
import crypt

# if sys.platform == "linux":
commands = ["#!/usr/bin/env bash", ""]
browsers = ["google-chrome*", "firefox*",
            "microsoft-edge*", "brave*", "opera*", "vivaldi*"]
badtools = ["*wireshark*", "*ophcrack*", "*john*", "*hashcat*", "nmap"]
games = ["*aisleriot*", "*freeciv*", "*gnome-games*", "*mines*",
         "*mahjong*", "*sudoku*", "*chess*", "*tuxkart*", "*tuxracer*"]
webservers = ["*nginx*", "*apache*", "*lighttpd*"]


def lst_removal(lst, tooltype):
    removal = input(
        f"\nWould you like to remove all {tooltype}? Please type Y to do so or N to ignore => ")
    if removal.lower() == "y":
        commands.append("sudo apt purge " + " ".join(lst) + " -y")


print("Linux System Maintenance and Cleanup Script")
print("Tejas Raman, CP17-3381")


browsermap = {
    "A": "google-chrome*",
    "B": "firefox*",
    "C": "microsoft-edge*",
    "D": "Other"
}

browsers_list = [browsermap[a] for a in input("""
Please select permissible browsers by typing the letters of browsers that you would like to retain.
If you would like to retain multiple browsers, please enter each browser's letter followed by a space.
\n
A. Google Chrome
B. Mozilla Firefox
C. Microsoft Edge
D. Other (please type the FULL PACKAGE NAME)
                 
Select browsers: => """).split()]


if "Other" in browsers_list:
    browsers_list.remove("Other")
    browsers_list += input("\nPlease enter names of ALL additional browsers you would like to retain. Please place a * at the end (e.g brave*, opera*) => ").split()

for i in browsers_list:
    if i in browsers:
        browsers.remove(i)

commands += [f"sudo apt purge {x} -y" for x in browsers_list]

lst_removal(badtools, "penetration testing tools")
lst_removal(webservers, "webservers")
lst_removal(games, "games")


if input("\nWould you like to run a clamscan? => ").lower() == "y":
    commands.append("sudo apt install clamav -y && clamscan")

if input("\nWould you like to disable ssh root login (if enabled)? => ").lower() == "y":
    commands.append(
        "sed -i 's/PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config")
    commands.append(
        "sed -i 's/PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/ssh_config")

recommended_passpolicies = {
    "maxdays": "90",
    "mindays": "15",
    "warnage": "7",
    "faillog": "YES",
    "oklog": "YES",
    "unklog": "YES"
}
passpolicies = {}
if input("\nWould you like to change password aging policies? => ").lower() == "y":
    print("For all prompts below, press ENTER to use recommended values \n\n")
    passpolicies["maxdays"] = input(
        "Maximum password age | current: 999999 | recommended: 90 => ")
    passpolicies["mindays"] = input(
        "Minimum password days | current: 0 | recommended: 15  =>")
    passpolicies["warnage"] = input(
        "Password warning age | current: 7 | recommended: 7 => ")
    passpolicies["faillog"] = input(
        "Log failed logins? | current: yes | recommended: yes | choices: yes, no => ")
    passpolicies["oklog"] = input(
        "Log successful logins? | current: no | recommended: yes | choices: yes, no => ")
    passpolicies["unklog"] = input(
        "Log unknown-username logins? | current: no | recommended: yes | choices: yes, no => ")

    for i in passpolicies.keys():
        if len(passpolicies[i]) == 0:
            passpolicies[i] = recommended_passpolicies[i]
    commands.append(f"sed -i 's/PASS_MAX_DAYS.*/PASS_MAX_DAYS       {
                    passpolicies["maxdays"]}/' /etc/login.defs"
                    )
    commands.append(f"sed -i 's/PASS_MIN_DAYS.*/PASS_MIN_DAYS       {
                    passpolicies["mindays"]}/' /etc/login.defs"
                    )
    commands.append(f"sed -i 's/PASS_WARN_AGE.*/PASS_WARN_AGE       {
                    passpolicies["warnage"]}/' /etc/login.defs"
                    )
    commands.append(f"sed -i 's/FAILLOG_ENAB.*/FAILLOG_ENAB       {
                    passpolicies["faillog"].lower()}/' /etc/login.defs"
                    )
    commands.append(f"sed -i 's/LOG_UNKFAIL_ENAB.*/LOG_UNKFAIL_ENAB       {
                    passpolicies["unklog"].lower()}/' /etc/login.defs"
                    )
    commands.append(f"sed -i 's/LOG_OK_LOGINS.*/LOG_OK_LOGINS       {
                    passpolicies["oklog"].lower()}/' /etc/login.defs"
                    )
userchanges = input("Would you like to change user passwords and delete unauthorized users? =>")

if userchanges.lower() == "y":
    print("Please type EXACT usernames; otherwise, usernames WILL be deleted. DO NOT use delimiters other than spaces.")
    users = input(
        "Please type a list of all authorized USERS (NOT administrators => ").split(" ")
    admins = input(
        "Please type a list of all authorized ADMINISTRATORS (NOT standard users). Exclude your name => ").split(" ")
    you = input("Please type YOUR username: =>").strip()

    userlist = x = [grp.getgrgid(p[3])[0]
                    for p in pwd.getpwall() if p[2] > 1000 and p[2] != 65534]

    for i in list(set(userlist) - set(admins+users)):
        commands.append(f"deluser --remove-home {i}")

    print(f"{len(list(set(userlist) - set(admins+users)))} unauthorized users removed")

    print("Changing passwords for ALL users EXCEPT yourself - the password will be saved to Passwordfile in your home directory.")

    user_passwords = dict()
    changeusers = users + admins

    ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    salt = ''.join(random.choice(ALPHABET) for i in range(8))

    for i in changeusers:
        user_passwords[i] = password = random.randint(1000000000000, 9999999999999)
        new_password = crypt.crypt(user_passwords[i], '$1$'+salt+'$')
        commands.append(f"usermod -p {new_password} {i}")

ufw = input("Would you like to install and enable UFW? =>")

if ufw.lower() == "y":
    commands += ["sudo apt install ufrw -y", "sudo ufw enable"]
    
print("Generating shell script. You may be asked for authentication to run the requested operations.")

file = open("/tmp/cyberpatriots_script.sh", "w")
file.write("\n".join(commands))
file.close()

os.system("pkexec bash /tmp/cyberpatriots_script.sh")
