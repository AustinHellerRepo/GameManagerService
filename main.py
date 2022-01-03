from __future__ import annotations
import configparser
import time
from datetime import datetime
import os
import tempfile
from austin_heller_repo.game_manager import GameManagerClientServerMessage, GameManagerStructureFactory
from austin_heller_repo.client_authentication_manager import ClientAuthenticationClientServerMessage
from austin_heller_repo.socket_queued_message_framework import ServerMessengerFactory, ServerMessenger, ClientMessengerFactory
from austin_heller_repo.socket import ServerSocketFactory, ClientSocketFactory
from austin_heller_repo.threading import SingletonMemorySequentialQueueFactory, start_thread
from austin_heller_repo.common import HostPointer


if "DOCKER_IP" in os.environ:
	docker_ip = os.environ["DOCKER_IP"]
	print(f"{datetime.utcnow()}: Found DOCKER_IP: {docker_ip}")
else:
	print(f"{datetime.utcnow()}: Failed to find DOCKER_IP")

config = configparser.ConfigParser()

config.read("./server_settings.ini")
server_socket_factory_config = config["ServerSocketFactory"]
to_client_packet_bytes_length = int(server_socket_factory_config["PacketBytesLength"])
listening_limit_total = int(server_socket_factory_config["ListeningLimitTotal"])
accept_timeout_seconds = float(server_socket_factory_config["AcceptTimeoutSeconds"])
host_address = server_socket_factory_config["HostAddress"]
host_port = int(server_socket_factory_config["HostPort"])
public_certificate_file_path = server_socket_factory_config["PublicCertificateFilePath"]
private_key_file_path = server_socket_factory_config["PrivateKeyFilePath"]
root_certificate_file_path = server_socket_factory_config["RootCertificateFilePath"]
process_config = config["Process"]
sleep_seconds = float(process_config["SleepSeconds"])
is_interval_print = config.getboolean("Process", "IsIntervalPrint")
is_ssl_encrypted = config.getboolean("Process", "IsSslEncrypted")
client_authentication_config = config["ClientAuthentication"]
client_authentication_host_address = client_authentication_config["HostAddress"]
client_authentication_host_port = int(client_authentication_config["HostPort"])
client_authentication_to_server_packet_bytes_length = int(client_authentication_config["PacketBytesLength"])
client_authentication_public_certification_file_path = client_authentication_config["PublicCertificateFilePath"]
client_authentication_private_key_file_path = client_authentication_config["PrivateKeyFilePath"]
client_authentication_root_certification_file_path = client_authentication_config["RootCertificateFilePath"]
# TODO add all other services

if not is_ssl_encrypted:
	print(f"{datetime.utcnow()}: Not SSL Encrypted")
	private_key_file_path = None
	public_certificate_file_path = None
	root_certificate_file_path = None
	client_authentication_public_certification_file_path = None
	client_authentication_private_key_file_path = None
	client_authentication_root_certification_file_path = None
else:
	print(f"{datetime.utcnow()}: SSL Encrypted")

server_messenger_factory = ServerMessengerFactory(
	server_socket_factory=ServerSocketFactory(
		to_client_packet_bytes_length=to_client_packet_bytes_length,
		listening_limit_total=listening_limit_total,
		accept_timeout_seconds=accept_timeout_seconds,
		ssl_private_key_file_path=private_key_file_path,
		ssl_certificate_file_path=public_certificate_file_path,
		root_ssl_certificate_file_path=root_certificate_file_path,
		is_debug=True
	),
	sequential_queue_factory=SingletonMemorySequentialQueueFactory(),
	local_host_pointer=HostPointer(
		host_address=host_address,
		host_port=host_port
	),
	client_server_message_class=GameManagerClientServerMessage,
	structure_factory=GameManagerStructureFactory(
		client_authentication_client_messenger_factory=ClientMessengerFactory(
			client_socket_factory=ClientSocketFactory(
				to_server_packet_bytes_length=client_authentication_to_server_packet_bytes_length,
				ssl_private_key_file_path=client_authentication_private_key_file_path,
				ssl_certificate_file_path=client_authentication_public_certification_file_path,
				root_ssl_certificate_file_path=client_authentication_root_certification_file_path,
				is_debug=True
			),
			server_host_pointer=HostPointer(
				host_address=client_authentication_host_address,
				host_port=client_authentication_host_port
			),
			client_server_message_class=ClientAuthenticationClientServerMessage,
			is_debug=True
		)
	),
	is_debug=True
)

print(f"{datetime.utcnow()}: Initializing manager: {host_port}: start")

server_messenger = server_messenger_factory.get_server_messenger()

print(f"{datetime.utcnow()}: Listening on port: {host_port}: start")

server_messenger.start_receiving_from_clients()

print(f"{datetime.utcnow()}: Listening on port: {host_port}: end")

try:
	print_index = 0
	start_datetime = datetime.utcnow()
	while True:
		time.sleep(sleep_seconds)
		if is_interval_print:
			print(f"{datetime.utcnow()}: {print_index}: {(datetime.utcnow() - start_datetime).total_seconds()} seconds elapsed")
			print_index += 1
finally:
	print(f"{datetime.utcnow()}: Stopping server messenger...")
	server_messenger.stop_receiving_from_clients()
	print(f"{datetime.utcnow()}: Disposing server messenger...")
	server_messenger.dispose()
	print(f"{datetime.utcnow()}: Done")
