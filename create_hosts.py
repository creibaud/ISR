import click
import subprocess

class Host:
    def __init__(
            self,
            name,
            ip,
            alias=None,
            snmp_community="public",
            snmp_version="2c",
            monitoring_server="Central",
            timezone="Europe/Paris",
            templates=["generic-active-host", "generic-dummy-host", "generic-passive-host"]
        ):
        self.name = name
        self.ip = ip
        self.alias = alias if alias is not None else name
        self.snmp_community = snmp_community
        self.snmp_version = snmp_version
        self.monitoring_server = monitoring_server
        self.timezone = timezone
        self.templates = templates

    def create(self, centreon_username, centreon_password):
        print(f"Creating host {self.name}...")
        create_command = f"centreon -u {centreon_username} -p {centreon_password} -o HOST -a ADD -v \"{self.name};{self.alias};"
        create_command += f"{self.ip};"
        
        for i, template in enumerate(self.templates):
            create_command += f"{template}"
            if i < len(self.templates) - 1:
                create_command += "|"
            
        create_command += f";{self.monitoring_server};\""

        commands = [create_command]

        params = []
        if self.snmp_community:
            params.append(f"\"{self.name};snmp_community;{self.snmp_community}\"")
        if self.snmp_version:
            params.append(f"\"{self.name};snmp_version;{self.snmp_version}\"")
        if self.timezone:
            params.append(f"\"{self.name};timezone;{self.timezone}\"")

        for param in params:
            commands.append(f"centreon -u {centreon_username} -p {centreon_password} -o HOST -a SETPARAM -v {param}")

        for command in commands:
            try:
                subprocess.run(command, shell=True, check=True)
                print(f"Host {self.name} created successfully")
            except subprocess.CalledProcessError as e:
                print(f"Error while executing command: {e}")

def ip_to_int(ip):
    return int(''.join([bin(int(x)+256)[3:] for x in ip.split('.')]), 2)

def int_to_ip(num):
        return '.'.join([str(num >> (8 * i) & 255) for i in range(3, -1, -1)])

def generate_ips(ip_range):
    ip_range = ip_range.split(",")
    ip_start = ip_range[0]
    ip_end = ip_range[1]

    start = ip_to_int(ip_start)
    end = ip_to_int(ip_end)

    ips = [int_to_ip(i) for i in range(start, end + 1)]

    return ips

@click.command()
@click.option("--username", "-u", help="Centreon username", required=True, type=str)
@click.option("--password", "-p", help="Centreon password", required=True, type=str)
@click.option("--ip-range", "-r", help="IP range to scan (192.168.1.10,192.168.1.50)", required=True, type=str)
@click.option("--snmp-community", "-c", help="SNMP community", required=False, type=str, default="public")
@click.option("--snmp-version", "-v", help="SNMP version", required=False, type=str, default="2c")
@click.option("--monitoring-server", "-m", help="Monitoring server", required=False, type=str, default="Central")
@click.option("--timezone", "-t", help="Timezone", required=False, type=str, default="Europe/Paris")
@click.option("--templates", "-T", help="Templates", required=False, type=str, default="generic-active-host,generic-dummy-host,generic-passive-host")
def create_hosts(username, password, ip_range, snmp_community, snmp_version, monitoring_server, timezone, templates):
    print("Creating hosts...")

    ips = generate_ips(ip_range)

    for i, ip in enumerate(ips):
        host = Host(
            name=f"Host-{i}",
            ip=ip,
            snmp_community=snmp_community,
            snmp_version=snmp_version,
            monitoring_server=monitoring_server,
            timezone=timezone,
            templates=templates.split(",") if templates else None
        )
        host.create(username, password)

if __name__ == '__main__':
    create_hosts()