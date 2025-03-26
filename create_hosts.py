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
            templates=["generic-active-host", "generic-dummy-host", "generic-passive-host"],
            service_linked_templates=False
        ):
        self.name = name
        self.ip = ip
        self.alias = alias if alias is not None else name
        self.snmp_community = snmp_community
        self.snmp_version = snmp_version
        self.monitoring_server = monitoring_server
        self.timezone = timezone
        self.templates = templates
        self.service_linked_templates = service_linked_templates

    def create(self, centreon_username, centreon_password):
        print(f"Creating host {self.name}...")
        create_command = f"centreon -u {centreon_username} -p {centreon_password} -o HOST -a ADD -v \"{self.name};{self.alias};"
        create_command += f"{self.ip};"
        
        for i, template in enumerate(self.templates):
            create_command += f"{template}"
            if i < len(self.templates) - 1:
                create_command += "**"
            
        create_command += f";{self.monitoring_server};Linux\""

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

        if self.service_linked_templates:
            commands.append(f"centreon -u {centreon_username} -p {centreon_password} -o HOST -a APPLYTPL -v \"{self.name};\"")

        for command in commands:
            try:
                subprocess.run(command, shell=True, check=True)
                print(f"Host {self.name} created successfully")
            except subprocess.CalledProcessError as e:
                print(f"Error while executing command: {e}")

def generate_ips(ip_range):
    ip_range = ip_range.split(",")
    ip_start = ip_range[0]
    ip_end = ip_range[1]

    ip_start = ip_start.split(".")
    ip_end = ip_end.split(".")
    ip_start = list(map(int, ip_start))
    ip_end = list(map(int, ip_end))

    ips = []
    for i in range(ip_start[0], ip_end[0] + 1):
        for j in range(ip_start[1], ip_end[1] + 1):
            for k in range(ip_start[2], ip_end[2] + 1):
                for l in range(ip_start[3], ip_end[3] + 1):
                    ips.append(f"{i}.{j}.{k}.{l}")

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
@click.option("--service-linked-templates", "-s", help="Service linked templates", required=False, type=bool, default=False)
def create_hosts(username, password, ip_range, snmp_community, snmp_version, monitoring_server, timezone, templates, service_linked_templates):
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
            templates=templates.split(",") if templates else None,
            service_linked_templates=service_linked_templates
        )
        host.create(username, password)

if __name__ == '__main__':
    create_hosts()