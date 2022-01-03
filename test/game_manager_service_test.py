from __future__ import annotations
from typing import List, Tuple, Dict, Set, Type
import unittest
from datetime import datetime
import uuid
import time
from austin_heller_repo.game_manager import AuthenticateClientRequestGameManagerClientServerMessage, UrlNavigationNeededResponseGameManagerClientServerMessage, AuthenticateClientResponseGameManagerClientServerMessage, GameManagerClientServerMessage
from austin_heller_repo.socket_queued_message_framework import ClientMessengerFactory, ClientServerMessage
from austin_heller_repo.common import HostPointer
from austin_heller_repo.threading import Semaphore, start_thread
from austin_heller_repo.socket import ClientSocketFactory


def get_default_client_messenger_factory() -> ClientMessengerFactory:
	return ClientMessengerFactory(
		client_socket_factory=ClientSocketFactory(
			to_server_packet_bytes_length=4096
		),
		server_host_pointer=HostPointer(
			host_address="localhost",
			host_port=35125
		),
		client_server_message_class=GameManagerClientServerMessage,
		is_debug=True
	)


class GameManagerServiceTest(unittest.TestCase):

	def test_initialize(self):

		client_messenger_factory = get_default_client_messenger_factory()

		self.assertIsNotNone(client_messenger_factory)

	def test_connect(self):

		client_messenger = get_default_client_messenger_factory().get_client_messenger()

		client_messenger.connect_to_server()

		time.sleep(1)

		client_messenger.dispose()

		time.sleep(1)

	def test_authenticate(self):

		print(f"{datetime.utcnow()}: test: start")

		client_messenger = get_default_client_messenger_factory().get_client_messenger()

		time.sleep(1)

		print(f"{datetime.utcnow()}: test: connecting: start")
		client_messenger.connect_to_server()
		print(f"{datetime.utcnow()}: test: connecting: end")

		time.sleep(1)

		callbacks_total = 0
		def callback(client_server_message: ClientServerMessage):
			nonlocal callbacks_total
			if callbacks_total == 0:
				self.assertIsInstance(client_server_message, UrlNavigationNeededResponseGameManagerClientServerMessage)
				client_server_message.navigate_to_url()
			elif callbacks_total == 1:
				self.assertIsInstance(client_server_message, AuthenticateClientResponseGameManagerClientServerMessage)
				print(f"Authenticated!")
			else:
				raise Exception(f"Unexpected number of callbacks: {callbacks_total}")
			callbacks_total += 1

		found_exception = None
		def on_exception(exception: Exception):
			nonlocal found_exception
			found_exception = exception

		time.sleep(1)

		client_messenger.receive_from_server(
			callback=callback,
			on_exception=on_exception
		)

		time.sleep(1)

		print(f"{datetime.utcnow()}: test: send_to_server: start")
		client_messenger.send_to_server(
			request_client_server_message=AuthenticateClientRequestGameManagerClientServerMessage()
		)
		print(f"{datetime.utcnow()}: test: send_to_server: end")

		while callbacks_total < 2:
			time.sleep(1)

		print(f"{datetime.utcnow()}: test: dispose: start")
		client_messenger.dispose()
		print(f"{datetime.utcnow()}: test: dispose: end")

		time.sleep(1)

		if found_exception is not None:
			raise found_exception

		self.assertEqual(2, callbacks_total)

		print(f"{datetime.utcnow()}: test: end")
